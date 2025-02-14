from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(120), nullable=False)

    tests = relationship("Test", back_populates="user", cascade="all, delete-orphan")