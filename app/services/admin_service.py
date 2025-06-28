from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Semester, DateRange
from schemas.admin import SemesterInfo, SemesterUpdateResponse, SemesterListResponse
from datetime import date

class AdminService:
    """管理员服务类"""
    
    def update_semester_time(self, semester_id: int, begin_date: date, end_date: date, db: Session) -> Tuple[bool, str, Optional[SemesterInfo]]:
        """修改学期时间"""
        try:
            # 验证日期有效性
            if begin_date >= end_date:
                return False, "开始日期必须早于结束日期", None
            
            # 查找学期
            semester = db.query(Semester).filter(Semester.semester_id == semester_id).first()
            if not semester:
                return False, "学期不存在", None
            
            # 查找对应的日期范围记录
            date_range = db.query(DateRange).filter(DateRange.date_id == semester.date_id).first()
            if not date_range:
                return False, "学期对应的日期范围不存在", None
            
            # 检查是否与其他学期时间冲突
            conflicting_semesters = db.query(Semester).join(DateRange).filter(
                and_(
                    Semester.semester_id != semester_id,  # 排除当前学期
                    # 检查时间重叠：新时间段与现有时间段有交集
                    and_(
                        DateRange.begin_date < end_date,
                        DateRange.end_date > begin_date
                    )
                )
            ).first()
            
            if conflicting_semesters:
                return False, "时间段与其他学期冲突", None
            
            # 更新日期范围
            date_range.begin_date = begin_date
            date_range.end_date = end_date
            
            db.commit()
            db.refresh(date_range)
            db.refresh(semester)
            
            # 构建响应数据
            semester_info = SemesterInfo(
                semester_id=semester.semester_id,
                semester_name=semester.semester_name,
                begin_date=date_range.begin_date,
                end_date=date_range.end_date,
                date_id=semester.date_id
            )
            
            return True, "学期时间更新成功", semester_info
            
        except Exception as e:
            db.rollback()
            print(f"更新学期时间失败: {e}")
            return False, f"更新失败: {str(e)}", None
    
    def get_semester_info(self, semester_id: int, db: Session) -> Optional[SemesterInfo]:
        """获取学期信息"""
        try:
            # 查询学期及其日期范围信息
            result = db.query(Semester, DateRange).join(
                DateRange, Semester.date_id == DateRange.date_id
            ).filter(Semester.semester_id == semester_id).first()
            
            if not result:
                return None
            
            semester, date_range = result
            
            return SemesterInfo(
                semester_id=semester.semester_id,
                semester_name=semester.semester_name,
                begin_date=date_range.begin_date,
                end_date=date_range.end_date,
                date_id=semester.date_id
            )
            
        except Exception as e:
            print(f"获取学期信息失败: {e}")
            return None

    # 学期管理方法
    def create_semester(self, semester_name: str, begin_date: date, end_date: date, db: Session) -> Tuple[bool, str, Optional[SemesterInfo]]:
        """创建学期"""
        try:
            # 验证日期有效性
            if begin_date >= end_date:
                return False, "开始日期必须早于结束日期", None

            # 检查是否与其他学期时间冲突
            conflicting_semesters = db.query(Semester).join(DateRange).filter(
                and_(
                    DateRange.begin_date < end_date,
                    DateRange.end_date > begin_date
                )
            ).first()

            if conflicting_semesters:
                return False, "时间段与其他学期冲突", None

            # 创建日期范围
            date_range = DateRange(
                begin_date=begin_date,
                end_date=end_date
            )
            db.add(date_range)
            db.flush()  # 获取date_range的ID

            # 创建学期
            semester = Semester(
                semester_name=semester_name,
                date_id=str(date_range.date_id)
            )
            db.add(semester)
            db.commit()
            db.refresh(semester)
            db.refresh(date_range)

            semester_info = SemesterInfo(
                semester_id=semester.semester_id,
                semester_name=semester.semester_name,
                begin_date=date_range.begin_date,
                end_date=date_range.end_date,
                date_id=semester.date_id
            )

            return True, "学期创建成功", semester_info

        except Exception as e:
            db.rollback()
            print(f"创建学期失败: {e}")
            return False, f"创建失败: {str(e)}", None

    def get_semesters(self, db: Session) -> SemesterListResponse:
        """获取学期列表"""
        try:
            # 查询所有学期及其日期范围信息
            results = db.query(Semester, DateRange).join(
                DateRange, Semester.date_id == DateRange.date_id
            ).all()

            semester_list = []
            for semester, date_range in results:
                semester_list.append(SemesterInfo(
                    semester_id=semester.semester_id,
                    semester_name=semester.semester_name,
                    begin_date=date_range.begin_date,
                    end_date=date_range.end_date,
                    date_id=semester.date_id
                ))

            return SemesterListResponse(
                semesters=semester_list,
                total=len(semester_list)
            )

        except Exception as e:
            print(f"获取学期列表失败: {e}")
            return SemesterListResponse(semesters=[], total=0)

    def delete_semester(self, semester_id: int, db: Session) -> Tuple[bool, str]:
        """删除学期"""
        try:
            semester = db.query(Semester).filter(Semester.semester_id == semester_id).first()
            if not semester:
                return False, "学期不存在"

            # 检查是否有关联的课程
            # 注意：这里需要根据实际的关系来检查
            # if hasattr(semester, 'courses') and semester.courses:
            #     return False, "该学期有关联的课程，无法删除"

            # 删除关联的日期范围
            date_range = db.query(DateRange).filter(DateRange.date_id == semester.date_id).first()
            if date_range:
                db.delete(date_range)

            db.delete(semester)
            db.commit()

            return True, "学期删除成功"

        except Exception as e:
            db.rollback()
            print(f"删除学期失败: {e}")
            return False, f"删除失败: {str(e)}"

# 全局管理员服务实例
admin_service = AdminService()
