from django.core.exceptions import PermissionDenied, ValidationError

from .models import Document

SCOPE_FIELDS = ["campaign", "milestone", "verification", "ngo", "beneficiary", "campaign_update"]


def _owning_campaign(fields: dict):
    """Resolve 'the campaign this document belongs to' regardless of
    which of the six scope fields was actually set, so a single
    permission rule can apply uniformly."""
    if fields.get("campaign"):
        return fields["campaign"]
    if fields.get("milestone"):
        return fields["milestone"].campaign
    if fields.get("verification"):
        return fields["verification"].campaign
    if fields.get("beneficiary"):
        return fields["beneficiary"].campaign
    if fields.get("campaign_update"):
        return fields["campaign_update"].campaign
    return None  # ngo-scoped org-level document — no campaign to check


def _can_upload(*, fields: dict, actor) -> bool:
    if actor.role == "admin":
        return True
    campaign = _owning_campaign(fields)
    if fields.get("ngo"):
        # Org-level document — only the NGO themself (or admin) may
        # upload to their own profile.
        return actor.id == fields["ngo"].id
    if campaign is None:
        return False
    if actor.role == "institution":
        return True
    return actor.role == "ngo" and campaign.created_by_id == actor.id


def validate_single_scope(fields: dict) -> None:
    set_scopes = [name for name in SCOPE_FIELDS if fields.get(name)]
    if len(set_scopes) != 1:
        raise ValidationError(
            f"Exactly one of {SCOPE_FIELDS} must be set (got {set_scopes or 'none'})."
        )


def upload_document(*, actor, file, document_type: str, **scope_fields) -> Document:
    validate_single_scope(scope_fields)
    if not _can_upload(fields=scope_fields, actor=actor):
        raise PermissionDenied("You don't have permission to upload a document to this scope.")

    return Document.objects.create(
        uploaded_by=actor, file=file, document_type=document_type, **scope_fields
    )


def review_document(*, document: Document, actor, new_status: str) -> Document:
    if actor.role not in ("institution", "admin"):
        raise PermissionDenied("Only an institution or admin may review documents.")
    if new_status not in ("verified", "rejected"):
        raise ValueError("new_status must be 'verified' or 'rejected'.")

    document.status = new_status
    document.verified_by = actor
    document.save(update_fields=["status", "verified_by"])
    return document


def delete_document(*, document: Document, actor) -> None:
    """Deletion only allowed before review — once verified/rejected, the
    document is part of the audit trail and should never disappear,
    consistent with why this table uses PROTECT everywhere it can."""
    if actor.role != "admin" and document.uploaded_by_id != actor.id:
        raise PermissionDenied("You don't have permission to delete this document.")
    if document.status != "pending":
        raise PermissionDenied("A reviewed document cannot be deleted — it's part of the audit trail.")
    document.delete()
