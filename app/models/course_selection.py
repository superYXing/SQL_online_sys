from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base

class CourseSelection(Base):
    """选课记录模型"""
    __tablename__ = "course_selection"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("course.course_id"), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    semester_id = Column(Integer, ForeignKey("semester.semester_id"), nullable=False)
    status = Column(Integer, nullable=False, default=1, comment="0为重修，1为正常")

    # 唯一约束
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id','semester_id', name='unique_student_course'),
    )
    # 关系
    student = relationship("Student", back_populates="course_selections")

    course = relationship("Course", back_populates="course_selections")
    
    def __repr__(self):
        return f"<CourseSelection(id={self.id}, student_id={self.student_id}, course_id={self.course_id})>" 