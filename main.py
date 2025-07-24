from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes,story_routes,stroy_nodes_routes,choices_routes,game_engine_routes
from app.database import Base, sync_engine


app = FastAPI(
    title="Interactive Story Platform",
    description="A platform for creating and playing interactive stories.",
    version="0.1.0",
)

# Create all tables
@app.on_event("startup")
async def startup_event():
    # This will create all tables defined in your models
    Base.metadata.create_all(bind=sync_engine)
    print("Database tables created successfully!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(story_routes.router)
app.include_router(stroy_nodes_routes.router)
app.include_router(choices_routes.router)
app.include_router(game_engine_routes.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Interactive Story Platform!"}