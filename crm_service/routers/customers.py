from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from crm_service.schemas import CustomerCreate, CustomerListResponse, CustomerResponse, CustomerUpdate
from crm_service.services import CustomerService, DuplicateCustomerError
from shared.database import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a customer",
)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> CustomerResponse:
    service = CustomerService(db)
    try:
        return service.create_customer(payload)
    except DuplicateCustomerError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "",
    response_model=CustomerListResponse,
    summary="List customers",
)
def list_customers(
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> CustomerListResponse:
    service = CustomerService(db)
    customers, total = service.list_customers(limit=limit, offset=offset)
    return CustomerListResponse(items=customers, total=total, limit=limit, offset=offset)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get a customer by ID",
)
def get_customer(customer_id: int, db: Session = Depends(get_db)) -> CustomerResponse:
    service = CustomerService(db)
    customer = service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return customer


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update a customer",
)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
) -> CustomerResponse:
    service = CustomerService(db)
    customer = service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    try:
        return service.update_customer(customer, payload)
    except DuplicateCustomerError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a customer",
)
def delete_customer(customer_id: int, db: Session = Depends(get_db)) -> None:
    service = CustomerService(db)
    customer = service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    service.delete_customer(customer)
