import type {
  Campaign,
  Category,
  Beneficiary,
  Milestone,
  FundAllocation,
  CampaignUpdate,
  TransparencyLogEntry,
  GrantLoopDocument,
  User,
  ExecutionPartner,
  Verification,
  FundRelease,
} from "@/types/entities";

// Realistic mock data matching the corrected schema exactly (Category,
// location, and date fields are real now, not placeholders). This module
// is the only thing that changes when real API calls replace it — hooks
// and components never import from here directly.

export const MOCK_CATEGORIES: Category[] = [
  { id: "cat-water", name: "Clean Water", slug: "clean-water" },
  { id: "cat-education", name: "Education", slug: "education" },
  { id: "cat-health", name: "Healthcare", slug: "healthcare" },
  { id: "cat-climate", name: "Climate Action", slug: "climate-action" },
  { id: "cat-disaster", name: "Disaster Relief", slug: "disaster-relief" },
];

const NGO_USER: User = { id: "u-waterhelp", username: "WaterHelp International", role: "ngo" };
const NGO_USER_2: User = { id: "u-globaledu", username: "Global Education Initiative", role: "ngo" };
export const INSTITUTION_USER: User = { id: "u-globaltrust", username: "Global Trust Audit Corp", role: "institution" };

const EXECUTION_PARTNER: ExecutionPartner = {
  id: "ep-ecogrid",
  user: { id: "u-ecogrid", username: "EcoGrid Solutions", role: "execution_partner" },
  organization: "EcoGrid Solutions Ltd",
  verification_status: "verified",
};

export const MOCK_CAMPAIGNS: Campaign[] = [
  {
    id: "c1",
    title: "Clean Water Initiative: Turkana Basin",
    description:
      "The Turkana Basin faces a unique hydrological challenge: abundant groundwater that is too saline for human consumption. This project installs three modular, solar-powered desalination units serving 45,000 residents.\n\nWithout intervention, families walk over 8km daily for safe water, and waterborne illness rates remain high across the region.\n\nOnce complete, the units provide a permanent 20-year water source, with four local technicians trained for ongoing maintenance.",
    goal_amount: 120000,
    raised_amount: 84200,
    campaign_currency: "USD",
    status: "live",
    category: MOCK_CATEGORIES[0],
    location_city: "Turkana",
    location_country: "KE",
    start_date: "2026-01-15",
    end_date: "2026-09-30",
    funding_percentage: 70.2,
    created_by: NGO_USER,
    created_at: "2026-01-10T09:00:00Z",
    updated_at: "2026-06-12T10:22:00Z",
  },
  {
    id: "c2",
    title: "Rural Digital Literacy Program",
    description:
      "Equipping 12 rural schools with solar-powered tablets and offline-first learning software, closing the digital divide for 3,000 students who currently have no access to computing devices.",
    goal_amount: 45000,
    raised_amount: 12500,
    campaign_currency: "USD",
    status: "live",
    category: MOCK_CATEGORIES[1],
    location_city: "Cusco",
    location_country: "PE",
    start_date: "2026-03-01",
    end_date: null,
    funding_percentage: 27.8,
    created_by: NGO_USER_2,
    created_at: "2026-02-20T09:00:00Z",
    updated_at: "2026-06-01T09:00:00Z",
  },
  {
    id: "c3",
    title: "Community Health Outreach: Naivasha",
    description:
      "Mobile health clinics providing prenatal care, vaccinations, and basic diagnostics to 8 underserved communities with no permanent medical facility.",
    goal_amount: 60000,
    raised_amount: 60000,
    campaign_currency: "USD",
    status: "completed",
    category: MOCK_CATEGORIES[2],
    location_city: "Naivasha",
    location_country: "KE",
    start_date: "2025-09-01",
    end_date: "2026-01-31",
    funding_percentage: 100,
    created_by: NGO_USER,
    created_at: "2025-08-15T09:00:00Z",
    updated_at: "2026-01-31T18:00:00Z",
  },
  {
    id: "c4",
    title: "Coastal Mangrove Restoration: Sundarbans Delta",
    description:
      "Replanting 40 hectares of mangrove forest to rebuild a natural storm barrier for 6 delta communities, using a community-employment planting model.",
    goal_amount: 38000,
    raised_amount: 0,
    campaign_currency: "USD",
    status: "pending_verification",
    category: MOCK_CATEGORIES[3],
    location_city: "Khulna",
    location_country: "BD",
    start_date: "2026-07-01",
    end_date: "2027-01-31",
    funding_percentage: 0,
    created_by: NGO_USER_2,
    created_at: "2026-06-28T11:00:00Z",
    updated_at: "2026-06-28T11:00:00Z",
  },
];

