# app/posts.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from app.models import User, Post
from app.auth import get_current_user
from app.database import get_database
from bson import ObjectId
import os
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/create_post", response_class=HTMLResponse)
async def get_create_post(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("create_post.html", {"request": request})

@router.post("/create_post", response_class=HTMLResponse)
async def create_post_form(
    request: Request,
    caption: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    db = get_database()
    images_dir = os.path.join("static", "images")
    os.makedirs(images_dir, exist_ok=True)
    image_path = os.path.join(images_dir, image.filename)
    with open(image_path, "wb") as file:
        contents = await image.read()
        file.write(contents)
    image_url = f"/static/images/{image.filename}"
    post_data = {
        "caption": caption,
        "image_url": image_url,
        "category": category,
        "user_id": current_user.id,
        "created_at": datetime.utcnow()
    }
    result = await db.posts.insert_one(post_data)
    return RedirectResponse(url="/feed", status_code=303)
