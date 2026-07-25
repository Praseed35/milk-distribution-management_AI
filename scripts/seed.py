from sqlalchemy import exists

from app.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.route import Route
from app.models.customer import Customer
from app.models.milk_type import MilkType
from app.models.employee import Employee
from app.models.subscription import Subscription


def seed():
    db = SessionLocal()

    try:

        existing_users = db.query(User.username).all()
        existing_usernames = {u.username for u in existing_users}

        users = [
            User(
                username="owner",
                password_hash=hash_password("owner123"),
                role="OWNER",
                is_active=True
            ),
            User(
                username="checker1",
                password_hash=hash_password("checker123"),
                role="CHECKER",
                is_active=True
            ),
            User(
                username="delivery1",
                password_hash=hash_password("delivery123"),
                role="DELIVERY_PARTNER",
                is_active=True
            ),
            User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="OWNER",
                is_active=True
            ),
            User(
                username="employee1",
                password_hash=hash_password("emp123"),
                role="EMPLOYEE",
                is_active=True
            ),
        ]
        new_users = [u for u in users if u.username not in existing_usernames]
        if new_users:
            db.add_all(new_users)
            db.commit()
            print(f"Seeded {len(new_users)} new users (skipped {len(users) - len(new_users)} existing)")
        else:
            print("All users already exist, skipping")

        existing_milk = db.query(MilkType.milk_name).all()
        existing_milk_names = {m.milk_name for m in existing_milk}

        milk_types = [
            MilkType(
                milk_name="Full Cream Milk",
                volume_ml=1000,
                description="Full cream dairy milk",
                is_active=True
            ),
            MilkType(
                milk_name="Toned Milk",
                volume_ml=500,
                description="Low fat toned milk",
                is_active=True
            ),
            MilkType(
                milk_name="Double Toned Milk",
                volume_ml=500,
                description="Double toned milk",
                is_active=True
            ),
            MilkType(
                milk_name="Standard Milk",
                volume_ml=1000,
                description="Standard pasteurized milk",
                is_active=True
            ),
            MilkType(
                milk_name="Small Pack Milk",
                volume_ml=250,
                description="250ml small pack",
                is_active=True
            ),
            MilkType(
                milk_name="Buffalo Milk",
                volume_ml=1000,
                description="Full cream buffalo milk",
                is_active=True
            ),
            MilkType(
                milk_name="Organic Milk",
                volume_ml=500,
                description="Certified organic milk",
                is_active=True
            ),
        ]
        new_milk = [m for m in milk_types if m.milk_name not in existing_milk_names]
        if new_milk:
            db.add_all(new_milk)
            db.commit()
            print(f"Seeded {len(new_milk)} new milk types (skipped {len(milk_types) - len(new_milk)} existing)")
        else:
            print("All milk types already exist, skipping")

        existing_routes = db.query(Route.route_code).all()
        existing_route_codes = {r.route_code for r in existing_routes}

        routes = [
            Route(
                route_code="R001",
                route_name="Downtown Route",
                description="Main downtown delivery route",
                is_active=True
            ),
            Route(
                route_code="R002",
                route_name="Uptown Route",
                description="Uptown residential delivery route",
                is_active=True
            ),
            Route(
                route_code="R003",
                route_name="Industrial Route",
                description="Industrial area delivery route",
                is_active=True
            ),
            Route(
                route_code="R004",
                route_name="Suburban Route",
                description="Suburban area delivery route",
                is_active=True
            ),
            Route(
                route_code="R005",
                route_name="City Center Route",
                description="City center commercial route",
                is_active=True
            ),
        ]
        new_routes = [r for r in routes if r.route_code not in existing_route_codes]
        if new_routes:
            db.add_all(new_routes)
            db.commit()
            print(f"Seeded {len(new_routes)} new routes (skipped {len(routes) - len(new_routes)} existing)")
        else:
            print("All routes already exist, skipping")

        existing_customers = db.query(Customer.customer_code).all()
        existing_customer_codes = {c.customer_code for c in existing_customers}

        customers = [
            Customer(
                customer_code="C00001",
                customer_name="Rajesh Kumar",
                primary_phone="9876543210",
                alternate_phone="9876543211",
                address="12 MG Road, Bangalore",
                route_id=1,
                remarks="Regular customer",
                is_active=True
            ),
            Customer(
                customer_code="C00002",
                customer_name="Priya Sharma",
                primary_phone="9876543220",
                alternate_phone=None,
                address="45 Park Street, Kolkata",
                route_id=1,
                remarks=None,
                is_active=True
            ),
            Customer(
                customer_code="C00003",
                customer_name="Amit Patel",
                primary_phone="9876543230",
                alternate_phone="9876543231",
                address="78 Nehru Nagar, Mumbai",
                route_id=2,
                is_active=True
            ),
            Customer(
                customer_code="C00004",
                customer_name="Sneha Reddy",
                primary_phone="9876543240",
                alternate_phone=None,
                address="23 Lake View, Hyderabad",
                route_id=2,
                remarks="Prefers evening delivery",
                is_active=True
            ),
            Customer(
                customer_code="C00005",
                customer_name="Vikram Singh",
                primary_phone="9876543250",
                alternate_phone="9876543251",
                address="56 Gandhi Road, Chennai",
                route_id=3,
                is_active=True
            ),
            Customer(
                customer_code="C00006",
                customer_name="Anjali Nair",
                primary_phone="9876543260",
                alternate_phone=None,
                address="89 Marine Drive, Kochi",
                route_id=3,
                remarks="Monthly payment",
                is_active=True
            ),
            Customer(
                customer_code="C00007",
                customer_name="Ravi Verma",
                primary_phone="9876543270",
                alternate_phone="9876543271",
                address="34 Civil Lines, Delhi",
                route_id=4,
                is_active=True
            ),
            Customer(
                customer_code="C00008",
                customer_name="Meera Joshi",
                primary_phone="9876543280",
                alternate_phone=None,
                address="67 Residency Road, Pune",
                route_id=4,
                is_active=True
            ),
            Customer(
                customer_code="C00009",
                customer_name="Suresh Menon",
                primary_phone="9876543290",
                alternate_phone="9876543291",
                address="90 Anna Salai, Chennai",
                route_id=5,
                remarks="Bulk order",
                is_active=True
            ),
            Customer(
                customer_code="C00010",
                customer_name="Deepa Iyer",
                primary_phone="9876543300",
                alternate_phone=None,
                address="12 BTM Layout, Bangalore",
                route_id=5,
                is_active=True
            ),
            Customer(
                customer_code="C00011",
                customer_name="Karthik Rao",
                primary_phone="9876543310",
                alternate_phone="9876543311",
                address="33 Jubilee Hills, Hyderabad",
                route_id=1,
                is_active=True
            ),
            Customer(
                customer_code="C00012",
                customer_name="Lakshmi Devi",
                primary_phone="9876543320",
                alternate_phone=None,
                address="44 T Nagar, Chennai",
                route_id=2,
                is_active=True
            ),
            Customer(
                customer_code="C00013",
                customer_name="Arjun Das",
                primary_phone="9876543330",
                alternate_phone="9876543331",
                address="55 Salt Lake, Kolkata",
                route_id=3,
                is_active=True
            ),
            Customer(
                customer_code="C00014",
                customer_name="Neha Gupta",
                primary_phone="9876543340",
                alternate_phone=None,
                address="66 Connaught Place, Delhi",
                route_id=4,
                remarks="VIP customer",
                is_active=True
            ),
            Customer(
                customer_code="C00015",
                customer_name="Rahul Bose",
                primary_phone="9876543350",
                alternate_phone="9876543351",
                address="77 Bandra West, Mumbai",
                route_id=5,
                is_active=True
            ),
        ]
        new_customers = [c for c in customers if c.customer_code not in existing_customer_codes]
        if new_customers:
            db.add_all(new_customers)
            db.commit()
            print(f"Seeded {len(new_customers)} new customers (skipped {len(customers) - len(new_customers)} existing)")
        else:
            print("All customers already exist, skipping")

        existing_employees = db.query(Employee.employee_code).all()
        existing_employee_codes = {e.employee_code for e in existing_employees}

        employees = [
            Employee(
                employee_code="E00001",
                name="Ramesh Kumar",
                phone="9876500001",
                address="Staff Quarters A, Bangalore",
                role="CHECKER",
                route_id=1,
                is_active=True,
                user_id=2
            ),
            Employee(
                employee_code="E00002",
                name="Suresh Babu",
                phone="9876500002",
                address="Staff Quarters B, Bangalore",
                role="DELIVERY_PARTNER",
                route_id=1,
                is_active=True,
                user_id=3
            ),
            Employee(
                employee_code="E00003",
                name="Venkat Reddy",
                phone="9876500003",
                address="Staff Colony, Hyderabad",
                role="DELIVERY_PARTNER",
                route_id=2,
                is_active=True,
                user_id=None
            ),
            Employee(
                employee_code="E00004",
                name="Ganesh Pai",
                phone="9876500004",
                address="Near Station, Mumbai",
                role="CHECKER",
                route_id=3,
                is_active=True,
                user_id=None
            ),
            Employee(
                employee_code="E00005",
                name="Shankar Naik",
                phone="9876500005",
                address="Main Road, Pune",
                role="DELIVERY_PARTNER",
                route_id=4,
                is_active=True,
                user_id=None
            ),
        ]
        new_employees = [e for e in employees if e.employee_code not in existing_employee_codes]
        if new_employees:
            db.add_all(new_employees)
            db.commit()
            print(f"Seeded {len(new_employees)} new employees (skipped {len(employees) - len(new_employees)} existing)")
        else:
            print("All employees already exist, skipping")

        existing_subs = (
            db.query(Subscription.customer_id, Subscription.milk_type_id)
            .filter(Subscription.is_active == True)
            .all()
        )
        existing_sub_keys = {(s.customer_id, s.milk_type_id) for s in existing_subs}

        subscriptions = [
            Subscription(
                customer_id=1,
                milk_type_id=1,
                morning_quantity=2,
                evening_quantity=1,
                status="ACTIVE",
                remarks="Rajesh - Full Cream Milk",
                is_active=True
            ),
            Subscription(
                customer_id=2,
                milk_type_id=2,
                morning_quantity=1,
                evening_quantity=0,
                status="ACTIVE",
                remarks="Priya - Toned Milk",
                is_active=True
            ),
            Subscription(
                customer_id=3,
                milk_type_id=4,
                morning_quantity=1,
                evening_quantity=1,
                status="ACTIVE",
                remarks="Amit - Standard Milk",
                is_active=True
            ),
            Subscription(
                customer_id=4,
                milk_type_id=5,
                morning_quantity=2,
                evening_quantity=0,
                status="ACTIVE",
                remarks="Sneha - Small Pack",
                is_active=True
            ),
            Subscription(
                customer_id=5,
                milk_type_id=1,
                morning_quantity=3,
                evening_quantity=2,
                status="ACTIVE",
                remarks="Vikram - Full Cream Milk",
                is_active=True
            ),
        ]
        new_subs = [
            s for s in subscriptions
            if (s.customer_id, s.milk_type_id) not in existing_sub_keys
        ]
        if new_subs:
            db.add_all(new_subs)
            db.commit()
            print(f"Seeded {len(new_subs)} new subscriptions (skipped {len(subscriptions) - len(new_subs)} existing)")
        else:
            print("All subscriptions already exist, skipping")

        print("\nSeed completed successfully!")
        print("\nTest credentials:")
        print("  Owner:            owner / owner123")
        print("  Checker:          checker1 / checker123")
        print("  Delivery Partner: delivery1 / delivery123")
        print("  Admin:            admin / admin123")
        print("  Employee:         employee1 / emp123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
