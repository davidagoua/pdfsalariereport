
import os
import sys

# Add the project root to sys.path to allow imports from app
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models import models
from app.core import security

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if admin:
            print("User 'admin' already exists.")
            return

        print("Creating admin user...")
        new_admin = models.User(
            username="admin",
            email="admin@performers.com",
            full_name="Admin User",
            hashed_password=security.get_password_hash("admin123")
        )
        db.add(new_admin)
        db.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
