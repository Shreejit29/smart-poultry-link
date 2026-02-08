from fastapi import FastAPI

app = FastAPI(
    title="Smart Poultry Link API",
    description="Backend service for Smart Poultry Link",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"status": "Backend is running"}
