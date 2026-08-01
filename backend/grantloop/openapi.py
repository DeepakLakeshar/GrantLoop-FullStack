"""
Centralized, reusable OpenAPI 3.0 schema decorators and multi-status response registries for all GrantLoop APIs.
"""
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiRequest,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from grantloop.openapi_examples import (
    ANALYTICS_DASHBOARD_EXAMPLE,
    AUTH_TOKEN_SUCCESS_EXAMPLE,
    BENEFICIARY_SUCCESS_EXAMPLE,
    CAMPAIGN_SUCCESS_EXAMPLE,
    DONATION_SUCCESS_EXAMPLE,
    ERROR_400_EXAMPLE,
    ERROR_401_EXAMPLE,
    ERROR_403_EXAMPLE,
    ERROR_404_EXAMPLE,
    ERROR_409_EXAMPLE,
    ERROR_422_EXAMPLE,
    ERROR_429_EXAMPLE,
    ERROR_500_EXAMPLE,
    NOTIFICATION_SUCCESS_EXAMPLE,
    PAYOUT_SUCCESS_EXAMPLE,
    RAZORPAY_WEBHOOK_PAYLOAD_EXAMPLE,
    REPORT_JSON_EXAMPLE,
    STRIPE_WEBHOOK_PAYLOAD_EXAMPLE,
    USER_PROFILE_EXAMPLE,
)

# --- Standardized Reusable Multi-Status Error Responses ---
RESP_400 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Bad Request - Invalid field parameter syntax or missing required values.",
    examples=[OpenApiExample("Validation Failure", value=ERROR_400_EXAMPLE)],
)
RESP_401 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Unauthorized - Missing, malformed, or expired JWT access token.",
    examples=[OpenApiExample("Unauthenticated", value=ERROR_401_EXAMPLE)],
)
RESP_403 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Forbidden - RBAC persona role violation (e.g., Donor attempting Admin operations).",
    examples=[OpenApiExample("Permission Denied", value=ERROR_403_EXAMPLE)],
)
RESP_404 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Not Found - Requested entity UUID does not exist or user lacks visibility.",
    examples=[OpenApiExample("Resource Not Found", value=ERROR_404_EXAMPLE)],
)
RESP_409 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Conflict - State transition rule violation (e.g., editing closed campaign or approved payout).",
    examples=[OpenApiExample("State Conflict", value=ERROR_409_EXAMPLE)],
)
RESP_422 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Unprocessable Entity - Financial reconciliation or accounting rule check failed.",
    examples=[OpenApiExample("Domain Verification Error", value=ERROR_422_EXAMPLE)],
)
RESP_429 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Too Many Requests - Throttled (e.g., ReportExportThrottle at 100/min). Check Retry-After response header.",
    examples=[OpenApiExample("Rate Limit Exceeded", value=ERROR_429_EXAMPLE)],
)
RESP_500 = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Internal Server Error - Upstream gateway exception or database connection disruption.",
    examples=[OpenApiExample("Server Exception", value=ERROR_500_EXAMPLE)],
)

# Shared common error mapping applied to all protected APIs
COMMON_ERROR_RESPONSES = {
    400: RESP_400,
    401: RESP_401,
    403: RESP_403,
    404: RESP_404,
    409: RESP_409,
    422: RESP_422,
    429: RESP_429,
    500: RESP_500,
}


# --- Standardized Reusable Filtering Query Parameters ---
FILTER_PARAMS_CORE = [
    OpenApiParameter("search", OpenApiTypes.STR, description="Case-insensitive substring search across titles or names."),
    OpenApiParameter("ordering", OpenApiTypes.STR, description="Order results by field prefix (e.g., '-created_at', 'title')."),
    OpenApiParameter("status", OpenApiTypes.STR, description="Filter entities by explicit lifecycle status string."),
    OpenApiParameter("page", OpenApiTypes.INT, description="Page number within paginated dataset (default page_size=20)."),
    OpenApiParameter("page_size", OpenApiTypes.INT, description="Custom page size override (if allowed)."),
]

FILTER_PARAMS_FINANCIAL = FILTER_PARAMS_CORE + [
    OpenApiParameter("campaign", OpenApiTypes.UUID, description="Filter by target Campaign UUID."),
    OpenApiParameter("ngo", OpenApiTypes.INT, description="Filter by associated NGO User ID."),
    OpenApiParameter("beneficiary", OpenApiTypes.UUID, description="Filter by target Beneficiary UUID."),
    OpenApiParameter("currency", OpenApiTypes.STR, description="Filter by currency ISO code (e.g., USD, INR, GBP)."),
    OpenApiParameter("year", OpenApiTypes.INT, description="Filter by explicit creation or execution year."),
    OpenApiParameter("month", OpenApiTypes.INT, description="Filter by 1-12 numerical month."),
]


# ==============================================================================
# Domain-Specific Reusable View Decorators
# ==============================================================================

