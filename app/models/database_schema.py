from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from models.base import Base

class DatabaseSchema(Base):
    """数据库模式模型"""
    __tablename__ = "database_schema"
    
    schema_id = Column(Integer, primary_key=True, autoincrement=True)
    schema_discription = Column(Text, nullable=True)  # 保持原SQL中的拼写
    schema_name = Column(Text, nullable=True)
    sql_schema = Column(Text, nullable=True, comment="数据库模式名称，用于USE语句")
    schema_author = Column(Text, nullable=True, comment="创建模式的教师姓名")
    sql_table = Column(Text, nullable=True, comment="数据库建表语句")
    schema_status = Column(Integer, nullable=False, default=1, comment="状态：0为禁用，1为启用")

    # 关系
    problems = relationship("Problem", back_populates="schema")
    
    def __repr__(self):
        return f"<DatabaseSchema(id={self.schema_id})>"