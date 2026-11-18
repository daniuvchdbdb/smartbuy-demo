import json
from datetime import datetime, timezone
from sqlalchemy import select
from .database import SessionLocal
from .models import Notification, PriceRecord, ProductVariant, TargetPriceAlert

def check_target_prices() -> int:
    """Idempotent job suitable for RQ Scheduler/Cron."""
    created = 0
    with SessionLocal() as db:
        alerts = db.scalars(select(TargetPriceAlert).where(TargetPriceAlert.active.is_(True))).all()
        for alert in alerts:
            latest = db.scalar(select(PriceRecord).where(PriceRecord.variant_id == alert.variant_id).order_by(PriceRecord.observed_at.desc()).limit(1))
            if latest and latest.effective_price <= alert.target_price:
                product = db.scalar(select(ProductVariant).where(ProductVariant.id == alert.variant_id))
                alert.active = False; alert.triggered_at = datetime.now(timezone.utc)
                db.add(Notification(user_id=alert.user_id, type="TARGET_PRICE", title="商品已达到目标价", body=f"演示价格已降至 ¥{latest.effective_price}", data=json.dumps({"variant_id": product.id})))
                created += 1
        db.commit()
    return created
