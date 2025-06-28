from .auth_service import AuthService
from .jwt_service import JWTService
from .auth_dependency import (
    get_current_user,
    get_current_admin,
    get_current_teacher,
    get_current_student,
    get_current_teacher_or_admin
)
from .student_service import student_service
from .admin_service import admin_service
from .user_management_service import user_management_service

__all__ = [
    "AuthService",
    "JWTService",
    "get_current_user",
    "get_current_admin",
    "get_current_teacher",
    "get_current_student",
    "get_current_teacher_or_admin",
    "student_service",
    "admin_service",
    "user_management_service"
]