from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard import DashboardStats
from app.auth.dependencies import require_admin
from app.models.user import User
from app.services.dashboard_service import get_dashboard_stats

router = APIRouter(prefix="/api/dashboard", tags=["Tableau de bord"])


@router.get("", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return get_dashboard_stats(db)
