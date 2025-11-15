# API endpoints and routes
from typing import Dict, Optional, List
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Path, Query, Body, status
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Instantiate FastAPI app
app = FastAPI(title="Clarity Cash API", version="0.1.0", docs_url="/docs")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Instansiate Pydantic class models
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., ge=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, ge=0)

class Item(ItemBase):
    id: str


# simple in-memory store
_items: Dict[str, Item] = {}


@app.on_event("startup")
async def startup_event():
    # seed example item
    item_id = str(uuid4())
    _items[item_id] = Item(id=item_id, name="Sample", description="Seed item", price=0.0)


@app.get("/", summary="Root", tags=["root"])
async def read_root():
    return {"message": "Welcome to Clarity Cash API"}


@app.get("/health", summary="Health check", tags=["root"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)