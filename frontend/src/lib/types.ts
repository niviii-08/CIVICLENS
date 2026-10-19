export interface PoliticalPromise {
  id: string;
  party: string;
  text: string;
  original_text?: string;
  status: 'Fulfilled' | 'In-Progress' | 'Broken' | 'Stalled' | 'Under Review' | string;
  category: string;
  target?: string;
  budget_allocation?: string | number;
  scheme_matches_count?: number;
  evidence_count?: number;
  verification_status?: string;
  year?: number;
}

export interface BudgetRecord {
  id: string | number;
  demand_no?: string;
  department_name: string;
  scheme_name: string;
  budget_estimate: number;
  revised_estimate: number;
  actual_expenditure: number;
  financial_year: string;
  utilization_rate?: number;
}

export interface ClaimVerification {
  id: string;
  claim_text: string;
  claimant?: string;
  date_made?: string;
  verdict: 'Verified True' | 'Partially True' | 'Misleading' | 'Unsubstantiated' | 'False';
  confidence_score: number;
  atomic_propositions?: {
    id: string;
    statement: string;
    truth_value: boolean | string;
    source: string;
  }[];
  sources?: string[];
  explanation: string;
}

export interface CivicGrievance {
  id: string;
  category: string;
  district: string;
  description: string;
  status: 'Resolved' | 'Pending' | 'Escalated' | 'SLA Breached';
  filed_date: string;
  sla_days: number;
  elapsed_days: number;
  department: string;
}

export interface Representative {
  id: string;
  name: string;
  constituency: string;
  party: string;
  attendance_percentage: number;
  questions_raised: number;
  mlacds_allocated: number;
  mlacds_utilized: number;
  criminal_cases: number;
}

export interface PolicyEvaluation {
  id: string;
  policy_name: string;
  target_sector: string;
  launch_year: number;
  beneficiaries_count: string | number;
  allocated_funds_cr: number;
  re_allocation_cr: number;
  actual_spent_cr: number;
  outcome_summary: string;
  baseline_status: string;
  evidence_links: string[];
}

export interface SearchResultItem {
  id: string;
  title: string;
  type: 'Government Scheme' | 'Promise' | 'Representative' | 'Civic Issue' | 'Public Claim' | 'Department' | 'Policy Evaluation';
  description: string;
  dateOrDepartment?: string;
  href: string;
  badgeColor?: string;
}

export interface UnifiedSearchResult {
  id: string;
  type: string;
  type_label: string;
  title: string;
  description: string;
  date_or_period: string;
  department_or_entity: string;
  route: string;
  badge: string;
  evidence_available: boolean;
  score: number;
}

export interface UnifiedSearchResponse {
  query: string;
  selected_category: string;
  total: number;
  page: number;
  limit: number;
  categories: Record<string, number>;
  items: UnifiedSearchResult[];
}

export interface SourceDocument {
  id: string;
  title: string;
  issuing_org: string;
  publication_date?: string;
  reporting_period?: string;
  source_type: 'Official Gazette' | 'Budget Demand' | 'ECI Disclosure' | 'Statutory SLA' | 'Audit Report' | 'News Analysis' | string;
  is_official: boolean;
  relationship: string;
  url?: string;
  page_number?: number | string;
  available: boolean;
  notes?: string;
}

export interface RelatedRecord {
  id: string;
  type: 'scheme' | 'promise' | 'representative' | 'claim' | 'civic' | 'policy' | 'budget' | 'evidence';
  type_label: string;
  title: string;
  relationship_reason: string;
  href: string;
}

export interface DetailedFinancials {
  budget_estimate_cr?: number;
  revised_estimate_cr?: number;
  actual_expenditure_cr?: number;
  financial_year?: string;
  demand_no?: string;
  utilization_rate?: number;
  notes?: string;
}

export interface DetailedCivicRecord {
  id: string;
  category_key: 'scheme' | 'promise' | 'representative' | 'claim' | 'civic' | 'policy';
  category_label: string;
  title: string;
  title_vernacular?: string;
  summary: string;
  status: string;
  status_explanation: string;
  reporting_period?: string;
  responsible_entity: string;
  geographic_scope?: string;
  target_group?: string;
  evidence_summary: string;
  financials?: DetailedFinancials;
  sources: SourceDocument[];
  related_records: RelatedRecord[];
  methodology_explanation?: string;
  technical_details?: Record<string, any>;
  data_limitations?: string[];
  incomplete_fields?: string[];
  // Category specific optional data
  atomic_propositions?: {
    id: string;
    statement: string;
    truth_value: boolean | string;
    source: string;
  }[];
  sla_metrics?: {
    statutory_days: number;
    elapsed_days: number;
    is_breached: boolean;
    department_response?: string;
    verified_resolution?: string;
  };
  representative_metrics?: {
    constituency: string;
    party: string;
    attendance_pct?: number;
    questions_count?: number;
    mlacds_allocated_cr?: number;
    mlacds_utilized_cr?: number;
    mlacds_utilization_pct?: number;
    active_terms?: string[];
  };
}

