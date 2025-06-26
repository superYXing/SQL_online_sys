from models.base import Base, engine
from models import (
    Student, Teacher, DateRange, Semester, Course, 
    CourseSelection, DatabaseSchema, Problem, AnswerRecord
)

def create_tables():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("所有表已创建成功！")

def drop_tables():
    """删除所有表"""
    Base.metadata.drop_all(bind=engine)
    print("所有表已删除！")

def recreate_tables():
    """重新创建所有表"""
    drop_tables()
    create_tables()
    print("所有表已重新创建！")

if __name__ == "__main__":
    create_tables() 