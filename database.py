from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Строка подключения к PostgreSQL (через pgAdmin)
# Пароль: postgres (или тот, что вводили при установке)
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/passazhiry_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()