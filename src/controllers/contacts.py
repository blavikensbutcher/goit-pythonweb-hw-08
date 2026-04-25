

from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.database import get_db
from src.services.contacts import get_contacts_service
from sqlalchemy.ext.asyncio import AsyncSession

from src.types.contract import ContactDto, ContactDtoResponse, UpdateContactDto


router = APIRouter(prefix="/contacts", tags=["Contacts"])


contactsService = get_contacts_service()



@router.get("",  response_model=List[ContactDtoResponse])
async def get_contacts(db: AsyncSession = Depends(get_db),) :
    return await contactsService.get_contacts(db)
    
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
    existing_contact = await contactsService.get_contact_by_id(db, contact_id)
    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact_data.model_dump(exclude_none=True).items():
        setattr(existing_contact, key, value)

    await db.commit()

    await db.refresh(existing_contact)

    return existing_contact