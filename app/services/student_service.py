from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from models import Student, Teacher, Course, CourseSelection, Semester, AnswerRecord, Problem, DatabaseSchema
from schemas.student import (
    StudentProfileResponse, StudentRankItem, AnswerRecordItem, AnswerRecordsResponse,
    ProblemItem, ProblemListResponse, DatabaseSchemaItem, DatabaseSchemaListResponse,
    StudentDashboardItem, StudentDashboardResponse, StudentAnswerRecord, StudentAnswerRecordsResponse
)
from services.database_engine_service import database_engine_service
from services.sql_method_service import sql_method_service
from datetime import datetime

class StudentService:
    """学生服务类"""
    
    def get_student_profile(self, student_id: str, db: Session) -> Optional[StudentProfileResponse]:
        """获取学生个人信息"""
        try:

            #调用公共服务获取当前学期id
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            semester_id = current_semester.semester_id


            # 根据提供的SQL查询获取学生信息,根据系学期确定课程范围

            result = db.query(
                Student.student_id,
                Student.student_name,
                Student.class_,
                Course.course_id,
                Teacher.teacher_name,
                Semester.semester_name
            ).select_from(CourseSelection).join(
                Student, CourseSelection.student_id == Student.id
            ).join(
                Course, CourseSelection.course_id == Course.course_id
            ).outerjoin(
                Teacher, Course.teacher_id == Teacher.id
            ).join(
                Semester, Semester.semester_id == Course.semester_id
            ).filter(
                Student.student_id == student_id,
                Course.semester_id == semester_id
            ).first()  # 添加 .first() 来获取第一条记录

            if not result:
                # 返回空数据而不是None，保持接口一致性
                return StudentProfileResponse(
                    学号="",
                    姓名="",
                    班级="",
                    当前学期="",
                    课序号="",
                    任课教师=""
                )

            # 构建响应数据
            return StudentProfileResponse(
                学号=result.student_id,
                姓名=result.student_name or "",
                班级=result.class_ or "",
                当前学期=result.semester_name or "",
                课序号=str(result.course_id) if result.course_id else "",
                任课教师=result.teacher_name or ""
            )

        except Exception as e:
            print(f"获取学生信息失败: {e}")
            # 异常时也返回空数据而不是None
            return StudentProfileResponse(
                学号="",
                姓名="",
                班级="",
                当前学期="",
                课序号="",
                任课教师=""
            )

    def get_student_rank(self, db: Session, limit: int = 10) -> List[Dict]:
        """获取学生排名"""
        try:
            # 1. 调用public接口获取当前学期号
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            if not current_semester:
                return []

            current_semester_id = current_semester.semester_id

            # 2. 根据学期号确认课程号范围
            courses = db.query(Course).filter(Course.semester_id == current_semester_id).all()
            if not courses:
                return []

            course_ids = [course.course_id for course in courses]

            # 3. 在选课表里根据课程号范围来确定学生名单
            students_in_semester = db.query(
                Student.id,
                Student.student_id,
                Student.student_name,
                Student.class_
            ).join(
                CourseSelection, CourseSelection.student_id == Student.id
            ).filter(
                CourseSelection.course_id.in_(course_ids)
            ).distinct().all()

            # 计算每个学生的排名数据
            student_rankings = []

            for student in students_in_semester:
                # 计算正确题目数（result_type = 0的不同题目数量）
                correct_problems = db.query(
                    distinct(AnswerRecord.problem_id)
                ).filter(
                    AnswerRecord.student_id == student.id,
                    AnswerRecord.result_type == 0
                ).count()

                # 获取该学生答过的所有题目号
                answered_problems = db.query(
                    distinct(AnswerRecord.problem_id)
                ).filter(
                    AnswerRecord.student_id == student.id
                ).all()

                # 计算总方法数（所有题目的方法数之和）
                total_methods = 0
                for problem_tuple in answered_problems:
                    problem_id = problem_tuple[0]
                    # 使用sql_method_service获取该学生该题目的方法数量
                    method_stats = sql_method_service.get_method_statistics(
                        student.student_id, problem_id, db
                    )
                    total_methods += method_stats.get("total_methods", 0)

                # 构建学生排名数据
                student_name = f"{student.class_} {student.student_name}" if student.class_ else student.student_name
                student_rankings.append({
                    "student_name": student_name,
                    "correct_count": correct_problems,
                    "method_count": total_methods
                })

            # 按正确题目数降序，方法数降序排序
            student_rankings.sort(
                key=lambda x: (x["correct_count"], x["method_count"]),
                reverse=True
            )

            # 构建最终结果
            result = []
            for i, student_data in enumerate(student_rankings[:limit], 1):
                result.append({
                    "名次": i,
                    "姓名": student_data["student_name"],
                    "题目数": student_data["correct_count"],
                    "方法数": student_data["method_count"]
                })

            return result

        except Exception as e:
            print(f"获取学生排名失败: {e}")
            return []

    def get_student_dashboard(self, student_id: str, problem_id: int, db: Session) -> StudentDashboardResponse:
        """获取学生对特定题目的答题情况"""
        try:
            # 首先获取学生的内部ID
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return StudentDashboardResponse(problems=[])

            # 查询基本统计信息
            basic_stats = db.query(
                func.count().label("submit_count"),  # 总提交次数
                func.count(case((AnswerRecord.result_type == 0, 1))).label("correct_count"),  # 正确次数
                func.count(case((AnswerRecord.result_type != 0, 1))).label("wrong_count"),  # 错误次数
                func.count(case((AnswerRecord.result_type == 1, 1))).label("syntax_error_count"),  # 语法错误数
                func.count(case((AnswerRecord.result_type == 2, 1))).label("result_error_count"),  # 结果错误数
            ).filter(
                AnswerRecord.student_id == student.id,
                AnswerRecord.problem_id == problem_id
            ).first()

            # 查询方法相关统计
            # 获取所有不同的答案内容及其出现次数
            method_stats = db.query(
                AnswerRecord.answer_content,
                func.count().label("method_count")
            ).filter(
                AnswerRecord.student_id == student.id,
                AnswerRecord.problem_id == problem_id
            ).group_by(AnswerRecord.answer_content).all()

            # 计算方法数量（不同答案内容的数量）
            correct_method_count = len(method_stats)

            # 计算重复方法数（每个方法重复次数之和，减去方法总数）
            total_submissions = sum(stat.method_count for stat in method_stats)
            repeat_method_count = total_submissions - correct_method_count if correct_method_count > 0 else 0

            # 构建响应数据
            dashboard_item = StudentDashboardItem(
                problem_id=problem_id,
                submit_count=basic_stats.submit_count if basic_stats else 0,
                correct_count=basic_stats.correct_count if basic_stats else 0,
                wrong_count=basic_stats.wrong_count if basic_stats else 0,
                correct_method_count=correct_method_count,
                repeat_method_count=repeat_method_count,
                syntax_error_count=basic_stats.syntax_error_count if basic_stats else 0,
                result_error_count=basic_stats.result_error_count if basic_stats else 0
            )

            return StudentDashboardResponse(problems=[dashboard_item])

        except Exception as e:
            print(f"获取学生数据面板失败: {e}")
            return StudentDashboardResponse(problems=[])

    def submit_answer(self, student_id: str, problem_id: int, answer_content: str, db: Session, engine_type: str = "mysql") -> Tuple[int, str, Optional[int]]:
        """提交答题结果"""
        try:
            # 首先验证学生是否存在
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return -1, "学生不存在", None

            # 验证题目是否存在
            problem = db.query(Problem).filter(Problem.problem_id == problem_id).first()
            if not problem:
                return -1, "题目不存在", None

            # 检查是否有标准答案
            if not problem.example_sql:
                return -1, "题目缺少标准答案", None

            # 获取题目对应的数据库模式
            schema = None
            if problem.schema_id:
                schema = db.query(DatabaseSchema).filter(DatabaseSchema.schema_id == problem.schema_id).first()

            # 记录使用的数据库引擎类型
            print(f"使用数据库引擎: {engine_type}")
            print(f"提交的SQL: {answer_content}")
            print(f"标准答案: {problem.example_sql}")
            if schema and schema.sql_schema:
                print(f"数据库模式: {schema.sql_schema}")

            # 初始化判断结果
            result_type = 0  # 0:正确  1：语法错误  2：结果错误
            message = "结果正确"
            method_count = None

            # 1. 如果有数据库模式，根据引擎类型切换数据库或模式
            if schema and schema.sql_schema:
                if engine_type == "mysql":
                    # MySQL使用USE语句切换数据库
                    switch_sql = f"USE {schema.sql_schema};"
                elif engine_type in ["postgresql", "opengauss"]:
                    # PostgreSQL和OpenGauss使用SET search_path切换模式
                    switch_sql = f"SET search_path TO {schema.sql_schema};"
                else:
                    switch_sql = f"USE {schema.sql_schema};"  # 默认使用USE语句

                switch_success, switch_message, _ = database_engine_service.execute_sql(switch_sql, engine_type)
                if not switch_success:
                    print(f"执行数据库切换失败: {switch_message}")
                    # 继续执行，不因切换失败而中断

            # 2. 检查学生SQL的语法
            success, error_msg, student_result = database_engine_service.execute_sql(answer_content, engine_type)

            if not success:
                # 语法错误
                result_type = 1
                message = f"语法错误: {error_msg}"
            else:
                # 语法正确，进行结果比较
                # 根据题目的is_orderd字段选择比较方式
                is_ordered = problem.is_ordered if problem.is_ordered is not None else 0

                # 构建完整的SQL语句（包含数据库切换语句）
                def build_full_sql(sql_content):
                    if schema and schema.sql_schema:
                        if engine_type == "mysql":
                            return f"USE {schema.sql_schema};\n{sql_content}"
                        elif engine_type in ["postgresql", "opengauss"]:
                            return f"SET search_path TO {schema.sql_schema};\n{sql_content}"
                        else:
                            return f"USE {schema.sql_schema};\n{sql_content}"  # 默认使用USE语句
                    return sql_content

                student_full_sql = build_full_sql(answer_content)
                answer_full_sql = build_full_sql(problem.example_sql)

                if is_ordered == 0:
                    # 行无序比较，使用EXCEPT ALL
                    result_match, compare_msg = database_engine_service.compare_results_unordered(
                        student_full_sql, answer_full_sql, engine_type
                    )
                else:
                    # 行有序比较，使用JSON数组比较
                    result_match, compare_msg = database_engine_service.compare_results_ordered(
                        student_full_sql, answer_full_sql, engine_type
                    )

                if not result_match:
                    result_type = 2
                    message = "结果错误"
                else:
                    result_type = 0
                    message = "结果正确"

            # 创建答题记录，使用当前服务器时间作为时间戳
            current_time = datetime.now()
            answer_record = AnswerRecord(
                student_id=student.id,
                problem_id=problem_id,
                answer_content=answer_content,
                result_type=result_type,
                timestep=current_time
            )

            db.add(answer_record)
            db.commit()
            db.refresh(answer_record)

            # 返回结果
            return result_type, message, answer_record.id

        except Exception as e:
            db.rollback()
            print(f"提交答案失败: {e}")
            return -1, f"提交失败: {str(e)}", None

    # 已删除: get_answer_records 方法 - 功能已整合到其他方法

    def get_problem_list(self, schema_id: Optional[int] = None, db: Session = None) -> ProblemListResponse:
        """获取题目列表"""
        try:
            query = db.query(Problem)

            # 如果指定了schema_id，则过滤
            if schema_id is not None:
                query = query.filter(Problem.schema_id == schema_id)

            problems = query.all()

            # 构建响应数据
            problem_list = []
            for problem in problems:
                problem_list.append(ProblemItem(
                    problem_id=problem.problem_id,
                    problem_content=problem.problem_content or "",
                    is_required=problem.is_required or 0,
                    schema_id=problem.schema_id or 0
                ))

            return ProblemListResponse(
                problems=problem_list,
                total=len(problem_list),
                schema_id=schema_id
            )

        except Exception as e:
            print(f"获取题目列表失败: {e}")
            return ProblemListResponse(problems=[], total=0, schema_id=schema_id)

    def get_database_schemas(self, db: Session) -> DatabaseSchemaListResponse:
        """获取数据库模式列表"""
        try:
            schemas = db.query(DatabaseSchema).all()

            # 构建响应数据
            schema_list = []
            for schema in schemas:
                schema_list.append(DatabaseSchemaItem(
                    schema_id=schema.schema_id,
                    schema_name=schema.schema_name,
                    schema_description=schema.schema_discription  # 注意原字段名的拼写
                ))

            return DatabaseSchemaListResponse(
                schemas=schema_list,
                total=len(schema_list)
            )

        except Exception as e:
            print(f"获取数据库模式列表失败: {e}")
            return DatabaseSchemaListResponse(schemas=[], total=0)

    def get_student_answer_records(self, student_id: str, problem_id: int, db: Session) -> Optional[StudentAnswerRecordsResponse]:
        """根据题目ID查询当前学生提交的答题记录"""
        try:
            # 获取学生的内部ID
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return None

            # 查询该学生该题目的所有答题记录，按时间倒序排列
            answer_records = db.query(AnswerRecord).filter(
                AnswerRecord.student_id == student.id,
                AnswerRecord.problem_id == problem_id
            ).order_by(AnswerRecord.timestep.desc()).all()

            if not answer_records:
                return None

            # 构建答题记录列表
            record_list = []
            for record in answer_records:
                record_list.append(StudentAnswerRecord(
                    answer_record_id=record.id,
                    result_type=record.result_type,
                    answer_content=record.answer_content,
                    timestep=record.timestep
                ))

            return StudentAnswerRecordsResponse(
                student_id=int(student_id),
                problem_id=problem_id,
                records=record_list
            )



        except Exception as e:
            print(f"获取学生答题记录失败: {e}")
            return None

# 全局学生服务实例
student_service = StudentService()