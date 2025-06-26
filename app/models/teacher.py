from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Teacher(Base):
    """教师模型"""
    __tablename__ = "teacher"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(String(255), nullable=False)
    teacher_name = Column(String(255), nullable=True)
    teacher_password = Column(String(255), nullable=True)
    
    # 关系
    courses = relationship("Course", back_populates="teacher")
    
    def __repr__(self):
        return f"<Teacher(id={self.teacher_id}, name='{self.teacher_name}')>" 