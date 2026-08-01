from dataclasses import dataclass


@dataclass
class VerificationResult:
    """
    Normalized result container for payment verification outcomes.
    Interchangeable across Stripe and Razorpay integrations.
    """
    verified: bool
    transaction_id: str
    gateway_metadata: dict


class BasePaymentGateway:
    """
    Abstract base class for all payment gateway clients.
    Defines the standard methods needed for initiating checkouts,
    verifying transaction status, and issuing refunds.
    """

    def create_order(self, *, original_amount, original_currency: str, settled_currency: str) -> dict:
        """
        Initiates a payment order session at the provider gateway.
        """
        raise NotImplementedError("Subclasses must implement create_order()")

    def verify_payment(self, *, gateway_order_id: str, gateway_transaction_id: str = None) -> VerificationResult:
        """
        Verifies transaction status directly via provider reference.
        """
        raise NotImplementedError("Subclasses must implement verify_payment()")

    def refund_payment(self, *, gateway_transaction_id: str, amount) -> dict:
        """
        Issues a total or partial refund back to the source donor.
        """
        raise NotImplementedError("Subclasses must implement refund_payment()")
