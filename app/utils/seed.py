from app.database import SessionLocal
from app.models.database_models import Role

def seed_roles():
    db=SessionLocal()
    required_roles=["admin", "user"]

    for role_name in required_roles:
        role_exists=db.query(Role).filter(Role.name==role_name).first()
        if not role_exists:
            new_role=Role(name=role_name)
            db.add(new_role)
    
    db.commit()
    db.close()