from typing import Optional, List, Dict
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class Customer(BaseModel):
    """Data the customer sends when filling the website form."""
    full_name: str = Field(description="Customer's full_name")
    email: str
    business_name: str = Field(description="Customer's business")
    num_locations: int = Field(description="Number of restaurant locations")
    phone: int
    role: str
    country: str

class CustomerUpdate(BaseModel):
    """Data the customer sends when filling the website form."""
    full_name: Optional[str]
    email: Optional[str]
    business_name: Optional[str]
    num_locations: Optional[int]
    phone: Optional[int]
    role: Optional[str]
    country: Optional[str]

class Location(BaseModel):
    """Representation of a single business location in the system."""
    business_id: int
    name: str
    address: str
    postcode: str
    country: str
    phone: Optional[int]
    website: Optional[str]

class Business(BaseModel):
    """Representation of a business in the system."""
    legal_id: str
    customer_id: int
    name: str
    locations: Location # should be dict

class Product(str, Enum):
    """"Options: Basic, Core or Premium"""
    basic = "Basic"
    core = "Core"
    premium = "Premium"

class Terms(BaseModel):
    """Representation of a customer's contract in the system."""
    customer_id: int
    business_id: int
    product: Product
    fee: float
    date: datetime
    status: str

class Payment(BaseModel):
    """Representation of a customer data needed to process a payment in the system."""
    customer_id: int
    business_id: int
    bank_name: str
    account: str
    card: int
