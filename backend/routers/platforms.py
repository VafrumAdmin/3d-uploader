from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import PLATFORMS
from database import get_db
from models.platform_session import PlatformSession
from schemas.platform import PlatformInfo
from browser.manager import browser_manager

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


@router.get("", response_model=list[PlatformInfo])
async def list_platforms(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlatformSession))
    sessions = {s.platform: s for s in result.scalars().all()}

    platforms = []
    for key, cfg in PLATFORMS.items():
        session = sessions.get(key)
        platforms.append(PlatformInfo(
            key=key,
            name=cfg["name"],
            color=cfg["color"],
            login_url=cfg["login_url"],
            is_logged_in=session.is_logged_in if session else False,
            username=session.username if session else None,
            last_verified=session.last_verified if session else None,
        ))
    return platforms


@router.post("/{platform}/login")
async def login_platform(platform: str, db: AsyncSession = Depends(get_db)):
    if platform not in PLATFORMS:
        raise HTTPException(400, f"Unbekannte Plattform: {platform}")

    cfg = PLATFORMS[platform]
    try:
        username = await browser_manager.open_login_browser(platform, cfg["login_url"])
    except Exception as e:
        raise HTTPException(500, f"Login fehlgeschlagen: {str(e)}")

    result = await db.execute(select(PlatformSession).where(PlatformSession.platform == platform))
    session = result.scalar_one_or_none()
    if not session:
        session = PlatformSession(platform=platform)
        db.add(session)

    session.is_logged_in = True
    session.username = username or platform
    session.last_verified = datetime.now(timezone.utc)
    session.session_path = str(browser_manager.get_session_path(platform))
    await db.commit()

    return {"status": "ok", "username": session.username}


@router.post("/{platform}/check")
async def check_session(platform: str, db: AsyncSession = Depends(get_db)):
    if platform not in PLATFORMS:
        raise HTTPException(400, f"Unbekannte Plattform: {platform}")

    is_valid = await browser_manager.check_session(platform, PLATFORMS[platform]["login_url"])

    result = await db.execute(select(PlatformSession).where(PlatformSession.platform == platform))
    session = result.scalar_one_or_none()
    if session:
        session.is_logged_in = is_valid
        session.last_verified = datetime.now(timezone.utc)
        await db.commit()

    return {"is_logged_in": is_valid}


@router.post("/{platform}/logout")
async def logout_platform(platform: str, db: AsyncSession = Depends(get_db)):
    if platform not in PLATFORMS:
        raise HTTPException(400, f"Unbekannte Plattform: {platform}")

    await browser_manager.clear_session(platform)

    result = await db.execute(select(PlatformSession).where(PlatformSession.platform == platform))
    session = result.scalar_one_or_none()
    if session:
        session.is_logged_in = False
        session.username = None
        await db.commit()

    return {"status": "ok"}
