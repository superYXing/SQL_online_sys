from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from models import Student, Teacher, Course, CourseSelection, Semester, AnswerRecord, Problem, DatabaseSchema
from schemas.student import (
    StudentProfileResponse, StudentRankItem, AnswerRecordItem, AnswerRecordsResponse,
    ProblemItem, ProblemListResponse, DatabaseSchemaItem, DatabaseSchemaListResponse,
    StudentDashboardItem, StudentDashboardResponse
)
from datetime import datetime

class StudentService:
    """学生服务类"""
    
    def get_student_profile(self, student_id: str, db: Session) -> Optional[StudentProfileResponse]:
        """获取学生个人信息"""
        try:
            # 根据提供的SQL查询获取学生信息
            # 注意：这里需要根据实际的外键关系来调整查询
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
                Student.student_id == student_id
            ).first()
            
            if not result:
                return None
            
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
            return None

    def get_student_rank(self, db: Session, limit: int = 10) -> List[Dict]:
        """获取学生排名"""
        # 使用正确的CASE WHEN语法
        correct_count = func.sum(
            case(
                (AnswerRecord.is_correct == 1, 1),
                else_=0
            )
        ).label("correct_count")

        # 使用COUNT DISTINCT
        method_count = func.count(
            distinct(AnswerRecord.answer_content)
        ).label("method_count")

        # 查询并按照正确数量和方法数量排序
        query_result = db.query(
            Student.student_name,
            Student.class_,
            correct_count,
            method_count
        ).join(
            AnswerRecord, AnswerRecord.student_id == Student.id
        ).group_by(
            Student.id, Student.student_name, Student.class_
        ).order_by(
            correct_count.desc(),
            method_count.desc()
        ).limit(limit).all()

        # 构建结果
        result = []
        for i, (name, class_name, correct, methods) in enumerate(query_result, 1):
            student_name = f"{class_name} {name}" if class_name else name
            result.append({
                "名次": i,
                "姓名": student_name,
                "题目数": correct,
                "方法数": methods
            })

        return result

    def get_student_dashboard(self, student_id: str, problem_id: int, db: Session) -> StudentDashboardResponse:
        """获取学生对特定题目的答题情况"""
        try:
            # 查询学生对特定题目的答题情况，使用正确的case语法
            result = db.query(
                func.count().label("submit_count"),  # 总提交次数
                func.count(case((AnswerRecord.is_correct == 1, 1))).label("correct_count"),  # 正确次数
                func.count(case((AnswerRecord.is_correct == 0, 1))).label("wrong_count"),  # 错误次数
                func.count(distinct(case((AnswerRecord.is_correct == 1, AnswerRecord.answer_content)))).label("correct_method_count")  # 正确方法数
            ).select_from(AnswerRecord).outerjoin(
                Student, AnswerRecord.student_id == Student.id
            ).filter(
                Student.student_id == student_id,
                AnswerRecord.problem_id == problem_id
            ).first()

            # 构建响应数据
            dashboard_item = StudentDashboardItem(
                problem_id=problem_id,
                submit_count=result.submit_count if result else 0,
                correct_count=result.correct_count if result else 0,
                wrong_count=result.wrong_count if result else 0,
                correct_method_count=result.correct_method_count if result else 0,
                repeat_method_count=0,  # 默认返回0，暂不添加sql查询逻辑
                syntax_error_count=0,    # 默认返回0，暂不添加sql查询逻辑
                result_error_count=0     # 默认返回0，暂不添加sql查询逻辑
            )

            return StudentDashboardResponse(problems=[dashboard_item])

        except Exception as e:
            print(f"获取学生数据面板失败: {e}")
            return StudentDashboardResponse(problems=[])

    def submit_answer(self, student_id: str, problem_id: int, answer_content: str, db: Session) -> Tuple[bool, str, Optional[int]]:
        """提交答题结果"""
        try:
            # 首先验证学生是否存在
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return False, "学生不存在", None

            # 验证题目是否存在
            problem = db.query(Problem).filter(Problem.problem_id == problem_id).first()
            if not problem:
                return False, "题目不存在", None

            # TODO: 实现SQL语句正确性判断逻辑
            # 根据接口文档要求，需要实现以下功能：
            # 1. 执行学生提交的SQL语句
            # 2. 与题目的标准答案或预期结果进行对比
            # 3. 判断答案是否正确
            # 4. 可能的实现方式：
            #    - 执行SQL并对比查询结果
            #    - 使用SQL解析器分析语法和语义
            #    - 与标准答案进行模式匹配

            # 目前先简单模拟：如果SQL包含SELECT关键字就认为是正确的
            is_correct = 1 if "SELECT" in answer_content.upper() else 0

            # 创建答题记录，使用当前服务器时间作为时间戳
            current_time = datetime.now()
            answer_record = AnswerRecord(
                student_id=student.id,
                problem_id=problem_id,
                answer_content=answer_content,
                is_correct=is_correct,
                timestep=current_time
            )

            db.add(answer_record)
            db.commit()
            db.refresh(answer_record)

            message = "答案正确！" if is_correct else "答案错误,再思考一下！。"
            return bool(is_correct), message, answer_record.id

        except Exception as e:
            db.rollback()
            print(f"提交答案失败: {e}")
            return False, f"提交失败: {str(e)}", None

    def get_answer_records(self, student_id: Optional[str] = None, problem_id: Optional[int] = None,
                          page: int = 1, limit: int = 20, db: Session = None) -> AnswerRecordsResponse:
        """获取答题记录"""
        try:
            # 构建基础查询
            query = db.query(AnswerRecord)

            # 如果指定了学生ID，添加学生过滤条件
            if student_id:
                student = db.query(Student).filter(Student.student_id == student_id).first()
                if student:
                    query = query.filter(AnswerRecord.student_id == student.id)
                else:
                    # 学生不存在，返回空结果
                    return AnswerRecordsResponse(records=[], total=0, page=page, limit=limit)

            # 如果指定了题目ID，添加题目过滤条件
            if problem_id:
                query = query.filter(AnswerRecord.problem_id == problem_id)

            # 获取总数
            total = query.count()

            # 分页查询
            offset = (page - 1) * limit
            records = query.order_by(AnswerRecord.timestep.desc()).offset(offset).limit(limit).all()

            # 构建响应数据
            record_items = []
            for record in records:
                record_items.append(AnswerRecordItem(
                    answer_id=record.id,
                    problem_id=record.problem_id,
                    answer_content=record.answer_content,
                    is_correct=record.is_correct,
                    submit_time=record.timestep
                ))

            return AnswerRecordsResponse(
                records=record_items,
                total=total,
                page=page,
                limit=limit
            )

        except Exception as e:
            print(f"获取答题记录失败: {e}")
            return AnswerRecordsResponse(records=[], total=0, page=page, limit=limit)

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

# 全局学生服务实例
student_service = StudentService()