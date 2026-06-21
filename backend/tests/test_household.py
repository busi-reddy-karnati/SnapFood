async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_household_get_creates_and_update(client):
    resp = await client.get("/household")
    assert resp.status_code == 200
    body = resp.json()
    assert body["household_id"]
    assert body["members"] == []
    assert body["goal"] is None

    resp = await client.put(
        "/household",
        json={"dietary_preferences": {"diet": "vegetarian", "allergies": ["peanuts"]},
              "cuisines": ["Indian", "Italian"]},
    )
    assert resp.status_code == 200
    assert resp.json()["dietary_preferences"]["diet"] == "vegetarian"
    assert "Indian" in resp.json()["cuisines"]


async def test_members_goal_schedule(client):
    resp = await client.post("/household/members", json={"name": "Sam", "age": 34})
    assert resp.status_code == 201
    members = resp.json()["members"]
    assert len(members) == 1
    member_id = members[0]["member_id"]

    resp = await client.put(f"/household/members/{member_id}", json={"age": 35})
    assert resp.json()["members"][0]["age"] == 35

    resp = await client.put("/household/goal", json={"description": "more protein"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "more protein"

    resp = await client.put(
        "/household/schedule",
        json={"meals": [{"label": "Dinner", "time_of_day": "19:00", "days_of_week": ["Mon"]}]},
    )
    assert resp.status_code == 200
    assert resp.json()["meals"][0]["label"] == "Dinner"

    # goal + schedule surface on the household
    resp = await client.get("/household")
    assert resp.json()["goal"]["description"] == "more protein"
    assert resp.json()["schedule"]["meals"][0]["label"] == "Dinner"

    resp = await client.delete(f"/household/members/{member_id}")
    assert resp.status_code == 200
    assert resp.json()["members"] == []
