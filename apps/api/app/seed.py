from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Brand, Category, PriceRecord, PriceSource, Product, ProductSpec, ProductVariant, SpecDefinition


PRODUCTS = [
    # category, brand, name, model, sku, title, current, low30, low90, performance, portability, battery, risk, specs
    ("laptops", "联想", "拯救者 Y7000P", "Y7000P 2026", "LNV-Y7P-5060", "RTX 5060 / 16GB / 1TB", 6199, 5999, 5799, 94, 58, 70, 18, {"cpu": "Core Ultra 7", "gpu": "RTX 5060", "ram_gb": 16, "storage_gb": 1024, "screen": "16英寸 2560×1600 165Hz", "weight_kg": 2.2}),
    ("laptops", "华硕", "天选 6 Pro", "FA507", "ASU-TX6-5060", "RTX 5060 / 16GB / 1TB", 6499, 6199, 5999, 92, 62, 68, 22, {"cpu": "Ryzen 9", "gpu": "RTX 5060", "ram_gb": 16, "storage_gb": 1024, "screen": "15.6英寸 2.5K 165Hz", "weight_kg": 2.1}),
    ("laptops", "惠普", "暗影精灵 11", "OMEN 11", "HP-OM11-5060", "RTX 5060 / 24GB / 1TB", 6799, 6599, 6299, 93, 55, 66, 20, {"cpu": "Core i9", "gpu": "RTX 5060", "ram_gb": 24, "storage_gb": 1024, "screen": "16英寸 2.5K 240Hz", "weight_kg": 2.35}),
    ("laptops", "苹果", "MacBook Air", "M5 13", "APL-MBA-M5-512", "M5 / 16GB / 512GB", 7499, 7299, 6999, 86, 96, 96, 10, {"cpu": "Apple M5", "gpu": "集成显卡", "ram_gb": 16, "storage_gb": 512, "screen": "13.6英寸", "weight_kg": 1.24}),
    ("laptops", "小米", "Redmi Book Pro 16", "2026", "MI-RBP16-1T", "32GB / 1TB", 5299, 4999, 4799, 80, 82, 84, 15, {"cpu": "Core Ultra 7", "gpu": "集成显卡", "ram_gb": 32, "storage_gb": 1024, "screen": "16英寸 3.1K 120Hz", "weight_kg": 1.75}),
    ("phones", "小米", "小米 16", "2510PN", "MI16-512", "16GB / 512GB", 4599, 4399, 4199, 93, 86, 88, 13, {"ram_gb": 16, "storage_gb": 512, "screen": "6.36英寸", "battery_mah": 5100}),
    ("phones", "苹果", "iPhone 17", "A3520", "IP17-256", "256GB", 5999, 5699, 5499, 91, 88, 84, 9, {"storage_gb": 256, "screen": "6.3英寸", "battery_mah": 3900}),
    ("phones", "华为", "Mate 80", "VYG-AL00", "HW-M80-512", "16GB / 512GB", 6499, 6299, 5999, 88, 83, 93, 11, {"ram_gb": 16, "storage_gb": 512, "screen": "6.7英寸", "battery_mah": 5500}),
    ("phones", "荣耀", "Magic8", "BKQ-AN00", "HON-M8-512", "16GB / 512GB", 4999, 4699, 4499, 91, 84, 92, 14, {"ram_gb": 16, "storage_gb": 512, "screen": "6.58英寸", "battery_mah": 5600}),
    ("phones", "OPPO", "Find X9", "CPH2791", "OP-X9-512", "16GB / 512GB", 5299, 4999, 4799, 92, 82, 90, 12, {"ram_gb": 16, "storage_gb": 512, "screen": "6.6英寸", "battery_mah": 5400}),
    ("monitors", "戴尔", "UltraSharp U2725Q", "U2725Q", "DEL-U2725Q", "27英寸 4K IPS Black", 3299, 3099, 2899, 90, 75, 80, 8, {"screen": "27英寸", "resolution": "3840×2160", "refresh_hz": 120, "ports": "USB-C 140W"}),
    ("monitors", "小米", "Mini LED 电竞显示器", "G Pro 27", "MI-GP27", "27英寸 2K 180Hz", 1799, 1599, 1499, 88, 72, 78, 18, {"screen": "27英寸", "resolution": "2560×1440", "refresh_hz": 180, "ports": "DP/HDMI"}),
    ("monitors", "AOC", "Q27G4ZMN", "Q27G4ZMN", "AOC-Q27G4", "27英寸 2K Mini LED", 2299, 2099, 1999, 91, 70, 76, 16, {"screen": "27英寸", "resolution": "2560×1440", "refresh_hz": 240, "ports": "DP/HDMI"}),
    ("monitors", "华硕", "ProArt PA279CRV", "PA279CRV", "ASU-PA279", "27英寸 4K 专业显示器", 3199, 2999, 2799, 86, 73, 82, 7, {"screen": "27英寸", "resolution": "3840×2160", "refresh_hz": 60, "ports": "USB-C 96W"}),
    ("headphones", "索尼", "WH-1000XM7", "YY2985", "SONY-XM7-B", "头戴式降噪耳机 黑色", 2399, 2099, 1999, 93, 81, 91, 17, {"connection": "Bluetooth 5.4", "battery_hours": 30, "weight_g": 254}),
    ("headphones", "苹果", "AirPods Pro 3", "A3060", "APL-APP3", "主动降噪真无线耳机", 1699, 1499, 1399, 90, 96, 82, 11, {"connection": "Bluetooth", "battery_hours": 8, "weight_g": 11}),
    ("headphones", "Bose", "QuietComfort Ultra II", "QCUII", "BOSE-QCUII", "头戴式降噪耳机", 2799, 2499, 2299, 92, 84, 88, 13, {"connection": "Bluetooth 5.4", "battery_hours": 32, "weight_g": 250}),
    ("headphones", "漫步者", "NeoBuds Pro 3", "NBP3", "ED-NBP3", "圈铁降噪真无线耳机", 799, 699, 649, 85, 94, 83, 15, {"connection": "Bluetooth 5.4", "battery_hours": 7, "weight_g": 12}),
    ("tablets", "苹果", "iPad Air M4", "A3416", "APL-IPA-M4", "11英寸 256GB", 4799, 4499, 4299, 94, 91, 89, 8, {"storage_gb": 256, "screen": "11英寸", "weight_g": 460}),
    ("tablets", "华为", "MatePad Pro 13.2", "WEB-W09", "HW-MPP132", "12GB / 512GB", 4999, 4699, 4399, 89, 78, 92, 10, {"ram_gb": 12, "storage_gb": 512, "screen": "13.2英寸", "weight_g": 580}),
    ("tablets", "小米", "小米平板 8 Pro", "25091RP04C", "MI-PAD8P", "12GB / 256GB", 2999, 2799, 2599, 88, 84, 87, 12, {"ram_gb": 12, "storage_gb": 256, "screen": "11.2英寸", "weight_g": 500}),
    ("accessories", "绿联", "氮化镓充电器", "CD244", "UG-100W-4P", "100W 四口 USB-C", 299, 249, 219, 86, 93, 82, 9, {"power_w": 100, "protocol": "PD/PPS", "ports": "3C1A"}),
    ("accessories", "闪迪", "至尊极速移动固态硬盘", "E61", "SD-E61-1T", "1TB USB-C", 699, 619, 579, 88, 91, 80, 14, {"storage_gb": 1024, "interface": "USB 3.2 Gen 2", "speed_mbps": 1050}),
    ("accessories", "贝尔金", "USB-C 11 合 1 扩展坞", "INC012", "BLK-DOCK-11", "双显示器 / 100W PD / 2.5G 网口", 699, 629, 599, 84, 88, 79, 10, {"power_w": 100, "display_output": "HDMI 2.0 + DP 1.4", "ports": "11", "network": "2.5GbE"}),
]

