"""
Idempotent seed script for SnapFood local development.
Uses psycopg2 with raw SQL (no ORM async complexity).
Run from backend/ with the venv active:
    python seed.py
"""

import json
import sys
import uuid

import psycopg2

DATABASE_URL = "postgresql://busi-reddy-karnati@/snapfood?host=/var/run/postgresql"

SEED_DEVICE_UUID = "00000000-0000-0000-0000-000000000001"


def main():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # --- Idempotency check ---
        cur.execute(
            "SELECT household_id FROM households WHERE device_uuid = %s",
            (SEED_DEVICE_UUID,),
        )
        row = cur.fetchone()
        if row:
            print(f"Seed household already exists (id={row[0]}). Skipping.")
            return

        # --- Household ---
        household_id = str(uuid.uuid4())
        dietary_preferences = json.dumps(
            {"diet": "none", "allergies": [], "dislikes": ["mushrooms"]}
        )
        cuisines = json.dumps(["Indian", "Mediterranean"])

        cur.execute(
            """
            INSERT INTO households (household_id, device_uuid, name, dietary_preferences, cuisines)
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb)
            """,
            (household_id, SEED_DEVICE_UUID, "Demo Kitchen", dietary_preferences, cuisines),
        )
        print(f"Created household: Demo Kitchen ({household_id})")

        # --- Members ---
        members = [
            {"name": "Alice", "age": 32, "role": "adult"},
            {"name": "Bob", "age": 8, "role": "child"},
        ]
        for m in members:
            member_id = str(uuid.uuid4())
            notes = f"role: {m['role']}"
            cur.execute(
                """
                INSERT INTO members (member_id, household_id, name, age, dietary_preferences, notes)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                """,
                (member_id, household_id, m["name"], m["age"], json.dumps({}), notes),
            )
            print(f"  Created member: {m['name']} (age={m['age']}, role={m['role']})")

        # --- Goal ---
        goal_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO goals (goal_id, household_id, description, target)
            VALUES (%s, %s, %s, %s::jsonb)
            """,
            (
                goal_id,
                household_id,
                "eat_healthier — reduce processed food",
                json.dumps({}),
            ),
        )
        print(f"  Created goal: eat_healthier")

        # --- Pantry items ---
        pantry_items = [
            ("rice", 2000, "g", "grain", "ok"),
            ("olive oil", 500, "ml", "oil", "low"),
            ("eggs", 6, "count", "dairy", "ok"),
            ("onions", 1000, "g", "produce", "ok"),
            ("tomatoes", 400, "g", "produce", "low"),
            ("chicken breast", 500, "g", "meat", "ok"),
            ("basmati rice", 1000, "g", "grain", "ok"),
            ("cumin", 50, "g", "spice", "ok"),
        ]
        for name, qty, unit, category, status in pantry_items:
            item_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO pantry_items (item_id, household_id, name, quantity, unit, category, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (item_id, household_id, name, qty, unit, category, status),
            )
            print(f"  Pantry: {name} ({qty}{unit}, {category}, {status})")

        # --- Grocery items ---
        grocery_items = [
            ("milk", 2000, "ml", "dairy", "active"),
            ("spinach", 200, "g", "produce", "active"),
            ("lentils", 1000, "g", "pulse", "active"),
            ("garlic", 100, "g", "produce", "active"),
            ("yogurt", 500, "g", "dairy", "active"),
        ]
        for name, qty, unit, category, status in grocery_items:
            item_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO grocery_items (item_id, household_id, name, quantity, unit, category, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (item_id, household_id, name, qty, unit, category, status),
            )
            print(f"  Grocery: {name} ({qty}{unit}, {category}, {status})")

        conn.commit()
        print("\nSeed complete.")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