auth_token_schema = extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Obtain JWT Access and Rotating Refresh Tokens",
        description="Authenticate with email and password to receive a 15-minute access token and 7-day rotating refresh token pair.",
        responses={200: OpenApiResponse(response=OpenApiTypes.OBJECT, description="Successful authentication token exchange.", examples=[OpenApiExample("Token Pair", value=AUTH_TOKEN_SUCCESS_EXAMPLE)]), 400: RESP_400, 401: RESP_401, 429: RESP_429, 500: RESP_500},
    )
)

user_register_schema = extend_schema_view(
    post=extend_schema(
        tags=["Accounts"],
        summary="Register New User Persona Account",
        description="Register a new account under Admin, NGO, or Donor personas.",
        responses={201: OpenApiResponse(response=OpenApiTypes.OBJECT, description="Account registered.", examples=[OpenApiExample("User Profile", value=USER_PROFILE_EXAMPLE)]), **COMMON_ERROR_RESPONSES},
    )
)

campaign_viewset_schema = extend_schema_view(
    list=extend_schema(tags=["Campaigns"], summary="List All Active Fundraising Campaigns", description="Paginated query feed of fundraising campaigns with filtering by search, status, and NGO ID.", parameters=FILTER_PARAMS_FINANCIAL),
    create=extend_schema(tags=["Campaigns"], summary="Create Fundraising Campaign", description="NGO or Admin creation of a new fundraising campaign. Sets initial state to draft or active.", responses={201: OpenApiResponse(response=OpenApiTypes.OBJECT, description="Campaign created.", examples=[OpenApiExample("Campaign Example", value=CAMPAIGN_SUCCESS_EXAMPLE)]), **COMMON_ERROR_RESPONSES}),
    retrieve=extend_schema(tags=["Campaigns"], summary="Retrieve Campaign Details by UUID", description="Get full details, goal progress, and milestone milestones for a specific campaign UUID.", responses={200: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[OpenApiExample("Campaign Detail", value=CAMPAIGN_SUCCESS_EXAMPLE)]), **COMMON_ERROR_RESPONSES}),
    update=extend_schema(tags=["Campaigns"], summary="Update Campaign Configuration", responses=COMMON_ERROR_RESPONSES),
    partial_update=extend_schema(tags=["Campaigns"], summary="Partially Update Campaign Fields", responses=COMMON_ERROR_RESPONSES),
    destroy=extend_schema(tags=["Campaigns"], summary="Delete or Archive Draft Campaign", responses=COMMON_ERROR_RESPONSES),
)

campaign_update_schema = extend_schema_view(
    list=extend_schema(tags=["Campaigns"], summary="List Progress Updates for Campaign", parameters=FILTER_PARAMS_CORE),
    create=extend_schema(tags=["Campaigns"], summary="Post Progress Update to Campaign", responses=COMMON_ERROR_RESPONSES),
)

beneficiary_viewset_schema = extend_schema_view(
    list=extend_schema(tags=["Beneficiaries"], summary="List Verified Beneficiaries", description="Returns role-isolated list of beneficiaries. Donors view only verified records.", parameters=FILTER_PARAMS_FINANCIAL),
    create=extend_schema(tags=["Beneficiaries"], summary="Onboard New Beneficiary Record", responses={201: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[OpenApiExample("Beneficiary", value=BENEFICIARY_SUCCESS_EXAMPLE)]), **COMMON_ERROR_RESPONSES}),
    retrieve=extend_schema(tags=["Beneficiaries"], summary="Retrieve Beneficiary Compliance Verification Details", responses=COMMON_ERROR_RESPONSES),
)

donation_viewset_schema = extend_schema_view(
    list=extend_schema(tags=["Donations"], summary="List Donor Contributions", description="Role-isolated donation records with full pagination and multi-currency filtering.", parameters=FILTER_PARAMS_FINANCIAL),
    create=extend_schema(tags=["Donations"], summary="Initiate Donation Contribution", description="Record a pledge or payment intent contribution and bind to Stripe or Razorpay gateways.", responses={201: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[OpenApiExample("Donation Receipt", value=DONATION_SUCCESS_EXAMPLE)]), **COMMON_ERROR_RESPONSES}),
)

stripe_webhook_schema = extend_schema(
    tags=["Donations"],
    summary="Stripe Payment Intent Succeeded Webhook",
    description=(
        "Idempotent webhook endpoint receiving Stripe `payment_intent.succeeded` events.\n\n"
        "### Signature Verification & Headers\n"
        "Requires exact HTTP header `Stripe-Signature` matching signed payload secret.\n"
        "### Idempotency Guarantee\n"
        "Repeat webhook calls with identical event IDs or gateway transaction references immediately return `200 OK` "
        "without generating duplicate donation entries or modifying platform accounting balances."
    ),
    request=OpenApiRequest(
        request=OpenApiTypes.OBJECT,
        examples=[OpenApiExample("Stripe Event Payload", value=STRIPE_WEBHOOK_PAYLOAD_EXAMPLE)],
    ),
    responses={200: OpenApiResponse(description="Webhook event verified and processed idempotently."), 400: RESP_400, 500: RESP_500},
)

