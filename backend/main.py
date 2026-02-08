from fastapi import FastAPI
from database import engine
from models import Base

app = FastAPI(
    title="Smart Poultry Link API",
    description="Backend service for Smart Poultry Link",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "Backend is running with database"}
