from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database import SessionLocal
from app.main import app
from app.models import PriceRecord


def test_complete_business_loop():
    with TestClient(app) as client:
        email = f"qa-{uuid4().hex[:8]}@smartbuy.cn"
        registration = client.post("/api/v1/auth/register", json={"email": email, "password": "SecurePass123", "display_name": "QA"})
        assert registration.status_code == 201
        headers = {"Authorization": f"Bearer {registration.json()['token']}"}

        parsed = client.post("/api/v1/shopping-intents", headers=headers, json={"text": "预算7000，主要编程和游戏，希望1TB硬盘，不要太重"})
        assert parsed.status_code == 201
        assert parsed.json()["requirements"]["storage_gb"] == 1024

        recommendation = client.post(f"/api/v1/shopping-intents/{parsed.json()['id']}/recommend", headers=headers)
        assert recommendation.status_code == 200
        results = recommendation.json()["results"]
        assert len(results) == 3
        assert all({"fit_score", "value_score", "price_score", "risk_score"} <= item.keys() for item in results)

        first, second = results[:2]
        comparison = client.get("/api/v1/compare", params=[("variant_ids", first["id"]), ("variant_ids", second["id"])])
        assert comparison.status_code == 200
        detail = client.get(f"/api/v1/products/{first['id']}")
        assert detail.status_code == 200
        assert len(detail.json()["price_history"]) >= 3

        assert client.post("/api/v1/target-price-alerts", headers=headers, json={"variant_id": first["id"], "target_price": 5999}).status_code == 201
        changed = client.post("/api/v1/demo/price-change", headers=headers, json={"variant_id": first["id"], "effective_price": 5899})
        assert changed.json()["notifications_created"] == 1
        assert client.get("/api/v1/notifications", headers=headers).json()["items"][0]["type"] == "TARGET_PRICE"

        purchased = client.post("/api/v1/owned-products", headers=headers, json={"variant_id": first["id"], "purchase_price": 5899, "purchase_date": "2026-08-14"})
        assert purchased.status_code == 201
        owned = client.get("/api/v1/owned-products", headers=headers).json()["items"]
        assert owned[0]["post_purchase_monitoring"] is True
        assert client.delete("/api/v1/me", headers=headers).status_code == 204
        with SessionLocal() as db:
            db.execute(delete(PriceRecord).where(PriceRecord.variant_id == first["id"], PriceRecord.effective_price == 5899))
            db.commit()
