from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import json
import os
import shutil
import re
from datetime import datetime
from src.db_ops import Database, verify_admin
from src.schemas import AdminLogin

router = APIRouter(tags=["last_trips"])

db = Database()


# Image upload for last trips
@router.post("/api/admin/upload/trip")
async def upload_trip_images(
    files: List[UploadFile] = File(...),
    username: str = Form(...),
    password: str = Form(...),
):
    if not verify_admin(username, password):
        raise HTTPException(status_code=401, detail="Unauthorized")

    os.makedirs(os.path.join("images", "last_trips"), exist_ok=True)
    saved_paths = []
    for file in files:
        original = file.filename or "upload"
        base, ext = os.path.splitext(original)
        safe_base = re.sub(r"[^A-Za-z0-9_-]+", "_", base) or "image"
        unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S%f")
        new_name = f"{safe_base}_{unique_suffix}{ext}"
        dest_path = os.path.join("images", "last_trips", new_name)
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
        saved_paths.append(f"/images/last_trips/{new_name}")
        file.file.close()

    return {"paths": saved_paths}


# Public endpoints
@router.get("/api/last_trips")
def list_last_trips():
    rows = db.fetchall_dicts(
        "SELECT * FROM last_trips WHERE available = 1 ORDER BY datetime(created_at) DESC"
    )
    return {"trips": rows}


@router.get("/api/last_trips/{trip_id}")
def get_last_trip(trip_id: int):
    trip = db.fetchone_dict("SELECT * FROM last_trips WHERE id = ?", (trip_id,))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    comments = db.fetchall_dicts(
        "SELECT id, name, comment, created_at FROM last_trip_comments WHERE trip_id = ? ORDER BY id DESC",
        (trip_id,),
    )
    trip["comments"] = comments
    return trip


@router.get("/api/last_trips/{trip_id}/comments")
def get_trip_comments(trip_id: int):
    return {
        "comments": db.fetchall_dicts(
            "SELECT id, name, comment, created_at FROM last_trip_comments WHERE trip_id = ? ORDER BY id DESC",
            (trip_id,),
        )
    }


class NewComment(AdminLogin):
    # Inherit for typing structure but not using admin creds here
    name: Optional[str] = None
    comment: str


@router.post("/api/last_trips/{trip_id}/comments")
def add_trip_comment(trip_id: int, payload: dict):
    name = payload.get("name") or "Guest"
    comment = payload.get("comment")
    if not comment:
        raise HTTPException(status_code=400, detail="Comment required")
    if not db.fetchone("SELECT 1 FROM last_trips WHERE id = ?", (trip_id,)):
        raise HTTPException(status_code=404, detail="Trip not found")
    db.insert(
        """
        INSERT INTO last_trip_comments (trip_id, name, comment, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (trip_id, name, comment, datetime.utcnow().isoformat()),
    )
    return {"message": "Comment added"}


# Admin CRUD
@router.post("/api/admin/last_trips")
def add_last_trip(payload: dict):
    admin = payload.get("admin")
    trip = payload.get("trip")
    if not admin or not verify_admin(admin.get("username"), admin.get("password")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not trip:
        raise HTTPException(status_code=400, detail="Missing trip data")

    # Expect fields: destination(str), spots(List[str] or str), days(int), persons(int), images(List[str]), start_date(str), end_date(str), feedback(str)
    spots_value = trip.get("spots")
    if isinstance(spots_value, list):
        spots_text = json.dumps(spots_value)
    else:
        # comma separated string to list
        spots_list = [s.strip() for s in (spots_value or "").split(",") if s.strip()]
        spots_text = json.dumps(spots_list)

    images_value = trip.get("images") or []
    images_text = json.dumps(images_value)

    last_id = db.insert(
        """
        INSERT INTO last_trips (destination, spots, days, persons, images, start_date, end_date, feedback, created_at, available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            trip.get("destination"),
            spots_text,
            int(trip.get("days", 0)),
            int(trip.get("persons", 0)),
            images_text,
            trip.get("start_date"),
            trip.get("end_date"),
            trip.get("feedback"),
            datetime.utcnow().isoformat(),
        ),
    )
    return {"message": "Trip added", "id": last_id}


