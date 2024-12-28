# app/main.py

import os
import bcrypt
import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Query,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.models import User, Post, Comment, Like
from app.auth import get_current_user, create_access_token
from app.database import get_database

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), '..', 'templates'))

# Configure logger
logger = logging.getLogger("app.main")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user_form(
    request: Request,
    username: str = Form(..., min_length=3, max_length=30),
    email: str = Form(...),
    password: str = Form(..., min_length=6),
):
    db = get_database()
    existing_user = await db.users.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing_user:
        error_message = "Username or email already exists."
        logger.warning(f"Registration failed: {error_message} Username: {username}, Email: {email}")
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": error_message}
        )
    hashed_password = hash_password(password)
    user_data = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "following": [],
        "followers": [],
    }
    result = await db.users.insert_one(user_data)
    logger.info(f"New user registered: {username} (ID: {result.inserted_id})")
    return RedirectResponse(url="/login", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_user_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    db = get_database()
    user = await db.users.find_one({"username": username})
    if not user:
        error_message = "Invalid username or password."
        logger.warning(f"Login failed: {error_message} Username: {username}")
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": error_message}
        )
    if not verify_password(password, user["password"]):
        error_message = "Invalid username or password."
        logger.warning(f"Login failed: {error_message} Username: {username}")
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": error_message}
        )
    # Create JWT token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    response = RedirectResponse(url="/feed", status_code=303)
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        samesite="Lax",  # Adjust based on your needs
        secure=False,     # Set to True in production when using HTTPS
    )
    logger.info(f"User logged in: {username} (ID: {user['_id']})")
    return response


@router.get("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("token")
    logger.info("User logged out.")
    return response


@router.get("/profile/{user_id}", response_class=HTMLResponse)
async def get_user_profile_page(request: Request, user_id: str, current_user: User = Depends(get_current_user)):
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        error_message = "User not found."
        logger.warning(f"Profile access failed: {error_message} User ID: {user_id}")
        return templates.TemplateResponse("index.html", {"request": request, "error": error_message})
    # Fetch user's posts with pagination
    skip = int(request.query_params.get("skip", 0))
    limit = int(request.query_params.get("limit", 10))
    query = {"user_id": ObjectId(user_id)}
    total_posts = await db.posts.count_documents(query)
    posts_cursor = db.posts.find(query).sort("created_at", -1).skip(skip).limit(limit)
    posts = await posts_cursor.to_list(length=limit)
    for post in posts:
        # Fetch likes and comments count
        post["likes_count"] = await db.likes.count_documents({"post_id": post["_id"]})
        post["comments_count"] = await db.comments.count_documents({"post_id": post["_id"]})
    has_next = (skip + limit) < total_posts
    has_prev = skip > 0
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "posts": posts,
            "current_user": current_user,
            "skip": skip,
            "limit": limit,
            "has_next": has_next,
            "has_prev": has_prev,
        },
    )


@router.get("/profile/", response_class=HTMLResponse)
async def get_my_profile(request: Request, current_user: User = Depends(get_current_user)):
    """
    Redirects to the current user's profile page.
    """
    return RedirectResponse(url=f"/profile/{current_user.id}", status_code=303)