CATEGORY_NAMES = {"laptops": "笔记本电脑", "phones": "手机", "monitors": "显示器", "headphones": "耳机", "tablets": "平板", "accessories": "配件"}


def seed_demo(db: Session) -> None:
    categories = {}
    for slug, name in CATEGORY_NAMES.items():
        category = db.scalar(select(Category).where(Category.slug == slug))
        if not category:
            category = Category(slug=slug, name=name)
            db.add(category)
        categories[slug] = category
    brands = {}
    for brand_name in {row[1] for row in PRODUCTS}:
        brand = db.scalar(select(Brand).where(Brand.name == brand_name))
        if not brand:
            brand = Brand(name=brand_name)
            db.add(brand)
        brands[brand_name] = brand
    db.flush()
    source = db.scalar(select(PriceSource).where(PriceSource.name == "SmartBuy 演示价格"))
    if not source:
        source = PriceSource(name="SmartBuy 演示价格", provider_type="mock")
        db.add(source)
    db.flush()
    definitions: dict[tuple[str, str], SpecDefinition] = {}
    now = datetime.now(timezone.utc)
    for category, brand, name, model, sku, title, current, low30, low90, performance, portability, battery, risk, specs in PRODUCTS:
        if db.scalar(select(ProductVariant.id).where(ProductVariant.sku == sku)):
            continue
        product = Product(category_id=categories[category].id, brand_id=brands[brand].id, name=name, model=model, demo_data=True)
        db.add(product)
        db.flush()
        variant = ProductVariant(product_id=product.id, sku=sku, title=title, performance_score=performance, portability_score=portability, battery_score=battery, risk_score=risk)
        db.add(variant)
        db.flush()
        for key, value in specs.items():
            definition = definitions.get((category, key)) or db.scalar(select(SpecDefinition).where(SpecDefinition.category_id == categories[category].id, SpecDefinition.key == key))
            if not definition:
                definition = SpecDefinition(category_id=categories[category].id, key=key, label=key.replace("_", " ").title(), value_type="number" if isinstance(value, (int, float)) else "text")
                definitions[(category, key)] = definition
                db.add(definition)
                db.flush()
            db.add(ProductSpec(variant_id=variant.id, definition_id=definition.id, value_number=float(value) if isinstance(value, (int, float)) else None, value_text=None if isinstance(value, (int, float)) else str(value)))
        for days, price in ((90, max(current, low90 + 700)), (60, low90), (30, low30), (7, round((current + low30) / 2)), (0, current)):
            db.add(PriceRecord(variant_id=variant.id, source_id=source.id, listed_price=Decimal(str(price)), effective_price=Decimal(str(price)), confidence=1, observed_at=now - timedelta(days=days)))
    db.commit()