@router.put("/api/admin/last_trips/{trip_id}")
def update_last_trip(trip_id: int, payload: dict):
    admin = payload.get("admin")
    trip = payload.get("trip")
    if not admin or not verify_admin(admin.get("username"), admin.get("password")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not trip:
        raise HTTPException(status_code=400, detail="Missing trip data")

    # Build update fields
    fields = []
    values = []

    if "destination" in trip and trip["destination"] is not None:
        fields.append("destination = ?")
        values.append(trip["destination"])
    if "spots" in trip and trip["spots"] is not None:
        val = trip["spots"]
        if isinstance(val, list):
            fields.append("spots = ?")
            values.append(json.dumps(val))
        else:
            spots_list = [s.strip() for s in val.split(",") if s.strip()]
            fields.append("spots = ?")
            values.append(json.dumps(spots_list))
    if "days" in trip and trip["days"] is not None:
        fields.append("days = ?")
        values.append(int(trip["days"]))
    if "persons" in trip and trip["persons"] is not None:
        fields.append("persons = ?")
        values.append(int(trip["persons"]))
    if "images" in trip and trip["images"] is not None:
        fields.append("images = ?")
        values.append(json.dumps(trip["images"]))
    if "start_date" in trip and trip["start_date"] is not None:
        fields.append("start_date = ?")
        values.append(trip["start_date"])
    if "end_date" in trip and trip["end_date"] is not None:
        fields.append("end_date = ?")
        values.append(trip["end_date"])
    if "feedback" in trip and trip["feedback"] is not None:
        fields.append("feedback = ?")
        values.append(trip["feedback"])
    if "available" in trip and trip["available"] is not None:
        fields.append("available = ?")
        values.append(1 if trip["available"] else 0)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(trip_id)
    db.execute(f"UPDATE last_trips SET {', '.join(fields)} WHERE id = ?", values)
    return {"message": "Trip updated"}


@router.delete("/api/admin/last_trips/{trip_id}")
def delete_last_trip(trip_id: int, payload: dict):
    admin = payload.get("admin")
    if not admin or not verify_admin(admin.get("username"), admin.get("password")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.execute("DELETE FROM last_trips WHERE id = ?", (trip_id,))
    return {"message": "Trip deleted"}


@router.put("/api/admin/last_trips/{trip_id}/comments/{comment_id}")
def admin_update_comment(trip_id: int, comment_id: int, payload: dict):
    admin = payload.get("admin")
    update = payload.get("update") or {}
    if not admin or not verify_admin(admin.get("username"), admin.get("password")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Ensure trip and comment exist and are linked
    if not db.fetchone("SELECT 1 FROM last_trips WHERE id = ?", (trip_id,)):
        raise HTTPException(status_code=404, detail="Trip not found")
    if not db.fetchone(
        "SELECT 1 FROM last_trip_comments WHERE id = ? AND trip_id = ?",
        (comment_id, trip_id),
    ):
        raise HTTPException(status_code=404, detail="Comment not found")

    fields = []
    values = []
    if "name" in update and update["name"] is not None:
        fields.append("name = ?")
        values.append(update["name"])
    if "comment" in update and update["comment"] is not None:
        fields.append("comment = ?")
        values.append(update["comment"])

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(comment_id)
    db.execute(
        f"UPDATE last_trip_comments SET {', '.join(fields)} WHERE id = ?", values
    )
    return {"message": "Comment updated"}


@router.delete("/api/admin/last_trips/{trip_id}/comments/{comment_id}")
def admin_delete_comment(trip_id: int, comment_id: int, payload: dict):
    admin = payload.get("admin")
    if not admin or not verify_admin(admin.get("username"), admin.get("password")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Ensure trip and comment exist and are linked
    if not db.fetchone("SELECT 1 FROM last_trips WHERE id = ?", (trip_id,)):
        raise HTTPException(status_code=404, detail="Trip not found")
    if not db.fetchone(
        "SELECT 1 FROM last_trip_comments WHERE id = ? AND trip_id = ?",
        (comment_id, trip_id),
    ):
        raise HTTPException(status_code=404, detail="Comment not found")

    db.execute("DELETE FROM last_trip_comments WHERE id = ?", (comment_id,))
    return {"message": "Comment deleted"}


@router.post("/api/admin/last_trips/list")
def admin_list_last_trips(payload: dict):
    admin = payload.get("admin")
    if not admin or not verify_admin(admin.get("username"), admin.get("password")):
        raise HTTPException(status_code=401, detail="Unauthorized")
    rows = db.fetchall_dicts(
        "SELECT * FROM last_trips ORDER BY datetime(created_at) DESC"
    )
    return {"trips": rows}
