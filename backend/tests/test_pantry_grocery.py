async def test_pantry_crud(client):
    resp = await client.post(
        "/pantry", json={"name": "Rice", "category": "grain", "quantity": 2, "unit": "kg"}
    )
    assert resp.status_code == 201
    item_id = resp.json()["item_id"]
    assert resp.json()["status"] == "ok"

    resp = await client.put(f"/pantry/{item_id}", json={"status": "low"})
    assert resp.json()["status"] == "low"

    resp = await client.get("/pantry")
    assert len(resp.json()) == 1

    resp = await client.delete(f"/pantry/{item_id}")
    assert resp.status_code == 204
    resp = await client.get("/pantry")
    assert resp.json() == []


async def test_grocery_add_and_soft_remove(client):
    resp = await client.post("/grocery", json={"name": "Olive Oil", "category": "oil"})
    assert resp.status_code == 201
    item_id = resp.json()["item_id"]
    assert resp.json()["source"] == "manual"

    resp = await client.get("/grocery")
    assert len(resp.json()) == 1

    # delete is a soft remove -> drops off the active list
    resp = await client.delete(f"/grocery/{item_id}")
    assert resp.status_code == 204
    resp = await client.get("/grocery")
    assert resp.json() == []
