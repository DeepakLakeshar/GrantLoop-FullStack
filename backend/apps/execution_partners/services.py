"""
Business logic for Execution Partners. Views/serializers must never
duplicate any of this — they call into these functions and translate the
result (or the exception) into an HTTP response, nothing more.
"""
from django.core.exceptions import PermissionDenied

from .models import ExecutionPartner

UPDATABLE_FIELDS = {"organization", "verification_status"}


# ---------------------------------------------------------------------------
# Authorization helpers — used both by these service functions and by
# permissions.py, so the "who can do this" rule is defined exactly once.
# ---------------------------------------------------------------------------

def is_owner(*, actor, partner: ExecutionPartner) -> bool:
    """True if `actor` is the user this ExecutionPartner record belongs to."""
    return bool(actor and actor.is_authenticated and actor.id == partner.user_id)


def can_manage_partner(*, actor, partner: ExecutionPartner) -> bool:
    """Admin can manage any partner record. A partner can manage their
    own (e.g. update their organization name) but not anyone else's, and
    never their own verification_status — that stays admin-only, enforced
    separately in update_partner()."""
    if not (actor and actor.is_authenticated):
        return False
    if actor.role == "admin":
        return True
    return is_owner(actor=actor, partner=partner)


def is_verified(partner: ExecutionPartner) -> bool:
    return partner.verification_status == "verified"


def _require_admin(actor) -> None:
    if not (actor and actor.is_authenticated and actor.role == "admin"):
        raise PermissionDenied("Only an admin may perform this action.")


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_partner(*, actor, user, organization: str = "") -> ExecutionPartner:
    """Only an admin provisions a new ExecutionPartner record — the
    account itself (User with role='execution_partner') already exists
    via registration; this is what turns that account into an active
    partner profile."""
    _require_admin(actor)
    if hasattr(user, "execution_partner_profile"):
        raise ValueError("This user already has an execution partner profile.")
    return ExecutionPartner.objects.create(user=user, organization=organization)


def update_partner(*, actor, partner: ExecutionPartner, **fields) -> ExecutionPartner:
    """The owning partner may update their own `organization`. Only an
    admin may change `verification_status` — a partner can't verify or
    unsuspend themselves."""
    unknown = set(fields) - UPDATABLE_FIELDS
    if unknown:
        raise ValueError(f"Cannot update unknown field(s): {unknown}")

    if "verification_status" in fields:
        _require_admin(actor)
    elif not can_manage_partner(actor=actor, partner=partner):
        raise PermissionDenied("You don't have permission to update this execution partner.")

    for name, value in fields.items():
        setattr(partner, name, value)
    partner.save(update_fields=list(fields.keys()))
    return partner


def archive_partner(*, actor, partner: ExecutionPartner) -> ExecutionPartner:
    """Archiving sets verification_status='suspended' — the frozen schema
    has no separate 'archived' state, and 'suspended' already carries the
    correct meaning (taken out of active service; history preserved via
    SET_NULL on Milestone.execution_partner)."""
    _require_admin(actor)
    partner.verification_status = "suspended"
    partner.save(update_fields=["verification_status"])
    return partner


# ---------------------------------------------------------------------------
# Retrieval helpers — for future APIs (a "my profile" endpoint, milestone
# assignment lookups, etc.) so callers never query the model directly.
# ---------------------------------------------------------------------------

def get_partner_for_user(user) -> ExecutionPartner | None:
    """Returns None rather than raising — "does this user have a partner
    profile yet" is a normal, expected question, not an error case."""
    if not (user and user.is_authenticated):
        return None
    return ExecutionPartner.objects.filter(user=user).first()


def get_partner_or_raise(*, actor, partner_id) -> ExecutionPartner:
    """Fetches a partner and confirms `actor` may view it. Read access is
    open to any authenticated user (frozen architecture — anonymous gets
    nothing, everyone logged in can read), so this only guards against a
    bad id, not against the requester's role."""
    try:
        return ExecutionPartner.objects.get(id=partner_id)
    except ExecutionPartner.DoesNotExist as exc:
        raise ValueError("Execution partner not found.") from exc


def list_verified_partners():
    """Helper for future assignment flows (e.g. an NGO picking a partner
    for a milestone) — only ever surface partners actually verified."""
    return ExecutionPartner.objects.filter(verification_status="verified")