export const MOCK_BENEFICIARIES: Record<string, Beneficiary[]> = {
  c1: [
    {
      id: "b1",
      campaign: "c1",
      name: "Turkana Basin Community",
      verification_status: "verified",
      contact_email: "liaison@turkanawater.org",
      contact_phone: "+254700111222",
      payout_account_reference: "acct_razorpay_route_9928",
    },
  ],
  c2: [
    {
      id: "b2",
      campaign: "c2",
      name: "12 partner rural schools",
      verification_status: "verified",
      contact_email: "admin@ruralschools-ke.org",
      contact_phone: "+254700333444",
      payout_account_reference: "acct_razorpay_route_1187",
    },
  ],
  c3: [
    {
      id: "b3",
      campaign: "c3",
      name: "8 communities, Naivasha region",
      verification_status: "pending",
      contact_email: "contact@naivashacoalition.org",
      contact_phone: "+254700555666",
      payout_account_reference: null,
    },
  ],
};

export const MOCK_MILESTONES: Record<string, Milestone[]> = {
  c1: [
    {
      id: "m1",
      campaign: "c1",
      execution_partner: EXECUTION_PARTNER,
      title: "Site survey & engineering approval",
      description: "Topographic mapping and structural integrity verification.",
      target_amount: 15000,
      released_amount: 15000,
      status: "completed",
      deadline: "2026-03-12",
      completed_at: "2026-03-10T00:00:00Z",
    },
    {
      id: "m2",
      campaign: "c1",
      execution_partner: EXECUTION_PARTNER,
      title: "Equipment procurement",
      description: "Solar modules and industrial inverters secured.",
      target_amount: 45000,
      released_amount: 45000,
      status: "completed",
      deadline: "2026-04-05",
      completed_at: "2026-04-05T00:00:00Z",
    },
    {
      id: "m3",
      campaign: "c1",
      execution_partner: EXECUTION_PARTNER,
      title: "Desalination unit installation",
      description: "Mounting and commissioning of all three units.",
      target_amount: 45000,
      released_amount: 24000,
      status: "in_progress",
      deadline: "2026-08-20",
      completed_at: null,
    },
    {
      id: "m4",
      campaign: "c1",
      execution_partner: EXECUTION_PARTNER,
      title: "Commissioning & water quality testing",
      description: "Independent lab testing before handover.",
      target_amount: 15000,
      released_amount: 0,
      status: "pending",
      deadline: "2026-09-25",
      completed_at: null,
    },
  ],
};

export const MOCK_FUND_ALLOCATIONS: Record<string, FundAllocation> = {
  c1: { id: "fa1", campaign: "c1", beneficiary_percentage: 80, execution_percentage: 15, platform_percentage: 5 },
  c2: { id: "fa2", campaign: "c2", beneficiary_percentage: 85, execution_percentage: 10, platform_percentage: 5 },
  c3: { id: "fa3", campaign: "c3", beneficiary_percentage: 78, execution_percentage: 18, platform_percentage: 4 },
};

export const MOCK_CAMPAIGN_UPDATES: Record<string, CampaignUpdate[]> = {
  c1: [
    {
      id: "cu1",
      campaign: "c1",
      milestone: "m3",
      posted_by: EXECUTION_PARTNER.user,
      update_type: "progress",
      content: "All 48 panels mounted and wired to the main inverter hub. Voltage output matches proposal specs.",
      image_url: "",
      created_at: "2026-06-10T16:00:00Z",
    },
    {
      id: "cu2",
      campaign: "c1",
      milestone: "m2",
      posted_by: NGO_USER,
      update_type: "fund_usage",
      content: "Equipment cleared customs and arrived on-site two weeks ahead of schedule.",
      image_url: "",
      created_at: "2026-04-08T12:00:00Z",
    },
  ],
};

