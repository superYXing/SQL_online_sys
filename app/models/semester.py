from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship, foreign
from models.base import Base

class Semester(Base):
    """学期模型"""
    __tablename__ = "semester"
    
    semester_id = Column(Integer, primary_key=True, autoincrement=True)
    date_id = Column(String(10), nullable=False, unique=True)
    semester_name = Column(String(255), nullable=True)
    
    # 关系
    date_range = relationship("DateRange",
                             primaryjoin="foreign(Semester.date_id) == func.cast(DateRange.date_id, String)",
                             back_populates="semesters")
    courses = relationship("Course", back_populates="semester")
    
    def __repr__(self):
        return f"<Semester(id={self.semester_id}, name='{self.semester_name}')>" 