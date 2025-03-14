from backend import create_app, db
from backend.models import Product

app = create_app()
app.app_context().push()

# Удаляем старые данные
db.drop_all()
db.create_all()

# Список товаров (огнестрельное оружие)
products = [
    Product(name="Glock 17", description="Semi-automatic pistol, 9mm, 17-round magazine.", price=550, stock=10),
    Product(name="Colt M1911", description="Classic .45 ACP pistol with single-stack design.", price=750, stock=5),
    Product(name="Smith & Wesson M&P15", description="AR-15 style rifle, 5.56mm NATO, lightweight and modular.", price=1200, stock=8),
    Product(name="Remington 870", description="Pump-action shotgun, 12 gauge, tactical design.", price=450, stock=12),
    Product(name="Barrett M82", description=".50 BMG sniper rifle, long-range precision.", price=8500, stock=2),
    Product(name="AK-47", description="7.62x39mm, durable and widely used worldwide.", price=1100, stock=15),
    Product(name="FN SCAR 17S", description="7.62 NATO battle rifle, modern design.", price=3200, stock=6),
    Product(name="Mossberg 500", description="Pump-action shotgun, versatile and reliable.", price=400, stock=10),
    Product(name="SIG Sauer P320", description="Modular 9mm pistol, used by the U.S. military.", price=650, stock=9),
    Product(name="Desert Eagle .50AE", description="Large-caliber semi-auto handgun, powerful stopping force.", price=1500, stock=4),
]

# Добавляем в базу данных
db.session.add_all(products)
db.session.commit()

print("✅ Products successfully added to the database!")
