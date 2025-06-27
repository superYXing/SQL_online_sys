from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base

class CourseSelection(Base):
    """选课记录模型"""
    __tablename__ = "course_selection"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    date_id = Column(String(10), nullable=False)
    course_id = Column(Integer, ForeignKey("course.course_id"), nullable=False)
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('student_id', 'date_id', 'course_id', name='student_id'),
    )
    
    # 关系
    student = relationship("Student", back_populates="course_selections")

    course = relationship("Course", back_populates="course_selections")
    
    def __repr__(self):
        return f"<CourseSelection(id={self.id}, student_id={self.student_id}, course_id={self.course_id})>" 