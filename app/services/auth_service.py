from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证密码
        if not self._verify_password(user, login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="密码错误"
            )
        
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
    
    def update_password(self, user_id: str, role: str, old_password: str, new_password: str, db: Session) -> bool:
        """修改用户密码"""
        # 根据角色获取用户
        user = self._get_user_by_role_and_id(role, user_id, db)
        
        if not user:
            return False
        
        # 验证旧密码
        if not self._verify_password(user, old_password):
            return False
        
        # 更新密码
        return self._update_user_password(user, role, new_password, db)
    
    def _update_user_password(self, user, role: str, new_password: str, db: Session) -> bool:
        """更新用户密码"""
        try:
            if role == "admin":
                # 管理员密码更新（实际应用中应该存储到数据库）
                # 这里只是示例，实际应该有专门的管理员表
                return True  # 暂时返回True，实际需要更新数据库
            elif role == "teacher":
                # 更新教师密码
                user.teacher_password = new_password  # 实际应用中应该加密
                db.commit()
                return True
            elif role == "student":
                # 更新学生密码
                user.student_password = new_password  # 实际应用中应该加密
                db.commit()
                return True
            
            return False
        except Exception:
            db.rollback()
            return False
    
    def _get_user_by_role_and_id(self, role: str, account: str, db: Session):
        """根据角色和用户名获取用户"""
        if role == "admin":
            # 管理员硬编码验证（可以后续改为数据库存储）
            if account == "admin":
                return {"id": "1", "admin_id": "admin", "password": "admin123"}  # 实际应用中应该加密
            return None
        elif role == "teacher":
            # 教师的用户名就是teacher_id的字符串形式
            return db.query(Teacher).filter(Teacher.teacher_id == account).first()
        elif role == "student":
            # 学生的用户名就是student_id的字符串形式
            return db.query(Student).filter(Student.student_id == account).first()
        
        return None
    
    def _verify_password(self, user, password: str) -> bool:
        """验证密码"""
        if isinstance(user, dict):  # 管理员
            return user.get("password") == password  # 实际应用中应该使用加密验证
        elif hasattr(user, 'teacher_password'):  # 教师
            # 清理密码字符串，去除可能的空白字符
            stored_password = str(user.teacher_password).strip() if user.teacher_password else ""
            input_password = str(password).strip() if password else ""
            
            # 详细调试信息
            print(f"stored password: '{stored_password}' (length: {len(stored_password)})")
            print(f"input password: '{input_password}' (length: {len(input_password)})")
            print(f"stored password repr: {repr(stored_password)}")
            print(f"input password repr: {repr(input_password)}")
            
            result = stored_password == input_password
            return result
        elif hasattr(user, 'student_password'):  # 学生
            # 同样处理学生密码
            stored_password = str(user.student_password).strip() if user.student_password else ""
            input_password = str(password).strip() if password else ""
            return stored_password == input_password
        
        return False
    
    def _create_user_info(self, user, role: str) -> UserInfo:
        """创建用户信息"""
        if isinstance(user, dict):  # 管理员
            return UserInfo(
                id=str(user["admin_id"]),
                username="admin",
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