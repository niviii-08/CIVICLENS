"""
CIVICLENS TN — Public Accountability & Procurement Explorer (Phase 11)

Comprehensive public accountability portal tracking:
1. Public Accountability Cases & 6-Stage Resolution Lifecycle
2. Public Procurement, Tenders, Contracts & Public Works
3. CAG State Audit Observations & Action Taken Reports (ATRs)
4. Right to Information (RTI) Transparency & SLA Compliance
5. Bitemporal Provenance & BNS 2023 Sec 356 Safeguards
"""
from __future__ import annotations
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import json
from datetime import datetime
import streamlit as st
import pandas as pd
from backend.database.session import SessionLocal
from backend.services.accountability_service import AccountabilityService
from backend.services.procurement_service import ProcurementService
from backend.services.cag_rti_service import CAGAndRTIService
from backend.services.evidence_graph_expansion_service import EvidenceGraphExpansionService
from backend.models.accountability import AccountabilityCase
from backend.models.procurement import Tender, ProcurementPublicWork
from backend.models.cag_rti import CAGReport, CAGAuditParagraph, RTIRequest, TNICSecondAppeal
from backend.models.provenance import GranularExtractionLineage, RightOfReplyRegistry, PublicCorrectionNotice


st.set_page_config(
    page_title="Public Accountability & Procurement - CIVICLENS TN",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚖️ Public Accountability & Procurement Explorer")
st.caption("Phase 11 — Evidence-Grounded Accountability, Statutory Oversight & Production Provenance")

# Guardrail Alert
st.info(
    "🔒 **Epistemic & Non-Causal Safeguard:** CIVICLENS TN displays official government gazettes, "
    "statutory audit observations, verified public tender records, and independent ground inspections. "
    "In compliance with BNS 2023 Section 356, the platform strictly presents objective administrative records "
    "without inferring personal culpability or assigning subjective labels."
)

db = SessionLocal()
try:
    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    proc_summary = ProcurementService.get_procurement_summary(db)
    cag_summary = CAGAndRTIService.get_cag_audit_summary(db)
    total_cases = db.query(AccountabilityCase).count()
    graph_cov = EvidenceGraphExpansionService.get_graph_coverage_metrics(db)

    with c1:
        st.metric("Accountability Cases", f"{total_cases} Tracked", "Active Lifecycle")
    with c2:
        st.metric("Tracked Works Value", f"₹{proc_summary.get('total_tender_value_cr', 0.0)} Cr", f"{proc_summary.get('completion_rate_pct', 0.0)}% Complete")
    with c3:
        st.metric("CAG Audit Findings", f"₹{cag_summary.get('total_monetary_implication_cr', 0.0)} Cr", f"{cag_summary.get('response_compliance_rate_pct', 0.0)}% ATR Rate")
    with c4:
        st.metric("Evidence Graph Connectivity", f"{graph_cov.get('connectivity_coverage_pct', 0.0)}%", f"{graph_cov.get('total_nodes', 0)} Nodes")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏛️ Accountability Cases",
        "🏗️ Procurement & Public Works",
        "📋 CAG Audit & ATR Follow-Through",
        "🔍 RTI Intelligence & SLAs",
        "🛡️ Provenance & Legal Safeguards",
    ])

    # --------------------------------------------------------------------------
    # TAB 1: Public Accountability Cases
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("Public Accountability Case Lifecycle")
        st.markdown(
            "Every detected anomaly or grievance breach is tracked across a 6-stage lifecycle: "
            "`Discovery` ➔ `Attribution` ➔ `Official Response` ➔ `Corrective Action` ➔ `Outcome Verification` ➔ `Dossier Export`."
        )

        cases = db.query(AccountabilityCase).all()
        if cases:
            case_map = {f"{c.case_id} — {c.title}": c.case_id for c in cases}
            selected_case_label = st.selectbox("Select an Accountability Case to Inspect:", list(case_map.keys()))
            selected_case_id = case_map[selected_case_label]

            dossier = AccountabilityService.generate_accountability_dossier(db, selected_case_id)

            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.write(f"**Domain:** {dossier['domain']}")
                st.write(f"**Trigger:** `{dossier['trigger_type']}`")
            with col_meta2:
                st.write(f"**Status:** `{dossier['status']}`")
                st.write(f"**Severity:** `{dossier['severity']}`")
            with col_meta3:
                st.write(f"**Financial Implication:** ₹{dossier.get('financial_implication_cr') or 'N/A'} Cr")
                st.write(f"**Provenance Hash:** `{dossier['provenance_hash'][:16]}...`")

            st.markdown("#### 1. Institutional Attribution")
            if dossier["institutional_attribution"]:
                attr_df = pd.DataFrame(dossier["institutional_attribution"])
                st.dataframe(attr_df, use_container_width=True)
            else:
                st.write("No institutional attribution recorded yet.")

            st.markdown("#### 2. Official Responses")
            if dossier["official_responses"]:
                resp_df = pd.DataFrame(dossier["official_responses"])
                st.dataframe(resp_df, use_container_width=True)
            else:
                st.write("No formal departmental response recorded yet.")

            st.markdown("#### 3. Corrective Actions")
            if dossier["corrective_actions"]:
                act_df = pd.DataFrame(dossier["corrective_actions"])
                st.dataframe(act_df, use_container_width=True)
            else:
                st.write("No corrective actions logged yet.")

            st.markdown("#### 4. Ground Outcome Verification")
            if dossier["ground_verifications"]:
                ver_df = pd.DataFrame(dossier["ground_verifications"])
                st.dataframe(ver_df, use_container_width=True)
            else:
                st.write("No independent ground outcome verifications recorded.")

            # Downloadable Dossier
            st.download_button(
                label="📥 Export Citation-Ready Accountability Dossier (JSON)",
                data=json.dumps(dossier, indent=2),
                file_name=f"{selected_case_id}_accountability_dossier.json",
                mime="application/json",
            )
        else:
            st.info("No accountability cases recorded in the database.")

    # --------------------------------------------------------------------------
    # TAB 2: Procurement & Works Intelligence
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("Public Procurement & Public Works Delivery")
        st.markdown("Tracking public funds from budget scheme sanction through tender bids to on-the-ground work orders.")

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            st.markdown("##### Published Tenders")
            tenders = db.query(Tender).all()
            if tenders:
                tender_data = [
                    {
                        "Tender ID": t.tender_id,
                        "Department": t.issuing_department,
                        "Title": t.title[:45] + "...",
                        "Estimate (₹ Cr)": t.estimated_cost_cr,
                        "Published": t.published_date.isoformat(),
                        "Status": t.status.value,
                    }
                    for t in tenders
                ]
                st.dataframe(pd.DataFrame(tender_data), use_container_width=True)
            else:
                st.write("No tenders recorded.")

        with col_w2:
            st.markdown("##### Public Works Execution")
            works = db.query(ProcurementPublicWork).all()
            if works:
                work_data = [
                    {
                        "Work ID": w.work_id,
                        "District": w.district,
                        "Budget (₹ Cr)": w.sanctioned_budget_cr,
                        "Spent (₹ Cr)": w.cumulative_expenditure_cr,
                        "Progress": f"{w.physical_progress_pct}%",
                        "Milestone": w.milestone_status.value,
                    }
                    for w in works
                ]
                st.dataframe(pd.DataFrame(work_data), use_container_width=True)
            else:
                st.write("No public works recorded.")

    # --------------------------------------------------------------------------
    # TAB 3: CAG Audit & ATR Follow-Through
    # --------------------------------------------------------------------------
    with tab3:
        st.subheader("Comptroller & Auditor General (CAG) Audit Observations")
        st.markdown("Monitoring constitutional audit findings, PAC legislative scrutiny, and departmental compliance.")

        paras = db.query(CAGAuditParagraph).all()
        if paras:
            para_data = [
                {
                    "Paragraph": p.paragraph_ref,
                    "Department": p.department_name,
                    "Heading": p.heading[:50] + "...",
                    "Impact (₹ Cr)": p.financial_implication_cr or 0.0,
                    "ATR Status": p.atr_status.value,
                    "PAC Status": p.pac_status.value,
                }
                for p in paras
            ]
            st.dataframe(pd.DataFrame(para_data), use_container_width=True)
        else:
            st.info("No CAG audit paragraphs recorded.")

    # --------------------------------------------------------------------------
    # TAB 4: RTI Intelligence & SLAs
    # --------------------------------------------------------------------------
    with tab4:
        st.subheader("Right to Information (RTI) Transparency & Statutory 30-Day SLA")
        st.markdown("Auditing institutional compliance with statutory RTI disclosure timelines under RTI Act 2005.")

        rtis = db.query(RTIRequest).all()
        if rtis:
            rti_data = [
                {
                    "Reg Number": r.registration_number,
                    "Authority": r.public_authority,
                    "Filed Date": r.filing_date.isoformat(),
                    "Decision": r.status.value,
                    "Turnaround (Days)": r.response.turnaround_days if r.response else "Pending",
                    "SLA Breached": r.response.statutory_sla_breached if r.response else False,
                }
                for r in rtis
            ]
            st.dataframe(pd.DataFrame(rti_data), use_container_width=True)
        else:
            st.info("No RTI applications recorded.")

    # --------------------------------------------------------------------------
    # TAB 5: Provenance & Legal Safeguards
    # --------------------------------------------------------------------------
    with tab5:
        st.subheader("Bitemporal Extraction Lineage & Legal Safeguards")
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.markdown("##### Sub-Document Extraction Lineage (Page / Table / Cell)")
            lineages = db.query(GranularExtractionLineage).all()
            if lineages:
                lin_data = [
                    {
                        "Target Record": f"{l.target_table}:{l.target_record_id}",
                        "Source Document": l.source_document_title[:35] + "...",
                        "Page": l.page_number,
                        "Table": l.table_index,
                        "Row": l.row_number,
                        "Verbatim Excerpt": l.extracted_verbatim_text[:40] + "...",
                    }
                    for l in lineages
                ]
                st.dataframe(pd.DataFrame(lin_data), use_container_width=True)
            else:
                st.write("No extraction lineages recorded.")

        with col_p2:
            st.markdown("##### Right of Reply Log (BNS 2023 Sec 356)")
            rors = db.query(RightOfReplyRegistry).all()
            if rors:
                ror_data = [
                    {
                        "Case Ref": r.reply_case_ref,
                        "Entity": r.entity_name,
                        "Status": r.status.value,
                        "Dispatched": r.notice_dispatched_at.strftime("%Y-%m-%d"),
                        "Rebuttal Summary": (r.rebuttal_statement[:35] + "...") if r.rebuttal_statement else "Pending",
                    }
                    for r in rors
                ]
                st.dataframe(pd.DataFrame(ror_data), use_container_width=True)
            else:
                st.write("No Right of Reply records logged.")

finally:
    db.close()
