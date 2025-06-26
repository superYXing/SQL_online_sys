from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Student(Base):
    """学生模型"""
    __tablename__ = "student"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(255), nullable=False)
    student_name = Column(String(255), nullable=True)
    class_ = Column("class", String(255), nullable=True)  # class是Python关键字，使用class_
    student_password = Column(String(255), nullable=True)
    
    # 关系
    answer_records = relationship("AnswerRecord", back_populates="student")
    course_selections = relationship("CourseSelection", back_populates="student")
    
    def __repr__(self):
        return f"<Student(id={self.student_id}, name='{self.student_name}', class='{self.class_}')>" 