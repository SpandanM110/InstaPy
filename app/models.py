# app/models.py

from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: str
    password: str
    following: List[PyObjectId] = []
    followers: List[PyObjectId] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "spandan",
                "email": "spandan@example.com",
                "password": "hashed_password",
                "following": [],
                "followers": [],
            }
        }


class Post(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    caption: str
    image_url: str
    category: str
    hashtags: List[str]
    user_id: PyObjectId
    created_at: datetime

    @staticmethod
    def extract_hashtags(caption: str) -> List[str]:
        return [word for word in caption.split() if word.startswith("#")]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "caption": "Enjoying the sunny day! #sunny #fun",
                "image_url": "/static/images/sunny_day.jpg",
                "category": "Lifestyle",
                "hashtags": ["sunny", "fun"],
                "user_id": "60d5f483f8d2e30d8c8b4567",
                "created_at": "2024-12-28T16:15:25.941Z",
            }
        }


class Comment(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    text: str
    user_id: PyObjectId
    post_id: PyObjectId
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "text": "Great post!",
                "user_id": "60d5f483f8d2e30d8c8b4567",
                "post_id": "60d5f483f8d2e30d8c8b4568",
                "created_at": "2024-12-28T16:20:00.000Z",
            }
        }


class Like(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    post_id: PyObjectId
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "60d5f483f8d2e30d8c8b4567",
                "post_id": "60d5f483f8d2e30d8c8b4568",
                "created_at": "2024-12-28T16:25:00.000Z",
            }
        }
