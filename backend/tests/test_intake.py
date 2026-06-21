import base64


async def test_intake_rice_updates_pantry_and_grocery(client):
    resp = await client.post(
        "/intake", json={"text": "Rice is almost over, order it next time"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert any("pantry" in a.lower() for a in body["applied"])
    assert any("grocery" in a.lower() for a in body["applied"])

    pantry = (await client.get("/pantry")).json()
    rice = [p for p in pantry if p["name"] == "Rice"]
    assert rice and rice[0]["status"] == "low"

    grocery = (await client.get("/grocery")).json()
    assert any(g["name"] == "Rice" for g in grocery)


async def test_intake_meal_preference_is_logged_only(client):
    resp = await client.post("/intake", json={"text": "I want to eat Lamb next week"})
    assert resp.status_code == 200
    assert resp.json()["intent_type"] == "meal_preference"
    # no pantry/grocery side effects
    assert (await client.get("/pantry")).json() == []
    assert (await client.get("/grocery")).json() == []


async def test_intake_image_extracts_pantry(client):
    img = base64.b64encode(b"fake-image-bytes").decode()
    resp = await client.post(
        "/intake", json={"image_base64": img, "image_mime": "image/jpeg"}
    )
    assert resp.status_code == 200
    pantry = (await client.get("/pantry")).json()
    assert any(p["name"] == "Tomatoes" for p in pantry)


async def test_intake_requires_input(client):
    resp = await client.post("/intake", json={})
    assert resp.status_code == 422
