from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db_ops import Database

router = APIRouter(tags=["admin"])  # ensure endpoints appear under admin section/tag

db = Database()

class AdminAuthorizer(BaseModel):
    username: str
    password: str

class NewAdmin(BaseModel):
    username: str
    password: str

class CreateAdminPayload(BaseModel):
    admin: AdminAuthorizer  # authorizing admin (must be a different admin)
    new_admin: NewAdmin     # credentials for the new admin to be created

@router.post("/api/admin/users")
def create_admin(payload: CreateAdminPayload):
    # Validate authorizer by admin username and password
    auth = payload.admin
    auth_row = db.fetchone("SELECT id, username FROM admin WHERE username = ? AND password = ?", (auth.username, auth.password))
    if not auth_row:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Ensure username is unique
    existing = db.fetchone("SELECT id FROM admin WHERE username = ?", (payload.new_admin.username,))
    if existing:
        raise HTTPException(status_code=400, detail="Admin with this username already exists")

    # Create new admin
    db.insert("INSERT INTO admin (username, password) VALUES (?, ?)", (payload.new_admin.username, payload.new_admin.password))
    return {"message": "Admin created successfully"}

class ChangePasswordPayload(BaseModel):
    admin: AdminAuthorizer  # authorizing admin (must be different from target admin)
    new_password: str

@router.put("/api/admin/users/{username}/password")
def change_admin_password(username: str, payload: ChangePasswordPayload):
    # Validate authorizer by admin username and password
    auth = payload.admin
    auth_row = db.fetchone("SELECT id, username FROM admin WHERE username = ? AND password = ?", (auth.username, auth.password))
    if not auth_row:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Ensure target admin exists
    target_row = db.fetchone("SELECT id FROM admin WHERE username = ?", (username,))
    if not target_row:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Enforce that another admin authorizes the change (not self)
    if auth.username == username:
        raise HTTPException(status_code=403, detail="Password change must be authorized by a different admin")

    # Perform password update
    db.execute("UPDATE admin SET password = ? WHERE username = ?", (payload.new_password, username))
    return {"message": "Password updated successfully"}
