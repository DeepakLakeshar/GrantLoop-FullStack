from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TransferResult:
    """
    Normalized result container for payment disbursement outcomes.
    Interchangeable across Stripe Connect, Razorpay Payouts, and Mock adapters.
    """

    success: bool
    gateway_reference: str
    transfer_reference: str
    status: str
    metadata: dict


class BasePayoutGateway:
    """
    Abstract base class for all payout gateway providers.
    Defines standard interfaces needed for initiating automated fund transfers
    and verifying settlement confirmations asynchronously.
    """

    def initiate_transfer(
        self,
        *,
        account_reference: str,
        amount: Decimal,
        currency: str,
        idempotency_key: str = None,
    ) -> TransferResult:
        """
        Initiates an automated payout transfer to an external beneficiary account.
        """
        raise NotImplementedError("Subclasses must implement initiate_transfer()")

    def verify_transfer(self, *, gateway_reference: str) -> TransferResult:
        """
        Verifies settlement status of an existing disbursement transfer directly with provider.
        """
        raise NotImplementedError("Subclasses must implement verify_transfer()")
