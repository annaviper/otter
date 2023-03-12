from uuid import UUID
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Path, Query
from datetime import datetime
import pandas as pd
from typing import List
from models import Customer, CustomerUpdate, Business, Location, Terms, Payment, Product

"""
Streamline the process and make it more efficient and effective for both Otter and customers.

1.Automation:
    - Enable data to be transferred between applications. Manage and collect data.
    - Process orchestration: A → B. Easy management of multiple processes (i.e.: create a new user automatically when they sign up via the website)
2. Expand: Integrations with other APIs (delivery partners, shipment, money processing.
"""

app = FastAPI(
    title="Otter case by Anna",
    description="Technical test for the Global Automation Specialist role",
    version="0.1.0",
)

db_customers = {
    1: Customer(full_name="Anna", email='a@z.c', business_name='Crepes', num_locations=1, phone=0, role='a', country='Spain'),
    2: Customer(full_name="Lloyd", email='l@z.c', business_name='Salt & Spice', num_locations=1,  phone=1, role='b', country='UK'),
    3: Customer(full_name="Niko", email='n@z.c', business_name='Anything Co.', num_locations=1,  phone=2, role='c', country='Norway')
}

db_contracts = {
    1: Terms(customer_id=1, business_id=1, product='Basic', fee=100, date=pd.to_datetime('2022-01-01')),
    2: Terms(customer_id=2,  business_id=2, product='Core', fee=200,  date=pd.to_datetime('2022-01-01')),
}

db_businesses = {
    7: Business(legal_id='abc', customer_id=1, name="Fake name", locations=List[Location])
}


# --------------------- CUSTOMERS --------------------- #
"""
Common requests to do with a user: get, create, modify and delete.
"""
@app.get("/")
def root() -> dict:
    return {"Hello": "World"}


@app.get("/customer")
async def fetch_users():
    return db_customers


@app.get("/customer/{customer_id}")
def query_customer_by_id(customer_id: int = Path(None, gt=0)) -> Customer:
    if customer_id not in db_customers:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id=} does not exist.")

    return db_customers[customer_id]


@app.post("/customer")
async def add_customer(customer: Customer):
    if customer_id in db_customers:
        raise HTTPException(status_code=409, detail=f"Customer {customer_id=} already exists.")

    customer_id = 4 # TODO should be randomly generated
    db_customers[customer_id] = customer
    return {"created": customer}


@app.put("/customer/{customer_id}")
async def update_customer(customer_update: CustomerUpdate, customer_id: int):
    if customer_id not in db_customers:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id=} does not exist.")

    # TODO: Needs to list all the field available in the enum
    if all(info is None for info in (
        customer_update.full_name,
        customer_update.email,
        customer_update.business_name
        )
    ):
        raise HTTPException(status_code=400, detail="No parameters provided for update.")

    customer = db_customers[customer_id]
    if customer_update.full_name is not None:
        customer.full_name = customer_update.full_name
    if customer_update.email is not None:
        customer.email = customer_update.email
    if customer_update.business_name is not None:
        customer.business_name = customer_update.business_name
    return {"updated": customer}


@app.delete("/customer/{customer_id}")
async def delete_customer(customer_id: int):
    if customer_id not in db_customers:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id=} does not exist.")

    deleted_customer = db_customers.pop(customer_id)
    return {"deleted": deleted_customer}


# --------------------- TERMS --------------------- #
"""
Contract process could be automated in the platform:
Otter sends the contract to the user, the customer can open it, sign it online
(through a 3rd party) and send it back to Otter without leaving the platform.
"""
@app.get("/terms/{contract_id}")
def get_terms(customer_id: int) -> dict[str, dict[int, Customer]]:
    """Return the contract of the specified customer"""
    if customer_id not in db_contracts:
        raise HTTPException(status_code=404, detail=f"Contract {customer_id=} does not exist.")

    return {"contract": db_contracts[customer_id]} # since customer_id and contract_id are the same


@app.post("/terms/{contract_id}")
def create_terms(customer_id: int, ) -> dict[str, dict[int, Customer]]:
    """Create contract for specified customer"""
    if customer_id not in db_customers:
        raise HTTPException(status_code=404, detail=f"Contract {customer_id=} does not exist.")

    customer = db_customers[customer_id]

    payload = {
        'contract_id': customer_id,
        'customer_id': customer_id,
        'business_id': customer.business_name,
        'product': Product.basic,
        'fee': 100,
        'date': datetime.now(),
        'status': 'pending'
    }
    # creation of contract logic: create document, upload to cloud, send to customer, etc.
    return {"contract created": payload}


@app.put("terms/{contract_id}")
def terms_signed(contract_id: int) -> dict[str, dict[int, Terms]]:
    """Update contract status once it's been signed by the user"""
    # Missing logic, probably third party API integration to handle signing documents online
    contract = get_terms(contract_id)
    contract['status'] = 'completed'
    return {"updated": contract}


@app.delete("terms/{contract_id}")
def delete_contract(contract_id: int) -> dict[str, dict[int, Terms]]:
    if contract_id not in db_contracts:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id=} does not exist.")

    deleted_contract = db_contracts.pop(contract_id)
    return {"deleted": deleted_contract}


# --------------------- PAYMENTS --------------------- #
db_billing = {
    1: Payment(customer_id=1, business_id=2, bank_name="", account="", card=1234)
}

@app.get("billing/{customer_id}")
def get_billing_data(customer_id: int):
    if customer_id not in db_customers:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id=} does not exist.")

    for i in db_billing:
        if i.customer_id == customer_id:
            return db_billing[i]
