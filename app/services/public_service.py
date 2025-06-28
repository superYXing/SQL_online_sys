from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models import Semester, DateRange, DatabaseSchema
from schemas.public import (
    CurrentSemesterResponse, SemesterInfo, SemesterListResponse,
    SystemInfoResponse, DatabaseSchemaPublicInfo, DatabaseSchemaPublicListResponse
)
from datetime import datetime, date

class PublicService:
    """公共服务类"""
    
    def get_current_semester(self, db: Session) -> Optional[CurrentSemesterResponse]:
        """根据当前日期获取当前学期"""
        try:
            current_date = date.today()
            
            # 查询当前日期所在的学期
            current_semester = db.query(
                Semester.semester_id,
                Semester.semester_name
            ).select_from(Semester).join(
                DateRange, Semester.date_id == DateRange.date_id
            ).filter(
                and_(
                    DateRange.begin_date <= current_date,
                    DateRange.end_date >= current_date
                )
            ).first()
            
            if current_semester:
                return CurrentSemesterResponse(
                    semester_id=current_semester.semester_id,
                    semester_name=current_semester.semester_name
                )
            
            # 如果没有找到当前学期，返回最新的学期
            latest_semester = db.query(
                Semester.semester_id,
                Semester.semester_name
            ).order_by(Semester.semester_id.desc()).first()
            
            if latest_semester:
                return CurrentSemesterResponse(
                    semester_id=latest_semester.semester_id,
                    semester_name=latest_semester.semester_name
                )
            
            return None
            
        except Exception as e:
            print(f"获取当前学期失败: {e}")
            return None

    def get_all_semesters(self, db: Session) -> SemesterListResponse:
        """获取所有学期列表"""
        try:
            current_date = date.today()
            
            # 查询所有学期及其日期范围
            semesters_query = db.query(
                Semester.semester_id,
                Semester.semester_name,
                DateRange.begin_date,
                DateRange.end_date
            ).select_from(Semester).outerjoin(
                DateRange, Semester.date_id == DateRange.date_id
            ).order_by(Semester.semester_id.desc()).all()
            
            # 获取当前学期
            current_semester = self.get_current_semester(db)
            
            # 构建学期列表
            semester_list = []
            for semester in semesters_query:
                is_current = (current_semester and 
                            semester.semester_id == current_semester.semester_id)
                
                semester_list.append(SemesterInfo(
                    semester_id=semester.semester_id,
                    semester_name=semester.semester_name,
                    begin_date=semester.begin_date,
                    end_date=semester.end_date,
                    is_current=is_current
                ))
            
            return SemesterListResponse(
                semesters=semester_list,
                total=len(semester_list),
                current_semester=current_semester
            )
            
        except Exception as e:
            print(f"获取学期列表失败: {e}")
            return SemesterListResponse(
                semesters=[],
                total=0,
                current_semester=None
            )

    def get_system_info(self, db: Session) -> SystemInfoResponse:
        """获取系统信息"""
        try:
            current_semester = self.get_current_semester(db)
            
            return SystemInfoResponse(
                system_name="SQL在线平台",
                version="1.0.0",
                current_time=datetime.now(),
                current_semester=current_semester
            )
            
        except Exception as e:
            print(f"获取系统信息失败: {e}")
            return SystemInfoResponse(
                system_name="SQL在线平台",
                version="1.0.0",
                current_time=datetime.now(),
                current_semester=None
            )

    def get_public_database_schemas(self, db: Session) -> DatabaseSchemaPublicListResponse:
        """获取公共数据库模式列表（所有用户可见）"""
        try:
            schemas = db.query(DatabaseSchema).all()
            
            # 构建响应数据
            schema_list = []
            for schema in schemas:
                schema_list.append(DatabaseSchemaPublicInfo(
                    schema_id=schema.schema_id,
                    schema_name=schema.schema_name,
                    schema_description=schema.schema_discription  # 注意原字段名的拼写
                ))
            
            return DatabaseSchemaPublicListResponse(
                schemas=schema_list,
                total=len(schema_list)
            )
            
        except Exception as e:
            print(f"获取公共数据库模式列表失败: {e}")
            return DatabaseSchemaPublicListResponse(schemas=[], total=0)

    def check_semester_exists(self, semester_id: int, db: Session) -> bool:
        """检查学期是否存在"""
        try:
            semester = db.query(Semester).filter(
                Semester.semester_id == semester_id
            ).first()
            return semester is not None
            
        except Exception as e:
            print(f"检查学期存在性失败: {e}")
            return False

    def get_semester_date_range(self, semester_id: int, db: Session) -> Optional[dict]:
        """获取学期的日期范围"""
        try:
            semester_info = db.query(
                Semester.semester_id,
                Semester.semester_name,
                DateRange.begin_date,
                DateRange.end_date
            ).select_from(Semester).outerjoin(
                DateRange, Semester.date_id == DateRange.date_id
            ).filter(
                Semester.semester_id == semester_id
            ).first()
            
            if semester_info:
                return {
                    "semester_id": semester_info.semester_id,
                    "semester_name": semester_info.semester_name,
                    "begin_date": semester_info.begin_date,
                    "end_date": semester_info.end_date
                }
            
            return None
            
        except Exception as e:
            print(f"获取学期日期范围失败: {e}")
            return None

# 全局公共服务实例
public_service = PublicService()
