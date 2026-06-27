from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.todos import router as todos_router
from app.api.v1.daily_content import router as daily_content_router
from app.api.v1.projects import router as projects_router
from app.api.v1.student_notes import router as student_notes_router
from app.api.v1.activity_logs import router as activity_logs_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.dashboard import router as dashboard_router, analytics_router as analytics_router
from app.api.v1.reports import router as reports_router
from app.api.v1.referral_links import router as referral_links_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.students import router as students_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["User Management"])
api_router.include_router(roles_router, prefix="/roles", tags=["Roles & Permissions"])
api_router.include_router(permissions_router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(todos_router, prefix="/todos", tags=["Todos"])
api_router.include_router(daily_content_router, prefix="/daily-content", tags=["Daily Content"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(student_notes_router, prefix="/students/{student_id}/notes", tags=["Student Notes"])
api_router.include_router(activity_logs_router, prefix="/activity-logs", tags=["Activity Logs"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(referral_links_router, prefix="/referral-links", tags=["Referral Links"])
api_router.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
api_router.include_router(students_router, prefix="/students", tags=["Students"])
