from app.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.route import Route
from app.models.customer import Customer
from app.models.milk_type import MilkType
from app.models.employee import Employee


def seed():
    db = SessionLocal()

    try:

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
        ]
        db.add_all(users)
        db.commit()
        print(f"Seeded {len(users)} users")

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
        db.add_all(milk_types)
        db.commit()
        print(f"Seeded {len(milk_types)} milk types")

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
        db.add_all(routes)
        db.commit()
        print(f"Seeded {len(routes)} routes")

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
        db.add_all(customers)
        db.commit()
        print(f"Seeded {len(customers)} customers")

        employees = [
            Employee(
                name="Ramesh Kumar",
                phone="9876500001",
                address="Staff Quarters A, Bangalore",
                is_active=True,
                user_id=2
            ),
            Employee(
                name="Suresh Babu",
                phone="9876500002",
                address="Staff Quarters B, Bangalore",
                is_active=True,
                user_id=3
            ),
            Employee(
                name="Venkat Reddy",
                phone="9876500003",
                address="Staff Colony, Hyderabad",
                is_active=True,
                user_id=None
            ),
            Employee(
                name="Ganesh Pai",
                phone="9876500004",
                address="Near Station, Mumbai",
                is_active=True,
                user_id=None
            ),
            Employee(
                name="Shankar Naik",
                phone="9876500005",
                address="Main Road, Pune",
                is_active=True,
                user_id=None
            ),
        ]
        db.add_all(employees)
        db.commit()
        print(f"Seeded {len(employees)} employees")

        print("\nSeed completed successfully!")
        print("\nTest credentials:")
        print("  Owner:           owner / owner123")
        print("  Checker:         checker1 / checker123")
        print("  Delivery Partner: delivery1 / delivery123")
        print("  Admin:           admin / admin123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
