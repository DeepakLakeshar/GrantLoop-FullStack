from .base import BasePaymentGateway
from .stripe import StripeGateway
from .razorpay import RazorpayGateway

_GATEWAY_REGISTRY = {
    "stripe": StripeGateway,
    "razorpay": RazorpayGateway,
}


def get_payment_gateway(gateway_type: str) -> BasePaymentGateway:
    """
    Gateway factory lookup returning interchangeable BasePaymentGateway adapters.
    """
    gateway_class = _GATEWAY_REGISTRY.get(gateway_type.lower())
    if not gateway_class:
        raise ValueError(f"Unsupported payment gateway: {gateway_type}")
    return gateway_class()
