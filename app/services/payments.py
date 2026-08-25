from abc import ABC, abstractmethod
from typing import Optional


class PaymentService(ABC):
    @abstractmethod
    def initiate_payment(self, amount: float, currency: str, parcel_id: int) -> dict:
        ...

    @abstractmethod
    def get_payment_status(self, provider_transaction_id: str) -> Optional[dict]:
        ...


class StubPaymentService(PaymentService):
    """Deterministic stub for local development and tests."""

    def initiate_payment(self, amount: float, currency: str, parcel_id: int) -> dict:
        return {
            "provider_transaction_id": f"stub-txn-{parcel_id}",
            "status": "completed",
            "provider": "stub",
        }

    def get_payment_status(self, provider_transaction_id: str) -> Optional[dict]:
        return {
            "provider_transaction_id": provider_transaction_id,
            "status": "completed",
            "provider": "stub",
        }
