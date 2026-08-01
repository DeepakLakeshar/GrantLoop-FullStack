import uuid
from decimal import Decimal
from .base import BasePayoutGateway, TransferResult


class StripePayoutGateway(BasePayoutGateway):
    """
    Stripe Connect Transfers API gateway wrapper (mock implementation for sandbox integration).
    """

    def initiate_transfer(
        self,
        *,
        account_reference: str,
        amount: Decimal,
        currency: str,
        idempotency_key: str = None,
    ) -> TransferResult:
        ref = idempotency_key or f"tr_stripe_{uuid.uuid4().hex[:16]}"
        return TransferResult(
            success=True,
            gateway_reference=ref,
            transfer_reference="",
            status="processing",
            metadata={"destination": account_reference, "amount": str(amount), "currency": currency},
        )

    def verify_transfer(self, *, gateway_reference: str) -> TransferResult:
        tx_ref = f"po_stripe_{uuid.uuid4().hex[:12]}" if gateway_reference else f"po_stripe_unknown_{uuid.uuid4().hex[:8]}"
        return TransferResult(
            success=True,
            gateway_reference=gateway_reference,
            transfer_reference=tx_ref,
            status="completed",
            metadata={"settled": True},
        )
