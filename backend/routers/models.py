from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.model3d import Model3D
from schemas.model3d import ModelCreate, ModelUpdate, ModelOut

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=list[ModelOut])
async def list_models(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Model3D)
        .options(selectinload(Model3D.files), selectinload(Model3D.images), selectinload(Model3D.uploads))
        .order_by(Model3D.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ModelOut, status_code=201)
async def create_model(data: ModelCreate, db: AsyncSession = Depends(get_db)):
    model = Model3D(**data.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model, ["files", "images", "uploads"])
    return model


@router.get("/{model_id}", response_model=ModelOut)
async def get_model(model_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Model3D)
        .where(Model3D.id == model_id)
        .options(selectinload(Model3D.files), selectinload(Model3D.images), selectinload(Model3D.uploads))
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(404, "Modell nicht gefunden")
    return model


@router.put("/{model_id}", response_model=ModelOut)
async def update_model(model_id: str, data: ModelUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Model3D).where(Model3D.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(404, "Modell nicht gefunden")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(model, key, value)
    await db.commit()
    await db.refresh(model, ["files", "images", "uploads"])
    return model


@router.delete("/{model_id}", status_code=204)
async def delete_model(model_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Model3D).where(Model3D.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(404, "Modell nicht gefunden")
    await db.delete(model)
    await db.commit()
