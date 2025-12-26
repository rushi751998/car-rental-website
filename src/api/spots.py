from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import json
from src.schemas import PicnicSpot, PicnicSpotUpdate, AdminLogin
from src.db_ops import Database, verify_admin

router = APIRouter(tags=["spots"])

db = Database()

# Image upload for picnic spot images
import os, shutil, re
from datetime import datetime

@router.post("/api/admin/upload/spot")
async def upload_spot_images(
    files: List[UploadFile] = File(...),
    username: str = Form(...),
    password: str = Form(...)
):
    if not verify_admin(username, password):
        raise HTTPException(status_code=401, detail="Unauthorized")

    os.makedirs(os.path.join("images", "spots"), exist_ok=True)
    saved_paths = []
    for file in files:
        original = file.filename or "upload"
        base, ext = os.path.splitext(original)
        safe_base = re.sub(r"[^A-Za-z0-9_-]+", "_", base) or "image"
        unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S%f")
        new_name = f"{safe_base}_{unique_suffix}{ext}"
        dest_path = os.path.join("images", "spots", new_name)
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
        saved_paths.append(f"/images/spots/{new_name}")
        file.file.close()

    return {"paths": saved_paths}

@router.get("/api/spots")
def get_spots():
    result = db.fetchall_dicts("SELECT * FROM picnic_spots WHERE available = 1")
    return {"spots": result}

@router.get("/api/spots/{spot_id}")
def get_spot(spot_id: int):
    spot = db.fetchone_dict("SELECT * FROM picnic_spots WHERE id = ?", (spot_id,))
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    return spot

@router.post("/api/admin/spots")
def add_spot(payload: dict):
    spot = payload.get('spot')
    admin = payload.get('admin')

    if not admin or not verify_admin(admin.get('username'), admin.get('password')):
        raise HTTPException(status_code=401, detail="Unauthorized")

    spot_obj = PicnicSpot(**spot)

    spot_id = db.insert('''
        INSERT INTO picnic_spots (name, price, location, images, short_description, detailed_description, trip_images, hotel_images, available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        spot_obj.name,
        spot_obj.price,
        spot_obj.location,
        json.dumps(spot_obj.images),
        spot_obj.short_description,
        spot_obj.detailed_description,
        json.dumps(spot_obj.trip_images or []),
        json.dumps(spot_obj.hotel_images or []),
        spot_obj.available,
    ))

    return {"message": "Spot added successfully", "id": spot_id}

@router.put("/api/admin/spots/{spot_id}")
def update_spot(spot_id: int, payload: dict):
    admin = payload.get('admin')
    spot = payload.get('spot')

    if not admin or not verify_admin(admin.get('username'), admin.get('password')):
        raise HTTPException(status_code=401, detail="Unauthorized")

    spot_update = PicnicSpotUpdate(**spot)

    update_fields = []
    values = []

    if spot_update.name is not None:
        update_fields.append("name = ?")
        values.append(spot_update.name)
    if spot_update.price is not None:
        update_fields.append("price = ?")
        values.append(spot_update.price)
    if spot_update.location is not None:
        update_fields.append("location = ?")
        values.append(spot_update.location)
    if spot_update.images is not None:
        update_fields.append("images = ?")
        values.append(json.dumps(spot_update.images))
    if spot_update.short_description is not None:
        update_fields.append("short_description = ?")
        values.append(spot_update.short_description)
    if spot_update.detailed_description is not None:
        update_fields.append("detailed_description = ?")
        values.append(spot_update.detailed_description)
    if spot_update.trip_images is not None:
        update_fields.append("trip_images = ?")
        values.append(json.dumps(spot_update.trip_images))
    if spot_update.hotel_images is not None:
        update_fields.append("hotel_images = ?")
        values.append(json.dumps(spot_update.hotel_images))
    if spot_update.available is not None:
        update_fields.append("available = ?")
        values.append(spot_update.available)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(spot_id)
    query = f"UPDATE picnic_spots SET {', '.join(update_fields)} WHERE id = ?"

    db.execute(query, values)

    return {"message": "Spot updated successfully"}

@router.delete("/api/admin/spots/{spot_id}")
def delete_spot(spot_id: int, payload: dict):
    admin = payload.get('admin')
    if not admin or not verify_admin(admin.get('username'), admin.get('password')):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.execute("DELETE FROM picnic_spots WHERE id = ?", (spot_id,))

    return {"message": "Spot deleted successfully"}
