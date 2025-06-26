from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base

class Course(Base):
    """课程模型"""
    __tablename__ = "course"
    
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teacher.teacher_id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semester.semester_id"), nullable=False)
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('teacher_id', 'semester_id', name='teacher_id'),
    )
    
    # 关系
    teacher = relationship("Teacher", back_populates="courses")
    semester = relationship("Semester", back_populates="courses")
    course_selections = relationship("CourseSelection", back_populates="course")
    
    def __repr__(self):
        return f"<Course(id={self.course_id}, teacher_id={self.teacher_id}, semester_id={self.semester_id})>" 