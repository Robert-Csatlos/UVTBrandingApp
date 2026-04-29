"""
Run from project root:  python seed_users.py
Skips any record whose unique key already exists in the database.
"""

from backend.database import SessionLocal, engine
from backend import models
from backend.auth import get_password_hash

models.Base.metadata.create_all(bind=engine)

SAMPLE_USERS = [
    {
        "email":     "superadmin@e-uvt.ro",
        "password":  "superadmin",
        "full_name": "Ion Popescu",
        "role":      "SuperAdmin",
    },
    {
        "email":     "admin.dept@e-uvt.ro",
        "password":  "admin1234",
        "full_name": "Maria Ionescu",
        "role":      "Admin",
    },
    {
        "email":     "coordinator@e-uvt.ro",
        "password":  "coord1234",
        "full_name": "Alexandru Muresan",
        "role":      "Coordinator",
    },
    {
        "email":     "vizualizator@e-uvt.ro",
        "password":  "viz123456",
        "full_name": "Ana Munteanu",
        "role":      "Vizualizator",
    },
]

SAMPLE_INVENTORY = [
    # Banners
    {
        "name": "Banner UVT Vertical Mare",
        "category": "Bannere",
        "inventory_code": "BAN-001",
        "quantity": 4,
        "status": "good",
        "location": "Depozit Central",
        "responsible_person": "Alexandru Muresan",
    },
    {
        "name": "Banner UVT Orizontal",
        "category": "Bannere",
        "inventory_code": "BAN-002",
        "quantity": 2,
        "status": "worn",
        "location": "Depozit Central",
        "responsible_person": "Alexandru Muresan",
    },
    {
        "name": "Roll-Up UVT Branding",
        "category": "Bannere",
        "inventory_code": "BAN-003",
        "quantity": 6,
        "status": "new",
        "location": "Sala Evenimente",
        "responsible_person": "Maria Ionescu",
    },
    # Flags / Steaguri
    {
        "name": "Steag UVT Interior",
        "category": "Steaguri",
        "inventory_code": "STG-001",
        "quantity": 10,
        "status": "good",
        "location": "Depozit Central",
        "responsible_person": "Alexandru Muresan",
    },
    {
        "name": "Steag UVT Exterior (catarg)",
        "category": "Steaguri",
        "inventory_code": "STG-002",
        "quantity": 3,
        "status": "good",
        "location": "Curtea UVT",
        "responsible_person": "Ion Popescu",
    },
    # Promotional items / Materiale promotionale
    {
        "name": "Mapa Conferinta UVT",
        "category": "Materiale Promotionale",
        "inventory_code": "PRO-001",
        "quantity": 150,
        "status": "new",
        "location": "Depozit Rectorat",
        "responsible_person": "Maria Ionescu",
    },
    {
        "name": "Pix Inscriptionat UVT",
        "category": "Materiale Promotionale",
        "inventory_code": "PRO-002",
        "quantity": 500,
        "status": "new",
        "location": "Depozit Rectorat",
        "responsible_person": "Maria Ionescu",
    },
    {
        "name": "Tricou UVT (M)",
        "category": "Materiale Promotionale",
        "inventory_code": "PRO-003",
        "quantity": 40,
        "status": "good",
        "location": "Depozit Central",
        "responsible_person": "Alexandru Muresan",
    },
    {
        "name": "Tricou UVT (L)",
        "category": "Materiale Promotionale",
        "inventory_code": "PRO-004",
        "quantity": 35,
        "status": "good",
        "location": "Depozit Central",
        "responsible_person": "Alexandru Muresan",
    },
    {
        "name": "Sacosa Textila UVT",
        "category": "Materiale Promotionale",
        "inventory_code": "PRO-005",
        "quantity": 200,
        "status": "new",
        "location": "Depozit Rectorat",
        "responsible_person": "Maria Ionescu",
    },
    # AV / Tech equipment
    {
        "name": "Proiector Epson EB-X51",
        "category": "Echipamente AV",
        "inventory_code": "AV-001",
        "quantity": 5,
        "status": "good",
        "location": "Sala Conferinte A",
        "responsible_person": "Alexandru Muresan",
    },
    {
        "name": "Ecran Proiectie 200x200cm",
        "category": "Echipamente AV",
        "inventory_code": "AV-002",
        "quantity": 3,
        "status": "good",
        "location": "Depozit Central",
        "responsible_person": "Alexandru Muresan",
    },
    {
        "name": "Microfon Wireless Sennheiser",
        "category": "Echipamente AV",
        "inventory_code": "AV-003",
        "quantity": 8,
        "status": "good",
        "location": "Sala Conferinte A",
        "responsible_person": "Ana Munteanu",
    },
    {
        "name": "Stativ Microfon",
        "category": "Echipamente AV",
        "inventory_code": "AV-004",
        "quantity": 6,
        "status": "worn",
        "location": "Depozit Central",
        "responsible_person": "Ana Munteanu",
    },
    # Furniture / Mobilier
    {
        "name": "Masa Pliabila Evenimente",
        "category": "Mobilier",
        "inventory_code": "MOB-001",
        "quantity": 12,
        "status": "good",
        "location": "Depozit Central",
        "responsible_person": "Alexandru Muresan",
    },
    {
        "name": "Scaun Pliabil",
        "category": "Mobilier",
        "inventory_code": "MOB-002",
        "quantity": 80,
        "status": "good",
        "location": "Depozit Central",
        "responsible_person": "Alexandru Muresan",
    },
    {
        "name": "Podium Conferinta",
        "category": "Mobilier",
        "inventory_code": "MOB-003",
        "quantity": 2,
        "status": "new",
        "location": "Sala Conferinte A",
        "responsible_person": "Ion Popescu",
    },
]


def seed_users(db):
    created = skipped = 0
    for u in SAMPLE_USERS:
        if db.query(models.User).filter(models.User.email == u["email"]).first():
            print(f"  SKIP  {u['email']} (already exists)")
            skipped += 1
            continue
        db.add(models.User(
            email=u["email"],
            hashed_password=get_password_hash(u["password"]),
            full_name=u["full_name"],
            role=u["role"],
        ))
        db.commit()
        print(f"  OK    {u['email']}  [{u['role']}]")
        created += 1
    print(f"  Users: {created} created, {skipped} skipped.\n")


def seed_inventory(db):
    created = skipped = 0
    for item in SAMPLE_INVENTORY:
        if db.query(models.Inventory).filter(
            models.Inventory.inventory_code == item["inventory_code"]
        ).first():
            print(f"  SKIP  {item['inventory_code']} — {item['name']} (already exists)")
            skipped += 1
            continue
        db.add(models.Inventory(
            **item,
            photo_path="pending.jpg",
            qr_code_path="pending.png",
        ))
        db.commit()
        print(f"  OK    {item['inventory_code']} — {item['name']}  [{item['status']}]")
        created += 1
    print(f"  Inventory: {created} created, {skipped} skipped.\n")


def seed():
    db = SessionLocal()
    try:
        print("=== Seeding Users ===")
        seed_users(db)
        print("=== Seeding Inventory ===")
        seed_inventory(db)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
