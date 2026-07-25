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



app = FastAPI()



app.include_router(user_router)
app.include_router(auth_router)
app.include_router(route_router)
app.include_router(customer_router)
app.include_router(milk_type_router)
app.include_router(subscription_router)
app.include_router(employee_router)
app.include_router(delivery_exception_router)

@app.get("/")
def home():
    return {
        "message": "Milk Management API"
    }