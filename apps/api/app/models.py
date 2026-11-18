from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(80), default="SmartBuy 用户")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    locale: Mapped[str] = mapped_column(String(20), default="zh-CN")


class UserPreference(Base):
    __tablename__ = "user_preferences"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    budget_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    performance_priority: Mapped[float] = mapped_column(Float, default=0.8)
    portability_priority: Mapped[float] = mapped_column(Float, default=0.5)
    battery_priority: Mapped[float] = mapped_column(Float, default=0.5)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(60))


class Brand(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    model: Mapped[str] = mapped_column(String(100), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500))
    demo_data: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped[Category] = relationship()
    brand: Mapped[Brand] = relationship()
    variants: Mapped[list[ProductVariant]] = relationship(back_populates="product")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(220))
    performance_score: Mapped[float] = mapped_column(Float)
    portability_score: Mapped[float] = mapped_column(Float)
    battery_score: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    product: Mapped[Product] = relationship(back_populates="variants")
    specs: Mapped[list[ProductSpec]] = relationship(back_populates="variant")
    prices: Mapped[list[PriceRecord]] = relationship(back_populates="variant")


class SpecDefinition(Base):
    __tablename__ = "spec_definitions"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    key: Mapped[str] = mapped_column(String(80))
    label: Mapped[str] = mapped_column(String(80))
    unit: Mapped[str | None] = mapped_column(String(20))
    value_type: Mapped[str] = mapped_column(String(20), default="text")
    __table_args__ = (UniqueConstraint("category_id", "key"),)


class ProductSpec(Base):
    __tablename__ = "product_specs"
    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id", ondelete="CASCADE"), index=True)
    definition_id: Mapped[int] = mapped_column(ForeignKey("spec_definitions.id"), index=True)
    value_text: Mapped[str | None] = mapped_column(String(255))
    value_number: Mapped[float | None] = mapped_column(Float)
    variant: Mapped[ProductVariant] = relationship(back_populates="specs")
    definition: Mapped[SpecDefinition] = relationship()
    __table_args__ = (UniqueConstraint("variant_id", "definition_id"),)


class PriceSource(Base):
    __tablename__ = "price_sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    provider_type: Mapped[str] = mapped_column(String(40))


class PriceRecord(Base):
    __tablename__ = "price_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("price_sources.id"))
    listed_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    effective_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, index=True)
    variant: Mapped[ProductVariant] = relationship(back_populates="prices")


class ShoppingIntent(Base):
    __tablename__ = "shopping_intents"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    original_text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(60))
    budget_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    usage: Mapped[str] = mapped_column(Text, default="[]")
    priorities: Mapped[str] = mapped_column(Text, default="{}")
    requirements: Mapped[str] = mapped_column(Text, default="{}")
    avoid: Mapped[str] = mapped_column(Text, default="[]")
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)


class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    intent_id: Mapped[int] = mapped_column(ForeignKey("shopping_intents.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class RecommendationResult(Base):
    __tablename__ = "recommendation_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("recommendation_sessions.id"), index=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"))
    rank: Mapped[int] = mapped_column(Integer)
    fit_score: Mapped[float] = mapped_column(Float)
    value_score: Mapped[float] = mapped_column(Float)
    price_score: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    final_score: Mapped[float] = mapped_column(Float)


class Watchlist(Base):
    __tablename__ = "watchlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    __table_args__ = (UniqueConstraint("user_id", "variant_id"),)


class TargetPriceAlert(Base):
    __tablename__ = "target_price_alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), index=True)
    target_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OwnedProduct(Base):
    __tablename__ = "owned_products"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), index=True)
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    purchase_date: Mapped[date | None] = mapped_column(Date)
    warranty_date: Mapped[date | None] = mapped_column(Date)
    serial_number: Mapped[str | None] = mapped_column(String(180))
    notes: Mapped[str | None] = mapped_column(Text)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(String(500))
    data: Mapped[str] = mapped_column(Text, default="{}")
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    resource: Mapped[str] = mapped_column(String(120))
    details: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


# Forward-compatible tables: defined now so migrations/data ownership are explicit.
class ProductAlias(Base):
    __tablename__ = "product_aliases"
    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), index=True)
    alias: Mapped[str] = mapped_column(String(255), index=True)
    source: Mapped[str] = mapped_column(String(50), default="manual")


class ProductMatch(Base):
    __tablename__ = "product_matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    raw_title: Mapped[str] = mapped_column(String(500))
    variant_id: Mapped[int | None] = mapped_column(ForeignKey("product_variants.id"))
    confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30))
    matching_features: Mapped[str] = mapped_column(Text, default="[]")
    conflicts: Mapped[str] = mapped_column(Text, default="[]")


def simple_entity(name: str, tablename: str):
    return type(
        name,
        (Base,),
        {
            "__tablename__": tablename,
            "id": mapped_column(Integer, primary_key=True),
            "data": mapped_column(Text, default="{}"),
            "created_at": mapped_column(DateTime(timezone=True), default=now_utc),
        },
    )


Platform = simple_entity("Platform", "platforms")
Merchant = simple_entity("Merchant", "merchants")
ProductListing = simple_entity("ProductListing", "product_listings")
ReviewSource = simple_entity("ReviewSource", "review_sources")
Review = simple_entity("Review", "reviews")
ReviewIssueCategory = simple_entity("ReviewIssueCategory", "review_issue_categories")
ReviewMention = simple_entity("ReviewMention", "review_mentions")
CompatibilityRule = simple_entity("CompatibilityRule", "compatibility_rules")
ProductRelationship = simple_entity("ProductRelationship", "product_relationships")
Order = simple_entity("Order", "orders")
OrderItem = simple_entity("OrderItem", "order_items")
ConsumerRight = simple_entity("ConsumerRight", "consumer_rights")
RightsDeadline = simple_entity("RightsDeadline", "rights_deadlines")
AffiliatePartner = simple_entity("AffiliatePartner", "affiliate_partners")
AffiliateLink = simple_entity("AffiliateLink", "affiliate_links")
AffiliateClick = simple_entity("AffiliateClick", "affiliate_clicks")
AffiliateConversion = simple_entity("AffiliateConversion", "affiliate_conversions")

