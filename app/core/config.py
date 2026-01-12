
import os

class Settings:
    # Paths
    ASSETS_DIR = "/Users/macbookpro/devspace/pdfsalarie/assets"
    TEMP_DIR = os.path.join(ASSETS_DIR, "temp")
    COMPLETED_DIR = os.path.join(ASSETS_DIR, "completed")
    
    # SMTP
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "herve.koffi@cperformers.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    # Ensure directories exist
    @classmethod
    def ensure_dirs(cls):
        os.makedirs(cls.ASSETS_DIR, exist_ok=True)
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.COMPLETED_DIR, exist_ok=True)

settings = Settings()
settings.ensure_dirs()
