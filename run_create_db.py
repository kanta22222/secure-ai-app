from sqlalchemy import create_engine
from database.db import DATABASE_URL
from server.models import Base

def create_database():
    # Replace aiosqlite with sqlite for synchronous
    sync_url = DATABASE_URL.replace("aiosqlite", "sqlite")
    engine = create_engine(sync_url, echo=True)
    Base.metadata.create_all(bind=engine)
    print("Database created successfully.")

if __name__ == "__main__":
    create_database()
