import uuid
from decimal import Decimal
from .base import BasePayoutGateway, TransferResult


class RazorpayPayoutGateway(BasePayoutGateway):
    """
    Razorpay X Payouts API gateway wrapper (mock implementation for sandbox integration).
    """

    def initiate_transfer(
        self,
        *,
        account_reference: str,
        amount: Decimal,
        currency: str,
        idempotency_key: str = None,
    ) -> TransferResult:
        ref = idempotency_key or f"pout_rzp_{uuid.uuid4().hex[:16]}"
        return TransferResult(
            success=True,
            gateway_reference=ref,
            transfer_reference="",
            status="processing",
            metadata={"fund_account_id": account_reference, "amount_paise": str(int(amount * 100))},
        )

    def verify_transfer(self, *, gateway_reference: str) -> TransferResult:
        tx_ref = f"utr_rzp_{uuid.uuid4().hex[:12]}" if gateway_reference else f"utr_rzp_{uuid.uuid4().hex[:8]}"
        return TransferResult(
            success=True,
            gateway_reference=gateway_reference,
            transfer_reference=tx_ref,
            status="completed",
            metadata={"settlement_utr": tx_ref},
        )
