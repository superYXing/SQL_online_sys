from sqlalchemy import Column, Integer, Date, String, func
from sqlalchemy.orm import relationship, foreign
from models.base import Base

class DateRange(Base):
    """日期范围模型"""
    __tablename__ = "date_range"
    
    date_id = Column(Integer, primary_key=True, autoincrement=True)
    begin_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # 关系
    semesters = relationship("Semester",
                           primaryjoin="func.cast(DateRange.date_id, String) == foreign(Semester.date_id)",
                           back_populates="date_range")
    
    def __repr__(self):
        return f"<DateRange(id={self.date_id}, begin={self.begin_date}, end={self.end_date})>" 