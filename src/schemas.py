from pydantic import BaseModel
from typing import List, Optional


class Car(BaseModel):
    name: str
    model: str
    price_per_day: float
    seats: int
    transmission: str
    fuel_type: str
    images: List[str]
    description: Optional[str] = ""
    available: bool = True


class CarUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    price_per_day: Optional[float] = None
    seats: Optional[int] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    images: Optional[List[str]] = None
    description: Optional[str] = None
    available: Optional[bool] = None


class PicnicSpot(BaseModel):
    name: str
    price: float
    location: str
    images: List[str]
    short_description: str
    detailed_description: str
    trip_images: Optional[List[str]] = None
    hotel_images: Optional[List[str]] = None
    available: bool = True


class PicnicSpotUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    images: Optional[List[str]] = None
    short_description: Optional[str] = None
    detailed_description: Optional[str] = None
    trip_images: Optional[List[str]] = None
    hotel_images: Optional[List[str]] = None
    available: Optional[bool] = None


class AdminLogin(BaseModel):
    username: str
    password: str


class UserLoginEmail(BaseModel):
    email: str
    password: str


class GoogleLoginRequest(BaseModel):
    token: str


class WhatsAppConfig(BaseModel):
    phone_number: str
    message: str
