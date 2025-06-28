from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Semester(Base):
    """学期模型"""
    __tablename__ = "semester"
    
    semester_id = Column(Integer, primary_key=True, autoincrement=True)
    date_id = Column(String(10), ForeignKey("date_range.date_id"), nullable=False, unique=True)
    semester_name = Column(String(255), nullable=True)
    
    # 关系
    date_range = relationship("DateRange", back_populates="semesters")
    courses = relationship("Course", back_populates="semester")
    
    def __repr__(self):
        return f"<Semester(id={self.semester_id}, name='{self.semester_name}')>" 