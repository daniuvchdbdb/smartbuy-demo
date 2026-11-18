from datetime import date

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(default="SmartBuy 用户", max_length=80)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class IntentRequest(BaseModel):
    text: str = Field(min_length=3, max_length=2000)


class TargetPriceRequest(BaseModel):
    variant_id: int
    target_price: float = Field(gt=0)


class PriceChangeRequest(BaseModel):
    variant_id: int
    effective_price: float = Field(gt=0)


class OwnedProductRequest(BaseModel):
    variant_id: int
    purchase_price: float = Field(gt=0)
    purchase_date: date
    warranty_date: date | None = None
    notes: str | None = Field(default=None, max_length=1000)


class EffectivePriceRequest(BaseModel):
    listed_price: float = Field(gt=0)
    discounts: list[dict]
    shipping: float = Field(default=0, ge=0)


class MatchRequest(BaseModel):
    title: str = Field(min_length=2, max_length=500)

