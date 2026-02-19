from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import json
from pathlib import Path

app = FastAPI()

DATA_FILE = Path("users.json")

class UserCreate(BaseModel):
    email: str
    full_name: str

class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None


# ---------- Helper functions ----------

def read_users():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())

def write_users(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))


# ---------- CRUD ----------

# CREATE
@app.post("/users")
def create_user(user: UserCreate):
    users = read_users()

    new_user = {
        "id": str(uuid4()),
        "email": user.email,
        "full_name": user.full_name
    }

    users.append(new_user)
    write_users(users)

    return new_user


# READ ALL
@app.get("/users")
def get_all_users():
    return read_users()


# READ ONE
@app.get("/users/{user_id}")
def get_user(user_id: str):
    users = read_users()
    for user in users:
        if user["id"] == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")


# UPDATE
@app.put("/users/{user_id}")
def update_user(user_id: str, updated_data: UserUpdate):
    users = read_users()

    for user in users:
        if user["id"] == user_id:
            if updated_data.email is not None:
                user["email"] = updated_data.email
            if updated_data.full_name is not None:
                user["full_name"] = updated_data.full_name

            write_users(users)
            return user

    raise HTTPException(status_code=404, detail="User not found")


# DELETE
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    users = read_users()
    new_users = [u for u in users if u["id"] != user_id]

    if len(users) == len(new_users):
        raise HTTPException(status_code=404, detail="User not found")

    write_users(new_users)
    return {"message": "User deleted"}