export const MOCK_TRANSPARENCY_LOGS: Record<string, TransparencyLogEntry[]> = {
  c1: [
    { id: "t1", campaign: "c1", action: "Campaign submitted", timestamp: "2026-01-10T09:00:00Z" },
    { id: "t2", campaign: "c1", action: "Verification approved by Global Trust Audit Corp", timestamp: "2026-01-15T14:30:00Z" },
    { id: "t3", campaign: "c1", action: "Campaign went live", timestamp: "2026-01-16T00:00:00Z" },
    { id: "t4", campaign: "c1", action: "Milestone completed: Site survey & engineering approval", timestamp: "2026-03-10T00:00:00Z" },
    { id: "t5", campaign: "c1", action: "Fund release approved: $15,000", timestamp: "2026-03-11T09:00:00Z" },
    { id: "t6", campaign: "c1", action: "Milestone completed: Equipment procurement", timestamp: "2026-04-05T00:00:00Z" },
    { id: "t7", campaign: "c1", action: "Donation received: $500", timestamp: "2026-06-12T10:22:00Z" },
  ],
};

export const MOCK_DOCUMENTS: Record<string, GrantLoopDocument[]> = {
  c1: [
    {
      id: "d1",
      campaign: "c1",
      milestone: null,
      verification: null,
      ngo: null,
      beneficiary: null,
      campaign_update: null,
      document_type: "photo",
      file_url: "https://images.unsplash.com/photo-1541800883812-a352b7cc50c9?w=1200",
      uploaded_by: NGO_USER,
      status: "verified",
      verified_by: INSTITUTION_USER,
      uploaded_at: "2026-01-10T09:00:00Z",
    },
    {
      id: "d2",
      campaign: "c1",
      milestone: "m2",
      verification: null,
      ngo: null,
      beneficiary: null,
      campaign_update: null,
      document_type: "invoice",
      file_url: "https://example.com/documents/invoice-882.pdf",
      uploaded_by: EXECUTION_PARTNER.user,
      status: "verified",
      verified_by: INSTITUTION_USER,
      uploaded_at: "2026-04-05T10:00:00Z",
    },
    {
      id: "d3",
      campaign: "c1",
      milestone: "m3",
      verification: null,
      ngo: null,
      beneficiary: null,
      campaign_update: null,
      document_type: "completion_report",
      file_url: "https://example.com/documents/completion-report-m3.pdf",
      uploaded_by: EXECUTION_PARTNER.user,
      status: "pending",
      verified_by: null,
      uploaded_at: "2026-06-10T16:05:00Z",
    },
  ],
};

export function getDonorCount(campaignId: string): number {
  // Computed aggregate — mirrors how funding_percentage is already a
  // computed API field rather than a stored one. Real implementation:
  // Donation.objects.filter(campaign=campaign).values("donor").distinct().count()
  const counts: Record<string, number> = { c1: 1240, c2: 340, c3: 2890 };
  return counts[campaignId] ?? 0;
}

// --- Institution Dashboard mock data ---

export const MOCK_VERIFICATIONS: Verification[] = [
  {
    id: "v1",
    campaign: "c1",
    verified_by: INSTITUTION_USER,
    status: "approved",
    notes: "Financial solvency and site survey confirmed.",
    created_at: "2026-01-12T10:00:00Z",
  },
  {
    id: "v2",
    campaign: "c3",
    verified_by: INSTITUTION_USER,
    status: "approved",
    notes: "Prior track record verified; approved on expedited review.",
    created_at: "2025-08-18T10:00:00Z",
  },
  {
    id: "v3",
    campaign: "c4",
    verified_by: INSTITUTION_USER,
    status: "pending",
    notes: "",
    created_at: "2026-06-28T11:05:00Z",
  },
];

export const MOCK_FUND_RELEASES: FundRelease[] = [
  {
    id: "fr1",
    milestone: "m3",
    amount: 24000,
    status: "released",
    initiated_by: EXECUTION_PARTNER.user,
    gateway_reference: "route_txn_88291",
    released_at: "2026-06-11T09:00:00Z",
    created_at: "2026-06-10T17:00:00Z",
    approvals: [
      {
        id: "fra1",
        fund_release: "fr1",
        approver: INSTITUTION_USER,
        approver_role: "institution",
        decision: "approved",
        notes: "Evidence matches milestone scope.",
        decided_at: "2026-06-11T08:30:00Z",
      },
    ],
  },
  {
    id: "fr2",
    milestone: "m4",
    amount: 15000,
    status: "pending",
    initiated_by: EXECUTION_PARTNER.user,
    gateway_reference: null,
    released_at: null,
    created_at: "2026-06-27T14:00:00Z",
    approvals: [],
  },
];
