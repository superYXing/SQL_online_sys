import re
from typing import List, Tuple
from sqlalchemy.orm import Session
from models import AnswerRecord, Student

class SQLMethodService:
    """SQL方法判断服务类"""
    
    # SQL关键词列表（按优先级排序）
    SQL_KEYWORDS = [
        "select", "from", "where", "group by", "having", "order by", 
        "limit", "offset", "fetch", "distinct", "as", "join", 
        "inner join", "left join", "right join", "full join", 
        "cross join", "lateral join", "natural join", "union", 
        "union all", "except", "intersect", "with", "case", 
        "when", "then", "else", "end"
    ]
    
    def __init__(self):
        pass
    
    def extract_sql_keywords(self, sql: str) -> List[str]:
        """
        从SQL语句中提取关键词序列
        
        Args:
            sql: SQL语句
            
        Returns:
            List[str]: 按顺序提取的关键词列表
        """
        # 将SQL转换为小写并去除多余空格
        sql_lower = re.sub(r'\s+', ' ', sql.lower().strip())
        
        # 存储找到的关键词及其位置
        found_keywords = []
        
        # 按关键词长度降序排序，优先匹配长关键词（如"group by"优先于"by"）
        sorted_keywords = sorted(self.SQL_KEYWORDS, key=len, reverse=True)
        
        # 查找所有关键词的位置
        for keyword in sorted_keywords:
            # 使用正则表达式确保关键词是完整的单词
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.finditer(pattern, sql_lower)
            
            for match in matches:
                start_pos = match.start()
                # 检查这个位置是否已经被更长的关键词占用
                if not any(existing_start <= start_pos < existing_end for existing_start, existing_end, _ in found_keywords):
                    found_keywords.append((start_pos, match.end(), keyword))
        
        # 按位置排序并返回关键词列表
        found_keywords.sort(key=lambda x: x[0])
        return [keyword for _, _, keyword in found_keywords]

    
    def get_method_statistics(self, student_id: str, problem_id: int, db: Session) -> dict:
        """
        获取方法统计信息

        Args:
            student_id: 学生ID
            problem_id: 题目ID
            db: 数据库会话

        Returns:
            dict: 方法统计信息
        """
        try:
            # 获取学生的内部ID
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return {"total_methods": 0, "max_method_count": 0}

            # 获取该学生该题目的所有答题记录
            records = db.query(AnswerRecord).filter(
                AnswerRecord.student_id == student.id,
                AnswerRecord.problem_id == problem_id
            ).all()

            if not records:
                return {"total_methods": 0, "max_method_count": 0}

            # 统计不同的方法（通过SQL关键词序列）
            unique_methods = set()
            max_method_count = 0

            for record in records:
                # 提取SQL关键词序列
                keywords = tuple(self.extract_sql_keywords(record.answer_content))
                unique_methods.add(keywords)

                # 检查是否有method_count字段（兼容历史数据）
                if hasattr(record, 'method_count') and record.method_count:
                    max_method_count = max(max_method_count, record.method_count)

            # 如果没有method_count数据，使用不同方法的数量作为最大方法数
            if max_method_count == 0:
                max_method_count = len(unique_methods)

            return {
                "total_methods": len(unique_methods),
                "max_method_count": max_method_count
            }

        except Exception as e:
            print(f"获取方法统计失败: {e}")
            return {"total_methods": 0, "max_method_count": 0}

# 全局SQL方法服务实例
sql_method_service = SQLMethodService()