@router.get("/create_post", response_class=HTMLResponse)
async def get_create_post(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("create_post.html", {"request": request})


@router.post("/create_post", response_class=HTMLResponse)
async def create_post_form(
    request: Request,
    caption: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    db = get_database()
    # Save image to static/images directory
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    image_path = os.path.join(images_dir, image.filename)
    with open(image_path, "wb") as file:
        contents = await image.read()
        file.write(contents)
    image_url = f"/static/images/{image.filename}"
    # Extract hashtags from caption
    hashtags = Post.extract_hashtags(caption)
    hashtags = [tag.lower().strip("#") for tag in hashtags]
    post_data = {
        "caption": caption,
        "image_url": image_url,
        "category": category,
        "hashtags": hashtags,
        "user_id": ObjectId(current_user.id),
        "created_at": datetime.utcnow(),
    }
    result = await db.posts.insert_one(post_data)
    logger.info(f"New post created by {current_user.username} (Post ID: {result.inserted_id})")
    return RedirectResponse(url="/feed", status_code=303)


@router.get("/feed", response_class=HTMLResponse)
async def get_feed(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of posts to retrieve"),
    current_user: User = Depends(get_current_user),
):
    db = get_database()
    following_users = current_user.following
    if following_users:
        query = {"user_id": {"$in": following_users}}
    else:
        # Show user's own posts if not following anyone
        query = {"user_id": ObjectId(current_user.id)}
    try:
        # Correctly count the total number of posts matching the query
        total_posts = await db.posts.count_documents(query)
        # Fetch the posts with the applied query, sorting, skipping, and limiting
        posts_cursor = db.posts.find(query).sort("created_at", -1).skip(skip).limit(limit)
        posts = await posts_cursor.to_list(length=limit)
        # Fetch usernames and compute likes and comments count for each post
        for post in posts:
            user = await db.users.find_one({"_id": post["user_id"]})
            post["username"] = user["username"] if user else "Unknown"
            # Get likes count
            post["likes_count"] = await db.likes.count_documents({"post_id": post["_id"]})
            # Get comments count
            post["comments_count"] = await db.comments.count_documents({"post_id": post["_id"]})
        # Calculate pagination details
        has_next = (skip + limit) < total_posts
        has_prev = skip > 0
        return templates.TemplateResponse(
            "feed.html",
            {
                "request": request,
                "posts": posts,
                "current_user": current_user,
                "skip": skip,
                "limit": limit,
                "has_next": has_next,
                "has_prev": has_prev,
            },
        )
    except Exception as e:
        logger.error(f"Error fetching feed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/posts/", response_class=HTMLResponse)
async def list_all_posts(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of posts to retrieve"),
    current_user: User = Depends(get_current_user),
):
    db = get_database()
    try:
        total_posts = await db.posts.count_documents({})
        posts_cursor = db.posts.find({}).sort("created_at", -1).skip(skip).limit(limit)
        posts = await posts_cursor.to_list(length=limit)
        
        for post in posts:
            user = await db.users.find_one({"_id": post["user_id"]})
            post["username"] = user["username"] if user else "Unknown"
            post["likes_count"] = await db.likes.count_documents({"post_id": post["_id"]})
            post["comments_count"] = await db.comments.count_documents({"post_id": post["_id"]})
        
        has_next = (skip + limit) < total_posts
        has_prev = skip > 0
        
        return templates.TemplateResponse(
            "list_posts.html",
            {
                "request": request,
                "posts": posts,
                "current_user": current_user,
                "skip": skip,
                "limit": limit,
                "has_next": has_next,
                "has_prev": has_prev,
            },
        )
    except Exception as e:
        logger.error(f"Error listing all posts: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/like/{post_id}", response_class=HTMLResponse)
async def like_post_api(
    request: Request,
    post_id: str,
    current_user: User = Depends(get_current_user),
):
    db = get_database()
    try:
        post = await db.posts.find_one({"_id": ObjectId(post_id)})
        if not post:
            error_message = "Post not found."
            logger.warning(f"Like action failed: {error_message} Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=error_message)
        existing_like = await db.likes.find_one({"post_id": post["_id"], "user_id": ObjectId(current_user.id)})
        if existing_like:
            # Unlike the post
            await db.likes.delete_one({"_id": existing_like["_id"]})
            logger.info(f"User {current_user.username} unliked post {post_id}.")
        else:
            # Like the post
            like_data = {
                "user_id": ObjectId(current_user.id),
                "post_id": post["_id"],
                "created_at": datetime.utcnow(),
            }
            await db.likes.insert_one(like_data)
            logger.info(f"User {current_user.username} liked post {post_id}.")
        return RedirectResponse(url=f"/posts/{post_id}", status_code=303)
    except Exception as e:
        logger.error(f"Error liking/unliking post: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/comment/{post_id}", response_class=HTMLResponse)
async def comment_on_post_api(
    request: Request,
    post_id: str,
    text: str = Form(..., min_length=1, max_length=500),
    current_user: User = Depends(get_current_user),
):
    db = get_database()
    try:
        post = await db.posts.find_one({"_id": ObjectId(post_id)})
        if not post:
            error_message = "Post not found."
            logger.warning(f"Comment action failed: {error_message} Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=error_message)
        comment_data = {
            "text": text,
            "user_id": ObjectId(current_user.id),
            "post_id": post["_id"],
            "created_at": datetime.utcnow(),
        }
        result = await db.comments.insert_one(comment_data)
        logger.info(f"User {current_user.username} commented on post {post_id} (Comment ID: {result.inserted_id}).")
        return RedirectResponse(url=f"/posts/{post_id}", status_code=303)
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/follow/{user_id}", response_class=HTMLResponse)
async def follow_user_api(
    request: Request,
    user_id: str,
    current_user: User = Depends(get_current_user),
):
    db = get_database()
    try:
        if str(current_user.id) == user_id:
            logger.warning(f"User {current_user.username} attempted to follow/unfollow themselves.")
            return RedirectResponse(url=f"/profile/{user_id}", status_code=303)
        target_user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not target_user:
            error_message = "User to follow/unfollow not found."
            logger.warning(f"Follow action failed: {error_message} User ID: {user_id}")
            raise HTTPException(status_code=404, detail=error_message)
        if ObjectId(user_id) in current_user.following:
            # Unfollow the user
            await db.users.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$pull": {"following": ObjectId(user_id)}},
            )
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"followers": ObjectId(current_user.id)}},
            )
            logger.info(f"User {current_user.username} unfollowed user {target_user['username']} (ID: {user_id}).")
        else:
            # Follow the user
            await db.users.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$addToSet": {"following": ObjectId(user_id)}},
            )
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$addToSet": {"followers": ObjectId(current_user.id)}},
            )
            logger.info(f"User {current_user.username} followed user {target_user['username']} (ID: {user_id}).")
        return RedirectResponse(url=f"/profile/{user_id}", status_code=303)
    except Exception as e:
        logger.error(f"Error following/unfollowing user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ---------- BONUS FEATURES START HERE ----------

# 1. Search Users by Username (Substring Search)
@router.get("/search_users", response_class=HTMLResponse)
async def search_users(
    request: Request,
    q: Optional[str] = Query(None, min_length=1, description="Search query for usernames"),
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of users to retrieve"),
    current_user: User = Depends(get_current_user),
):
    db = get_database()
    try:
        if not q:
            # Render the search form if 'q' is not provided
            return templates.TemplateResponse(
                "search_users.html",
                {"request": request, "users": None, "current_user": current_user},
            )
        # Case-insensitive substring search
        query = {"username": {"$regex": q, "$options": "i"}}
        total_users = await db.users.count_documents(query)
        users_cursor = db.users.find(query).skip(skip).limit(limit)
        users = await users_cursor.to_list(length=limit)
        has_next = (skip + limit) < total_users
        has_prev = skip > 0
        return templates.TemplateResponse(
            "search_users.html",
            {
                "request": request,
                "users": users,
                "query": q,
                "skip": skip,
                "limit": limit,
                "has_next": has_next,
                "has_prev": has_prev,
                "current_user": current_user,
            },
        )
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 2. Search Posts by Hashtags with Pagination and Filters
@router.get("/search_posts", response_class=HTMLResponse)
async def search_posts(
    request: Request,
    hashtag: Optional[str] = Query(None, min_length=1, description="Hashtag to search for (without #)"),
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of posts to retrieve"),
    current_user: User = Depends(get_current_user),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Start date for date filter"),
    end_date: Optional[datetime] = Query(None, description="End date for date filter"),
):
    db = get_database()
    try:
        if not hashtag:
            # Render the search form if 'hashtag' is not provided
            return templates.TemplateResponse(
                "search_posts.html",
                {
                    "request": request,
                    "posts": None,
                    "hashtag": None,
                    "category": None,
                    "start_date": "",
                    "end_date": "",
                    "current_user": current_user,
                },
            )
        # Build the query
        query = {"hashtags": {"$in": [hashtag.lower()]}}
        # Apply category filter if provided
        if category:
            query["category"] = category
        # Apply date filters if provided
        if start_date and end_date:
            query["created_at"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["created_at"] = {"$gte": start_date}
        elif end_date:
            query["created_at"] = {"$lte": end_date}
        total_posts = await db.posts.count_documents(query)
        posts_cursor = db.posts.find(query).sort("created_at", -1).skip(skip).limit(limit)
        posts = await posts_cursor.to_list(length=limit)
        # Fetch usernames and compute likes and comments count for each post
        for post in posts:
            user = await db.users.find_one({"_id": post["user_id"]})
            post["username"] = user["username"] if user else "Unknown"
            # Get likes count
            post["likes_count"] = await db.likes.count_documents({"post_id": post["_id"]})
            # Get comments count
            post["comments_count"] = await db.comments.count_documents({"post_id": post["_id"]})
        # Calculate pagination details
        has_next = (skip + limit) < total_posts
        has_prev = skip > 0
        return templates.TemplateResponse(
            "search_posts.html",
            {
                "request": request,
                "posts": posts,
                "hashtag": hashtag,
                "category": category,
                "start_date": start_date.strftime("%Y-%m-%d") if start_date else "",
                "end_date": end_date.strftime("%Y-%m-%d") if end_date else "",
                "skip": skip,
                "limit": limit,
                "has_next": has_next,
                "has_prev": has_prev,
                "current_user": current_user,
            },
        )
    except Exception as e:
        logger.error(f"Error searching posts: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 3. Pagination for Listing Users Who Liked a Post
@router.get("/posts/{post_id}/likes", response_class=HTMLResponse)
async def get_post_likes(
    request: Request,
    post_id: str,
    skip: int = Query(0, ge=0, description="Number of likes to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of likes to retrieve"),
    current_user: User = Depends(get_current_user),
):
    db = get_database()
    try:
        post = await db.posts.find_one({"_id": ObjectId(post_id)})
        if not post:
            error_message = "Post not found."
            logger.warning(f"Like listing failed: {error_message} Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=error_message)
        total_likes = await db.likes.count_documents({"post_id": post["_id"]})
        likes_cursor = db.likes.find({"post_id": post["_id"]}).skip(skip).limit(limit)
        likes = await likes_cursor.to_list(length=limit)
        user_ids = [like["user_id"] for like in likes]
        users_cursor = db.users.find({"_id": {"$in": user_ids}})
        users = await users_cursor.to_list(length=len(user_ids))
        has_next = (skip + limit) < total_likes
        has_prev = skip > 0
        return templates.TemplateResponse(
            "post_likes.html",
            {
                "request": request,
                "users": users,
                "post": post,
                "skip": skip,
                "limit": limit,
                "has_next": has_next,
                "has_prev": has_prev,
                "current_user": current_user,
            },
        )
    except Exception as e:
        logger.error(f"Error fetching post likes: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 4. Pagination for Listing Comments and Commenting Users on a Post
@router.get("/posts/{post_id}/comments", response_class=HTMLResponse)
async def get_post_comments(
    request: Request,
    post_id: str,
    skip: int = Query(0, ge=0, description="Number of comments to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of comments to retrieve"),
    current_user: User = Depends(get_current_user),
):
    db = get_database()
    try:
        post = await db.posts.find_one({"_id": ObjectId(post_id)})
        if not post:
            error_message = "Post not found."
            logger.warning(f"Comment listing failed: {error_message} Post ID: {post_id}")
            raise HTTPException(status_code=404, detail=error_message)
        total_comments = await db.comments.count_documents({"post_id": post["_id"]})
        comments_cursor = db.comments.find({"post_id": post["_id"]}).sort("created_at", -1).skip(skip).limit(limit)
        comments = await comments_cursor.to_list(length=limit)
        user_ids = [comment["user_id"] for comment in comments]
        users_cursor = db.users.find({"_id": {"$in": user_ids}})
        users = await users_cursor.to_list(length=len(user_ids))
        user_dict = {user["_id"]: user["username"] for user in users}
        comments_with_users = []
        for comment in comments:
            comments_with_users.append({
                "id": str(comment["_id"]),
                "text": comment["text"],
                "created_at": comment["created_at"],
                "username": user_dict.get(comment["user_id"], "Unknown"),
            })
        has_next = (skip + limit) < total_comments
        has_prev = skip > 0
        return templates.TemplateResponse(
            "post_comments.html",
            {
                "request": request,
                "comments": comments_with_users,
                "post": post,
                "skip": skip,
                "limit": limit,
                "has_next": has_next,
                "has_prev": has_prev,
                "current_user": current_user,
            },
        )
    except Exception as e:
        logger.error(f"Error fetching post comments: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 5. Search Users by Username (Already Implemented Above)
# (This comment is to indicate that the feature is implemented above)


# 6. Search Posts by Hashtags with Pagination and Filters (Already Implemented Above)
# (This comment is to indicate that the feature is implemented above)


# ---------- BONUS FEATURES END HERE ----------
