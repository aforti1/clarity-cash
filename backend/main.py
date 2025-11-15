from fastapi import FastAPI

app = FastAPI(title="Group Project Backend")

@app.get("/")
def home():
    return {"message": "Hello! FastAPI backend is running 🎉"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "status": "User fetched successfully"}

@app.post("/login")
def login(username: str, password: str):
    return {"message": "Login request received", "username": username}


