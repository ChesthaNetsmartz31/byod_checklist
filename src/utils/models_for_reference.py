from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Boolean, ForeignKey, SmallInteger, Text, func, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# from sqlalchemy import (
#     Column, Integer, String, Boolean, DateTime, Date, Time, 
#     Text, SmallInteger, ForeignKey, JSON, UUID
# )
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from pydantic import BaseModel, EmailStr
# from typing import Optional, List
# from datetime import datetime, date, time
# import uuid

# Base = declarative_base()

# # SQLAlchemy Models
# class Organization(Base):
#     __tablename__ = "organization"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     identifier = Column(String(255), nullable=False)
#     uuid = Column(String(255), nullable=False)
#     administrator_first_name = Column(String(255), nullable=False)
#     administrator_last_name = Column(String(255), nullable=False)
#     administrator_email = Column(String(255), nullable=False)
#     suspended = Column(Boolean, default=False, nullable=False)
#     partner = Column(Boolean, default=False, nullable=False)
#     created_at = Column(DateTime, nullable=False)
#     updated_at = Column(DateTime, nullable=True)
    
#     # Relationships
#     products = relationship("OrganizationProduct", back_populates="organization")


# class Product(Base):
#     __tablename__ = "product"
    
#     id = Column(Integer, primary_key=True, index=True)
#     label = Column(String(255), nullable=False)
#     deleted = Column(Boolean, default=False, nullable=False)
    
#     # Relationships
#     organizations = relationship("OrganizationProduct", back_populates="product")


# class OrganizationProduct(Base):
#     __tablename__ = "organization_product"
    
#     organization_id = Column(Integer, ForeignKey("organization.id", ondelete="CASCADE"), primary_key=True)
#     product_id = Column(Integer, ForeignKey("product.id", ondelete="CASCADE"), primary_key=True)
    
#     # Relationships
#     organization = relationship("Organization", back_populates="products")
#     product = relationship("Product", back_populates="organizations")


# class Module(Base):
#     __tablename__ = "module"
    
#     id = Column(Integer, primary_key=True, index=True)
#     label = Column(String(255), nullable=False)
#     deleted = Column(Boolean, default=False, nullable=False)


# class Permission(Base):
#     __tablename__ = "permission"
    
#     id = Column(Integer, primary_key=True, index=True)
#     label = Column(String(255), nullable=False)
#     type = Column(String(255), nullable=False)
#     deleted = Column(Boolean, default=False, nullable=False)


