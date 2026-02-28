from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from passlib.hash import bcrypt

from app.models import models 
from app.schemas import schemas 
from app.db.database import *
from app.core.security import get_current_admin_user, get_current_user

router = APIRouter()

# POST API
@router.post("/", response_model=schemas.UserResponse)
async def create_user(request: schemas.UserCreate, db: AsyncSession= Depends(get_db)):
    # hash password before storing
    hashed_pwd = bcrypt.hash(request.password)
    new_user = models.User(username=request.username, email=request.email, password=hashed_pwd)
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    await db.refresh(new_user)
    return new_user


# GET API
@router.get("/all", response_model=list[schemas.UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db), 
                        admin_user: models.User = Depends(get_current_admin_user)):
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")
    return users


# PUT API
@router.put("/admin/{user_id}", response_model=schemas.UserResponse)
async def update_user(user_id: int,
                      request: schemas.UserCreate,
                      db: AsyncSession = Depends(get_db),
                      admin_user: models.User = Depends(get_current_admin_user)):
    
    result = await db.execute(select(models.User).filter(models.User.id ==user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed_pwd = bcrypt.hash(request.password)
    user.username = request.username
    user.email = request.email
    user.password = hashed_pwd
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already in use")
    await db.refresh(user)
    return user


@router.put("/", response_model=schemas.UserResponse)
async def update_current_user(request: schemas.UserCreate,
                              db: AsyncSession = Depends(get_db),
                              current_user: models.User = Depends(get_current_user)):
    
    hashed_pwd = bcrypt.hash(request.password)
    current_user.username = request.username
    current_user.email = request.email
    current_user.password = hashed_pwd
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already in use")
    await db.refresh(current_user)
    return current_user


# DELETE API
@router.delete("/")
async def delete_user(db: AsyncSession = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    await db.delete(current_user)
    await db.commit()
    return "User deleted successfully"


@router.delete("/admin/{user_id}")
async def delete_specific_user(user_id: int,
                               db: AsyncSession = Depends(get_db),
                               admin_user: models.User = Depends(get_current_admin_user)):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return "User deleted successfully"


@router.delete("/all")
async def delete_all_users(db: AsyncSession = Depends(get_db),
                           admin_user: models.User = Depends(get_current_admin_user)):
    result = await db.execute(select(models.User).filter(models.User.role != "admin"))
    users = result.scalars().all()
    if not users:
        raise HTTPException(status_code=404, detail="No users to delete")
    
    await db.execute(delete(models.User).filter(models.User.role != "admin"))
    await db.commit()
    return "Users deleted successfully"
