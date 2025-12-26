from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
from src.db_ops import db, verify_admin
from src.utils import create_folders, config

# Create necessary folders
create_folders()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/images", StaticFiles(directory="images"), name="images")
# Serve public static files under /public to avoid shadowing API routes
app.mount("/public", StaticFiles(directory="public", html=True), name="public")

# Database operations are provided by src.db_ops.Database (imported as db)

# Include API routers (cars, spots) for production-ready structure
from src.api.cars import router as cars_router
from src.api.spots import router as spots_router
from src.api.users import router as users_router
from src.api.chat import router as chat_router
from src.api.last_trips import router as last_trips_router
from src.api.admin import router as admin_router
app.include_router(cars_router)
app.include_router(spots_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(last_trips_router)
app.include_router(admin_router)

# Serve HTML pages explicitly
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse("public/index.html")

@app.get("/spots.html", include_in_schema=False)
async def serve_spots():
    return FileResponse("public/spots.html")

@app.get("/spot-detail.html", include_in_schema=False)
async def serve_spot_detail():
    return FileResponse("public/spot-detail.html")

@app.get("/car-detail.html", include_in_schema=False)
async def serve_car_detail():
    return FileResponse("public/car-detail.html")

@app.get("/cars.html", include_in_schema=False)
async def serve_cars():
    return FileResponse("public/cars.html")

@app.get("/last-trips.html", include_in_schema=False)
async def serve_last_trips():
    return FileResponse("public/last-trips.html")

@app.get("/last-trip-detail.html", include_in_schema=False)
async def serve_last_trip_detail():
    return FileResponse("public/last-trip-detail.html")

@app.get("/login.html", include_in_schema=False)
async def serve_login():
    return FileResponse("public/login.html")

@app.get("/register.html", include_in_schema=False)
async def serve_register():
    return FileResponse("public/register.html")

@app.get("/admin.html", include_in_schema=False)
async def serve_admin():
    return FileResponse("public/admin.html")

@app.get("/index.html", include_in_schema=False)
async def serve_admin():
    return FileResponse("public/index.html")

@app.get("/admin", include_in_schema=False)
async def serve_admin():
    return FileResponse("public/admin.html")

# Admin authentication
class AdminLogin(BaseModel):
    username: str
    password: str

@app.post("/api/admin/login", tags=['admin'])
def admin_login(admin: AdminLogin):
    if verify_admin(admin.username, admin.password):
        return {"message": "Login successful", "token": "dummy_token"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# verify_admin imported from src.db_ops

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
