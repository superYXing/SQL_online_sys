from typing import Optional, List, Dict, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct, and_
from models import (
    Teacher, Course, Semester, Student, CourseSelection, AnswerRecord, Problem,
    DatabaseSchema
)
from schemas.teacher import (
    TeacherProfileResponse, CourseInfo, TeacherCourseListResponse,
    StudentGradeInfo, CourseGradeResponse, StudentCreateRequest,
    StudentCreateResponse, ImportFailDetail, StudentImportResponse,
    ScoreCalculateRequest, StudentScoreInfo, ScoreUpdateResponse, ScoreListResponse,
    TeacherStudentInfo, TeacherStudentListResponse, ScoreExportRequest, ExportStudentInfo,
    DashboardMatrixResponse, SQLQueryResponse, StudentProfileDocResponse,
    ProblemStatisticsResponse, DatasetExportResponse
)
from datetime import datetime
import pandas as pd
import io
import json

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

    def get_teacher_courses(self, teacher_id: str, db: Session) -> TeacherCourseListResponse:
        """获取教师的课程列表"""
        try:
            # 获取教师对象
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return TeacherCourseListResponse(courses=[], total=0)
            
            # 查询教师的所有课程
            courses_query = db.query(
                Course.course_id,
                Course.course_name,
                Semester.semester_name,
                func.count(CourseSelection.student_id).label("student_count")
            ).select_from(Course).outerjoin(
                Semester, Semester.semester_id == Course.semester_id
            ).outerjoin(
                CourseSelection, CourseSelection.course_id == Course.course_id
            ).filter(
                Course.teacher_id == teacher.id
            ).group_by(
                Course.course_id, Course.course_name, Semester.semester_name
            ).all()
            
            # 构建课程列表
            course_list = []
            for course in courses_query:
                course_list.append(CourseInfo(
                    course_id=course.course_id,
                    course_name=course.course_name or "未命名课程",
                    semester_name=course.semester_name or "未知学期",
                    student_count=course.student_count or 0
                ))
            
            return TeacherCourseListResponse(
                courses=course_list,
                total=len(course_list)
            )
            
        except Exception as e:
            print(f"获取教师课程列表失败: {e}")
            return TeacherCourseListResponse(courses=[], total=0)

    def get_course_grades(self, teacher_id: str, course_id: str, db: Session) -> Optional[CourseGradeResponse]:
        """获取课程的学生成绩"""
        try:
            # 验证教师是否有权限查看该课程
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return None
            
            course = db.query(Course).filter(
                Course.course_id == course_id,
                Course.teacher_id == teacher.id
            ).first()
            if not course:
                return None
            
            # 获取选课学生及其成绩
            students_query = db.query(
                Student.student_id,
                Student.student_name,
                Student.class_,
                func.count(distinct(AnswerRecord.problem_id)).label("total_problems"),
                func.count(distinct(case((AnswerRecord.is_correct == 1, AnswerRecord.problem_id)))).label("correct_problems")
            ).select_from(CourseSelection).join(
                Student, CourseSelection.student_id == Student.id
            ).outerjoin(
                AnswerRecord, AnswerRecord.student_id == Student.id
            ).filter(
                CourseSelection.course_id == course.course_id
            ).group_by(
                Student.id, Student.student_id, Student.student_name, Student.class_
            ).all()
            
            # 构建学生成绩列表
            student_grades = []
            for student in students_query:
                total_problems = student.total_problems or 0
                correct_problems = student.correct_problems or 0
                score = (correct_problems / total_problems * 100) if total_problems > 0 else 0
                
                student_grades.append(StudentGradeInfo(
                    student_id=student.student_id,
                    student_name=student.student_name or "未知",
                    class_name=student.class_ or "未知班级",
                    total_problems=total_problems,
                    correct_problems=correct_problems,
                    score=round(score, 2)
                ))
            
            return CourseGradeResponse(
                course_id=course.course_id,
                course_name=course.course_name or "未命名课程",
                students=student_grades,
                total_students=len(student_grades)
            )
            
        except Exception as e:
            print(f"获取课程成绩失败: {e}")
            return None

    def export_course_grades(self, teacher_id: str, course_id: str, db: Session) -> Optional[Dict]:
        """导出课程成绩（返回可用于生成Excel的数据）"""
        try:
            course_grades = self.get_course_grades(teacher_id, course_id, db)
            if not course_grades:
                return None
            
            # 构建导出数据
            export_data = {
                "course_info": {
                    "course_id": course_grades.course_id,
                    "course_name": course_grades.course_name,
                    "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_students": course_grades.total_students
                },
                "students": []
            }
            
            for student in course_grades.students:
                export_data["students"].append({
                    "学号": student.student_id,
                    "姓名": student.student_name,
                    "班级": student.class_name,
                    "总题目数": student.total_problems,
                    "正确题目数": student.correct_problems,
                    "得分": student.score
                })
            
            return export_data
            
        except Exception as e:
            print(f"导出课程成绩失败: {e}")
            return None

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

    def import_students_from_excel(self, teacher_id: str, file_content: bytes,
                                  db: Session) -> StudentImportResponse:
        """从Excel文件批量导入学生"""
        try:
            # 验证教师是否存在
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return StudentImportResponse(
                    code=400,
                    msg="教师不存在",
                    success_count=0,
                    fail_count=0,
                    fail_details=[]
                )

            # 读取Excel文件
            try:
                df = pd.read_excel(io.BytesIO(file_content))
            except Exception as e:
                return StudentImportResponse(
                    code=400,
                    msg=f"Excel文件格式错误: {str(e)}",
                    success_count=0,
                    fail_count=0,
                    fail_details=[]
                )

            # 验证必需的列
            required_columns = ['学号', '姓名', '班级', '密码']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return StudentImportResponse(
                    code=400,
                    msg=f"Excel文件缺少必需的列: {', '.join(missing_columns)}",
                    success_count=0,
                    fail_count=0,
                    fail_details=[]
                )

            success_count = 0
            fail_count = 0
            fail_details = []

            # 逐行处理学生数据
            for index, row in df.iterrows():
                try:
                    student_id = str(row['学号']).strip()
                    student_name = str(row['姓名']).strip()
                    class_ = str(row['班级']).strip()
                    password = str(row['密码']).strip()

                    # 验证数据
                    if not student_id or not student_name or not class_ or not password:
                        fail_count += 1
                        fail_details.append(ImportFailDetail(
                            row=index + 2,  # Excel行号从2开始（包含表头）
                            reason="数据不完整，请检查学号、姓名、班级、密码是否都已填写"
                        ))
                        continue

                    # 检查学生ID是否已存在
                    existing_student = db.query(Student).filter(
                        Student.student_id == student_id
                    ).first()
                    if existing_student:
                        fail_count += 1
                        fail_details.append(ImportFailDetail(
                            row=index + 2,
                            reason=f"学生ID {student_id} 已存在"
                        ))
                        continue

                    # 创建学生
                    new_student = Student(
                        student_id=student_id,
                        student_name=student_name,
                        class_=class_,
                        student_password=password
                    )

                    db.add(new_student)
                    success_count += 1

                except Exception as e:
                    fail_count += 1
                    fail_details.append(ImportFailDetail(
                        row=index + 2,
                        reason=f"处理数据时出错: {str(e)}"
                    ))

            # 提交事务
            if success_count > 0:
                db.commit()

            return StudentImportResponse(
                code=200,
                msg=f"导入完成，成功 {success_count} 条，失败 {fail_count} 条",
                success_count=success_count,
                fail_count=fail_count,
                fail_details=fail_details
            )

        except Exception as e:
            db.rollback()
            print(f"批量导入学生失败: {e}")
            return StudentImportResponse(
                code=500,
                msg=f"导入失败: {str(e)}",
                success_count=0,
                fail_count=0,
                fail_details=[]
            )

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
                    # 查询学生在指定题目上的正确答题数
                    correct_count = db.query(func.count(distinct(AnswerRecord.problem_id))).filter(
                        AnswerRecord.student_id == course_selection.student_id,
                        AnswerRecord.problem_id.in_(problem_ids),
                        AnswerRecord.is_correct == 1
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

    def export_scores_to_excel(self, students_data: List[ExportStudentInfo]) -> bytes:
        """将学生分数数据导出为Excel文件"""
        try:
            import io
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill
            from datetime import datetime

            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "成绩表"

            # 设置表头
            headers = ["学号", "姓名", "班级", "课序号", "状态", "总分数"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # 填充数据
            for row, student in enumerate(students_data, 2):
                ws.cell(row=row, column=1, value=student.student_id)
                ws.cell(row=row, column=2, value=student.student_name)
                ws.cell(row=row, column=3, value=student.class_)
                ws.cell(row=row, column=4, value=student.course_id)
                ws.cell(row=row, column=5, value=student.status)
                ws.cell(row=row, column=6, value=student.total_score)

                # 设置数据行样式
                for col in range(1, 7):
                    cell = ws.cell(row=row, column=col)
                    cell.alignment = Alignment(horizontal="center", vertical="center")

            # 调整列宽
            column_widths = [15, 10, 15, 8, 8, 10]
            for col, width in enumerate(column_widths, 1):
                ws.column_dimensions[chr(64 + col)].width = width

            # 保存到内存
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)

            return excel_buffer.getvalue()

        except Exception as e:
            print(f"生成Excel文件失败: {e}")
            raise Exception(f"生成Excel文件失败: {str(e)}")

    def generate_export_filename(self, students_data: List[ExportStudentInfo]) -> str:
        """生成导出文件名"""
        try:
            from datetime import datetime

            if not students_data:
                return f"成绩表-{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            # 获取学期和班级信息（这里简化处理，实际可以从数据库查询）
            first_student = students_data[0]
            class_name = first_student.class_

            # 提取班级中的数字部分作为班级标识
            import re
            class_match = re.search(r'(\d+)', class_name)
            class_num = class_match.group(1) if class_match else "未知班级"

            # 生成文件名：学期-班级-成绩表.xlsx
            current_year = datetime.now().year
            semester = f"{current_year}年春季"  # 可以根据实际情况调整
            filename = f"{semester}-{class_num}班-成绩表.xlsx"

            return filename

        except Exception as e:
            print(f"生成文件名失败: {e}")
            return f"成绩表-{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    def get_dashboard_matrix(self, year_term: Optional[str], db: Session) -> DashboardMatrixResponse:
        """获取态势矩阵数据"""
        try:
            # 构建学期筛选条件
            semester_filter = []
            if year_term:
                semester_filter.append(Semester.semester_name.like(f"%{year_term}%"))

            # 获取符合条件的学期
            semesters_query = db.query(Semester)
            if semester_filter:
                semesters_query = semesters_query.filter(*semester_filter)
            semesters = semesters_query.all()

            # 获取所有数据库模式
            schemas = db.query(DatabaseSchema).all()

            matrix_data = []

            for semester in semesters:
                semester_schemas = {}

                for schema in schemas:
                    # 1. 根据学期号找到所有课程号
                    course_ids = db.query(Course.course_id).filter(
                        Course.semester_id == semester.semester_id
                    ).subquery()

                    # 2. 根据课程号找到所有学生号
                    student_ids = db.query(distinct(CourseSelection.student_id)).filter(
                        CourseSelection.course_id.in_(
                            db.query(course_ids.c.course_id)
                        )
                    ).subquery()

                    # 3. 统计该学期该模式下的数据
                    # 学生数量
                    student_count = db.query(func.count(distinct(CourseSelection.student_id))).filter(
                        CourseSelection.course_id.in_(
                            db.query(Course.course_id).filter(Course.semester_id == semester.semester_id)
                        )
                    ).scalar() or 0

                    # 题目数量（该模式下的所有题目）
                    problem_count = db.query(func.count(Problem.problem_id)).filter(
                        Problem.schema_id == schema.schema_id
                    ).scalar() or 0

                    # 提交数量（该学期该模式下的所有提交）
                    submit_count = db.query(func.count(AnswerRecord.answer_id)).filter(
                        and_(
                            AnswerRecord.student_id.in_(
                                db.query(CourseSelection.student_id).filter(
                                    CourseSelection.course_id.in_(
                                        db.query(Course.course_id).filter(Course.semester_id == semester.semester_id)
                                    )
                                )
                            ),
                            AnswerRecord.problem_id.in_(
                                db.query(Problem.problem_id).filter(Problem.schema_id == schema.schema_id)
                            )
                        )
                    ).scalar() or 0

                    # 只有当有数据时才添加到矩阵中
                    if student_count > 0 or problem_count > 0 or submit_count > 0:
                        semester_schemas[schema.schema_name or f"schema_{schema.schema_id}"] = {
                            "student_count": student_count,
                            "problem_count": problem_count,
                            "submit_count": submit_count
                        }

                # 只有当学期有数据时才添加到矩阵中
                if semester_schemas:
                    matrix_data.append({
                        "semester": semester.semester_name or f"semester_{semester.semester_id}",
                        "schemas": semester_schemas
                    })

            return DashboardMatrixResponse(
                code=200,
                msg="查询成功",
                matrix=matrix_data
            )

        except Exception as e:
            print(f"获取态势矩阵失败: {e}")
            return DashboardMatrixResponse(
                code=500,
                msg=f"获取态势矩阵失败: {str(e)}",
                matrix=[]
            )

    def execute_sql_query(self, sql: str, schema_id: int, db: Session) -> SQLQueryResponse:
        """执行SQL查询"""
        try:
            # 验证数据库模式是否存在
            schema = db.query(DatabaseSchema).filter(DatabaseSchema.schema_id == schema_id).first()
            if not schema:
                return SQLQueryResponse(
                    success=False,
                    data=[],
                    columns=[],
                    row_count=0,
                    error_message="数据库模式不存在"
                )

            # TODO: 实际的SQL执行逻辑
            # 这里应该根据schema_id连接到对应的数据库并执行SQL
            # 为了安全考虑，应该对SQL进行验证和过滤

            # 模拟查询结果
            mock_data = [
                {"id": 1, "name": "张三", "department": "技术部"},
                {"id": 2, "name": "李四", "department": "市场部"}
            ]
            mock_columns = ["id", "name", "department"]

            return SQLQueryResponse(
                success=True,
                data=mock_data,
                columns=mock_columns,
                row_count=len(mock_data),
                error_message=None
            )

        except Exception as e:
            print(f"执行SQL查询失败: {e}")
            return SQLQueryResponse(
                success=False,
                data=[],
                columns=[],
                row_count=0,
                error_message=f"查询执行失败: {str(e)}"
            )

    def get_student_profile_doc(self, student_id: str, db: Session) -> Optional[StudentProfileDocResponse]:
        """获取学生答题概况"""
        try:
            # 获取学生信息
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return None

            # 获取当前学期
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            if not current_semester:
                # 默认学期号是6，也就是2024-2025第二学期
                current_semester_id = 6
            else:
                current_semester_id = current_semester.semester_id

            # 根据学期号找到所有课程号
            courses = db.query(Course).filter(Course.semester_id == current_semester_id).all()
            if not courses:
                return None

            course_id = courses[0].course_id  # 取第一个课程作为示例

            # 根据课程号找到所有题目
            problems = db.query(Problem).join(
                Course, Course.semester_id == current_semester_id
            ).all()

            problem_ids = [p.problem_id for p in problems]

            # 到答题记录表里根据学号和课程的时间范围和题目的范围确认答题的正确数量和总提交数
            answer_records = db.query(AnswerRecord).filter(
                AnswerRecord.student_id == student.id,
                AnswerRecord.problem_id.in_(problem_ids)
            ).all()

            # 计算正确数量和总提交数
            submit_count = len(answer_records)
            correct_count = sum(1 for record in answer_records if record.is_correct)

            return StudentProfileDocResponse(
                student_id=student.student_id,
                student_name=student.student_name or "",
                class_name=student.class_ or "",
                course_id=course_id,
                correct_count=correct_count,
                submit_count=submit_count
            )

        except Exception as e:
            print(f"获取学生答题概况失败: {e}")
            return None

    def export_dataset(self, schema_name: str, format: str, db: Session) -> Tuple[Optional[Any], str, str]:
        """导出数据库模式相关数据"""
        try:
            # 获取数据库模式
            schema = db.query(DatabaseSchema).filter(DatabaseSchema.schema_name == schema_name).first()
            if not schema:
                return None, "数据库模式不存在", ""

            # 获取当前学期
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            if not current_semester:
                return None, "未找到当前学期", ""

            # 根据数据库模式获取题目范围
            problems = db.query(Problem).filter(Problem.schema_id == schema.schema_id).all()
            if not problems:
                return None, "该数据库模式下没有题目", ""

            problem_ids = [p.problem_id for p in problems]

            # 获取当前学期的所有学生
            students = db.query(Student).join(
                CourseSelection, Student.id == CourseSelection.student_id
            ).join(
                Course, CourseSelection.course_id == Course.course_id
            ).filter(
                Course.semester_id == current_semester.semester_id
            ).distinct().all()

            # 构建导出数据
            export_data = []
            for student in students:
                # 查询该学生在指定题目范围内的所有提交记录
                answer_records = db.query(AnswerRecord).filter(
                    AnswerRecord.student_id == student.id,
                    AnswerRecord.problem_id.in_(problem_ids)
                ).all()

                if answer_records:  # 只导出有提交记录的学生
                    # 计算统计数据
                    submit_count = len(answer_records)
                    correct_count = sum(1 for record in answer_records if record.is_correct)

                    # 计算完成题目总数（去重）
                    completed_problem_ids = set(record.problem_id for record in answer_records)
                    problem_count = len(completed_problem_ids)

                    # 计算不同解法数量（根据不同的SQL语句）
                    unique_sqls = set(record.student_answer for record in answer_records if record.student_answer)
                    method_count = len(unique_sqls)

                    export_data.append({
                        "student_id": student.student_id,
                        "student_name": student.student_name or "",
                        "class": student.class_ or "",
                        "problem_count": problem_count,
                        "submit_count": submit_count,
                        "correct_count": correct_count,
                        "method_count": method_count
                    })

            if not export_data:
                return None, "没有找到相关数据", ""

            # 根据格式生成文件
            if format.upper() == "XLSX":
                file_data, filename, media_type = self._generate_excel_export(export_data, schema_name)
                return file_data, "", media_type
            elif format.upper() == "JSON":
                file_data, filename, media_type = self._generate_json_export(export_data, schema_name)
                return file_data, "", media_type
            elif format.upper() == "XML":
                file_data, filename, media_type = self._generate_xml_export(export_data, schema_name)
                return file_data, "", media_type
            else:
                return None, "不支持的导出格式", ""

        except Exception as e:
            print(f"导出数据失败: {e}")
            return None, f"导出数据失败: {str(e)}", ""

    def _generate_excel_export(self, data: List[Dict], schema_name: str) -> Tuple[io.BytesIO, str, str]:
        """生成Excel格式导出"""
        try:
            df = pd.DataFrame(data)

            # 重命名列
            df.columns = ["学号", "姓名", "班级", "题目数", "提交数", "正确数", "解法数"]

            # 创建Excel文件
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=schema_name, index=False)

            output.seek(0)
            filename = f"{schema_name}_数据导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            return output, filename, media_type

        except Exception as e:
            print(f"生成Excel导出失败: {e}")
            raise

    def _generate_json_export(self, data: List[Dict], schema_name: str) -> Tuple[io.BytesIO, str, str]:
        """生成JSON格式导出"""
        try:
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            output = io.BytesIO(json_str.encode('utf-8'))
            filename = f"{schema_name}_数据导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            media_type = "application/json"

            return output, filename, media_type

        except Exception as e:
            print(f"生成JSON导出失败: {e}")
            raise

    def _generate_xml_export(self, data: List[Dict], schema_name: str) -> Tuple[io.BytesIO, str, str]:
        """生成XML格式导出"""
        try:
            # 简单的XML生成
            xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
            xml_lines.append(f'<{schema_name}_export>')

            for item in data:
                xml_lines.append('  <student>')
                for key, value in item.items():
                    xml_lines.append(f'    <{key}>{value}</{key}>')
                xml_lines.append('  </student>')

            xml_lines.append(f'</{schema_name}_export>')

            xml_str = '\n'.join(xml_lines)
            output = io.BytesIO(xml_str.encode('utf-8'))
            filename = f"{schema_name}_数据导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
            media_type = "application/xml"

            return output, filename, media_type

        except Exception as e:
            print(f"生成XML导出失败: {e}")
            raise

    def get_problem_statistics(self, schema_id: int, db: Session) -> Optional[ProblemStatisticsResponse]:
        """获取题目完成情况统计"""
        try:
            # 验证数据库模式是否存在
            schema = db.query(DatabaseSchema).filter(DatabaseSchema.schema_id == schema_id).first()
            if not schema:
                return None

            # 获取当前学期
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            if not current_semester:
                return None

            # 获取该模式下的所有题目
            problems = db.query(Problem).filter(Problem.schema_id == schema_id).all()
            if not problems:
                return ProblemStatisticsResponse(
                    schema_name=schema.schema_name or "",
                    total_problems=0,
                    problem_stats=[]
                )

            problem_ids = [p.problem_id for p in problems]

            # 获取当前学期的所有学生
            students = db.query(Student).join(
                CourseSelection, Student.id == CourseSelection.student_id
            ).join(
                Course, CourseSelection.course_id == Course.course_id
            ).filter(
                Course.semester_id == current_semester.semester_id
            ).distinct().all()

            total_students = len(students)
            student_ids = [s.id for s in students]

            # 统计每个题目的完成情况
            problem_stats = []
            for problem in problems:
                # 查询该题目的所有提交记录
                answer_records = db.query(AnswerRecord).filter(
                    AnswerRecord.problem_id == problem.problem_id,
                    AnswerRecord.student_id.in_(student_ids)
                ).all()

                # 统计提交学生数（去重）
                submitted_students = set(record.student_id for record in answer_records)
                submit_count = len(submitted_students)

                # 统计正确提交的学生数
                correct_students = set(
                    record.student_id for record in answer_records
                    if record.is_correct
                )
                correct_count = len(correct_students)

                # 计算完成率
                completion_rate = (submit_count / total_students * 100) if total_students > 0 else 0
                accuracy_rate = (correct_count / submit_count * 100) if submit_count > 0 else 0

                problem_stats.append({
                    "problem_id": problem.problem_id,
                    "problem_content": problem.problem_content or "",
                    "submit_count": submit_count,
                    "correct_count": correct_count,
                    "completion_rate": round(completion_rate, 2),
                    "accuracy_rate": round(accuracy_rate, 2)
                })

            return ProblemStatisticsResponse(
                schema_name=schema.schema_name or "",
                total_problems=len(problems),
                problem_stats=problem_stats
            )

        except Exception as e:
            print(f"获取题目统计失败: {e}")
            return None

# 全局教师服务实例
teacher_service = TeacherService()
