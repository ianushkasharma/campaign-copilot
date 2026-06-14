from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crm_service.models import Customer
from crm_service.repositories import CustomerRepository
from crm_service.schemas import CustomerCreate, CustomerUpdate


class DuplicateCustomerError(Exception):
    pass


class CustomerService:
    def __init__(self, db: Session) -> None:
        self.repository = CustomerRepository(db)

    def create_customer(self, data: CustomerCreate) -> Customer:
        try:
            return self.repository.create(data)
        except IntegrityError as exc:
            raise DuplicateCustomerError("A customer with this email already exists.") from exc

    def list_customers(self, limit: int, offset: int) -> tuple[list[Customer], int]:
        return self.repository.list(limit=limit, offset=offset)

    def get_customer(self, customer_id: int) -> Customer | None:
        return self.repository.get(customer_id)

    def update_customer(self, customer: Customer, data: CustomerUpdate) -> Customer:
        try:
            return self.repository.update(customer, data)
        except IntegrityError as exc:
            raise DuplicateCustomerError("A customer with this email already exists.") from exc

    def delete_customer(self, customer: Customer) -> None:
        self.repository.delete(customer)
