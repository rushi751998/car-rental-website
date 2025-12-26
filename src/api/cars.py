from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List
import json
from src.schemas import Car, CarUpdate, AdminLogin
from src.db_ops import Database, verify_admin

router = APIRouter(tags=["cars"])

db = Database()

# Image upload for car images
import os, shutil, re
from datetime import datetime

@router.post("/api/admin/upload/car")
async def upload_car_images(
    files: List[UploadFile] = File(...),
    username: str = Form(...),
    password: str = Form(...)
):
    if not verify_admin(username, password):
        raise HTTPException(status_code=401, detail="Unauthorized")

    os.makedirs(os.path.join("images", "cars"), exist_ok=True)
    saved_paths = []
    for file in files:
        original = file.filename or "upload"
        base, ext = os.path.splitext(original)
        safe_base = re.sub(r"[^A-Za-z0-9_-]+", "_", base) or "image"
        unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S%f")
        new_name = f"{safe_base}_{unique_suffix}{ext}"
        dest_path = os.path.join("images", "cars", new_name)
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
        saved_paths.append(f"/images/cars/{new_name}")
        file.file.close()

    return {"paths": saved_paths}

@router.get("/api/cars")
def get_cars():
    result = db.fetchall_dicts("SELECT * FROM cars WHERE available = 1")
    return {"cars": result}

@router.get("/api/cars/{car_id}")
def get_car(car_id: int):
    car = db.fetchone_dict("SELECT * FROM cars WHERE id = ?", (car_id,))
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@router.post("/api/admin/cars")
def add_car(payload: dict):
    # Expect payload to contain 'car' and 'admin' keys
    car = payload.get('car')
    admin = payload.get('admin')

    if not admin or not verify_admin(admin.get('username'), admin.get('password')):
        raise HTTPException(status_code=401, detail="Unauthorized")

    car_obj = Car(**car)

    car_id = db.insert('''
        INSERT INTO cars (name, model, price_per_day, seats, transmission, fuel_type, images, description, available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        car_obj.name,
        car_obj.model,
        car_obj.price_per_day,
        car_obj.seats,
        car_obj.transmission,
        car_obj.fuel_type,
        json.dumps(car_obj.images),
        car_obj.description,
        car_obj.available,
    ))

    return {"message": "Car added successfully", "id": car_id}

@router.put("/api/admin/cars/{car_id}")
def update_car(car_id: int, payload: dict):
    admin = payload.get('admin')
    car = payload.get('car')

    if not admin or not verify_admin(admin.get('username'), admin.get('password')):
        raise HTTPException(status_code=401, detail="Unauthorized")

    car_update = CarUpdate(**car)

    update_fields = []
    values = []

    if car_update.name is not None:
        update_fields.append("name = ?")
        values.append(car_update.name)
    if car_update.model is not None:
        update_fields.append("model = ?")
        values.append(car_update.model)
    if car_update.price_per_day is not None:
        update_fields.append("price_per_day = ?")
        values.append(car_update.price_per_day)
    if car_update.seats is not None:
        update_fields.append("seats = ?")
        values.append(car_update.seats)
    if car_update.transmission is not None:
        update_fields.append("transmission = ?")
        values.append(car_update.transmission)
    if car_update.fuel_type is not None:
        update_fields.append("fuel_type = ?")
        values.append(car_update.fuel_type)
    if car_update.images is not None:
        update_fields.append("images = ?")
        values.append(json.dumps(car_update.images))
    if car_update.description is not None:
        update_fields.append("description = ?")
        values.append(car_update.description)
    if car_update.available is not None:
        update_fields.append("available = ?")
        values.append(car_update.available)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(car_id)
    query = f"UPDATE cars SET {', '.join(update_fields)} WHERE id = ?"

    db.execute(query, values)

    return {"message": "Car updated successfully"}

@router.delete("/api/admin/cars/{car_id}")
def delete_car(car_id: int, payload: dict):
    admin = payload.get('admin')
    if not admin or not verify_admin(admin.get('username'), admin.get('password')):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.execute("DELETE FROM cars WHERE id = ?", (car_id,))

    return {"message": "Car deleted successfully"}
