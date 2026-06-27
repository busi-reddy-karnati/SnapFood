"""Gemini-backed parsing and generation. Mirrors Fitnesswispr's gemini_service:
same client setup, gemini-2.5-flash, JSON response mode, temperature 0.1,
thinking disabled, async via asyncio.to_thread, and the {"parse_error": true}
convention.
"""
import asyncio
import json
import logging

from fastapi import HTTPException
from google import genai
from google.genai import types

from app.config import settings

# Disable Gemini 2.5 "thinking" for extraction/generation tasks — it adds large
# latency on structured outputs with little accuracy gain.
_NO_THINKING = types.ThinkingConfig(thinking_budget=0)

logger = logging.getLogger(__name__)

_MODEL = "gemini-2.5-flash"


INTAKE_SYSTEM_PROMPT = """You are SnapFood's input parser. The user speaks, types, or photographs something about feeding their household. Turn it into a list of structured ACTIONS and return ONLY valid JSON (no markdown fences, no commentary).

Today's date is {today}.

Current household context (use it to resolve references like "it" / "the rice"):
DIETARY PREFERENCES: {dietary}
PANTRY: {pantry}

Produce JSON in exactly this shape:
{{
  "summary": "one short sentence describing what you understood",
  "intents": [ {{ "type": "...", ... }} ]
}}

Each intent object's "type" is one of, with these fields:
- "pantry_update": {{"name": "Rice", "category": "grain", "status": "low", "quantity": null, "unit": null}}
    status is one of ok/low/out. Use "low" for "almost over/running low", "out" for "finished/empty".
- "grocery_add": {{"name": "Rice", "category": "grain", "quantity": null, "unit": null}}
    Add when the user wants to buy/order/restock something.
- "meal_preference": {{"item": "Lamb", "timeframe": "next week", "note": null}}
    Use when they express wanting to eat a food/dish at some time.
- "dietary_change": {{"change": "vegetarian", "details": {{}}}}
- "goal_change": {{"description": "more protein"}}
- "schedule_change": {{"note": "skip breakfast on weekends"}}
- "eat_out_note": {{"cuisine": "Indian", "when": "tonight", "note": "doesn't want to cook"}}
    Use for takeout/restaurant/"don't want to cook" intents. (Ordering ships later; we just record it.)
- "unknown": {{"note": "verbatim of what wasn't understood"}}

Rules:
1. A single input can yield MULTIPLE intents. "Rice is almost over, order it next time" ->
   one pantry_update (Rice, low) AND one grocery_add (Rice).
2. If an image is provided (a fridge/pantry/receipt photo), extract each visible food item as a
   pantry_update with your best status/quantity estimate.
3. Capitalize food names normally (e.g. "Rice", "Lamb", "Olive Oil"). Pick a sensible category from:
   produce, grain, pulse, oil, dairy, meat, spice, other.
4. Never invent items the user didn't mention or that aren't visible in the image.
5. If nothing is parseable, return {{"summary": "", "intents": [{{"type": "unknown", "note": "<input>"}}]}}.
6. On hard failure: return {{"parse_error": true, "reason": "explanation"}}.
"""


