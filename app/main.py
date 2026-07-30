# app/main.py

from fastapi import FastAPI

from app.database import engine
from app.models.user import User
from app.models.employee import Employee
from app.models.route import Route


from app.database import Base
from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.routes import router as route_router
from app.routers.customers import router as customer_router
from app.routers.milk_types import router as milk_type_router
from app.routers.subscriptions import router as subscription_router
from app.routers.employees import router as employee_router
from app.routers.delivery_exceptions import router as delivery_exception_router
from app.routers.token_books import router as token_book_router
from app.routers.deliveries import router as deliveries_router
from app.routers.delivery_edit import router as delivery_edit_router
from app.routers.payments import router as payment_router
from app.routers.reports import router as reports_router



app = FastAPI()



app.include_router(user_router)
app.include_router(auth_router)
app.include_router(route_router)
app.include_router(customer_router)
app.include_router(milk_type_router)
app.include_router(subscription_router)
app.include_router(employee_router)
app.include_router(delivery_exception_router)
app.include_router(token_book_router)
app.include_router(deliveries_router)
app.include_router(delivery_edit_router)
app.include_router(payment_router)
app.include_router(reports_router)

@app.get("/")
def home():
    return {
        "message": "Milk Management API"
    }