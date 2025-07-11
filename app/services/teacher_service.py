from typing import Optional, List, Dict, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct, and_
from models import (
    Teacher, Course, Semester, Student, CourseSelection, AnswerRecord, Problem,
    DatabaseSchema
)
from schemas.teacher import (
    TeacherProfileResponse, StudentCreateRequest,
    StudentCreateResponse,
    ScoreCalculateRequest, StudentScoreInfo, ScoreUpdateResponse, ScoreListResponse,
    TeacherStudentInfo, TeacherStudentListResponse,
    StudentInfoResponse, StudentProfileNewResponse, StudentProfileDocResponse,
    StudentCourseAddRequest, StudentCourseAddResponse, StudentCourseItem,
    SchemaCreateRequest, SchemaCreateResponse, SchemaUpdateRequest, SchemaUpdateResponse,
    SQLQueryRequest, SQLQueryResponse,
    ProblemCreateRequest, ProblemCreateResponse
)
# 已删除无用导入: CourseInfo, TeacherCourseListResponse, StudentGradeInfo, CourseGradeResponse, ProblemStatisticsResponse, DashboardMatrixResponse
from datetime import datetime
import json
import os
import psycopg2
from services.public_service import public_service

class TeacherService:
    """教师服务类"""



    
    def get_teacher_profile(self, teacher_id: str, db: Session) -> Optional[TeacherProfileResponse]:
        """获取教师个人信息"""
        try:
            # 获取教师基本信息
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return None

            # 获取当前学期（调用公共服务）
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            semester_name = current_semester.semester_name if current_semester else "暂无学期"

            # 获取教师信息，这里假设任课教师就是教师本人
            # 根据实际业务逻辑调整
            return TeacherProfileResponse(
                teacher_id=teacher.teacher_id,
                teacher_name=teacher.teacher_name or "未知",
                semester_name=semester_name,
            )

        except Exception as e:
            print(f"获取教师个人信息失败: {e}")
            return None

    # 已删除: get_teacher_courses 方法 - 功能已整合到其他方法

    # 已删除: get_course_grades 方法 - 功能已整合到其他方法

    # 已删除: export_course_grades 方法 - 功能已整合到其他方法

    def create_student(self, teacher_id: str, student_data: StudentCreateRequest,
                      db: Session) -> Tuple[bool, str, Optional[StudentCreateResponse]]:
        """教师创建学生"""
        try:
            # 验证教师是否存在
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return False, "教师不存在", None

            # 检查学生ID是否已存在
            existing_student = db.query(Student).filter(
                Student.student_id == student_data.student_id
            ).first()
            if existing_student:
                return False, f"学生ID {student_data.student_id} 已存在", None

            # 创建新学生
            new_student = Student(
                student_id=student_data.student_id,
                student_name=student_data.student_name,
                class_=student_data.class_,
                student_password=student_data.student_password
            )

            db.add(new_student)
            db.commit()
            db.refresh(new_student)

            # 构建响应
            response = StudentCreateResponse(
                id=new_student.id,
                student_id=new_student.student_id,
                student_name=new_student.student_name,
                class_=new_student.class_
            )

            return True, "学生创建成功", response

        except Exception as e:
            db.rollback()
            print(f"创建学生失败: {e}")
            return False, f"创建失败: {str(e)}", None

    def add_student_course_batch(self, teacher_id: str, course_data_list: List[StudentCourseItem],
                                db: Session) -> Tuple[bool, str, Optional[StudentCourseAddResponse]]:
        """批量添加学生选课信息"""
        try:
            # 验证教师是否存在
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return False, "教师不存在", None

            # 获取当前学期ID
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            if not current_semester:
                return False, "无法获取当前学期信息", None

            success_count = 0
            fail_count = 0
            fail_details = []

            for course_data in course_data_list:
                try:
                    # 验证课程是否存在
                    course = db.query(Course).filter(Course.course_id == course_data.course_id).first()
                    if not course:
                        fail_count += 1
                        fail_details.append(f"学生 {course_data.student_id}: 课程ID {course_data.course_id} 不存在")
                        continue

                    # 检查学生是否已存在
                    existing_student = db.query(Student).filter(
                        Student.student_id == course_data.student_id
                    ).first()

                    if existing_student:
                        # 学生已存在，检查是否已经选择了该课程
                        existing_selection = db.query(CourseSelection).filter(
                            CourseSelection.student_id == existing_student.id,
                            CourseSelection.course_id == course_data.course_id,
                            CourseSelection.semester_id == current_semester.semester_id
                        ).first()

                        if existing_selection:
                            fail_count += 1
                            fail_details.append(f"学生 {course_data.student_id} 已经选择了课程 {course_data.course_id}")
                            continue

                        # 创建选课记录
                        new_selection = CourseSelection(
                            student_id=existing_student.id,
                            course_id=course_data.course_id,
                            status=course_data.status,
                            semester_id=current_semester.semester_id,
                            score=0  # 默认分数为0
                        )

                        db.add(new_selection)
                        success_count += 1

                    else:
                        # 学生不存在，先创建学生
                        new_student = Student(
                            student_id=course_data.student_id,
                            student_name=course_data.student_name,
                            class_=course_data.class_,
                            student_password="default@password"  # 默认密码
                        )

                        db.add(new_student)
                        db.flush()  # 获取新学生的ID

                        # 创建选课记录
                        new_selection = CourseSelection(
                            student_id=new_student.id,
                            course_id=course_data.course_id,
                            status=course_data.status,
                            semester_id=current_semester.semester_id,
                            score=0  # 默认分数为0
                        )

                        db.add(new_selection)
                        success_count += 1

                except Exception as e:
                    fail_count += 1
                    fail_details.append(f"学生 {course_data.student_id}: {str(e)}")

            # 提交事务
            if success_count > 0:
                db.commit()

            if fail_count > 0:
                message = f"批量添加完成，成功 {success_count} 条，失败 {fail_count} 条。失败详情: {'; '.join(fail_details)}"
            else:
                message = f"批量添加成功，共添加 {success_count} 条学生选课信息"

            response = StudentCourseAddResponse(code=200, msg="添加成功")
            return True, message, response

        except Exception as e:
            db.rollback()
            print(f"批量添加学生选课信息失败: {e}")
            return False, f"批量添加失败: {str(e)}", None





    def calculate_scores(self, teacher_id: str, problem_ids: List[int],
                        db: Session) -> ScoreUpdateResponse:
        """教师核算分数"""
        try:
            # 验证教师是否存在
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return ScoreUpdateResponse(
                    code=400,
                    msg="教师不存在"
                )

            # 获取当前学期
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            if not current_semester:
                return ScoreUpdateResponse(
                    code=400,
                    msg="未找到当前学期"
                )

            # 获取本学期的所有课程
            courses = db.query(Course).filter(
                Course.semester_id == current_semester.semester_id
            ).all()

            if not courses:
                return ScoreUpdateResponse(
                    code=400,
                    msg="当前学期没有课程"
                )

            score_list = []

            # 遍历每门课程
            for course in courses:
                # 获取选课学生及其选课记录
                course_selections = db.query(
                    CourseSelection,
                    Student.student_id,
                    Student.student_name,
                    Student.class_
                ).join(
                    Student, CourseSelection.student_id == Student.id
                ).filter(
                    CourseSelection.course_id == course.course_id
                ).all()

                # 计算每个学生的分数
                for course_selection, student_id, student_name, student_class in course_selections:
                    # 查询学生在指定题目上的正确答题数（result_type == 0表示正确）
                    correct_count = db.query(func.count(distinct(AnswerRecord.problem_id))).filter(
                        AnswerRecord.student_id == course_selection.student_id,
                        AnswerRecord.problem_id.in_(problem_ids),
                        AnswerRecord.result_type == 0
                    ).scalar() or 0

                    # 每道题10分
                    total_score = correct_count * 10
                    # 分数上限是100分
                    total_score = min(total_score, 100)

                    # 更新选课记录中的分数
                    course_selection.score = total_score

                    score_list.append(StudentScoreInfo(
                        course_id=course.course_id,
                        student_id=student_id,
                        student_name=student_name or "未知",
                        class_=student_class or "",
                        total_score=total_score
                    ))

            # 提交数据库事务，保存分数更新
            db.commit()

            return ScoreUpdateResponse(
                code=200,
                msg="更新分数成功"
            )

        except Exception as e:
            print(f"核算分数失败: {e}")
            return ScoreUpdateResponse(
                code=500,
                msg=f"核算失败: {str(e)}"
            )

    def get_student_scores(self, teacher_id: str, db: Session) -> ScoreListResponse:
        """获取学生分数列表"""
        try:
            # 验证教师是否存在
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return ScoreListResponse(
                    code=400,
                    msg="教师不存在",
                    scorelist=[]
                )

            # 获取当前学期
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            if not current_semester:
                return ScoreListResponse(
                    code=400,
                    msg="未找到当前学期",
                    scorelist=[]
                )

            # 获取当前学期的所有课程
            courses = db.query(Course).filter(
                Course.semester_id == current_semester.semester_id
            ).all()

            if not courses:
                return ScoreListResponse(
                    code=200,
                    msg="",
                    scorelist=[]
                )

            score_list = []

            # 遍历每门课程，获取学生分数
            for course in courses:
                # 获取选课学生及其分数
                course_selections = db.query(
                    CourseSelection,
                    Student.student_id,
                    Student.student_name,
                    Student.class_
                ).join(
                    Student, CourseSelection.student_id == Student.id
                ).filter(
                    CourseSelection.course_id == course.course_id
                ).all()

                # 构建分数列表
                for course_selection, student_id, student_name, student_class in course_selections:
                    score_list.append(StudentScoreInfo(
                        course_id=course.course_id,
                        student_id=student_id,
                        student_name=student_name or "未知",
                        class_=student_class or "",
                        total_score=course_selection.score or 0
                    ))

            return ScoreListResponse(
                code=200,
                msg="",
                scorelist=score_list
            )

        except Exception as e:
            print(f"获取学生分数失败: {e}")
            return ScoreListResponse(
                code=500,
                msg=f"获取失败: {str(e)}",
                scorelist=[]
            )

    def export_scores(self, teacher_id: str, course_id: int, class_id: Optional[str] = None,
                     db: Session = None) -> Optional[Dict]:
        """导出分数结果"""
        try:
            # 验证教师权限
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return None

            course = db.query(Course).filter(
                Course.course_id == course_id,
                Course.teacher_id == teacher.id
            ).first()
            if not course:
                return None

            # 获取当前学期
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            semester_name = current_semester.semester_name if current_semester else "未知学期"

            # 构建查询条件
            query = db.query(
                Student.student_id,
                Student.student_name,
                Student.class_
            ).select_from(CourseSelection).join(
                Student, CourseSelection.student_id == Student.id
            ).filter(
                CourseSelection.course_id == course_id
            )

            # 如果指定了班级，添加班级过滤
            if class_id:
                query = query.filter(Student.class_ == class_id)

            students = query.all()

            # 构建导出数据
            export_data = {
                "course_info": {
                    "course_id": course_id,
                    "course_name": course.course_name or "未命名课程",
                    "semester_name": semester_name,
                    "class_filter": class_id or "全部班级",
                    "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_students": len(students)
                },
                "students": []
            }
            for student in students:
                # 根据学号和课程号查询选课表里的分数
                query = db.query(
                    CourseSelection.score
                ).select_from(CourseSelection).join(
                    Student, CourseSelection.student_id == Student.id
                ).filter(
                    CourseSelection.course_id == course_id,
                    CourseSelection.student_id == student.student_id

                )
                export_data["students"].append({
                    "学号": student.student_id,
                    "姓名": student.student_name,
                    "班级": student.class_,
                    "总分": CourseSelection.score  # 模拟分数
                })

            return export_data

        except Exception as e:
            print(f"导出分数失败: {e}")
            return None

    def get_students_by_semester(self, page: int = 1, limit: int = 20, search: Optional[str] = None,
                                class_filter: Optional[str] = None, semester_id: Optional[int] = None,
                                db: Session = None) -> TeacherStudentListResponse:
        """根据学期获取学生列表"""
        try:
            from sqlalchemy import or_

            # 构建基础查询
            query = db.query(
                Student.student_id,
                Student.student_name,
                Student.class_,
                Teacher.teacher_name,
                Semester.semester_name,
                Course.course_id
            ).select_from(CourseSelection).join(
                Student, CourseSelection.student_id == Student.id
            ).join(
                Course, CourseSelection.course_id == Course.course_id
            ).join(
                Teacher, Course.teacher_id == Teacher.id
            ).join(
                Semester, Course.semester_id == Semester.semester_id
            )

            # 如果指定了学期ID，则过滤
            if semester_id is not None:
                query = query.filter(Semester.semester_id == semester_id)

            # 搜索功能
            if search:
                query = query.filter(
                    or_(
                        Student.student_id.contains(search),
                        Student.student_name.contains(search)
                    )
                )

            # 班级过滤
            if class_filter:
                query = query.filter(Student.class_.contains(class_filter))

            # 获取总数
            total = query.count()

            # 分页查询
            offset = (page - 1) * limit
            results = query.offset(offset).limit(limit).all()

            # 构建响应数据
            student_list = []
            for result in results:
                student_list.append(TeacherStudentInfo(
                    student_id=result.student_id,
                    student_name=result.student_name or "",
                    class_=result.class_ or "",
                    teacher_name=result.teacher_name or "",
                    semester_name=result.semester_name or "",
                    course_id=str(result.course_id) if result.course_id else ""
                ))

            return TeacherStudentListResponse(
                students=student_list,
                total=total,
                page=page,
                limit=limit
            )

        except Exception as e:
            print(f"获取学生列表失败: {e}")
            return TeacherStudentListResponse(students=[], total=0, page=page, limit=limit)



    # 已删除: get_dashboard_matrix 方法 - 接口已废弃

    def execute_sql_query(self, teacher_id: str, query_data: SQLQueryRequest, db: Session) -> SQLQueryResponse:
        """执行SQL查询"""
        try:
            # 验证教师是否存在
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return SQLQueryResponse(
                    code=400,
                    msg="教师不存在",
                    columns=[],
                    rows=[]
                )

            # 验证数据库模式是否存在
            schema = db.query(DatabaseSchema).filter(DatabaseSchema.schema_id == query_data.schema_id).first()
            if not schema:
                return SQLQueryResponse(
                    code=400,
                    msg="数据库模式不存在",
                    columns=[],
                    rows=[]
                )

            # 使用database_engine_service执行SQL查询，默认使用PostgreSQL
            from services.database_engine_service import database_engine_service

            # 构建完整的SQL语句，包含数据库切换语句
            if schema.sql_schema:
                # 根据引擎类型选择切换语句（默认使用PostgreSQL）
                engine_type = "postgresql"
                if engine_type == "mysql":
                    switch_sql = f"USE {schema.sql_schema};"
                elif engine_type in ["postgresql", "opengauss"]:
                    switch_sql = f"SET search_path TO {schema.sql_schema};"
                else:
                    switch_sql = f"SET search_path TO {schema.sql_schema};"  # 默认使用PostgreSQL语法
                # 输出切换语句
                print(f"执行切换语句: {switch_sql}")
                # 执行切换语句
                switch_success, switch_message, _ = database_engine_service.execute_sql(
                    sql=switch_sql,
                    engine_type=engine_type
                )

                if not switch_success:
                    print(f"执行数据库切换失败: {switch_message}")
                    # 继续执行用户SQL，不因切换失败而中断

            # 执行用户的SQL查询
            success, message, result_data = database_engine_service.execute_sql(
                sql=query_data.sql,
                engine_type="postgresql"
            )

            if not success:
                return SQLQueryResponse(
                    code=400,
                    msg=f"SQL执行失败: {message}",
                    columns=[],
                    rows=[]
                )

            # 处理查询结果
            if result_data and len(result_data) > 0:
                # 获取列名
                columns = list(result_data[0].keys()) if result_data else []

                # 将字典列表转换为二维数组
                rows = []
                for row_dict in result_data:
                    row = [row_dict.get(col) for col in columns]
                    rows.append(row)

                return SQLQueryResponse(
                    code=200,
                    msg="查询成功",
                    columns=columns,
                    rows=rows
                )
            else:
                # 空结果集
                return SQLQueryResponse(
                    code=200,
                    msg="查询成功",
                    columns=[],
                    rows=[]
                )

        except Exception as e:
            print(f"执行SQL查询失败: {e}")
            return SQLQueryResponse(
                code=500,
                msg=f"查询执行失败: {str(e)}",
                columns=[],
                rows=[]
            )

    def get_student_profile_doc(self, student_id: str, schema_id: int, db: Session) -> Optional[StudentProfileDocResponse]:
        """获取学生答题概况"""
        try:
            # 1. 调用public接口获取当前学期号
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            if not current_semester:
                return None

            current_semester_id = current_semester.semester_id

            # 2. 根据学期号确认课程号范围
            courses = db.query(Course).filter(Course.semester_id == current_semester_id).all()
            if not courses:
                return None

            # 3. 根据学号在课程号范围里确认课程号(使用.first())
            # 获取学生信息
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return None

            # 查找学生在当前学期的选课记录
            course_selection = db.query(CourseSelection).join(
                Course, CourseSelection.course_id == Course.course_id
            ).filter(
                CourseSelection.student_id == student.id,
                Course.semester_id == current_semester_id
            ).first()

            if not course_selection:
                return None

            course_id = course_selection.course_id
            status = course_selection.status if hasattr(course_selection, 'status') else 1  # 默认为正常

            # 4. 根据数据库模式id得到题目id范围
            problems = db.query(Problem).filter(Problem.schema_id == schema_id).all()
            if not problems:
                # 如果没有题目，返回基本信息但答题统计为0
                return StudentProfileDocResponse(
                    student_id=student.student_id,
                    student_name=student.student_name or "",
                    class_name=student.class_ or "",
                    course_id=course_id,
                    status=status,
                    correct_count=0,
                    submit_count=0
                )

            problem_ids = [p.problem_id for p in problems]

            # 5. 到答题记录表里根据学号和题目的范围确认答题的正确数量和总提交数
            answer_records = db.query(AnswerRecord).filter(
                AnswerRecord.student_id == student.id,
                AnswerRecord.problem_id.in_(problem_ids)
            ).all()

            # 计算正确数量和总提交数
            submit_count = len(answer_records)
            correct_count = sum(1 for record in answer_records if record.result_type == 0)

            return StudentProfileDocResponse(
                student_id=student.student_id,
                student_name=student.student_name or "",
                class_name=student.class_ or "",
                course_id=course_id,
                status=status,
                correct_count=correct_count,
                submit_count=submit_count
            )

        except Exception as e:
            print(f"获取学生答题概况失败: {e}")
            return None





    # 已删除: get_problem_statistics 方法 - 功能已整合到其他方法

    def get_all_problems(self, db: Session) -> 'TeacherProblemListDocResponse':
        """获取所有题目列表"""
        try:
            from schemas.teacher import TeacherProblemListDocResponse, TeacherProblemItem

            # 查询所有题目
            problems = db.query(Problem).all()

            # 构建题目列表
            problem_list = []
            for problem in problems:
                problem_list.append(TeacherProblemItem(
                    problem_id=problem.problem_id,
                    is_required=problem.is_required or 0,
                    is_ordered=problem.is_ordered or 0,
                    problem_content=problem.problem_content or "",
                    example_sql=problem.example_sql or ""
                ))

            return TeacherProblemListDocResponse(
                code=200,
                msg="查询成功",
                data=problem_list
            )

        except Exception as e:
            print(f"获取所有题目列表失败: {e}")
            from schemas.teacher import TeacherProblemListDocResponse
            return TeacherProblemListDocResponse(
                code=500,
                msg=f"获取题目列表失败: {str(e)}",
                data=[]
            )

    def create_problem(self, teacher_id: str, problem_data: ProblemCreateRequest, db: Session) -> ProblemCreateResponse:
        """创建题目"""
        try:
            # 验证教师是否存在
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return ProblemCreateResponse(
                    code=400,
                    msg="教师不存在"
                )

            # 验证必要参数
            if problem_data.problem_content is None or problem_data.problem_content.strip() == "":
                return ProblemCreateResponse(
                    code=400,
                    msg="题目内容不能为空"
                )

            if problem_data.example_sql is None or problem_data.example_sql.strip() == "":
                return ProblemCreateResponse(
                    code=400,
                    msg="示例SQL不能为空"
                )

            # 如果指定了schema_id，验证数据库模式是否存在
            if problem_data.schema_id is not None:
                schema = db.query(DatabaseSchema).filter(DatabaseSchema.schema_id == problem_data.schema_id).first()
                if not schema:
                    return ProblemCreateResponse(
                        code=400,
                        msg="指定的数据库模式不存在"
                    )

            # 创建新题目
            new_problem = Problem(
                schema_id=problem_data.schema_id,
                problem_content=problem_data.problem_content.strip(),
                is_required=problem_data.is_required,
                is_ordered=problem_data.is_ordered,
                example_sql=problem_data.example_sql.strip()
            )

            db.add(new_problem)
            db.commit()
            db.refresh(new_problem)

            return ProblemCreateResponse(
                code=200,
                msg="题目创建成功"
            )

        except Exception as e:
            db.rollback()
            print(f"创建题目失败: {e}")
            return ProblemCreateResponse(
                code=500,
                msg=f"创建题目失败: {str(e)}"
            )

    def update_database_schema(self, teacher_id: str, schema_data: SchemaUpdateRequest,
                              db: Session) -> Tuple[bool, str, Optional[SchemaUpdateResponse]]:
        """更新数据库模式"""
        try:
            # 验证教师是否存在
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return False, "教师不存在", None

            # 检查数据库模式是否存在
            schema = db.query(DatabaseSchema).filter(DatabaseSchema.schema_id == schema_data.schema_id).first()
            if not schema:
                return False, "数据库模式不存在", None

            # 如果提供了SQL文件内容，则验证和执行SQL更新
            if schema_data.sql_file_content and schema_data.sql_file_content.strip():
                # 验证SQL语句（只允许建表语句）
                from utils.sql_validator import SQLValidator
                is_valid, validation_msg = SQLValidator.validate_create_table_sql(schema_data.sql_file_content)
                if not is_valid:
                    return False, validation_msg, None

                # 执行SQL更新
                success, error_msg = self._execute_schema_sql_update(schema_data)
                if not success:
                    return False, f"执行SQL失败: {error_msg}", None

                # 更新sql_table字段
                schema.sql_table = schema_data.sql_file_content

            # 更新数据库模式记录
            schema.schema_name = schema_data.schema_name
            schema.schema_discription = schema_data.schema_description
            schema.sql_schema = schema_data.sql_schema

            # 如果提供了作者信息，则更新
            if schema_data.schema_author:
                schema.schema_author = schema_data.schema_author

            db.commit()

            return True, "修改数据库模式成功", SchemaUpdateResponse(
                code=200,
                msg="修改数据库模式成功"
            )

        except Exception as e:
            db.rollback()
            print(f"更新数据库模式失败: {e}")
            return False, f"更新数据库模式失败: {str(e)}", None

    def _execute_schema_sql_update(self, schema_data: SchemaUpdateRequest) -> Tuple[bool, str]:
        """执行数据库模式SQL更新的私有方法"""
        try:
            from services.database_engine_service import database_engine_service

            # 需要更新的数据库引擎列表
            engines_to_update = ['mysql', 'postgresql', 'opengauss']
            failed_engines = []
            success_count = 0

            for sql_engine in engines_to_update:
                try:
                    # 检查引擎是否可用
                    if sql_engine not in database_engine_service.engines:
                        failed_engines.append(f"{sql_engine}(不可用)")
                        continue

                    engine = database_engine_service.engines[sql_engine]

                    # 执行SQL
                    with engine.connect() as connection:
                        from sqlalchemy import text

                        # 根据数据库类型切换模式
                        if sql_engine == "mysql":
                            # MySQL切换代码
                            connection.execute(text(f"DROP SCHEMA IF EXISTS {schema_data.sql_schema}"))
                            connection.execute(text(f"CREATE SCHEMA {schema_data.sql_schema}"))
                            connection.execute(text(f"USE {schema_data.sql_schema}"))
                        elif sql_engine in ["postgresql", "opengauss"]:
                            # PostgreSQL+OpenGauss切换代码
                            connection.execute(text(f"DROP SCHEMA IF EXISTS {schema_data.sql_schema} CASCADE"))
                            connection.execute(text(f"CREATE SCHEMA {schema_data.sql_schema}"))
                            connection.execute(text(f"SET search_path TO {schema_data.sql_schema}"))

                        # 执行SQL文件内容（更新时使用单一SQL内容）
                        connection.execute(text(schema_data.sql_file_content))
                        connection.commit()
                        success_count += 1

                except Exception as e:
                    failed_engines.append(f"{sql_engine}({str(e)})")
                    continue

            # 如果有引擎执行失败，记录但不阻止整个操作（至少有一个成功即可）
            if failed_engines:
                print(f"警告：以下数据库引擎更新失败: {', '.join(failed_engines)}")

            # 如果所有引擎都失败，返回错误
            if success_count == 0:
                return False, f"所有数据库引擎执行都失败: {', '.join(failed_engines)}"

            return True, "SQL执行成功"

        except Exception as e:
            return False, f"执行SQL时发生异常: {str(e)}"

    def create_database_schema(self, teacher_id: str, schema_data: SchemaCreateRequest,
                              db: Session) -> Tuple[bool, str, Optional[SchemaCreateResponse]]:
        """根据HTML格式文本、数据库模式名称、SQL引擎和SQL建表文件创建数据库模式"""
        try:
            # 验证教师是否存在
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return False, "教师不存在", None

            # 验证必要参数
            if not schema_data.schema_description or not schema_data.schema_description.strip():
                return False, "模式描述不能为空", None
            if not schema_data.schema_name or not schema_data.schema_name.strip():
                return False, "数据库模式名称不能为空", None
            if not schema_data.sql_file_content:
                return False, "SQL文件内容不能为空", None
            if not schema_data.sql_file_content.mysql_engine or not schema_data.sql_file_content.mysql_engine.strip():
                return False, "MySQL建表语句不能为空", None
            if not schema_data.sql_file_content.postgresql_opengauss_engine or not schema_data.sql_file_content.postgresql_opengauss_engine.strip():
                return False, "PostgreSQL/OpenGauss建表语句不能为空", None
            if not schema_data.sql_schema or not schema_data.sql_schema.strip():
                return False, "SQL模式名称不能为空", None
            if not schema_data.schema_author or not schema_data.schema_author.strip():
                return False, "模式作者不能为空", None

            # 1. 判断此模式是否已经存在
            existing_schema = db.query(DatabaseSchema).filter(
                DatabaseSchema.schema_name == schema_data.schema_name
            ).first()
            if existing_schema:
                return False, f"数据库模式 '{schema_data.schema_name}' 已存在", None

            # 2. 连接指定的SQL引擎并执行SQL文件
            from services.database_engine_service import database_engine_service

            # 执行MySQL建表语句
            mysql_schema_setup_sql = f"DROP SCHEMA IF EXISTS {schema_data.sql_schema};\nCREATE SCHEMA {schema_data.sql_schema};\nUSE {schema_data.sql_schema};"
            mysql_complete_sql = mysql_schema_setup_sql + "\n" + schema_data.sql_file_content.mysql_engine

            print(f"执行MySQL SQL语句: {mysql_complete_sql}")

            mysql_success, mysql_error_msg, _ = database_engine_service.execute_sql(
                sql=mysql_complete_sql,
                engine_type="mysql"
            )

            # 执行PostgreSQL建表语句
            postgresql_schema_setup_sql = f"DROP SCHEMA IF EXISTS {schema_data.sql_schema} CASCADE;\nCREATE SCHEMA {schema_data.sql_schema};\nSET search_path TO {schema_data.sql_schema};"
            postgresql_complete_sql = postgresql_schema_setup_sql + "\n" + schema_data.sql_file_content.postgresql_opengauss_engine

            print(f"执行PostgreSQL SQL语句: {postgresql_complete_sql}")

            postgresql_success, postgresql_error_msg, _ = database_engine_service.execute_sql(
                sql=postgresql_complete_sql,
                engine_type="postgresql"
            )

            # 执行OpenGauss建表语句（使用直接psycopg2连接）
            opengauss_schema_setup_sql = f"DROP SCHEMA IF EXISTS {schema_data.sql_schema} CASCADE;\nCREATE SCHEMA {schema_data.sql_schema};\nSET search_path TO {schema_data.sql_schema};"
            opengauss_complete_sql = opengauss_schema_setup_sql + "\n" + schema_data.sql_file_content.postgresql_opengauss_engine

            opengauss_success = False
            opengauss_error_msg = ""

            try:
                # 从环境变量获取 OpenGauss 连接配置
                host = os.getenv("OPENGAUSS_HOST", "localhost")
                port = os.getenv("OPENGAUSS_PORT", "15432")
                database = os.getenv("OPENGAUSS_DATABASE", "postgres")
                user = os.getenv("OPENGAUSS_USER", "gaussdb")
                password = os.getenv("OPENGAUSS_PASSWORD", "@Wyx778899")

                # 使用psycopg2直接连接OpenGauss
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                )

                with conn.cursor() as cur:
                    # 分割并执行多个SQL语句
                    sql_statements = [stmt.strip() for stmt in opengauss_complete_sql.split(';') if stmt.strip()]
                    for statement in sql_statements:
                        cur.execute(statement)

                    # 提交事务
                    conn.commit()
                    opengauss_success = True

            except psycopg2.Error as e:
                opengauss_error_msg = f"OpenGauss连接错误: {e}"
            except Exception as e:
                opengauss_error_msg = f"OpenGauss执行错误: {e}"
            finally:
                # 确保关闭连接
                if 'conn' in locals() and conn:
                    conn.close()

            # 检查执行结果
            success_count = 0
            error_messages = []

            if mysql_success:
                success_count += 1
                print("MySQL执行成功")
            else:
                error_messages.append(f"MySQL错误: {mysql_error_msg}")

            if postgresql_success:
                success_count += 1
                print("PostgreSQL执行成功")
            else:
                error_messages.append(f"PostgreSQL错误: {postgresql_error_msg}")

            if opengauss_success:
                success_count += 1
                print("OpenGauss执行成功")
            else:
                error_messages.append(f"OpenGauss错误: {opengauss_error_msg}")

            # 如果所有引擎都失败，返回错误
            if success_count == 0:
                return False, f"所有数据库引擎执行都失败: {'; '.join(error_messages)}", None
            elif success_count < 3:
                print(f"部分数据库引擎执行失败: {'; '.join(error_messages)}")
                # 继续执行，只要有一个成功就算成功

            # 4. 执行成功后将数据插入到database_schema表中
            new_schema = DatabaseSchema(
                schema_name=schema_data.schema_name,
                schema_discription=schema_data.schema_description,  # 使用模式描述
                sql_schema=schema_data.sql_schema,  # 保存SQL模式名称
                schema_author=schema_data.schema_author,  # 使用请求中的作者
                sql_table=schema_data.sql_file_content.postgresql_opengauss_engine  # 保存PostgreSQL建表语句
            )

            db.add(new_schema)
            db.commit()
            db.refresh(new_schema)

            response = SchemaCreateResponse(
                code=200,
                msg="创建数据库模式成功"
            )

            return True, "创建数据库模式成功", response

        except Exception as e:
            db.rollback()
            print(f"创建数据库模式失败: {e}")
            return False, f"创建失败: {str(e)}", None

    def get_student_answer_records(self, semester_ids: List[int], db: Session) -> List[Dict[str, Any]]:
        """根据学期ID列表获取学生答题记录"""
        try:
            from schemas.teacher import StudentAnswerRecord
            from models.course_selection import CourseSelection
            
            # 根据学期ID从选课表中获取学生范围，然后查询这些学生的答题记录
            records = db.query(
                Student.student_id,
                Problem.problem_content,
                AnswerRecord.result_type,
                AnswerRecord.answer_content,
                AnswerRecord.timestep
            ).join(
                AnswerRecord, Student.id == AnswerRecord.student_id
            ).join(
                Problem, AnswerRecord.problem_id == Problem.problem_id
            ).join(
                CourseSelection, Student.id == CourseSelection.student_id
            ).filter(
                CourseSelection.semester_id.in_(semester_ids)
            ).order_by(
                AnswerRecord.timestep.desc()
            ).all()

            # 转换为字典列表
            result = []
            for record in records:
                result.append({
                    "student_id": record.student_id,
                    "problem_content": record.problem_content or "",
                    "result_type": record.result_type,
                    "answer_content": record.answer_content or "",
                    "timestep": record.timestep.strftime("%Y-%m-%d %H:%M:%S") if record.timestep else ""
                })

            return result

        except Exception as e:
            print(f"获取学生答题记录失败: {e}")
            return []

# 全局教师服务实例
teacher_service = TeacherService()
