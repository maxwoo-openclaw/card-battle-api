from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/stats")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_games = current_user.wins + current_user.losses + current_user.draws
    win_rate = (current_user.wins / total_games * 100) if total_games > 0 else 0.0

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "wins": current_user.wins,
        "losses": current_user.losses,
        "draws": current_user.draws,
        "total_games": total_games,
        "win_rate": round(win_rate, 1),
        "rating": current_user.rating,
    }
