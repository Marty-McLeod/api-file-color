from database import Base
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, Field
from auth.api_key import API_KEY_MIN_LEN, API_KEY_MAX_LEN


class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String)
    email = Column(String)
    auth_level = Column(String, default="user")
    active = Column(Boolean, default=False)


class UserRequest(BaseModel):
    api_key: str | None = Field(min_length=API_KEY_MIN_LEN, max_length=API_KEY_MAX_LEN)
    email: str = Field(min_length=6, max_length=40)
    auth_level: str = Field(min_length=4, max_length=22)
    active: bool