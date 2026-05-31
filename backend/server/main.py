from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.config import get_settings
from server.database import engine, Base
from server.routers import auth, ingredients, recipes, cooking_logs, users, households, favorites, upload, comments
from server.tasks.scheduler import scheduler

settings = get_settings()

app = FastAPI(
    title="食光机 API",
    description="别让食材辜负时光",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(ingredients.router, prefix="/api/v1")
app.include_router(recipes.router, prefix="/api/v1")
app.include_router(cooking_logs.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(households.router, prefix="/api/v1")
app.include_router(favorites.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if settings.APP_ENV != "test":
        scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    if settings.APP_ENV != "test":
        scheduler.shutdown()


@app.get("/api/v1/health")
async def health_check():
    return {"code": 0, "message": "healthy", "data": {"environment": settings.APP_ENV}}