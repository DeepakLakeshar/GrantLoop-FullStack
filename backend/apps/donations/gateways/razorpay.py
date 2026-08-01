import uuid
from .base import BasePaymentGateway, VerificationResult


class RazorpayGateway(BasePaymentGateway):
    """
    Razorpay payment gateway wrapper (mock implementation).
    """

    def create_order(self, *, original_amount, original_currency: str, settled_currency: str) -> dict:
        return {
            "gateway_type": "razorpay",
            "gateway_order_id": f"razorpay_order_{uuid.uuid4().hex}",
            "settled_amount": original_amount,
            "settled_currency": settled_currency,
        }

    def verify_payment(self, *, gateway_order_id: str, gateway_transaction_id: str = None) -> VerificationResult:
        tx_id = gateway_transaction_id or f"pay_{uuid.uuid4().hex}"
        return VerificationResult(
            verified=True,
            transaction_id=tx_id,
            gateway_metadata={"method": "upi", "bank": "HDFC"},
        )

    def refund_payment(self, *, gateway_transaction_id: str, amount) -> dict:
        return {
            "status": "refunded",
            "refund_id": f"razorpay_refund_{uuid.uuid4().hex}",
            "amount": amount,
        }
