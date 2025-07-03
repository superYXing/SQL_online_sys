
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

    def switch_database_or_schema(self, schema_name: str, engine_type: str = "mysql") -> Tuple[bool, str]:
        """
        根据数据库引擎类型切换数据库或模式

        Args:
            schema_name: 数据库名或模式名
            engine_type: 数据库引擎类型

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        if engine_type not in self.engines:
            return False, f"不支持的数据库引擎: {engine_type}"

        session_class = self.sessions[engine_type]
        session = session_class()

        try:
            if engine_type == "mysql":
                # MySQL使用USE语句切换数据库
                switch_sql = f"USE {schema_name};"
            elif engine_type in ["postgresql", "opengauss"]:
                # PostgreSQL和OpenGauss使用SET search_path切换模式
                switch_sql = f"SET search_path TO {schema_name};"
            else:
                return False, f"不支持的数据库引擎: {engine_type}"

            # 执行切换语句
            session.execute(text(switch_sql))
            session.commit()
            return True, f"成功切换到{schema_name}"

        except SQLAlchemyError as e:
            session.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            return False, f"切换失败: {error_msg}"
        except Exception as e:
            session.rollback()
            return False, f"切换失败: {str(e)}"
        finally:
            session.close()

    def execute_sql(self, sql: str, engine_type: str = "mysql") -> Tuple[bool, str, Optional[List[Dict]]]:
        """
        执行SQL语句（支持多语句执行）

        Args:
            sql: SQL语句（可能包含多个语句，如USE + SELECT）
            engine_type: 数据库引擎类型

        Returns:
            Tuple[bool, str, Optional[List[Dict]]]: (是否成功, 消息, 结果数据)
        """
        if engine_type not in self.engines:
            return False, f"不支持的数据库引擎: {engine_type}", None

        session_class = self.sessions[engine_type]
        session = session_class()

        try:
            # 分割多个SQL语句
            sql_statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]

            last_result = None
            last_columns = None

            for i, statement in enumerate(sql_statements):
                # 执行每个SQL语句
                result = session.execute(text(statement))

                # 如果是查询语句，保存结果
                if statement.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    # 将结果转换为字典列表
                    columns = result.keys()
                    data = []
                    for row in rows:
                        row_dict = {}
                        for j, column in enumerate(columns):
                            value = row[j]
                            # 处理特殊数据类型
                            if hasattr(value, 'isoformat'):  # datetime对象
                                value = value.isoformat()
                            elif isinstance(value, (bytes, bytearray)):  # 二进制数据
                                value = str(value)
                            row_dict[column] = value
                        data.append(row_dict)

                    last_result = data
                    last_columns = columns

            session.commit()

            # 返回最后一个查询的结果，如果没有查询则返回空列表
            if last_result is not None:
                return True, "执行成功", last_result
            else:
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
            student_sql: 学生的SQL语句（可能包含USE语句）
            answer_sql: 标准答案SQL语句（可能包含USE语句）
            engine_type: 数据库引擎类型

        Returns:
            Tuple[bool, str]: (是否一致, 消息)
        """
        try:
            # 提取实际的查询语句（去除USE语句和SET search_path语句）
            def extract_query_sql(sql):
                lines = sql.strip().split('\n')
                query_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.upper().startswith('USE ') and not line.upper().startswith('SET SEARCH_PATH'):
                        query_lines.append(line)
                return '\n'.join(query_lines)

            student_query = extract_query_sql(student_sql)
            answer_query = extract_query_sql(answer_sql)

            # 去除末尾分号
            if student_query.endswith(";"):
                student_query = student_query[:-1]
            if answer_query.endswith(";"):
                answer_query = answer_query[:-1]

            # 先执行完整的SQL（包含USE语句）获取结果
            success1, msg1, student_result = self.execute_sql(student_sql, engine_type)
            if not success1:
                return False, f"执行学生SQL失败: {msg1}"

            success2, msg2, answer_result = self.execute_sql(answer_sql, engine_type)
            if not success2:
                return False, f"执行标准答案SQL失败: {msg2}"

            # 比较结果集大小
            if len(student_result) != len(answer_result):
                return False, "结果错误"

            # 如果都是空结果集
            if len(student_result) == 0:
                return True, "结果正确"

            # 构建EXCEPT ALL查询来比较结果
            except_query1 = f"({student_query}) EXCEPT ALL ({answer_query})"
            except_query2 = f"({answer_query}) EXCEPT ALL ({student_query})"

            # 执行EXCEPT查询
            success3, msg3, result1 = self.execute_sql(except_query1, engine_type)
            success4, msg4, result2 = self.execute_sql(except_query2, engine_type)

            # 如果EXCEPT查询失败，使用直接比较
            if not success3 or not success4:
                # 直接比较结果内容
                if student_result == answer_result:
                    return True, "结果正确"
                else:
                    return False, "结果错误"

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
            student_sql: 学生的SQL语句（可能包含USE语句）
            answer_sql: 标准答案SQL语句（可能包含USE语句）
            engine_type: 数据库引擎类型

        Returns:
            Tuple[bool, str]: (是否一致, 消息)
        """
        try:
            # 执行学生的SQL（包含USE语句）
            success1, msg1, student_result = self.execute_sql(student_sql, engine_type)
            if not success1:
                return False, f"执行学生SQL失败: {msg1}"

            # 执行标准答案SQL（包含USE语句）
            success2, msg2, answer_result = self.execute_sql(answer_sql, engine_type)
            if not success2:
                return False, f"执行标准答案SQL失败: {msg2}"

            # 直接比较结果列表（有序比较）
            if student_result == answer_result:
                return True, "结果正确"
            else:
                return False, "结果错误"

        except Exception as e:
            return False, f"结果比较失败: {str(e)}"

# 全局数据库引擎服务实例
database_engine_service = DatabaseEngineService()
