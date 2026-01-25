from fastapi import FastAPI
from database import engine, Base
from routers import books_router, users_router
from routers.auth import router as auth_router

app = FastAPI(title="Borrowed Book System")

Base.metadata.create_all(bind=engine)

app.include_router(books_router)
app.include_router(users_router)
app.include_router(auth_router)
