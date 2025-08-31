from fastapi import FastAPI
from app.api import order_routes

app = FastAPI(title="Colmado AI", description="API for Colmado AI application", version="1.0.0")

app.include_router(order_routes.router, tags=["orders"])

