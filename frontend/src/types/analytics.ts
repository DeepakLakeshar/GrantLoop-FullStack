import { Campaign, Donation, Notification, FundRelease } from "./entities";

export interface RecentCampaign {
  id: string;
  title: string;
  status: string;
  goal_amount: string;
  raised_amount: string;
  campaign_currency: string;
  creator_email: string;
  category_name: string;
  created_at: string;
}

export interface RecentDonation {
  id: string;
  campaign: string;
  campaign_title: string;
  donor: string;
  donor_email: string;
  settled_amount: string;
  settled_currency: string;
  status: string;
  created_at: string;
}

export interface RecentNotification {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
}

export interface RecentPayout {
  id: string;
  campaign: string;
  campaign_title: string;
  ngo: string;
  ngo_email: string;
  requested_amount: string;
  approved_amount: string | null;
  currency: string;
  status: string;
  created_at: string;
}

export interface AdminDashboardMetrics {
  total_users: number;
  total_ngos: number;
  verified_ngos: number;
  pending_ngo_verifications: number;

  total_campaigns: number;
  draft_campaigns: number;
  pending_campaigns: number;
  live_campaigns: number;
  completed_campaigns: number;
  rejected_campaigns: number;

  total_donations: number;
  successful_donations: number;
  pending_donations: number;
  failed_donations: number;
  refunded_donations: number;

  total_donation_amount: string;
  average_donation: string;
  largest_donation: string;

  total_beneficiaries: number;
  verified_beneficiaries: number;
  pending_beneficiaries: number;
  rejected_beneficiaries: number;

  total_payout_requests: number;
  pending_payouts: number;
  approved_payouts: number;
  completed_payouts: number;
  failed_payouts: number;
  cancelled_payouts: number;

  total_paid_amount: string;
  platform_balance: string;

  recent_campaigns: RecentCampaign[];
  recent_donations: RecentDonation[];
  recent_notifications: RecentNotification[];
  recent_payout_requests: RecentPayout[];
}