SUGGESTION_SYSTEM_PROMPT = """You are SnapFood's meal planner. Using ONLY the household profile below, produce practical suggestions and return ONLY valid JSON (no markdown fences).

Today's date is {today}.

HOUSEHOLD: {household}
MEMBERS: {members}
DIETARY PREFERENCES: {dietary}
GOAL: {goal}
EATING SCHEDULE: {schedule}
CURRENT PANTRY (what they already have): {pantry}
RECENT REQUESTS (most recent first): {requests}
RECENT FEEDBACK (avoid disliked, favor liked): {feedback}

Generate the kinds requested: {kinds}.

Return JSON in exactly this shape:
{{
  "grocery": [
    {{"name": "Spinach", "category": "produce", "quantity": 1, "unit": "bunch",
      "reason": "boosts fiber toward the goal",
      "nutrition": {{"calories": 23, "protein_g": 2.9, "fiber_g": 2.2}}}}
  ],
  "recipes": [
    {{"title": "Chickpea Spinach Curry", "uses_pantry": ["Rice", "Chickpeas"],
      "needs": ["Spinach"], "steps": ["..."], "serves": 4,
      "why": "high protein + fiber, uses what's on hand"}}
  ],
  "rationale": "1-2 sentences tying the plan to the goal",
  "goal_alignment": "how this advances the goal"
}}

Rules:
1. For "grocery_list": list what to BUY. EXCLUDE anything already in the pantry with status ok.
   INCLUDE pantry items whose status is low/out. Give a per-item nutrition estimate (per the unit).
2. For "cook_with_pantry": 1-3 recipes that use mostly on-hand pantry ingredients.
3. Respect every dietary preference and allergy strictly. Honor recent meal_preference requests.
4. Bias the whole plan toward the GOAL.
5. If a requested kind isn't applicable, return an empty list for it.
"""


def _strip_json(raw: str) -> dict:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1] if "```" in text else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip("` \n")
    return json.loads(text)


async def parse_input(
    *,
    today: str,
    raw_text: str | None,
    image_bytes: bytes | None,
    image_mime: str | None,
    dietary: dict,
    pantry: list[dict],
) -> dict:
    """Parse a multimodal intake into a list of structured actions."""
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    system_prompt = INTAKE_SYSTEM_PROMPT.format(
        today=today,
        dietary=json.dumps(dietary or {}),
        pantry=json.dumps(pantry or []),
    )

    parts: list = []
    if image_bytes is not None:
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime or "image/jpeg"))
    parts.append(raw_text or "Extract any food items from this image.")

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=_MODEL,
            contents=parts,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.1,
                thinking_config=_NO_THINKING,
                max_output_tokens=settings.INTAKE_MAX_OUTPUT_TOKENS,
            ),
        )
    except Exception as exc:
        logger.exception("Gemini API error (intake): %s", exc)
        raise HTTPException(status_code=502, detail="Gemini API error") from exc

    try:
        parsed = _strip_json(response.text)
    except json.JSONDecodeError as exc:
        logger.error("Bad intake JSON: %s", (response.text or "")[:500])
        raise HTTPException(status_code=502, detail="Could not understand that input") from exc

    if parsed.get("parse_error"):
        raise HTTPException(status_code=422, detail=parsed.get("reason", "Could not parse input"))
    return parsed


async def generate_suggestions(*, today: str, profile: dict, kinds: list[str]) -> dict:
    """Generate grocery + recipe suggestions from the household profile."""
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    system_prompt = SUGGESTION_SYSTEM_PROMPT.format(
        today=today,
        household=json.dumps(profile.get("household", {})),
        members=json.dumps(profile.get("members", [])),
        dietary=json.dumps(profile.get("dietary", {})),
        goal=json.dumps(profile.get("goal")),
        schedule=json.dumps(profile.get("schedule")),
        pantry=json.dumps(profile.get("pantry", [])),
        requests=json.dumps(profile.get("requests", [])),
        feedback=json.dumps(profile.get("feedback", [])),
        kinds=json.dumps(kinds),
    )

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=_MODEL,
            contents="Generate the suggestions now.",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.3,
                thinking_config=_NO_THINKING,
                max_output_tokens=settings.SUGGESTION_MAX_OUTPUT_TOKENS,
            ),
        )
    except Exception as exc:
        logger.exception("Gemini API error (suggestions): %s", exc)
        raise HTTPException(status_code=502, detail="Gemini API error") from exc

    try:
        parsed = _strip_json(response.text)
    except json.JSONDecodeError as exc:
        logger.error("Bad suggestions JSON: %s", (response.text or "")[:500])
        raise HTTPException(status_code=502, detail="Could not generate suggestions") from exc

    if parsed.get("parse_error"):
        raise HTTPException(status_code=502, detail=parsed.get("reason", "Could not generate suggestions"))
    return parsed
