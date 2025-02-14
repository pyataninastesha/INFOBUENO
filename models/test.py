from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase


class Test(SqlAlchemyBase):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    score = Column(Integer, nullable=False)

    user = relationship("User", back_populates="tests")
    topic = relationship("Topic", back_populates="tests")