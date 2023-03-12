from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Path, Query
from datetime import datetime
import pandas as pd


app = FastAPI(
    title="Otter case by Anna",
    description="Technical test for the Global Automation Specialist role",
    version="0.1.0",
)

class Customer(BaseModel):
    """Representation of a customer in the system."""

    full_name: str = Field(description="Customer's full_name")
    email: str
    business_name: str = Field(description="Customer's business")
    num_locations: int = Field(description="Number of restaurant locations")
    phone: int
    role: str
    country: str

class Location(BaseModel):
    business_id: int
    name: str
    address: str
    postcode: str
    country: str
    phone: int
    website: str

class Business(BaseModel):
    legal_id: str
    customer_id: int
    name: str
    locations: Location # TODO: should be a dictionary of locations

class CSM(BaseModel):
    customer_id: int
    status: str = Field(description="Examples: Active, Paused, Churned, Blocked...")

class Terms(BaseModel):
    customer_id: int
    business_id: int
    product: str = Field(description="Options: Basic, Core or Premium")
    fee: float
    date: datetime

class Payment(BaseModel):
    customer_id: int
    business_id: int
    bank_name: str
    account: str
    card: int


# --------------------- CUSTOMERS --------------------- #
customers = {
    1: Customer(full_name="Anna", email='a@z.c', business_name='Crepes', num_locations=1, phone=0, role='a', country='Spain', ),
    2: Customer(full_name="Lloyd",  email='l@z.c', business_name='Salt & Spice', num_locations=1,  phone=1, role='b', country='UK'),
    3: Customer(full_name="Niko",  email='n@z.c', business_name='Anything Co.', num_locations=1,  phone=2, role='c', country='Norway')
    }

@app.get("/")
def index() -> dict[str, dict[int, Customer]]:
    """Return all customers"""
    return {"Customers": customers}

@app.get("/customer/{customer_id}")
def query_customer_by_id(customer_id: int = Path(None, gt=0)) -> Customer:
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id=} does not exist.")
    return customers[customer_id]

@app.post("/customer/{customer_id}")
def add_customer(customer: Customer, customer_id: int = Path(None, gt=0)) -> dict[str, Customer]:
    if customer_id in customers: # if customer_id in customers:
        raise HTTPException(status_code=400, detail=f"Customer {customer_id=} already exists.")
    customers[customer_id] = customer # customer_id
    return {"added": customer}

@app.put("customer/{customer_id}")
def update_customer(customer: Customer, customer_id: int = Path(None, gt=0)) -> dict:
    if all(info is None for info in (customer.full_name, customer.email, customer.business_name)):
        raise HTTPException(status_code=400, detail="No parameters provided for update.")

    # TODO: type all fields present in Customer or filter the fields specified in the query
    current_customer = customers[customer_id]
    if customer.full_name is not None:
        current_customer.full_name = customer.full_name
    if customer.email is not None:
        current_customer.email = customer.email
    if customer.business_name is not None:
        current_customer.business_name = customer.business_name

    return {"updated": customer}

@app.delete("/customer/{customer_id}")
def delete_customer(customer_id: int) -> dict[str, Customer]:
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id=} does not exist.")

    deleted_customer = customers.pop(customer_id)
    return {"deleted": deleted_customer}


# --------------------- TERMS --------------------- #
contracts = {
    1: Terms(customer_id=1, business_id=1, product='Basic', fee=100, date=pd.to_datetime('2022-01-01')),
    2: Terms(customer_id=2,  business_id=2, product='Core', fee=200,  date=pd.to_datetime('2022-01-01')),
    3: Terms(customer_id=3,  business_id=3, product='Premium', fee=300,  date=pd.to_datetime('2022-01-01'))
}
@app.post("/terms/{contract_id}")
def create_terms(customer_id: int, ) -> dict[str, dict[int, Customer]]:
    """Create contract for specified customer"""
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id=} does not exist.")

    customer = customers[customer_id]

    payload = {
        'contract_id': 4, # generate automatically,
        'customer_id': customer_id,
        'business_id': customer.business_name,
        'product': 'Basic',
        'fee': 100,
        'date': datetime.now()
    }
    # creation of contract logic: create file, upload to cloud, send to customer, etc.
    return {"created contract": payload}

@app.get("/terms/{contract_id}")
def get_terms(customer_id: int) -> dict[str, dict[int, Customer]]:
    """Return the contract of the specified customer"""
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id=} does not exist.")


    return {"contract": customers}

###########################

@app.get("/restaurant")
def query_item_by_parameters(full_name: str, business: str, role: int) -> dict:
    def check_item(item: Customer):
        """Check if the item matches the query arguments from the outer scope."""
        return all(
            (
                full_name is None or item.full_name == full_name,
                business is None or item.business == business,
                role is None or item.role != role,
            )
        )

    selection = [item for item in customers.values() if check_item(item)]
    return {
        "query": {"full_name": full_name, "business": business, "role": role},
        "selection": selection,
    }

@app.get("restaurant/{location}")
def get_location():
    return Location


@app.put("/update/{item_id}", responses={404: {"description": "Item not found"}, 400: {"description": "No arguments specified"}})
# The Query and Path classes also allow us to add documentation to query and path parameters.
def update(
    item_id: int = Path(title="Item ID", description="Unique integer that specifies an item.", ge=0),
    full_name: str
          | None = Query(
        title="Name",
        description="New full_name of the item.",
        default=None,
        min_length=1,
        max_length=8,
    ),
    business: float
           | None = Query(
        title="Price",
        description="New business of the item in Euro.",
        default=None,
        gt=0.0,
    ),
    role: int
           | None = Query(
        title="Count",
        description="New amount of instances of this item in stock.",
        default=None,
        ge=0,
    ),
):
    if item_id not in customers:
        HTTPException(status_code=404, detail=f"Item with {item_id=} does not exist.")
    if all(info is None for info in (full_name, business, role)):
        raise HTTPException(
            status_code=400, detail="No parameters provided for update."
        )

    item = customers[item_id]
    if full_name is not None:
        item.full_name = full_name
    if business is not None:
        item.business = business
    if role is not None:
        item.role = role

    return {"updated": item}


@app.delete("/delete/{item_id}")
def delete_item(item_id: int) -> dict[str, Customer]:

    if item_id not in customers:
        raise HTTPException(
            status_code=404, detail=f"Item with {item_id=} does not exist."
        )

    item = customers.pop(item_id)
    return {"deleted": item}
