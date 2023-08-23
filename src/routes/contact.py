from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactResponse, ContactSchema, ContactUpdateSchema
from src.repository import contact as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def get_all(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db),
                  user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(db)
    return contacts[offset:][:limit]


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, db, user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.get("/upcoming-birthdays/", response_model=List[ContactResponse])
async def get_upcoming_birthdays(db: Session = Depends(get_db)):
    return await repository_contacts.get_upcoming_birthdays(db)
