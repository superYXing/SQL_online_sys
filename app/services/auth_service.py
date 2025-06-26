from typing import Optional, Tuple
from sqlalchemy.orm import Session
from models import Student, Teacher
from models.base import get_db
from schemas.auth import LoginRequest, UserInfo
from services.jwt_service import jwt_service

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.jwt_service = jwt_service
    
    def authenticate_user(self, login_data: LoginRequest, db: Session) -> Optional[Tuple[UserInfo, str]]:
        """用户认证"""
        user = self._get_user_by_role_and_id(login_data.role, login_data.account, db)
        
        if not user:
            return None
        
        # 验证密码
        if not self._verify_password(user, login_data.password):
            return None
        
        # 创建用户信息
        user_info = self._create_user_info(user, login_data.role)
        
        # 创建JWT令牌
        token_data = {
            "sub": str(user_info.id),
            "username": user_info.username,
            "role": user_info.role
        }
        access_token = self.jwt_service.create_access_token(data=token_data)
        
        return user_info, access_token
    
    def _get_user_by_role_and_id(self, role: str, account: str, db: Session):
        """根据角色和用户名获取用户"""
        if role == "admin":
            # 管理员硬编码验证（可以后续改为数据库存储）
            if account == "admin":
                return {"id": "1", "admin_id": "admin", "password": "admin123"}  # 实际应用中应该加密
            return None
        elif role == "teacher":
            # 这里假设教师的用户名就是teacher_id的字符串形式
            try:
                teacher_id = int(account)
                return db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            except ValueError:
                return None
        elif role == "student":
            # 这里假设学生的用户名就是student_id的字符串形式
            try:
                student_id = int(account)
                return db.query(Student).filter(Student.student_id == student_id).first()
            except ValueError:
                return None
        
        return None
    
    def _verify_password(self, user, password: str) -> bool:
        """验证密码"""
        if isinstance(user, dict):  # 管理员
            return user.get("admin_password") == password  # 实际应用中应该使用加密验证
        elif hasattr(user, 'teacher_password'):  # 教师
            return user.teacher_password == password  # 实际应用中应该使用加密验证
        elif hasattr(user, 'student_password'):  # 学生
            return user.student_password == password  # 实际应用中应该使用加密验证
        
        return False
    
    def _create_user_info(self, user, role: str) -> UserInfo:
        """创建用户信息"""
        if isinstance(user, dict):  # 管理员
            return UserInfo(
                id=str(user.admin_id),
                username=user["account"],
            
                role=role
            )
        elif hasattr(user, 'teacher_id'):  # 教师
            return UserInfo(
                id=str(user.teacher_id),
                username=str(user.teacher_name),
               
                role=role
            )
        elif hasattr(user, 'student_id'):  # 学生
            return UserInfo(
                id=str(user.student_id),
                username=str(user.student_name),
               
                role=role
            )
        
        raise ValueError("未知的用户类型")

# 全局认证服务实例
auth_service = AuthService() 