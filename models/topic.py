from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase


class Topic(SqlAlchemyBase):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    name = Column(String, nullable=False)

    subject = relationship("Subject", back_populates="topics")
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="topic")