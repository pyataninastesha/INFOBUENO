from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase

class Subject(SqlAlchemyBase):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="subject")