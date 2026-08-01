// Mirrors Architecture Freeze v1.0. Keep in sync with the Django models —
// do not add fields here that don't exist on the backend.

export type UserRole = "donor" | "ngo" | "institution" | "execution_partner" | "admin";

export interface User {
  id: string;
  username: string;
  role: UserRole;
}

export type CampaignStatus =
  | "draft"
  | "pending_verification"
  | "live"
  | "completed"
  | "rejected"
  | "archived";

export interface Category {
  id: string;
  name: string;
  slug: string;
}

export interface Campaign {
  id: string;
  title: string;
  description: string;
  goal_amount: number;
  raised_amount: number;
  campaign_currency: string; // ISO 4217
  status: CampaignStatus;
  category: Category | null;
  location_city: string;
  location_country: string; // ISO 3166-1 alpha-2
  start_date: string | null; // ISO date
  end_date: string | null; // ISO date, null = no fixed deadline
  funding_percentage: number;
  created_by: User;
  created_at: string;
  updated_at: string;
}

/** Computed client-side, mirrors Campaign.days_remaining on the backend.
 * Never stored — null means "no fixed deadline," rendered as "Ongoing,"
 * never as a fabricated number. */
export function getDaysRemaining(campaign: Pick<Campaign, "end_date">): number | null {
  if (!campaign.end_date) return null;
  const end = new Date(campaign.end_date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffMs = end.getTime() - today.getTime();
  return Math.max(Math.ceil(diffMs / (1000 * 60 * 60 * 24)), 0);
}

export type DonationStatus = "pending" | "success" | "failed" | "refunded";
export type PaymentGateway = "razorpay" | "stripe";

export interface Donation {
  id: string;
  donor: User | { id: null; username: "Anonymous Donor"; role: "donor" };
  campaign: string; // campaign id
  original_amount: number;
  original_currency: string;
  settled_amount: number;
  settled_currency: string;
  is_anonymous: boolean;
  status: DonationStatus;
  timestamp: string;
  // Nullable — populated asynchronously after status='success'. A null
  // value means "still generating," not "no receipt exists."
  receipt_url: string | null;
}

export type BeneficiaryVerificationStatus = "pending" | "verified" | "rejected";

export interface Beneficiary {
  id: string;
  campaign: string;
  name: string;
  verification_status: BeneficiaryVerificationStatus;
  contact_email: string;
  contact_phone: string;
  // Deliberately a reference to the payment gateway's own Connect/Route
  // beneficiary object — never a raw bank account number or IFSC code.
  // Keeps GrantLoop non-custodial (ADR-004) and out of raw-bank-data
  // handling entirely. See Client Requirements Reconciliation v1.1,
  // section 12, item 2.
  payout_account_reference: string | null;
}

export type VerificationStatus = "pending" | "approved" | "rejected" | "more_info_requested";

export interface Verification {
  id: string;
  campaign: string;
  verified_by: User;
  status: VerificationStatus;
  notes: string;
  created_at: string;
}

export interface TransparencyLogEntry {
  id: string;
  campaign: string;
  action: string;
  timestamp: string;
}

export type ExecutionPartnerStatus = "pending" | "verified" | "suspended";

export interface ExecutionPartner {
  id: string;
  user: User;
  organization: string;
  verification_status: ExecutionPartnerStatus;
}

export type MilestoneStatus = "pending" | "in_progress" | "completed";

export interface Milestone {
  id: string;
  campaign: string;
  execution_partner: ExecutionPartner | null;
  title: string;
  description: string;
  target_amount: number;
  released_amount: number; // derived sum of released FundRelease rows
  status: MilestoneStatus;
  deadline: string | null;
  completed_at: string | null;
}

export interface FundAllocation {
  id: string;
  campaign: string;
  beneficiary_percentage: number;
  execution_percentage: number;
  platform_percentage: number;
}

export type CampaignUpdateType = "progress" | "fund_usage" | "closure_report";

export interface CampaignUpdate {
  id: string;
  campaign: string;
  milestone: string | null;
  posted_by: User;
  update_type: CampaignUpdateType;
  content: string;
  image_url: string;
  created_at: string;
}

export type FundReleaseStatus = "pending" | "approved" | "released" | "rejected";

export interface FundReleaseApproval {
  id: string;
  fund_release: string;
  approver: User;
  approver_role: "institution" | "admin";
  decision: "approved" | "rejected";
  notes: string;
  decided_at: string;
}

export interface FundRelease {
  id: string;
  milestone: string;
  amount: number;
  status: FundReleaseStatus;
  initiated_by: User;
  gateway_reference: string | null;
  released_at: string | null;
  created_at: string;
  approvals: FundReleaseApproval[];
}

export type DocumentType =
  | "photo"
  | "invoice"
  | "certificate"
  | "completion_report"
  | "inspection_report"
  | string; // deliberately open — new types shouldn't require a frontend change

export type DocumentStatus = "pending" | "verified" | "rejected";

export interface GrantLoopDocument {
  id: string;
  campaign: string | null;
  milestone: string | null;
  verification: string | null;
  ngo: string | null;
  beneficiary: string | null;
  campaign_update: string | null;
  document_type: DocumentType;
  file_url: string;
  uploaded_by: User;
  status: DocumentStatus;
  verified_by: User | null;
  uploaded_at: string;
}

// Admin-only — never rendered in any donor/public-facing view
export interface AuditEvent {
  id: string;
  actor: User | null;
  action: string;
  category:
    | "user_management"
    | "permissions"
    | "refunds"
    | "admin"
    | "verification"
    | "fund_release"
    | "system";
  target_type: string;
  target_id: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export type NotificationChannel = "email" | "in_app" | "sms" | "web_push" | "whatsapp";

export interface Notification {
  id: string;
  event_type: string;
  channel: NotificationChannel;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
  related_object_type: string | null;
  related_object_id: string | null;
}

// --- Added in Client Requirements Reconciliation v1.1 ---

/** Mirrors ExecutionPartner's existing shape exactly — same pattern,
 * not a new design language. */
export interface NGOProfile {
  id: string;
  user: User;
  organization_name: string;
  description: string;
  logo_url: string | null;
  website_url: string | null;
}

export type FraudReportStatus = "open" | "reviewing" | "dismissed" | "confirmed";

export interface FraudReport {
  id: string;
  campaign: string;
  reported_by: User | null; // null = system-generated flag
  reason: string;
  status: FraudReportStatus;
  reviewed_by: User | null;
  created_at: string;
  resolved_at: string | null;
}

export type ReportType = "donor_tax_receipt" | "ngo_fund_usage" | "admin_platform";
export type ReportExportStatus = "pending" | "ready" | "failed";

export interface ReportExport {
  id: string;
  requested_by: User;
  report_type: ReportType;
  status: ReportExportStatus;
  file_url: string | null;
  created_at: string;
}
