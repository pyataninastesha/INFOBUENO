import os
from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base

# Получаем URL базы данных из переменных окружения
database_url = os.getenv("DATABASE_URL")

# Если DATABASE_URL отсутствует, используем локальную SQLite
if not database_url:
    database_url = "sqlite:///db/database.db"

# Fix для SQLAlchemy (если PostgreSQL, заменяем "postgres://" на "postgresql://")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://")

# Создаем подключение к базе данных
engine = create_engine(database_url)
SessionLocal = orm.sessionmaker(bind=engine)

Base = declarative_base()

def create_session():
    return SessionLocal()

def global_init():
    """Инициализация базы данных"""
    Base.metadata.create_all(engine)
