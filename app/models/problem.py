from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.base import Base

class Problem(Base):
    """题目模型"""
    __tablename__ = "problem"
    
    problem_id = Column(Integer, primary_key=True, autoincrement=True)
    schema_id = Column(Integer, ForeignKey("database_schema.schema_id"), nullable=True)
    problem_content = Column(String(255), nullable=True)
    is_required = Column(SmallInteger, nullable=True)
    example_sql = Column(Text, nullable=True)
    is_ordered = Column(SmallInteger, nullable=True, comment="判断数据的标准：0为行无序，1为行有序")
    knowledge = Column(Text, nullable=True, comment="题目知识点")

    # 关系
    schema = relationship("DatabaseSchema", back_populates="problems")
    answer_records = relationship("AnswerRecord", back_populates="problem")
    
    def __repr__(self):
        return f"<Problem(id={self.problem_id}, content='{self.problem_content}', required={self.is_required})>"