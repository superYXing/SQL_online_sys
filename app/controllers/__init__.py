from .auth_controller import auth_router
from .student_controller import student_router
from .admin_controller import admin_router

__all__ = [
    "auth_router",
    "student_router",
    "admin_router"
]