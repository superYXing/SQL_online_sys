from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from models import Teacher, Course, Semester, Student, CourseSelection, AnswerRecord, Problem
from schemas.teacher import (
    TeacherProfileResponse, CourseInfo, TeacherCourseListResponse,
    StudentGradeInfo, CourseGradeResponse, StudentCreateRequest,
    StudentCreateResponse, ImportFailDetail, StudentImportResponse,
    ScoreCalculateRequest, StudentScoreInfo, ScoreUpdateResponse, ScoreListResponse
)
from datetime import datetime
import pandas as pd
import io

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

    def export_scores(self, teacher_id: str, course_id: str, class_id: Optional[str] = None,
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

# 全局教师服务实例
teacher_service = TeacherService()
