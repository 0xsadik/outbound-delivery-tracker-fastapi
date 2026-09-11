from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine

from app.routers import products, customers, delivery_agents, delivery_orders ,deliveries


app = FastAPI(title="Outbound delivery Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return{
        "status" : "ok"
    }


app.include_router(products.router)
app.include_router(customers.router)
app.include_router(delivery_agents.router)
app.include_router(delivery_orders.router)
app.include_router(deliveries.router)