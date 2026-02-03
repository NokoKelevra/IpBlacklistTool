import os
from dotenv import load_dotenv

# Cargar .env (si existe)
load_dotenv()

class Settings:
    def __init__(self):
        self.SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
        self.DB_PATH = os.getenv("DB_PATH", "db/blacklist.db")
        self.BLACKLIST_OUTPUT_FILE = os.getenv("BLACKLIST_OUTPUT_FILE")

        self.validate()

    def validate(self):
        missing = []
        if not self.SHODAN_API_KEY:
            missing.append("SHODAN_API_KEY")
        if not self.BLACKLIST_OUTPUT_FILE:
            missing.append("BLACKLIST_OUTPUT_FILE")

        if missing:
            raise RuntimeError(
                f"Faltan variables de entorno: {', '.join(missing)}"
            )

settings = Settings()
