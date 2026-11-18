from __future__ import annotations

import json
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session, selectinload

from .config import PROJECT_ROOT, settings
from .database import Base, SessionLocal, engine, get_db
from .engines import BuyTimingEngine, Discount, EffectivePriceEngine, ProductMatchingEngine, ScoringEngine, ShoppingIntentParser
from .models import (
    AuditLog,
    AuthSession,
    Brand,
    Category,
    Notification,
    OwnedProduct,
    PriceRecord,
    PriceSource,
    Product,
    ProductSpec,
    ProductVariant,
    RecommendationResult,
    RecommendationSession,
    ShoppingIntent,
    TargetPriceAlert,
    User,
    UserProfile,
    UserPreference,
    Watchlist,
)
from .schemas import EffectivePriceRequest, IntentRequest, LoginRequest, MatchRequest, OwnedProductRequest, PriceChangeRequest, RegisterRequest, TargetPriceRequest
from .security import create_session, current_user, hash_password, verify_password
from .seed import seed_demo


@asynccontextmanager
async def lifespan(_: FastAPI):
    (PROJECT_ROOT / "data").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_demo(db)
        if not db.scalar(select(User).where(User.email == "demo@example.com")):
            demo = User(email="demo@example.com", password_hash=hash_password("SmartBuy123"), display_name="演示用户")
            db.add(demo)
            db.flush()
            db.add_all([UserProfile(user_id=demo.id), UserPreference(user_id=demo.id, budget_max=7000)])
            db.commit()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"] if settings.cors_origins == "*" else settings.cors_origins.split(","), allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

rate_windows: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = rate_windows[key]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= 180:
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "请求过于频繁"}, status_code=429)
        window.append(now)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


def specs_for(variant: ProductVariant) -> dict:
    return {item.definition.key: item.value_number if item.value_number is not None else item.value_text for item in variant.specs}


def price_rows(variant: ProductVariant) -> list[PriceRecord]:
    return sorted(variant.prices, key=lambda row: row.observed_at)


def serialize_variant(variant: ProductVariant, intent: dict | None = None) -> dict:
    prices = price_rows(variant)
    history = [float(row.effective_price) for row in prices]
    current = history[-1] if history else None
    price_score = ScoringEngine.price_score(current, history) if current is not None else 0
    base_intent = intent or {"priorities": {"performance": 0.7, "portability": 0.5, "battery": 0.5}}
    fit = ScoringEngine.fit_score(variant, base_intent, specs_for(variant))
    value = ScoringEngine.value_score(fit, price_score, variant.risk_score)
    return {
        "id": variant.id,
        "product_id": variant.product_id,
        "name": variant.product.name,
        "brand": variant.product.brand.name,
        "category": variant.product.category.slug,
        "model": variant.product.model,
        "variant": variant.title,
        "sku": variant.sku,
        "image_url": variant.product.image_url,
        "demo_data": variant.product.demo_data,
        "current_price": current,
        "fit_score": fit,
        "value_score": value,
        "price_score": price_score,
        "risk_score": variant.risk_score,
        "final_score": ScoringEngine.final_score(fit, value, price_score, variant.risk_score),
        "buy_advice": BuyTimingEngine.analyze(current, history) if current is not None else {"code": "INSUFFICIENT_DATA", "label": "数据不足"},
        "specs": specs_for(variant),
    }


def variant_query():
    return select(ProductVariant).options(selectinload(ProductVariant.product).selectinload(Product.brand), selectinload(ProductVariant.product).selectinload(Product.category), selectinload(ProductVariant.specs).selectinload(ProductSpec.definition), selectinload(ProductVariant.prices))


def get_variant(db: Session, variant_id: int) -> ProductVariant:
    variant = db.scalar(variant_query().where(ProductVariant.id == variant_id))
    if not variant:
        raise HTTPException(404, "商品型号不存在")
    return variant


def audit(db: Session, user_id: int | None, action: str, resource: str, details: dict | None = None) -> None:
    db.add(AuditLog(user_id=user_id, action=action, resource=resource, details=json.dumps(details or {}, ensure_ascii=False)))


