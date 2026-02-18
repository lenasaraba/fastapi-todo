import logging
from sqlalchemy.orm import Session
from app.models.database_models import Role

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_roles(db: Session):
    required_roles = ["admin", "user"]
    
    try:
        for role_name in required_roles:
            role_exists = db.query(Role).filter(Role.name == role_name).first()
            if not role_exists:
                db.add(Role(name=role_name))
                logger.info(f"Adding role: {role_name}")
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding roles: {e}")