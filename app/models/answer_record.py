from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, String, DateTime, SmallInteger, Text
from sqlalchemy.orm import relationship
from models.base import Base

class AnswerRecord(Base):
    """答题记录模型"""
    __tablename__ = "answer_record"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problem.problem_id"), nullable=False)
    result_type = Column(SmallInteger, nullable=False,comment="0:正确  1：语法错误  2：结果错误")
    answer_content = Column(Text, nullable=False)
    timestep = Column(DateTime, nullable=False)

    
    # 关系
    student = relationship("Student", back_populates="answer_records")
    problem = relationship("Problem", back_populates="answer_records")
    
    def __repr__(self):
        return f"<AnswerRecord(id={self.id}, student_id={self.student_id}, problem_id={self.problem_id})>"