@app.get("/api/v1/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok", "demo_mode": settings.demo_mode, "products": db.scalar(select(func.count(Product.id)))}


@app.post("/api/v1/auth/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "邮箱已注册")
    user = User(email=email, password_hash=hash_password(payload.password), display_name=payload.display_name)
    db.add(user)
    db.flush()
    db.add_all([UserProfile(user_id=user.id), UserPreference(user_id=user.id)])
    audit(db, user.id, "REGISTER", f"user:{user.id}")
    db.commit()
    return {"token": create_session(db, user.id), "user": {"id": user.id, "email": user.email, "display_name": user.display_name}}


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "邮箱或密码错误")
    audit(db, user.id, "LOGIN", f"user:{user.id}")
    db.commit()
    return {"token": create_session(db, user.id), "user": {"id": user.id, "email": user.email, "display_name": user.display_name}}


@app.get("/api/v1/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "display_name": user.display_name}


@app.get("/api/v1/products")
def products(q: str | None = None, category: str | None = None, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    stmt = variant_query().join(Product)
    if q:
        stmt = stmt.join(Brand).where(or_(Product.name.ilike(f"%{q}%"), Product.model.ilike(f"%{q}%"), ProductVariant.title.ilike(f"%{q}%"), Brand.name.ilike(f"%{q}%")))
    if category:
        stmt = stmt.join(Category).where(Category.slug == category)
    rows = db.scalars(stmt.offset(offset).limit(limit)).all()
    return {"items": [serialize_variant(row) for row in rows], "offset": offset, "limit": limit, "data_label": "演示数据"}


@app.get("/api/v1/products/{variant_id}")
def product_detail(variant_id: int, db: Session = Depends(get_db)):
    variant = get_variant(db, variant_id)
    payload = serialize_variant(variant)
    history = price_rows(variant)
    payload["price_history"] = [{"price": float(row.effective_price), "observed_at": row.observed_at.isoformat(), "confidence": row.confidence} for row in history]
    payload["price_summary"] = {"current": payload["current_price"], "lowest_30d": min((float(row.effective_price) for row in history if (datetime.now(timezone.utc) - row.observed_at.replace(tzinfo=timezone.utc)).days <= 30), default=None), "lowest_90d": min((float(row.effective_price) for row in history), default=None), "all_time_low": min((float(row.effective_price) for row in history), default=None)}
    payload["risk_profile"] = {"level": "低" if variant.risk_score < 15 else "中" if variant.risk_score < 30 else "高", "score": variant.risk_score, "note": "演示风险分，尚未接入真实评论样本"}
    return payload


@app.post("/api/v1/shopping-intents", status_code=201)
def parse_intent(payload: IntentRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    parsed = ShoppingIntentParser().parse(payload.text)
    row = ShoppingIntent(user_id=user.id, original_text=payload.text, category=parsed["category"], budget_max=parsed["budget_max"], usage=json.dumps(parsed["usage"]), priorities=json.dumps(parsed["priorities"]), requirements=json.dumps(parsed["requirements"]), avoid=json.dumps(parsed["avoid"]))
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "original_text": row.original_text, **parsed, "confirmed": False}


def decode_intent(row: ShoppingIntent) -> dict:
    return {"category": row.category, "budget_max": float(row.budget_max) if row.budget_max is not None else None, "usage": json.loads(row.usage), "priorities": json.loads(row.priorities), "requirements": json.loads(row.requirements), "avoid": json.loads(row.avoid)}


@app.post("/api/v1/shopping-intents/{intent_id}/recommend")
def recommend(intent_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    intent_row = db.scalar(select(ShoppingIntent).where(ShoppingIntent.id == intent_id, ShoppingIntent.user_id == user.id))
    if not intent_row:
        raise HTTPException(404, "需求不存在")
    intent_row.confirmed = True
    intent = decode_intent(intent_row)
    stmt = variant_query().join(Product).join(Category).where(Category.slug == intent["category"])
    candidates = db.scalars(stmt).all()
    ranked = []
    for variant in candidates:
        item = serialize_variant(variant, intent)
        if intent["budget_max"] and item["current_price"] > intent["budget_max"]:
            continue
        item["why"] = f"适合度 {item['fit_score']:.0f}，{item['buy_advice']['reason']}；核心结论来自结构化参数与演示价格。"
        ranked.append(item)
    ranked.sort(key=lambda row: row["final_score"], reverse=True)
    session = RecommendationSession(user_id=user.id, intent_id=intent_id)
    db.add(session)
    db.flush()
    for index, item in enumerate(ranked[:3], 1):
        db.add(RecommendationResult(session_id=session.id, variant_id=item["id"], rank=index, fit_score=item["fit_score"], value_score=item["value_score"], price_score=item["price_score"], risk_score=item["risk_score"], final_score=item["final_score"]))
    audit(db, user.id, "RECOMMEND", f"intent:{intent_id}", {"results": [item["id"] for item in ranked[:3]]})
    db.commit()
    return {"session_id": session.id, "intent": intent, "results": ranked[:3], "data_label": "演示数据"}


@app.get("/api/v1/compare")
def compare(variant_ids: list[int] = Query(min_length=2, max_length=4), db: Session = Depends(get_db)):
    items = [serialize_variant(get_variant(db, variant_id)) for variant_id in variant_ids]
    dimensions = ["current_price", "fit_score", "value_score", "price_score", "risk_score"]
    differences = []
    for key in dimensions:
        best = min(items, key=lambda x: x[key]) if key in ("current_price", "risk_score") else max(items, key=lambda x: x[key])
        differences.append({"dimension": key, "best_variant_id": best["id"], "values": {str(item["id"]): item[key] for item in items}})
    return {"items": items, "differences": differences, "summary": f"{max(items, key=lambda x: x['fit_score'])['name']} 的综合适合度最高；请同时关注价格与风险差异。"}


@app.post("/api/v1/watchlist/{variant_id}", status_code=201)
def save_watchlist(variant_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    get_variant(db, variant_id)
    existing = db.scalar(select(Watchlist).where(Watchlist.user_id == user.id, Watchlist.variant_id == variant_id))
    if not existing:
        db.add(Watchlist(user_id=user.id, variant_id=variant_id))
        db.commit()
    return {"saved": True, "variant_id": variant_id}


@app.get("/api/v1/watchlist")
def list_watchlist(user: User = Depends(current_user), db: Session = Depends(get_db)):
    ids = db.scalars(select(Watchlist.variant_id).where(Watchlist.user_id == user.id)).all()
    return {"items": [serialize_variant(get_variant(db, item)) for item in ids]}


@app.post("/api/v1/target-price-alerts", status_code=201)
def create_alert(payload: TargetPriceRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    get_variant(db, payload.variant_id)
    row = TargetPriceAlert(user_id=user.id, variant_id=payload.variant_id, target_price=Decimal(str(payload.target_price)))
    db.add(row)
    audit(db, user.id, "CREATE_TARGET_PRICE", f"variant:{payload.variant_id}", {"target": payload.target_price})
    db.commit()
    db.refresh(row)
    return {"id": row.id, "variant_id": row.variant_id, "target_price": float(row.target_price), "active": row.active}


@app.post("/api/v1/demo/price-change")
def demo_price_change(payload: PriceChangeRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not settings.demo_mode:
        raise HTTPException(404)
    variant = get_variant(db, payload.variant_id)
    source = db.scalar(select(PriceSource).where(PriceSource.provider_type == "mock"))
    db.add(PriceRecord(variant_id=variant.id, source_id=source.id, listed_price=Decimal(str(payload.effective_price)), effective_price=Decimal(str(payload.effective_price)), confidence=1))
    alerts = db.scalars(select(TargetPriceAlert).where(TargetPriceAlert.variant_id == variant.id, TargetPriceAlert.active.is_(True), TargetPriceAlert.target_price >= payload.effective_price)).all()
    for alert in alerts:
        alert.active = False
        alert.triggered_at = datetime.now(timezone.utc)
        db.add(Notification(user_id=alert.user_id, type="TARGET_PRICE", title=f"{variant.product.name} 已达到目标价", body=f"演示价格已降至 ¥{payload.effective_price:.0f}", data=json.dumps({"variant_id": variant.id})))
    audit(db, user.id, "DEMO_PRICE_CHANGE", f"variant:{variant.id}", {"price": payload.effective_price, "alerts": len(alerts)})
    db.commit()
    return {"recorded": True, "notifications_created": len(alerts), "data_label": "演示数据"}


@app.get("/api/v1/notifications")
def notifications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())).all()
    return {"items": [{"id": row.id, "type": row.type, "title": row.title, "body": row.body, "created_at": row.created_at.isoformat()} for row in rows]}


@app.post("/api/v1/owned-products", status_code=201)
def mark_purchased(payload: OwnedProductRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    variant = get_variant(db, payload.variant_id)
    row = OwnedProduct(user_id=user.id, variant_id=payload.variant_id, purchase_price=Decimal(str(payload.purchase_price)), purchase_date=payload.purchase_date, warranty_date=payload.warranty_date, notes=payload.notes)
    db.add(row)
    audit(db, user.id, "MARK_PURCHASED", f"variant:{payload.variant_id}", {"price": payload.purchase_price})
    db.commit()
    db.refresh(row)
    return {"id": row.id, "name": variant.product.name, "purchase_price": float(row.purchase_price), "post_purchase_monitoring": True}


@app.get("/api/v1/owned-products")
def owned_products(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(OwnedProduct).where(OwnedProduct.user_id == user.id)).all()
    return {"items": [{"id": row.id, "product": serialize_variant(get_variant(db, row.variant_id)), "purchase_price": float(row.purchase_price) if row.purchase_price else None, "purchase_date": row.purchase_date.isoformat() if row.purchase_date else None, "warranty_date": row.warranty_date.isoformat() if row.warranty_date else None, "post_purchase_monitoring": True} for row in rows]}


@app.delete("/api/v1/owned-products/{owned_id}", status_code=204)
def delete_owned(owned_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(OwnedProduct).where(OwnedProduct.id == owned_id, OwnedProduct.user_id == user.id))
    if not row:
        raise HTTPException(404, "设备不存在")
    db.delete(row)
    db.commit()


@app.get("/api/v1/me/export")
def export_my_data(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"user": {"id": user.id, "email": user.email, "display_name": user.display_name}, "owned_products": owned_products(user, db)["items"], "watchlist_variant_ids": list(db.scalars(select(Watchlist.variant_id).where(Watchlist.user_id == user.id)).all())}


@app.delete("/api/v1/me", status_code=204)
def delete_account(user: User = Depends(current_user), db: Session = Depends(get_db)):
    session_ids = select(RecommendationSession.id).where(RecommendationSession.user_id == user.id)
    db.execute(delete(RecommendationResult).where(RecommendationResult.session_id.in_(session_ids)))
    for model in (RecommendationSession, ShoppingIntent, Notification, OwnedProduct, TargetPriceAlert, Watchlist, AuditLog, AuthSession, UserPreference, UserProfile):
        db.execute(delete(model).where(model.user_id == user.id))
    db.delete(user)
    db.commit()


@app.post("/api/v1/tools/effective-price")
def calculate_effective_price(payload: EffectivePriceRequest):
    return EffectivePriceEngine.calculate(payload.listed_price, [Discount(label=item["label"], amount=float(item["amount"]), verified=bool(item.get("verified", False))) for item in payload.discounts], payload.shipping)


@app.post("/api/v1/tools/product-match")
def product_match(payload: MatchRequest, db: Session = Depends(get_db)):
    rows = db.scalars(variant_query()).all()
    candidates = [{"id": row.id, "brand": row.product.brand.name, "model": row.product.model, "title": row.title, "sku": row.sku} for row in rows]
    return ProductMatchingEngine.match(payload.title, candidates)


@app.get("/api/v1/admin/overview")
def admin_overview(db: Session = Depends(get_db)):
    return {"products": db.scalar(select(func.count(Product.id))), "variants": db.scalar(select(func.count(ProductVariant.id))), "prices": db.scalar(select(func.count(PriceRecord.id))), "users": db.scalar(select(func.count(User.id))), "active_alerts": db.scalar(select(func.count(TargetPriceAlert.id)).where(TargetPriceAlert.active.is_(True))), "data_label": "演示数据"}
