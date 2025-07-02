from ftplib import print_line
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class DatabaseEngineService:
    """数据库引擎服务类"""
    
    def __init__(self):
        self.engines = {}
        self.sessions = {}
        self._init_engines()
    
    def _init_engines(self):
        """初始化数据库引擎"""
        try:
            # MySQL引擎
            mysql_url = os.getenv("MYSQL_DATABASE_URL")
            if mysql_url:
                self.engines["mysql"] = create_engine(mysql_url)
                self.sessions["mysql"] = sessionmaker(bind=self.engines["mysql"])
            
            # PostgreSQL引擎
            postgresql_url = os.getenv("POSTGRESQL_DATABASE_URL")
            if postgresql_url:
                self.engines["postgresql"] = create_engine(postgresql_url)
                self.sessions["postgresql"] = sessionmaker(bind=self.engines["postgresql"])
            
            # OpenGauss引擎（使用PostgreSQL驱动）
            opengauss_url = os.getenv("OPENGAUSS_DATABASE_URL")
            if opengauss_url:
                self.engines["opengauss"] = create_engine(opengauss_url)
                self.sessions["opengauss"] = sessionmaker(bind=self.engines["opengauss"])
                
        except Exception as e:
            print(f"初始化数据库引擎失败: {e}")
    
    def execute_sql(self, sql: str, engine_type: str = "mysql") -> Tuple[bool, str, Optional[List[Dict]]]:
        """
        执行SQL语句
        
        Args:
            sql: SQL语句
            engine_type: 数据库引擎类型
            
        Returns:
            Tuple[bool, str, Optional[List[Dict]]]: (是否成功, 消息, 结果数据)
        """
        if engine_type not in self.engines:
            return False, f"不支持的数据库引擎: {engine_type}", None
        
        session_class = self.sessions[engine_type]
        session = session_class()
        
        try:
            # 执行SQL语句
            result = session.execute(text(sql))
            
            # 如果是查询语句，获取结果
            if sql.strip().upper().startswith('SELECT'):
                rows = result.fetchall()
                # 将结果转换为字典列表
                columns = result.keys()
                data = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(columns):
                        value = row[i]
                        # 处理特殊数据类型
                        if hasattr(value, 'isoformat'):  # datetime对象
                            value = value.isoformat()
                        elif isinstance(value, (bytes, bytearray)):  # 二进制数据
                            value = str(value)
                        row_dict[column] = value
                    data.append(row_dict)
                
                session.commit()
                return True, "执行成功", data
            else:
                # 非查询语句
                session.commit()
                return True, "执行成功", []
                
        except SQLAlchemyError as e:
            session.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            return False, f"SQL语法错误: {error_msg}", None
        except Exception as e:
            session.rollback()
            return False, f"执行错误: {str(e)}", None
        finally:
            session.close()
    
    def compare_results_unordered(self, student_sql: str, answer_sql: str, engine_type: str = "postgresql") -> Tuple[bool, str]:
        """
        比较无序结果（使用EXCEPT ALL）
        
        Args:
            student_sql: 学生的SQL语句
            answer_sql: 标准答案SQL语句
            engine_type: 数据库引擎类型
            
        Returns:
            Tuple[bool, str]: (是否一致, 消息)
        """
        try:
            # 如果student_sql最后一个字符是";"结尾，则去掉它
            if student_sql.endswith(";"):
                student_sql = student_sql[:-1]
            if answer_sql.endswith(";"):
                answer_sql = answer_sql[:-1]

            # 构建EXCEPT ALL查询
            except_query1 = f"({student_sql}) EXCEPT ALL ({answer_sql})"
            except_query2 = f"({answer_sql}) EXCEPT ALL ({student_sql})"

            print_line("except_query1:"+ except_query1)
            print_line("except_query2:"+ except_query2)
            # 执行第一个EXCEPT查询
            success1, msg1, result1 = self.execute_sql(except_query1, engine_type)
            if not success1:
                return False, f"比较查询1失败: {msg1}"
            
            # 执行第二个EXCEPT查询
            success2, msg2, result2 = self.execute_sql(except_query2, engine_type)
            if not success2:
                return False, f"比较查询2失败: {msg2}"
            
            # 如果两个EXCEPT查询结果都为空，说明结果一致
            if len(result1) == 0 and len(result2) == 0:
                return True, "结果正确"
            else:
                return False, "结果错误"
                
        except Exception as e:
            return False, f"结果比较失败: {str(e)}"
    
    def compare_results_ordered(self, student_sql: str, answer_sql: str, engine_type: str = "postgresql") -> Tuple[bool, str]:
        """
        比较有序结果（使用JSON数组比较）
        
        Args:
            student_sql: 学生的SQL语句
            answer_sql: 标准答案SQL语句
            engine_type: 数据库引擎类型
            
        Returns:
            Tuple[bool, str]: (是否一致, 消息)
        """
        try:
            # 执行学生的SQL
            success1, msg1, student_result = self.execute_sql(student_sql, engine_type)
            if not success1:
                return False, f"执行学生SQL失败: {msg1}"
            
            # 执行标准答案SQL
            success2, msg2, answer_result = self.execute_sql(answer_sql, engine_type)
            if not success2:
                return False, f"执行标准答案SQL失败: {msg2}"
            
            # 直接比较结果列表
            if student_result == answer_result:
                return True, "结果正确"
            else:
                return False, "结果错误"
                
        except Exception as e:
            return False, f"结果比较失败: {str(e)}"

# 全局数据库引擎服务实例
database_engine_service = DatabaseEngineService()
