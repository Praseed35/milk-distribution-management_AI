# app/main.py

from datetime import datetime

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1 = APIRouter(prefix="/api/v1")

api_v1.include_router(user_router)
api_v1.include_router(auth_router)
api_v1.include_router(route_router)
api_v1.include_router(customer_router)
api_v1.include_router(milk_type_router)
api_v1.include_router(subscription_router)
api_v1.include_router(employee_router)
api_v1.include_router(delivery_exception_router)
api_v1.include_router(token_book_router)
api_v1.include_router(deliveries_router)
api_v1.include_router(delivery_edit_router)
api_v1.include_router(payment_router)
api_v1.include_router(reports_router)

app.include_router(api_v1)

@api_v1.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Legacy root-level routes (deprecated — kept for backward compatibility)
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