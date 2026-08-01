from .base import BasePayoutGateway, TransferResult
from .stripe import StripePayoutGateway
from .razorpay import RazorpayPayoutGateway
from .mock import MockPayoutGateway

_PAYOUT_GATEWAY_REGISTRY = {
    "stripe": StripePayoutGateway,
    "razorpay": RazorpayPayoutGateway,
    "mock": MockPayoutGateway,
}


def get_payout_gateway(gateway_type: str) -> BasePayoutGateway:
    """
    Gateway factory returning interchangeable BasePayoutGateway adapters.
    """
    gateway_class = _PAYOUT_GATEWAY_REGISTRY.get(gateway_type.lower())
    if not gateway_class:
        raise ValueError(f"Unsupported payout gateway provider: {gateway_type}")
    return gateway_class()