razorpay_webhook_schema = extend_schema(
    tags=["Donations"],
    summary="Razorpay Order Paid Notification Webhook",
    description=(
        "Idempotent webhook endpoint receiving Razorpay `order.paid` and capture events.\n\n"
        "### Signature Verification & Headers\n"
        "Requires HTTP header `X-Razorpay-Signature` verified via HMAC-SHA256 computation.\n"
        "### Idempotency Guarantee\n"
        "Duplicate order notifications are gracefully acknowledged with HTTP `200 OK` without duplicating financial ledger entries."
    ),
    request=OpenApiRequest(
        request=OpenApiTypes.OBJECT,
        examples=[OpenApiExample("Razorpay Event Payload", value=RAZORPAY_WEBHOOK_PAYLOAD_EXAMPLE)],
    ),
    responses={200: OpenApiResponse(description="Webhook event verified and processed idempotently."), 400: RESP_400, 500: RESP_500},
)

notification_viewset_schema = extend_schema_view(
    list=extend_schema(tags=["Notifications"], summary="List User Real-time Alerts & Notifications", parameters=FILTER_PARAMS_CORE, responses={200: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[OpenApiExample("Notification List", value=[NOTIFICATION_SUCCESS_EXAMPLE])]), **COMMON_ERROR_RESPONSES}),
)

payout_viewset_schema = extend_schema_view(
    list=extend_schema(tags=["Payouts"], summary="List NGO Fund Withdrawal & Payout Requests", parameters=FILTER_PARAMS_FINANCIAL),
    create=extend_schema(tags=["Payouts"], summary="Submit NGO Withdrawal Request", description="Initiate withdrawal request for an active campaign with available balance audit snapshot.", responses={201: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[OpenApiExample("Payout Request", value=PAYOUT_SUCCESS_EXAMPLE)]), **COMMON_ERROR_RESPONSES}),
)

milestone_viewset_schema = extend_schema_view(
    list=extend_schema(tags=["Milestones"], summary="List Project Escrow Milestones", parameters=FILTER_PARAMS_CORE),
    create=extend_schema(tags=["Milestones"], summary="Define New Campaign Milestone Target", responses=COMMON_ERROR_RESPONSES),
)

execution_partner_schema = extend_schema_view(
    list=extend_schema(tags=["Execution Partners"], summary="List Registered Implementation Partners", parameters=FILTER_PARAMS_CORE),
    create=extend_schema(tags=["Execution Partners"], summary="Register On-the-ground Implementation Partner", responses=COMMON_ERROR_RESPONSES),
)

document_viewset_schema = extend_schema_view(
    list=extend_schema(tags=["Documents"], summary="List Uploaded Compliance Documents", parameters=FILTER_PARAMS_CORE),
    create=extend_schema(tags=["Documents"], summary="Upload Compliance Verification Document", description="Multipart form data file upload for NGO governance and campaign evidence tracking.", responses=COMMON_ERROR_RESPONSES),
)

analytics_dashboard_schema = extend_schema(
    tags=["Analytics"],
    summary="Role-Isolated Interactive Financial Dashboard Feed",
    description="Returns aggregate donation volumes, payout disbursement balances, active campaign counts, and verification indicators tailored precisely to Admin, NGO, or Donor access roles.",
    responses={200: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[OpenApiExample("Analytics Dashboard", value=ANALYTICS_DASHBOARD_EXAMPLE)]), **COMMON_ERROR_RESPONSES},
)

report_json_schema = extend_schema(
    tags=["Reports"],
    summary="Paginated Tabular Audit Report JSON Feed",
    description="Returns structured paginated report data (page_size=20) with embedded cryptographic audit generation timestamp, user attribution, and filter metadata.",
    parameters=FILTER_PARAMS_FINANCIAL,
    responses={200: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[OpenApiExample("Report JSON Feed", value=REPORT_JSON_EXAMPLE)]), **COMMON_ERROR_RESPONSES},
)

report_export_schema = extend_schema(
    tags=["Reports"],
    summary="Stream Raw Complete Export Document (CSV, Excel, or PDF)",
    description=(
        "Generates and streams an unpaginated, complete filtered report document attachment.\n\n"
        "### Supported Formats (`?format=csv|xlsx|pdf`)\n"
        "- **CSV**: Streaming chunked memory-efficient string buffers.\n"
        "- **Excel (`xlsx`)**: Formatted workbook with frozen top headers (A6), auto-sized widths, bold typography, and currency cell formatting.\n"
        "- **PDF**: ReportLab styled presentation document with page numbers (`Page X of Y`), running timestamps, and GrantLoop branding.\n\n"
        "### Rate Limit & Cooldown\n"
        "Protected by `ReportExportThrottle` (`100/minute`). If throttled, inspect HTTP `Retry-After: <seconds>` response header."
    ),
    parameters=FILTER_PARAMS_FINANCIAL + [OpenApiParameter("format", OpenApiTypes.STR, required=True, enum=["csv", "xlsx", "pdf"], description="File format export selection.")],
    responses={200: OpenApiResponse(description="Binary streaming file download attachment named `grantloop_<report>_<timestamp>.<ext>`."), 400: RESP_400, 401: RESP_401, 403: RESP_403, 429: RESP_429, 500: RESP_500},
)
