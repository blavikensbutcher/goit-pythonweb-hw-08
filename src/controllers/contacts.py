from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.database import get_db
from src.services.contacts import get_contacts_service
from sqlalchemy.ext.asyncio import AsyncSession

from src.types.contract import ContactDto, ContactDtoResponse, UpdateContactDto


router = APIRouter(prefix="/contacts", tags=["Contacts"])


contactsService = get_contacts_service()


@router.get("", response_model=List[ContactDtoResponse])
async def get_contacts(
    name: Optional[str] = Query(default=None, description="Filter by first name"),
    lastname: Optional[str] = Query(default=None, description="Filter by lastname"),
    email: Optional[str] = Query(default=None, description="Filter by email"),
    db: AsyncSession = Depends(get_db),
):
    contacts = await contactsService.get_contacts(
        db=db,
        name=name,
        lastname=lastname,
        email=email,
    )
    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found")
    else:
        return contacts
    

@router.get("/birthdays/upcoming", response_model=List[ContactDtoResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    return await contactsService.find_contacts_birthday_in_week(db)

    
@router.post("", response_model=ContactDtoResponse)
async def create_contact(contact_data: ContactDto, db: AsyncSession = Depends(get_db)):
    return await contactsService.create_contact(db, contact_data)

@router.get("/{contact_id}", response_model=ContactDtoResponse)
async def get_contact(contact_id: str, db: AsyncSession = Depends(get_db)):
    try:
        contact = await contactsService.get_contact_by_id(db, contact_id)
        return contact
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await contactsService.remove_contact_by_id(db, contact_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{contact_id}", response_model=ContactDto)
async def update_contact(
    contact_id: str,
    contact_data: UpdateContactDto,
    db: AsyncSession = Depends(get_db),

):
    updated_contact = await contactsService.update_contact(db, contact_id, contact_data)
    return updated_contact