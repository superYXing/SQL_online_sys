from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from models import Teacher, Student, CourseSelection, Course, Semester, AnswerRecord
from schemas.admin import (
    TeacherInfo, TeacherListResponse, StudentInfo
)
from schemas.teacher import StudentDetailInfo, StudentUpdateResponse

class UserManagementService:
    """用户管理服务类"""

    def _verify_admin_role(self, current_user: dict) -> None:
        """验证管理员角色"""
        if not current_user or current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限才能执行此操作"
            )
    
    # 学生管理方法
    def get_student_by_id(self, student_id: str, current_user: dict, db: Session) -> Optional[StudentDetailInfo]:
        """根据学生ID获取学生信息（包含课程ID）"""
        try:
            # 验证用户权限（教师或管理员可以访问）
            if not current_user or current_user.get("role") not in ["teacher", "admin"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="需要教师或管理员权限才能访问学生信息"
                )

            # 查询学生信息
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return None

            # 获取当前学期
            from services.public_service import public_service
            current_semester = public_service.get_current_semester(db)
            if not current_semester:
                # 如果没有当前学期，返回基本信息，course_id设为0
                return StudentDetailInfo(
                    id=student.id,
                    student_id=student.student_id,
                    student_name=student.student_name,
                    class_=student.class_,
                    course_id=0
                )

            # 查询学生在当前学期的选课记录
            course_selection = db.query(CourseSelection).join(
                Course, CourseSelection.course_id == Course.course_id
            ).filter(
                CourseSelection.student_id == student.id,
                Course.semester_id == current_semester.semester_id
            ).first()

            course_id = course_selection.course_id if course_selection else 0

            return StudentDetailInfo(
                id=student.id,
                student_id=student.student_id,
                student_name=student.student_name,
                class_=student.class_,
                course_id=course_id
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"获取学生信息失败: {e}")
            return None

    def update_student(self, student_id: str, student_name: Optional[str] = None,
                      class_: Optional[str] = None, student_password: Optional[str] = None,
                      current_user: dict = None, db: Session = None) -> Tuple[bool, str, Optional[StudentUpdateResponse]]:
        """更新学生信息"""
        try:
            # 验证用户权限（教师或管理员可以访问）
            if not current_user or current_user.get("role") not in ["teacher", "admin"]:
                return False, "需要教师或管理员权限才能更新学生信息", None

            # 查询学生是否存在
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return False, "学生不存在", None

            # 更新学生信息
            if student_name is not None:
                student.student_name = student_name
            if class_ is not None:
                student.class_ = class_
            if student_password is not None:
                student.student_password = student_password

            db.commit()
            db.refresh(student)

            response = StudentUpdateResponse(
                code=200,
                msg="更新成功"
            )

            return True, "学生信息更新成功", response

        except Exception as e:
            db.rollback()
            print(f"更新学生信息失败: {e}")
            return False, f"更新失败: {str(e)}", None

    def delete_student(self, student_id: str, current_user: dict, db: Session) -> Tuple[bool, str]:
        """删除学生"""
        try:
            # 验证用户权限（教师或管理员可以访问）
            if not current_user or current_user.get("role") not in ["teacher", "admin"]:
                return False, "需要教师或管理员权限才能删除学生"

            # 查询学生是否存在
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return False, "学生不存在"

            # 删除关联的答题记录
            answer_records = db.query(AnswerRecord).filter(AnswerRecord.student_id == student.id).all()
            answer_count = len(answer_records)
            if answer_count > 0:
                for answer_record in answer_records:
                    db.delete(answer_record)

            # 删除关联的选课记录
            course_selections = db.query(CourseSelection).filter(CourseSelection.student_id == student.id).all()
            course_selection_count = len(course_selections)
            if course_selection_count > 0:
                for course_selection in course_selections:
                    db.delete(course_selection)

            # 删除学生
            db.delete(student)
            db.commit()

            # 构建删除成功消息
            message_parts = ["学生删除成功"]
            if answer_count > 0:
                message_parts.append(f"同时删除了 {answer_count} 条答题记录")
            if course_selection_count > 0:
                message_parts.append(f"同时删除了 {course_selection_count} 条选课记录")

            return True, "，".join(message_parts)

        except Exception as e:
            db.rollback()
            print(f"删除学生失败: {e}")
            return False, f"删除失败: {str(e)}"

    # 教师管理方法
    def create_teacher(self, teacher_id: str, teacher_name: str, teacher_password: str,
                      current_user: dict, db: Session) -> Tuple[bool, str, Optional[TeacherInfo]]:
        """创建教师"""
         

        try:

            # 检查教师ID是否已存在
            existing_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if existing_teacher:
                return False, "教师ID已存在", None

            # 创建新教师
            new_teacher = Teacher(
                teacher_id=teacher_id,
                teacher_name=teacher_name,
                teacher_password=teacher_password
            )
            
            db.add(new_teacher)
            db.commit()
            db.refresh(new_teacher)
            
            teacher_info = TeacherInfo(
                id=new_teacher.id,
                teacher_id=new_teacher.teacher_id,
                teacher_name=new_teacher.teacher_name
            )
            
            return True, "教师创建成功", teacher_info
            
        except Exception as e:
            db.rollback()
            print(f"创建教师失败: {e}")
            return False, f"创建失败: {str(e)}", None

    def get_teachers(self, page: int = 1, limit: int = 20, search: Optional[str] = None,
                    current_user: dict = None, db: Session = None) -> TeacherListResponse:
        """获取教师列表"""
         

        try:
            query = db.query(Teacher)
            
            # 搜索功能
            if search:
                query = query.filter(
                    or_(
                        Teacher.teacher_id.contains(search),
                        Teacher.teacher_name.contains(search)
                    )
                )
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            offset = (page - 1) * limit
            teachers = query.offset(offset).limit(limit).all()
            
            # 构建响应数据
            teacher_list = []
            for teacher in teachers:
                teacher_list.append(TeacherInfo(
                    id=teacher.id,
                    teacher_id=teacher.teacher_id,
                    teacher_name=teacher.teacher_name
                ))
            
            return TeacherListResponse(
                teachers=teacher_list,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            print(f"获取教师列表失败: {e}")
            return TeacherListResponse(teachers=[], total=0, page=page, limit=limit)

    def get_teacher_by_id(self, teacher_id: str, current_user: dict, db: Session) -> Optional[TeacherInfo]:
        """根据ID获取教师信息"""
         

        try:
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return None
            
            return TeacherInfo(
                id=teacher.id,
                teacher_id=teacher.teacher_id,
                teacher_name=teacher.teacher_name
            )
            
        except Exception as e:
            print(f"获取教师信息失败: {e}")
            return None

    def update_teacher(self, teacher_id: str, teacher_name: Optional[str] = None,
                      teacher_password: Optional[str] = None, current_user: dict = None,
                      db: Session = None) -> Tuple[bool, str, Optional[TeacherInfo]]:
        """更新教师信息"""
         

        try:
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return False, "教师不存在", None
            
            # 更新字段
            if teacher_name is not None:
                teacher.teacher_name = teacher_name
            if teacher_password is not None:
                teacher.teacher_password = teacher_password
            
            db.commit()
            db.refresh(teacher)
            
            teacher_info = TeacherInfo(
                id=teacher.id,
                teacher_id=teacher.teacher_id,
                teacher_name=teacher.teacher_name
            )
            
            return True, "教师信息更新成功", teacher_info
            
        except Exception as e:
            db.rollback()
            print(f"更新教师信息失败: {e}")
            return False, f"更新失败: {str(e)}", None

    def delete_teacher(self, teacher_id: str, current_user: dict, db: Session) -> Tuple[bool, str]:
        """删除教师"""
         

        try:
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return False, "教师不存在"
            
            # 检查是否有关联的课程
            # 注意：这里需要根据实际的关系来检查
            # if hasattr(teacher, 'courses') and teacher.courses:
            #     return False, "该教师有关联的课程，无法删除"
            
            db.delete(teacher)
            db.commit()
            
            return True, "教师删除成功"
            
        except Exception as e:
            db.rollback()
            print(f"删除教师失败: {e}")
            return False, f"删除失败: {str(e)}"

# 全局用户管理服务实例
user_management_service = UserManagementService()
