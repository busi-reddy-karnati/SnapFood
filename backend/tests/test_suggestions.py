from app import ratelimit


async def test_generate_suggestions_and_feedback_reinforcement(client):
    await client.put("/household/goal", json={"description": "more fiber"})

    resp = await client.post("/suggestions", json={"kinds": ["grocery_list"]})
    assert resp.status_code == 200
    first = resp.json()
    names = [g["name"] for g in first["payload"]["grocery"]]
    assert "Spinach" in names

    # thumbs-down Spinach
    resp = await client.post(
        "/feedback",
        json={"suggestion_id": first["suggestion_id"], "rating": "down", "comment": "no spinach please"},
    )
    assert resp.status_code == 201

    # regenerate -> disliked item avoided
    resp = await client.post("/suggestions", json={"kinds": ["grocery_list"]})
    names = [g["name"] for g in resp.json()["payload"]["grocery"]]
    assert "Spinach" not in names

    # history reflects both runs
    resp = await client.get("/history")
    assert len(resp.json()["suggestions"]) == 2


async def test_llm_rate_limit_returns_429(client):
    original = ratelimit.device_llm_limiter.max_requests
    ratelimit.device_llm_limiter.max_requests = 1
    try:
        r1 = await client.post("/intake", json={"text": "hello"})
        assert r1.status_code == 200
        r2 = await client.post("/intake", json={"text": "hello again"})
        assert r2.status_code == 429
        assert "Retry-After" in r2.headers
    finally:
        ratelimit.device_llm_limiter.max_requests = original
