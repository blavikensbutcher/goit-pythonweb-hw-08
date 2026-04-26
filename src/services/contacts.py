from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.contacts import ContactModel
from src.types.contract import ContactDto, UpdateContactDto


class ContactsService:
    @staticmethod
    async def get_contacts(db: AsyncSession, name: str | None = None, lastname: str | None = None, email: str | None = None):
        query = select(ContactModel)
        if name:
            query = query.where(ContactModel.first_name == name)
        if lastname:
            query = query.where(ContactModel.last_name == lastname)
        if email:
            query = query.where(ContactModel.email == email)
        result = await db.execute(query)
        contacts = result.scalars().all()
        return contacts
    
    @staticmethod
    async def find_contacts_birthday_in_week(db: AsyncSession):
            today = date.today()
            next_week = today + timedelta(days=7)

            today_md = today.strftime("%m-%d")
            next_week_md = next_week.strftime("%m-%d")
            birthday_month_day = func.to_char(ContactModel.birthday, "MM-DD")

            if today_md <= next_week_md:
                query = select(ContactModel).where(
                    birthday_month_day.between(today_md, next_week_md)
                )
            else:
                query = select(ContactModel).where(
                    or_(
                        birthday_month_day >= today_md,
                        birthday_month_day <= next_week_md,
                    )
                )

            result = await db.execute(query)
            return result.scalars().all()
        
    @staticmethod
    async def create_contact(db: AsyncSession, contact_data: ContactDto):
        existsing_contact = await db.execute(
            select(ContactModel).where(ContactModel.email == contact_data.email)
        )
        if existsing_contact.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Contact with this email already exists")
        
        new_contact = ContactModel(**contact_data.model_dump(exclude_none=True))
        db.add(new_contact)
        await db.commit()
        await db.refresh(new_contact)
        return new_contact
    
    @staticmethod
    async def get_contact_by_id(db: AsyncSession, contact_id: str):
        result = await db.execute(select(ContactModel).where(ContactModel.id == contact_id))
        contact = result.scalar_one_or_none()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return contact
    
    @staticmethod
    async def remove_contact_by_id( db: AsyncSession, contact_id: str):
        result = await db.execute(select(ContactModel).where(ContactModel.id == contact_id))
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        if contact:
            await db.delete(contact)
            await db.commit()
            return True
        return False
    
    @staticmethod
    async def update_contact(db: AsyncSession, contact_id: str, contact_data: UpdateContactDto):
        result = await db.execute(select(ContactModel).where(ContactModel.id == contact_id))
        contact = result.scalar_one_or_none()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        for key, value in contact_data.model_dump(exclude_none=True).items():
            setattr(contact, key, value)
        
        await db.commit()
        await db.refresh(contact)
        return contact

def get_contacts_service() -> ContactsService:
    """Dependency for ContactsService"""
    return ContactsService()