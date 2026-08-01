import uuid
from decimal import Decimal
from .base import BasePayoutGateway, TransferResult


class MockPayoutGateway(BasePayoutGateway):
    """
    Instantaneous mock payout gateway for automated sandbox tests and local simulations.
    """

    def initiate_transfer(
        self,
        *,
        account_reference: str,
        amount: Decimal,
        currency: str,
        idempotency_key: str = None,
    ) -> TransferResult:
        ref = idempotency_key or f"mock_gw_{uuid.uuid4().hex[:12]}"
        return TransferResult(
            success=True,
            gateway_reference=ref,
            transfer_reference=f"mock_tx_{uuid.uuid4().hex[:10]}",
            status="processing",
            metadata={"mock_account": account_reference, "amount": str(amount)},
        )

    def verify_transfer(self, *, gateway_reference: str) -> TransferResult:
        tx_ref = f"mock_settle_{uuid.uuid4().hex[:10]}"
        return TransferResult(
            success=True,
            gateway_reference=gateway_reference or "mock_gw_default",
            transfer_reference=tx_ref,
            status="completed",
            metadata={"verified_by_mock": True},
        )
