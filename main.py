from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from database.database import Base, engine
from database.seed_data import seed_data
from middleware.middleware import add_process_time_header
from routes.v1.inventory import inventory_router
from routes.v1.permission import permission_router
from routes.v1.role import role_router
from routes.v1.sales import sales_router
from routes.v1.store import store_router
from routes.v1.user import user_router

# Create the database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_data()
    yield


app = FastAPI(
    title="Retaler API",
    description="A RESTful API for managing users in a retail application",
    version="1.0.0",
    contact={
        "name": "Retaler Support",
        "email": "retaler@mail.com",
        "url": "https://retaler.com/support",
    },
    lifespan=lifespan,
)


@app.get("/")
async def Read_root():
    return {"message": "Welcome to retaler"}


app.add_middleware(
    CORSMiddleware, allow_origins=["*"],allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)
app.middleware("http")(add_process_time_header)

app.include_router(user_router, prefix="/v1/users", tags=["users"])
app.include_router(store_router, prefix="/v1/store", tags=["store"])
app.include_router(sales_router, prefix="/v1/store", tags=["sales"])
app.include_router(inventory_router, prefix="/v1/store", tags=["inventory"])
app.include_router(role_router, prefix="/v1/store", tags=["role"])
app.include_router(permission_router, prefix="/v1/store", tags=["permission"])
