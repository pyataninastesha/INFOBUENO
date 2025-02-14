from sqlalchemy import Column, Integer, String, ForeignKey, Text, BLOB
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    task_type = Column(String, nullable=True)  # text or image
    task = Column(Text, nullable=True)        # for text-based tasks
    task_blob = Column(BLOB, nullable=True)   # for image-based tasks
    answer = Column(String, nullable=False)

    topic = relationship("Topic", back_populates="questions")
    subject = relationship("Subject", back_populates="questions")

    def set_task(self, task_data, task_type="text"):
        """
        Sets the task content and type.

        :param task_data: The task data (text or binary).
        :param task_type: The type of the task ('text' or 'image').
        """
        self.task_type = task_type
        if task_type == "text":
            self.task = task_data
            self.task_blob = None
        elif task_type == "image":
            self.task = None
            self.task_blob = task_data
        else:
            raise ValueError("Invalid task_type. Must be 'text' or 'image'.")

    def get_task(self):
        """
        Returns the task content based on its type.

        :return: The task content (text or binary).
        """
        if self.task_type == "text":
            return self.task
        elif self.task_type == "image":
            return self.task_blob
        else:
            return None