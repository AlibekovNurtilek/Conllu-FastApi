from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_tables, delete_tables
from import_data import start_import_data
from app.routers.sentences import router as sentence_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    #await delete_tables()
    #await create_tables()
    print("База готова")
    #await start_import_data()
    yield
    print("Выключение")
app = FastAPI(lifespan=lifespan)

app.include_router(sentence_router)