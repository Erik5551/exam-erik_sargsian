from database import engine, SessionLocal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Определяем модели прямо здесь (чтобы не зависеть от models.py)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    fio = Column(String(200), nullable=False)
    birth_date = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transport_type = Column(String(50), nullable=False)
    start_date = Column(String(10), nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), default="Novaya")
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    text = Column(Text, nullable=False)
    rating = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    db = SessionLocal()
    admin = db.query(User).filter(User.login == "Admin26").first()
    if not admin:
        admin = User(
            login="Admin26",
            password="Demo20",
            fio="Administrator",
            birth_date="01.01.1990",
            phone="8(999)999-99-99",
            email="admin@passazhiry.ru",
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("✅ Admin created: Admin26 / Demo20")
    db.close()

if __name__ == "__main__":
    init_db()