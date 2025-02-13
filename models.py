from pydantic import BaseModel, ConfigDict
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Developer(Base):
    __tablename__ = 'developers'

    developer_id = Column(String, primary_key=True)
    developer_website = Column(String)
    developer_email = Column(String)

    # Relationship
    apps = relationship("App", back_populates="developer")

class Category(Base):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)

    # Relationship
    apps = relationship("App", back_populates="category")

class App(Base):
    __tablename__ = "apps"

    app_id = Column(String, primary_key=True)
    app_name = Column(String(255), nullable=False)
    developer_id = Column(String, ForeignKey("developers.developer_id"))
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    rating = Column(Float)
    """
    rating_count = Column(BigInteger)
    installs = Column(String(50))
    minimum_installs = Column(BigInteger)
    maximum_installs = Column(BigInteger)
    free = Column(Boolean, default=True)
    price = Column(Float, default=0.0)
    currency = Column(String(10))
    size = Column(Float)
    released = Column(DateTime)
    last_updated = Column(DateTime)
    content_rating = Column(String(50))
    privacy_policy = Column(Text)
    ad_supported = Column(Boolean, default=False)
    in_app_purchases = Column(Boolean, default=False)
    editors_choice = Column(Boolean, default=False)
    """

    # Relationships
    developer = relationship("Developer", back_populates="apps")
    category = relationship("Category", back_populates="apps")


# Developer Schema
class DeveloperSchema(BaseModel):
    developer_id: str
    developer_website: Optional[str]
    developer_email: Optional[str]

    class Config:
        ConfigDict(from_attributes=True)

# Category Schema
class CategorySchema(BaseModel):
    category_id: int
    category: str

    class Config:
        ConfigDict(from_attributes=True)

        

# App Schema
class AppSchema(BaseModel):
    app_id: str
    app_name: str
    developer_id: str
    category_id: int
    rating: Optional[float]
    """
    rating_count: Optional[int]
    installs: Optional[str]
    minimum_installs: Optional[int]
    maximum_installs: Optional[int]
    free: Optional[bool] = True
    price: Optional[float] = 0.0
    currency: Optional[str]
    size: Optional[float]
    released: Optional[str]
    last_updated: Optional[str]
    content_rating: Optional[str]
    privacy_policy: Optional[str]
    ad_supported: Optional[bool] = False
    in_app_purchases: Optional[bool] = False
    editors_choice: Optional[bool] = False
    """

    class Config:
        ConfigDict(from_attributes=True)