class UserType(Base):
    __tablename__ = "user_type"
    
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False)
    active = Column(Boolean, default=False, nullable=False)


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(Integer, ForeignKey("user_type.id"), nullable=True)
    first_name = Column(String(255), nullable=False)
    middle_name = Column(String(255), nullable=False, default="")
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    salt = Column(String(1020), nullable=False)
    temp_password = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    roles = Column(JSON, nullable=False)
    suspended = Column(Boolean, default=False, nullable=False)
    synced = Column(Boolean, default=False, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    ghost = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    user_type_rel = relationship("UserType")
    security_roles = relationship("SecurityRole", foreign_keys="SecurityRole.user_id", back_populates="user")
    created_security_roles = relationship("SecurityRole", foreign_keys="SecurityRole.created_by_id")
    updated_security_roles = relationship("SecurityRole", foreign_keys="SecurityRole.updated_by_id")


class Workplace(Base):
    __tablename__ = "workplace"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    street_address = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    postcode = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    archived = Column(Boolean, default=False, nullable=False)


# class SecurityRole(Base):
#     __tablename__ = "security_role"
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
#     workplace_id = Column(Integer, ForeignKey("workplace.id"), nullable=False)
#     module_id = Column(Integer, ForeignKey("module.id"), nullable=False)
#     permission_id = Column(Integer, ForeignKey("permission.id"), nullable=False)
#     created_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
#     updated_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)
#     identifier = Column(String(255), nullable=False)
#     view = Column(Boolean, default=False, nullable=False)
#     edit = Column(Boolean, default=False, nullable=False)
#     delete = Column(Boolean, default=False, nullable=False)
#     execute = Column(Boolean, default=False, nullable=False)
#     deleted = Column(Boolean, default=False, nullable=False)
#     created_at = Column(DateTime, nullable=False)
#     updated_at = Column(DateTime, nullable=True)
    
#     # Relationships
#     user = relationship("User", foreign_keys=[user_id], back_populates="security_roles")
#     workplace = relationship("Workplace")
#     module = relationship("Module")
#     permission = relationship("Permission")


# class JobCode(Base):
#     __tablename__ = "job_codes"
    
#     id = Column(Integer, primary_key=True, index=True)
#     label = Column(String(255), nullable=False, unique=True)
#     archived = Column(Boolean, default=False, nullable=False)
#     background_color = Column(String(255), nullable=False)
#     text_color = Column(String(255), nullable=False)


# class Priority(Base):
#     __tablename__ = "priority"
    
#     id = Column(Integer, primary_key=True, index=True)
#     label = Column(String(255), nullable=False)
#     deleted = Column(Boolean, default=False, nullable=False)


# class Status(Base):
#     __tablename__ = "status"
    
#     id = Column(Integer, primary_key=True, index=True)
#     label = Column(String(255), nullable=False)
#     deleted = Column(Boolean, default=False, nullable=False)


# class Day(Base):
#     __tablename__ = "day"
    
#     id = Column(Integer, primary_key=True, index=True)
#     label = Column(String(255), nullable=False)
#     locale = Column(String(255), nullable=False)
#     position = Column(String(255), nullable=False)
#     deleted = Column(Boolean, default=False, nullable=False)


# class ChecklistCategory(Base):
#     __tablename__ = "checklist_category"
    
#     id = Column(Integer, primary_key=True, index=True)
#     label = Column(String(255), nullable=False)
#     active = Column(Boolean, nullable=False)
#     deleted = Column(Boolean, nullable=False)


# class ChecklistFrequency(Base):
#     __tablename__ = "checklist_frequency"
    
#     id = Column(Integer, primary_key=True, index=True)
#     label = Column(String(255), nullable=False)
#     active = Column(Boolean, nullable=False)
#     deleted = Column(Boolean, nullable=False)


# class ChecklistTemplate(Base):
#     __tablename__ = "checklist_template"
    
#     id = Column(Integer, primary_key=True, index=True)
#     author = Column(Integer, ForeignKey("user.id"), nullable=True)
#     category = Column(Integer, ForeignKey("checklist_category.id"), nullable=True)
#     frequency = Column(Integer, ForeignKey("checklist_frequency.id"), nullable=True)
#     workplace = Column(Integer, ForeignKey("workplace.id"), nullable=False)
#     label = Column(String(255), nullable=False)
#     template_uid = Column(UUID, nullable=False)
#     version = Column(Integer, default=1, nullable=False)
#     template_owner = Column(String(55), nullable=True)
#     signoff_required = Column(Boolean, default=False)
#     active = Column(Boolean, nullable=False)
#     deleted = Column(Boolean, nullable=False)
#     created_at = Column(DateTime, nullable=True)
#     updated_at = Column(DateTime, nullable=True)
    
#     # Relationships
#     author_rel = relationship("User")
#     category_rel = relationship("ChecklistCategory")
#     frequency_rel = relationship("ChecklistFrequency")
#     workplace_rel = relationship("Workplace")
#     tasks = relationship("ChecklistTask", back_populates="parent_template")


# class ChecklistTask(Base):
#     __tablename__ = "checklist_task"
    
#     id = Column(Integer, primary_key=True, index=True)
#     parent = Column(Integer, ForeignKey("checklist_template.id"), nullable=False)
#     section = Column(String(510), nullable=True)
#     duty = Column(String(510), nullable=False)
#     instructions = Column(String(1020), nullable=False)
#     answer_type = Column(String(20), nullable=False)
#     expected_answer = Column(String(20), nullable=False)
#     list_order = Column(Integer, default=0, nullable=False)
#     active = Column(Boolean, nullable=False)
#     deleted = Column(Boolean, nullable=False)
#     created_at = Column(DateTime, nullable=True)
#     updated_at = Column(DateTime, nullable=True)
    
#     # Relationships
#     parent_template = relationship("ChecklistTemplate", back_populates="tasks")


# class ChecklistGroup(Base):
#     __tablename__ = "checklist_group"
    
#     id = Column(Integer, primary_key=True, index=True)
#     workplace = Column(Integer, ForeignKey("workplace.id"), nullable=False)
#     author = Column(Integer, ForeignKey("user.id"), nullable=False)
#     job_code = Column(Integer, ForeignKey("job_codes.id"), nullable=True)
#     label = Column(String(255), nullable=False)
#     active = Column(Boolean, default=True, nullable=False)
#     deleted = Column(Boolean, default=False, nullable=False)
#     created_at = Column(DateTime, nullable=False)
#     updated_at = Column(DateTime, nullable=False)
    
#     # Relationships
#     workplace_rel = relationship("Workplace")
#     author_rel = relationship("User")
#     job_code_rel = relationship("JobCode")


# class ChecklistSchedule(Base):
#     __tablename__ = "checklist_schedule"
    
#     id = Column(Integer, primary_key=True, index=True)
#     workplace = Column(Integer, ForeignKey("workplace.id"), nullable=False)
#     checklist_template = Column(Integer, ForeignKey("checklist_template.id"), nullable=False)
#     created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
#     assignment_type = Column(String(20), nullable=False)
#     assignee = Column(Integer, ForeignKey("user.id"), nullable=True)
#     checklist_group = Column(Integer, ForeignKey("checklist_group.id"), nullable=True)
#     checklist_frequency = Column(Integer, ForeignKey("checklist_frequency.id"), nullable=False)
#     daily_time = Column(Time, nullable=True)
#     weekly_day = Column(SmallInteger, nullable=True)
#     weekly_time = Column(Time, nullable=True)
#     monthly_schedule_type = Column(String(20), nullable=True)
#     monthly_day = Column(SmallInteger, nullable=True)
#     monthly_time = Column(Time, nullable=True)
#     monthly_week_of_month = Column(SmallInteger, nullable=True)
#     monthly_weekday = Column(SmallInteger, nullable=True)
#     weekday_time = Column(Time, nullable=True)
#     past_due_after_day = Column(Integer, nullable=True)
#     past_due_after_hour = Column(String(10), nullable=True)
#     template_version = Column(Integer, default=1, nullable=False)
#     status = Column(Boolean, default=True, nullable=False)
#     created_at = Column(DateTime, default=func.now(), nullable=False)
#     updated_at = Column(DateTime, default=func.now(), nullable=False)
    
#     # Relationships
#     workplace_rel = relationship("Workplace")
#     template_rel = relationship("ChecklistTemplate")
#     created_by_rel = relationship("User", foreign_keys=[created_by])
#     assignee_rel = relationship("User", foreign_keys=[assignee])
#     group_rel = relationship("ChecklistGroup")
#     frequency_rel = relationship("ChecklistFrequency")


# class ChecklistScheduleDate(Base):
#     __tablename__ = "checklist_schedule_date"
    
#     id = Column(Integer, primary_key=True, index=True)
#     checklist_schedule = Column(Integer, ForeignKey("checklist_schedule.id"), nullable=False)
#     scheduled_date = Column(Date, nullable=False)
#     scheduled_time = Column(Time, nullable=False)
#     created_at = Column(DateTime, nullable=True)
#     updated_at = Column(DateTime, nullable=True)
    
#     # Relationships
#     schedule_rel = relationship("ChecklistSchedule")


# class ChecklistScheduleEvent(Base):
#     __tablename__ = "checklist_schedule_event"
    
#     id = Column(Integer, primary_key=True, index=True)
#     workplace = Column(Integer, ForeignKey("workplace.id"), nullable=False)
#     checklist_schedule = Column(Integer, ForeignKey("checklist_schedule.id"), nullable=False)
#     checklist_template = Column(Integer, ForeignKey("checklist_template.id"), nullable=False)
#     scheduled_date = Column(Date, nullable=True)
#     scheduled_time = Column(Time, nullable=True)
#     status = Column(String(20), nullable=False)
#     completed_by = Column(Integer, ForeignKey("user.id"), nullable=True)
#     completed_at = Column(DateTime, nullable=True)
#     notes = Column(Text, nullable=True)
#     signoff_required = Column(Boolean, default=False, nullable=False)
#     approved = Column(Boolean, default=False, nullable=False)
#     approved_by = Column(Integer, ForeignKey("user.id"), nullable=True)
#     created_at = Column(DateTime, default=func.now(), nullable=False)
#     updated_at = Column(DateTime, default=func.now(), nullable=False)
    
#     # Relationships
#     workplace_rel = relationship("Workplace")
#     schedule_rel = relationship("ChecklistSchedule")
#     template_rel = relationship("ChecklistTemplate")
#     completed_by_rel = relationship("User", foreign_keys=[completed_by])
#     approved_by_rel = relationship("User", foreign_keys=[approved_by])


# class DoctrineMigrationVersions(Base):
#     __tablename__ = "doctrine_migration_versions"
    
#     version = Column(String(191), primary_key=True)
#     executed_at = Column(DateTime, nullable=True)
#     execution_time = Column(Integer, nullable=True)


# # Pydantic Schemas
# class OrganizationBase(BaseModel):
#     name: str
#     identifier: str
#     uuid: str
#     administrator_first_name: str
#     administrator_last_name: str
#     administrator_email: EmailStr
#     suspended: bool = False
#     partner: bool = False

# class OrganizationCreate(OrganizationBase):
#     pass

# class Organization(OrganizationBase):
#     id: int
#     created_at: datetime
#     updated_at: Optional[datetime] = None
    
#     class Config:
#         from_attributes = True


# class UserBase(BaseModel):
#     first_name: str
#     middle_name: str = ""
#     last_name: str
#     email: EmailStr
#     suspended: bool = False
#     synced: bool = False
#     archived: bool = False
#     ghost: bool = False

# class UserCreate(UserBase):
#     password: str
#     roles: dict

# class User(UserBase):
#     id: int
#     user_type: Optional[int] = None
#     created_at: datetime
#     updated_at: datetime
    
#     class Config:
#         from_attributes = True


# class ChecklistTemplateBase(BaseModel):
#     label: str
#     version: int = 1
#     template_owner: Optional[str] = None
#     signoff_required: bool = False
#     active: bool
#     deleted: bool

# class ChecklistTemplateCreate(ChecklistTemplateBase):
#     workplace: int
#     author: Optional[int] = None
#     category: Optional[int] = None
#     frequency: Optional[int] = None

# class ChecklistTemplate(ChecklistTemplateBase):
#     id: int
#     template_uid: uuid.UUID
#     workplace: int
#     author: Optional[int] = None
#     category: Optional[int] = None
#     frequency: Optional[int] = None
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None
    
#     class Config:
#         from_attributes = True


# class ChecklistTaskBase(BaseModel):
#     section: Optional[str] = None
#     duty: str
#     instructions: str
#     answer_type: str
#     expected_answer: str
#     list_order: int = 0
#     active: bool
#     deleted: bool

# class ChecklistTaskCreate(ChecklistTaskBase):
#     parent: int

# class ChecklistTask(ChecklistTaskBase):
#     id: int
#     parent: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None
    
#     class Config:
#         from_attributes = True


# class ChecklistScheduleEventBase(BaseModel):
#     scheduled_date: Optional[date] = None
#     scheduled_time: Optional[time] = None
#     status: str
#     notes: Optional[str] = None
#     signoff_required: bool = False
#     approved: bool = False

# class ChecklistScheduleEventCreate(ChecklistScheduleEventBase):
#     workplace: int
#     checklist_schedule: int
#     checklist_template: int

# class ChecklistScheduleEvent(ChecklistScheduleEventBase):
#     id: int
#     workplace: int
#     checklist_schedule: int
#     checklist_template: int
#     completed_by: Optional[int] = None
#     completed_at: Optional[datetime] = None
#     approved_by: Optional[int] = None
#     created_at: datetime
#     updated_at: datetime
    
#     class Config:
#         from_attributes = True



class ChecklistScheduleEvent(Base):
    __tablename__ = "checklist_schedule_event"
    
    id = Column(Integer, primary_key=True, index=True)
    workplace = Column(Integer, ForeignKey("workplace.id"), nullable=False)
    checklist_schedule = Column(Integer, ForeignKey("checklist_schedule.id"), nullable=False)
    checklist_template = Column(Integer, ForeignKey("checklist_template.id"), nullable=False)
    scheduled_date = Column(Date, nullable=True)
    scheduled_time = Column(Time, nullable=True)
    status = Column(String(20), nullable=False)
    completed_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    signoff_required = Column(Boolean, default=False, nullable=False)
    approved = Column(Boolean, default=False, nullable=False)
    approved_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    workplace_rel = relationship("Workplace")
    schedule_rel = relationship("ChecklistSchedule")
    template_rel = relationship("ChecklistTemplate")
    completed_by_rel = relationship("User", foreign_keys=[completed_by])
    approved_by_rel = relationship("User", foreign_keys=[approved_by])

class ChecklistScheduleDate(Base):
    __tablename__ = "checklist_schedule_date"
    
    id = Column(Integer, primary_key=True, index=True)
    checklist_schedule = Column(Integer, ForeignKey("checklist_schedule.id"), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(Time, nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    schedule_rel = relationship("ChecklistSchedule")

class ChecklistSchedule(Base):
    __tablename__ = "checklist_schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    workplace = Column(Integer, ForeignKey("workplace.id"), nullable=False)
    checklist_template = Column(Integer, ForeignKey("checklist_template.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    assignment_type = Column(String(20), nullable=False)
    assignee = Column(Integer, ForeignKey("user.id"), nullable=True)
    checklist_group = Column(Integer, ForeignKey("checklist_group.id"), nullable=True)
    checklist_frequency = Column(Integer, ForeignKey("checklist_frequency.id"), nullable=False)
    daily_time = Column(Time, nullable=True)
    weekly_day = Column(SmallInteger, nullable=True)
    weekly_time = Column(Time, nullable=True)
    monthly_schedule_type = Column(String(20), nullable=True)
    monthly_day = Column(SmallInteger, nullable=True)
    monthly_time = Column(Time, nullable=True)
    monthly_week_of_month = Column(SmallInteger, nullable=True)
    monthly_weekday = Column(SmallInteger, nullable=True)
    weekday_time = Column(Time, nullable=True)
    past_due_after_day = Column(Integer, nullable=True)
    past_due_after_hour = Column(String(10), nullable=True)
    template_version = Column(Integer, default=1, nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    workplace_rel = relationship("Workplace")
    template_rel = relationship("ChecklistTemplate")
    created_by_rel = relationship("User", foreign_keys=[created_by])
    assignee_rel = relationship("User", foreign_keys=[assignee])
    group_rel = relationship("ChecklistGroup")
    frequency_rel = relationship("ChecklistFrequency")

class ChecklistTemplate(Base):
    __tablename__ = "checklist_template"
    
    id = Column(Integer, primary_key=True, index=True)
    author = Column(Integer, ForeignKey("user.id"), nullable=True)
    category = Column(Integer, ForeignKey("checklist_category.id"), nullable=True)
    frequency = Column(Integer, ForeignKey("checklist_frequency.id"), nullable=True)
    workplace = Column(Integer, ForeignKey("workplace.id"), nullable=False)
    label = Column(String(255), nullable=False)
    template_uid = Column(String, nullable=False)  # Adjusted to String for UUID
    version = Column(Integer, default=1, nullable=False)
    template_owner = Column(String(55), nullable=True)
    signoff_required = Column(Boolean, default=False)
    active = Column(Boolean, nullable=False)
    deleted = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    author_rel = relationship("User")
    category_rel = relationship("ChecklistCategory")
    frequency_rel = relationship("ChecklistFrequency")
    workplace_rel = relationship("Workplace")
    tasks = relationship("ChecklistTask", back_populates="parent_template")

class ChecklistFrequency(Base):
    __tablename__ = "checklist_frequency"
    
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(255), nullable=False)
    active = Column(Boolean, nullable=False)
    deleted = Column(Boolean, nullable=False)