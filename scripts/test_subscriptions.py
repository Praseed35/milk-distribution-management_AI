import httpx
import json

BASE_URL = "http://localhost:8000"

def login():
    response = httpx.post(
        f"{BASE_URL}/auth/login",
        json={"username": "owner", "password": "owner123"}
    )
    data = response.json()
    return data["access_token"]

headers = {}

def test_create_subscription():
    print("\n=== TEST 1: Create Subscription (Success) ===")
    response = httpx.post(
        f"{BASE_URL}/subscriptions/",
        headers=headers,
        json={
            "customer_id": 5,
            "milk_type_id": 4,
            "morning_quantity": 2,
            "evening_quantity": 1,
            "status": "ACTIVE",
            "remarks": "Vikram - Standard Milk"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json() if response.status_code == 201 else None

def test_create_duplicate(sub):
    print("\n=== TEST 2: Create Duplicate Subscription (Error) ===")
    response = httpx.post(
        f"{BASE_URL}/subscriptions/",
        headers=headers,
        json={
            "customer_id": sub["customer_id"],
            "milk_type_id": sub["milk_type_id"],
            "morning_quantity": 1,
            "evening_quantity": 0,
            "status": "ACTIVE"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_invalid_customer():
    print("\n=== TEST 3: Create Subscription - Invalid Customer (Error) ===")
    response = httpx.post(
        f"{BASE_URL}/subscriptions/",
        headers=headers,
        json={
            "customer_id": 999,
            "milk_type_id": 1,
            "morning_quantity": 1,
            "evening_quantity": 0,
            "status": "ACTIVE"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_invalid_milk_type():
    print("\n=== TEST 4: Create Subscription - Invalid Milk Type (Error) ===")
    response = httpx.post(
        f"{BASE_URL}/subscriptions/",
        headers=headers,
        json={
            "customer_id": 5,
            "milk_type_id": 999,
            "morning_quantity": 1,
            "evening_quantity": 0,
            "status": "ACTIVE"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_zero_quantities():
    print("\n=== TEST 5: Create Subscription - Zero Quantities (Error) ===")
    response = httpx.post(
        f"{BASE_URL}/subscriptions/",
        headers=headers,
        json={
            "customer_id": 6,
            "milk_type_id": 5,
            "morning_quantity": 0,
            "evening_quantity": 0,
            "status": "ACTIVE"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_all():
    print("\n=== TEST 6: Get All Subscriptions ===")
    response = httpx.get(
        f"{BASE_URL}/subscriptions/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Count: {len(data)}")
    for sub in data:
        print(f"  ID={sub['id']} Customer={sub['customer_id']} MilkType={sub['milk_type_id']} Active={sub['is_active']}")
    return data

def test_get_by_id(sub_id):
    print(f"\n=== TEST 7: Get Subscription by ID ({sub_id}) ===")
    response = httpx.get(
        f"{BASE_URL}/subscriptions/{sub_id}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_not_found():
    print("\n=== TEST 8: Get Subscription Not Found (Error) ===")
    response = httpx.get(
        f"{BASE_URL}/subscriptions/99999",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_by_customer(customer_id):
    print(f"\n=== TEST 9: Get Subscriptions by Customer ID ({customer_id}) ===")
    response = httpx.get(
        f"{BASE_URL}/subscriptions/customer/{customer_id}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_update(sub_id):
    print(f"\n=== TEST 10: Update Subscription ({sub_id}) ===")
    response = httpx.put(
        f"{BASE_URL}/subscriptions/{sub_id}",
        headers=headers,
        json={
            "morning_quantity": 3,
            "evening_quantity": 2,
            "remarks": "Updated to 3 morning, 2 evening"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_delete(sub_id):
    print(f"\n=== TEST 11: Delete (Deactivate) Subscription ({sub_id}) ===")
    response = httpx.delete(
        f"{BASE_URL}/subscriptions/{sub_id}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_resubscribe(sub):
    print(f"\n=== TEST 12: Re-subscribe After Deactivation ===")
    response = httpx.post(
        f"{BASE_URL}/subscriptions/",
        headers=headers,
        json={
            "customer_id": sub["customer_id"],
            "milk_type_id": sub["milk_type_id"],
            "morning_quantity": 1,
            "evening_quantity": 1,
            "status": "ACTIVE",
            "remarks": "Re-subscribed"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_after_delete(sub_id):
    print(f"\n=== TEST 13: Get Deactivated Subscription ({sub_id}) ===")
    response = httpx.get(
        f"{BASE_URL}/subscriptions/{sub_id}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("=== Subscription Module Test Suite ===")

    token = login()
    headers["Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = "application/json"
    print(f"Login successful.")

    # Test 1: Create
    sub = test_create_subscription()
    sub_id = sub["id"]

    # Test 2: Duplicate
    test_create_duplicate(sub)

    # Test 3: Invalid customer
    test_create_invalid_customer()

    # Test 4: Invalid milk type
    test_create_invalid_milk_type()

    # Test 5: Zero quantities
    test_create_zero_quantities()

    # Test 6: Get all
    test_get_all()

    # Test 7: Get by ID
    test_get_by_id(sub_id)

    # Test 8: Get not found
    test_get_not_found()

    # Test 9: Get by customer
    test_get_by_customer(sub["customer_id"])

    # Test 10: Update
    test_update(sub_id)

    # Test 11: Delete
    test_delete(sub_id)

    # Test 12: Re-subscribe after deactivation
    test_resubscribe(sub)

    # Test 13: Verify deactivated is hidden from GET
    test_get_after_delete(sub_id)

    print("\n=== All 13 Tests Completed ===")
