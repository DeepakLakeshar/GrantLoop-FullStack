"""
Comprehensive multi-status JSON example dictionaries and concrete webhook payloads for OpenAPI schema documentation.
"""

# --- Standard Error Payload Examples ---
ERROR_400_EXAMPLE = {
    "detail": ["Invalid field parameter syntax or missing required argument."],
    "code": "invalid_parameter"
}

ERROR_401_EXAMPLE = {
    "detail": "Authentication credentials were not provided or access token has expired.",
    "code": "not_authenticated"
}

ERROR_403_EXAMPLE = {
    "detail": "You do not have permission to perform this action under your persona role (RBAC policy violation).",
    "code": "permission_denied"
}

ERROR_404_EXAMPLE = {
    "detail": "No matching resource entity found for the provided UUID.",
    "code": "not_found"
}

ERROR_409_EXAMPLE = {
    "detail": "State transition conflict: cannot modify an already approved payout or verified beneficiary.",
    "code": "conflict"
}

ERROR_422_EXAMPLE = {
    "detail": "Unprocessable Entity: domain calculation or accounting rule verification failed.",
    "code": "unprocessable_entity"
}

ERROR_429_EXAMPLE = {
    "detail": "Request limit exceeded. Expected available in 45 seconds. Check Retry-After response header.",
    "code": "throttled"
}

ERROR_500_EXAMPLE = {
    "detail": "Internal server error: upstream payment gateway communication timed out or database disconnect occurred.",
    "code": "server_error"
}


# --- Concrete Webhook Event Payloads ---
STRIPE_WEBHOOK_PAYLOAD_EXAMPLE = {
    "id": "evt_3Nq2vN2eZvKYlo2C17fC8KxF",
    "object": "event",
    "api_version": "2023-10-16",
    "created": 1722518400,
    "type": "payment_intent.succeeded",
    "data": {
        "object": {
            "id": "pi_3Nq2vN2eZvKYlo2C1W0aBzqT",
            "object": "payment_intent",
            "amount": 25000,
            "currency": "usd",
            "status": "succeeded",
            "metadata": {
                "donation_id": "8c96b3fa-b111-878e-2643-65a1c1e647a1",
                "campaign_id": "c1e647a1-8c96-b3fa-b111-878e264365a1"
            }
        }
    }
}

RAZORPAY_WEBHOOK_PAYLOAD_EXAMPLE = {
    "entity": "event",
    "account_id": "acc_JMZzNzHwTj1rY1",
    "event": "order.paid",
    "contains": ["order", "payment"],
    "created_at": 1722518405,
    "payload": {
        "order": {
            "entity": {
                "id": "order_Lp9gVnXK2jG7qF",
                "amount": 500000,
                "currency": "INR",
                "status": "paid",
                "receipt": "don_receipt_8c96b3fa"
            }
        },
        "payment": {
            "entity": {
                "id": "pay_Lp9gW1vQ8aF3mB",
                "amount": 500000,
                "currency": "INR",
                "status": "captured",
                "method": "upi",
                "order_id": "order_Lp9gVnXK2jG7qF"
            }
        }
    }
}


# --- Domain Feed Success Payload Examples ---
AUTH_TOKEN_SUCCESS_EXAMPLE = {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access_token_payload.fake_signature_hash",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh_token_payload.fake_signature_hash"
}

USER_PROFILE_EXAMPLE = {
    "id": 1,
    "email": "director@hopefoundation.org",
    "first_name": "Deepak",
    "last_name": "Lakeshar",
    "role": "NGO",
    "is_active": True
}

CAMPAIGN_SUCCESS_EXAMPLE = {
    "id": "c1e647a1-8c96-b3fa-b111-878e264365a1",
    "title": "Clean Water Expansion Project 2026",
    "description": "Constructing 25 clean solar-powered water filtration installations across rural villages.",
    "target_amount": "150000.00",
    "raised_amount": "45000.00",
    "currency": "USD",
    "status": "active",
    "start_date": "2026-08-01",
    "end_date": "2026-12-31",
    "ngo_id": 2
}

BENEFICIARY_SUCCESS_EXAMPLE = {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1a2b3c4d5e6f",
    "full_name": "Ananya Sharma",
    "phone_number": "+919876543210",
    "verification_status": "verified",
    "campaign_id": "c1e647a1-8c96-b3fa-b111-878e264365a1",
    "created_at": "2026-08-01T10:00:00Z"
}

DONATION_SUCCESS_EXAMPLE = {
    "id": "8c96b3fa-b111-878e-2643-65a1c1e647a1",
    "amount": "250.00",
    "currency": "USD",
    "status": "confirmed",
    "payment_gateway": "stripe",
    "gateway_transaction_id": "pi_3Nq2vN2eZvKYlo2C1W0aBzqT",
    "donor_email": "generous.donor@example.com",
    "created_at": "2026-08-01T12:30:00Z"
}

PAYOUT_SUCCESS_EXAMPLE = {
    "id": "d7e8f9a0-1b2c-3d4e-5f6a-7b8c9d0e1f2a",
    "requested_amount": "10000.00",
    "approved_amount": "10000.00",
    "currency": "USD",
    "status": "completed",
    "gateway_reference": "po_3Nq2vN2eZvKYlo2C9kLpMnR",
    "available_balance_before": "45000.00",
    "available_balance_after": "35000.00",
    "created_at": "2026-08-01T14:15:00Z"
}

NOTIFICATION_SUCCESS_EXAMPLE = {
    "id": "f1e2d3c4-b5a6-9c8d-7e6f-5a4b3c2d1e0f",
    "title": "Payout Request Approved",
    "message": "Your withdrawal request of $10,000.00 for Clean Water Expansion has been approved and processed.",
    "is_read": False,
    "created_at": "2026-08-01T14:16:00Z"
}

ANALYTICS_DASHBOARD_EXAMPLE = {
    "role": "ADMIN",
    "total_donations_volume": "450000.00",
    "total_payouts_volume": "120000.00",
    "platform_available_balance": "330000.00",
    "active_campaigns_count": 24,
    "verified_beneficiaries_count": 1420,
    "currency": "USD"
}

REPORT_JSON_EXAMPLE = {
    "metadata": {
        "generated_at": "2026-08-01T20:50:00Z",
        "generated_by": "admin@grantloop.example",
        "filters_applied": {"status": "confirmed"},
        "total_records": 1030,
        "report_version": "v1.0"
    },
    "data": [
        DONATION_SUCCESS_EXAMPLE
    ]
}
