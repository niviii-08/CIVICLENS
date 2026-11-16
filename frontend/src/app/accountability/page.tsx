'use client';

import React, { useState } from 'react';
import {
  FileCheck2,
  Building2,
  AlertCircle,
  FileText,
  Shield,
  CheckCircle2,
  Clock,
  ExternalLink,
  ChevronRight,
  Filter,
  Users,
  Search,
  Download,
  Database,
  Cpu,
  Layers,
  Sparkles,
} from 'lucide-react';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';

type PortalPersona = 'all' | 'citizen' | 'journalist' | 'researcher' | 'admin';

export default function AccountabilityPage() {
  const [activePersona, setActivePersona] = useState<PortalPersona>('all');
  const [activeTab, setActiveTab] = useState<'cases' | 'procurement' | 'cag' | 'rti' | 'assurances' | 'safeguards'>('cases');
  const [selectedDistrict, setSelectedDistrict] = useState<string>('All Districts');

  const cases = [
    {
      id: "CASE-TN-2024-KMUT-01",
      title: "KMUT Beneficiary Exclusion & Appellate Turnaround Verification",
      title_ta: "கலைஞர் மகளிர் உரிமைத் திட்ட விண்ணப்ப மேல்முறையீட்டு ஆய்வு",
      domain: "Social Welfare & DBT",
      district: "Statewide",
      trigger: "Grievance Appeal Window Lag",
      status: "INDEPENDENTLY_VERIFIED",
      statusColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
      implication: "₹148.20 Cr",
      department: "Special Programme Implementation Dept (SPID)",
      action: "Special VAO grievance camps conducted; 1.12L applicants onboarded",
      verification: "State Planning Commission third-party audit confirmed resolution",
    },
    {
      id: "CASE-TN-2024-GCC-SWD-02",
      title: "GCC Kosasthalaiyar Basin SWD Package 4 Gradient Rectification",
      title_ta: "சென்னை மாநகராட்சி கொசஸ்தலையாறு வடிநில மழைநீர் வடிகால் பணி",
      domain: "Municipal Administration & Floods",
      district: "Chennai",
      trigger: "Procurement Defect Notice",
      status: "CORRECTIVE_ACTION_PENDING",
      statusColor: "text-amber-400 bg-amber-500/10 border-amber-500/30",
      implication: "₹48.50 Cr",
      department: "Greater Chennai Corporation (Special Projects)",
      action: "Rectification of micro-level gradient defects in 3.2 km section",
      verification: "Independent physical inspection scheduled post-remedial work",
    },
    {
      id: "CASE-TN-2024-SED-ICT-03",
      title: "Government High Schools ICT Lab Broadband Connectivity",
      title_ta: "அரசு மேல்நிலைப் பள்ளிகள் கணினி ஆய்வக இணைய வசதி",
      domain: "School Education",
      district: "Madurai",
      trigger: "CAG Audit Paragraph 3.4.2",
      status: "RESPONSE_RECEIVED",
      statusColor: "text-blue-400 bg-blue-500/10 border-blue-500/30",
      implication: "₹42.50 Cr",
      department: "School Education Department",
      action: "TANFINET fiber optic commissioning expedited under PAC direction",
      verification: "Quarterly ATR submission due before Assembly Committee",
    },
  ];

  const tenders = [
    {
      id: "TNTENDER-2024-GCC-SWD-042",
      title: "Construction of Integrated SWD in Kosasthalaiyar Basin Pkg 4",
      department: "Municipal Admin & Water Supply (GCC)",
      estimate: "₹52.40 Cr",
      award: "₹49.80 Cr (-4.96%)",
      contractor: "Sri Balaji Infrastructure Projects Ltd",
      workId: "WORK-GCC-SWD-KOS-2024",
      district: "Chennai",
      physicalProgress: "78.5%",
      disbursed: "₹38.60 Cr",
      inspectionStatus: "PASSED_CONFORMANT",
    },
    {
      id: "TNTENDER-2024-WRO-CAUVERY-08",
      title: "Desilting and Silt Disposal in Vennar & Cauvery Delta Channels",
      department: "Water Resources Department (WRD)",
      estimate: "₹18.50 Cr",
      award: "₹17.90 Cr (-3.24%)",
      contractor: "Delta Earthmovers & Engineering Ltd",
      workId: "WORK-WRD-CAUV-2024",
      district: "Thanjavur",
      physicalProgress: "100%",
      disbursed: "₹17.90 Cr",
      inspectionStatus: "PASSED_CONFORMANT",
    },
  ];

  const cagParas = [
    {
      ref: "Para 3.4.2",
      report: "CAG Report on General & Social Sector (FY 2022-23)",
      dept: "School Education Department",
      heading: "Unutilized ICT Infrastructure & Hardware in 624 Schools",
      amount: "₹42.50 Cr",
      atrStatus: "Reply Submitted / Under PAC Review",
      pacAction: "Directed 90-day physical compliance report tabling",
    },
    {
      ref: "Para 2.1.4",
      report: "CAG Report on State Finances (FY 2022-23)",
      dept: "Finance Department (Treasuries)",
      heading: "Persistent Unreconciled Inter-Departmental Balances",
      amount: "₹35.20 Cr",
      atrStatus: "Accepted Satisfactory / PAC Dropped",
      pacAction: "Reconciled with AG (A&E) Tamil Nadu ledger",
    },
  ];

  const rtis = [
    {
      regNo: "RTI/GOTN/SWD/2024/00812",
      authority: "Social Welfare and Women Empowerment",
      subject: "Pudhumai Penn Scheme district-wise sanction and rejection figures",
      turnaround: "22 Days",
      slaStatus: "Compliant (<30 Days)",
      slaColor: "text-emerald-400 bg-emerald-500/10",
      decision: "Full Disclosure",
    },
    {
      regNo: "RTI/GOTN/GCC/2024/01244",
      authority: "Greater Chennai Corporation (Storm Water Drains)",
      subject: "Package 4 contractor payment vouchers and quality test reports",
      turnaround: "43 Days",
      slaStatus: "Breached (>30 Days)",
      slaColor: "text-rose-400 bg-rose-500/10",
      decision: "Partial Disclosure / TNIC Second Appeal Filed",
    },
  ];

  const assurances = [
    {
      code: "ASSUR-TNLA-16-2023-084",
      mla: "Dr. T. Velmurugan (Panruti)",
      minister: "Minister for School Education",
      dept: "School Education Department",
      date: "2023-04-12",
      statement: "Broadband optical fiber connectivity through TANFINET will be commissioned across all 624 remaining secondary schools before December 2023.",
      status: "IMPLEMENTATION_IN_PROGRESS",
      statusColor: "text-blue-400 bg-blue-500/10 border-blue-500/30",
    },
  ];

  const filteredCases = selectedDistrict === 'All Districts'
    ? cases
    : cases.filter(c => c.district === selectedDistrict || c.district === 'Statewide');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 space-y-8">
      {/* Page Header */}
      <PageHeader
        title="Public Accountability & Procurement Intelligence"
        description="Phase 11 Master System — Tracing Governance Anomaly ➔ Institutional Attribution ➔ Official Response ➔ Corrective Action ➔ Independent Ground Verification"
        badge={
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
            Phase 11 Production Complete
          </span>
        }
      />

      {/* 4 Tailored User Personas Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 ml-2">
            <Users className="w-3.5 h-3.5 text-blue-400" /> UX Viewport:
          </span>
          {[
            { key: 'all', label: '🌐 All Modules' },
            { key: 'citizen', label: '👤 Citizen Portal' },
            { key: 'journalist', label: '📰 Journalist Workbench' },
            { key: 'researcher', label: '🔬 Researcher Portal' },
            { key: 'admin', label: '⚙️ Admin Console' },
          ].map((persona) => (
            <button
              key={persona.key}
              onClick={() => setActivePersona(persona.key as PortalPersona)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activePersona === persona.key
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              {persona.label}
            </button>
          ))}
        </div>

        {/* District Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">District Filter:</span>
          <select
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="All Districts">All Districts (Statewide)</option>
            <option value="Chennai">Chennai</option>
            <option value="Madurai">Madurai</option>
            <option value="Thanjavur">Thanjavur</option>
            <option value="Coimbatore">Coimbatore</option>
            <option value="Salem">Salem</option>
          </select>
        </div>
      </div>

      {/* Persona Custom Callouts */}
      {activePersona === 'citizen' && (
        <div className="bg-gradient-to-r from-blue-900/30 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-blue-300 font-bold text-sm">
            <span>👤 பொது மக்கள் சேவை முகப்பு (Citizen Hyperlocal Explorer)</span>
          </div>
          <p className="text-xs text-slate-300">
            உங்கள் மாவட்டத்தின் நலத்திட்டங்கள், குடிமக்கள் மனுக்களின் நிலை, மற்றும் நடைபெறும் பொதுப்பணிகளின் முன்னேற்றத்தை எளிமையாக அறியலாம். ஏதேனும் முரண்பாடு இருந்தால் ஆதாரங்களுடன் மேல்முறையீடு செய்யலாம்.
          </p>
        </div>
      )}

      {activePersona === 'journalist' && (
        <div className="bg-gradient-to-r from-amber-900/30 to-orange-900/20 border border-amber-500/30 rounded-2xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-amber-300 font-bold text-sm">
            <span>📰 Investigative Journalist Workbench</span>
          </div>
          <p className="text-xs text-slate-300">
            Detect cross-source discrepancies between Assembly budget allocations, published tenders, contractor disbursements, and ground delivery. Export citation-ready dossiers with cryptographic provenance hashes.
          </p>
        </div>
      )}

      {activePersona === 'researcher' && (
        <div className="bg-gradient-to-r from-emerald-900/30 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-emerald-300 font-bold text-sm">
            <span>🔬 Academic Researcher & Policy Analyst Portal</span>
          </div>
          <p className="text-xs text-slate-300">
            Access bitemporal valid-time data series, sub-document cell extraction lineages, ML Model cards with drift thresholds, and standardized OpenAPI schemas with zero causal leaps.
          </p>
        </div>
      )}

      {activePersona === 'admin' && (
        <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/20 border border-purple-500/30 rounded-2xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-purple-300 font-bold text-sm">
            <span>⚙️ Platform Administrator & Data Governance Console</span>
          </div>
          <p className="text-xs text-slate-300">
            Monitor ingestion pipeline health, automated DPDPA 2023 privacy redactions, Right of Reply dispatch queues under BNS 2023 Sec 356, and audit logs.
          </p>
        </div>
      )}

      {/* Epistemic Alert */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex items-start gap-3 text-xs text-slate-300">
        <Shield className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-white">BNS 2023 Sec 356 & Epistemic Safeguards: </span>
          CIVICLENS TN tracks objective administrative documents, statutory audit findings, and verified physical inspection records. The platform enforces strict non-causal discipline and never assigns personal corruption or criminal guilt without an explicit statutory court decree.
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Accountability Cases"
          value={`${filteredCases.length} Active`}
          change="6-Stage Resolution"
          changeType="positive"
          accentColor="blue"
          icon={<FileCheck2 className="w-5 h-5" />}
        />
        <MetricCard
          title="Tracked Works Value"
          value="₹70.90 Cr"
          change="89.2% Executed"
          changeType="positive"
          accentColor="emerald"
          icon={<Building2 className="w-5 h-5" />}
        />
        <MetricCard
          title="CAG Audit Impact"
          value="₹77.70 Cr"
          change="100% ATR Tracked"
          changeType="positive"
          accentColor="amber"
          icon={<AlertCircle className="w-5 h-5" />}
        />
        <MetricCard
          title="RTI 30-Day SLA"
          value="91.4%"
          change="Statutory Timeliness"
          changeType="positive"
          accentColor="cyan"
          icon={<FileText className="w-5 h-5" />}
        />
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-slate-800 space-x-2">
        {[
          { key: 'cases', label: '🏛️ Accountability Cases' },
          { key: 'procurement', label: '🏗️ Procurement & Works' },
          { key: 'cag', label: '📋 CAG Audit Follow-Through' },
          { key: 'rti', label: '🔍 RTI Intelligence & SLAs' },
          { key: 'assurances', label: '⚖️ Ministerial Assurances' },
          { key: 'safeguards', label: '🛡️ Provenance & Safeguards' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-4 py-2.5 text-xs font-bold transition-all border-b-2 ${
              activeTab === tab.key
                ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Accountability Cases */}
      {activeTab === 'cases' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Tracked Governance Issues & Resolution Workflows
            </h3>
            <span className="text-xs text-slate-400">Independent outcome verification prevents false closures</span>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {filteredCases.map((c) => (
              <div
                key={c.id}
                className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 hover:border-slate-700 transition-all space-y-4"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-blue-400 font-bold">{c.id}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${c.statusColor}`}>
                        {c.status}
                      </span>
                    </div>
                    <h4 className="text-base font-bold text-white mt-1">{c.title}</h4>
                    <p className="text-xs text-slate-400 font-medium">{c.title_ta}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-400">Financial Implication</span>
                    <p className="text-base font-extrabold text-amber-400">{c.implication}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs bg-slate-950/60 rounded-xl p-3 border border-slate-800/60">
                  <div>
                    <span className="text-slate-400 block font-medium">Institutional Attribution</span>
                    <span className="text-slate-200 font-semibold">{c.department}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Sanctioned Corrective Action</span>
                    <span className="text-slate-200">{c.action}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Ground Outcome Verification</span>
                    <span className="text-emerald-400 font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> {c.verification}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Procurement & Works */}
      {activeTab === 'procurement' && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Public Tenders, Contractor Awards & Work Orders
          </h3>
          <div className="overflow-x-auto rounded-2xl border border-slate-800">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3">Tender ID</th>
                  <th className="p-3">Title & Department</th>
                  <th className="p-3">Estimate / Award</th>
                  <th className="p-3">Awarded Contractor</th>
                  <th className="p-3">Physical Progress</th>
                  <th className="p-3">Inspection Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                {tenders.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="p-3 font-mono font-bold text-blue-400">{t.id}</td>
                    <td className="p-3">
                      <p className="font-bold text-white">{t.title}</p>
                      <p className="text-[11px] text-slate-400">{t.department}</p>
                    </td>
                    <td className="p-3">
                      <span className="text-slate-400">{t.estimate}</span> ➔ <span className="text-emerald-400 font-bold">{t.award}</span>
                    </td>
                    <td className="p-3 font-medium text-slate-200">{t.contractor}</td>
                    <td className="p-3">
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: t.physicalProgress }} />
                        </div>
                        <span className="font-bold text-white">{t.physicalProgress}</span>
                      </div>
                    </td>
                    <td className="p-3">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        {t.inspectionStatus}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: CAG Audit Follow-Through */}
      {activeTab === 'cag' && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Comptroller & Auditor General (CAG) Audit Paragraphs & ATR Scrutiny
          </h3>
          <div className="grid grid-cols-1 gap-4">
            {cagParas.map((p, idx) => (
              <div key={idx} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-mono font-bold text-amber-400">{p.ref}</span>
                    <span className="text-xs text-slate-400 ml-2">({p.dept})</span>
                    <h4 className="text-sm font-bold text-white mt-1">{p.heading}</h4>
                    <p className="text-xs text-slate-400">{p.report}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-400">Financial Impact</span>
                    <p className="text-sm font-bold text-amber-400">{p.amount}</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs bg-slate-950/60 p-3 rounded-xl border border-slate-800/60">
                  <div>
                    <span className="text-slate-400 block font-medium">Departmental Action Taken Report (ATR)</span>
                    <span className="text-slate-200 font-semibold">{p.atrStatus}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Public Accounts Committee (PAC) Scrutiny</span>
                    <span className="text-blue-400 font-semibold">{p.pacAction}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: RTI Intelligence & SLAs */}
      {activeTab === 'rti' && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Right to Information (RTI) Transparency & Statutory 30-Day SLA Monitoring
          </h3>
          <div className="overflow-x-auto rounded-2xl border border-slate-800">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3">Application Reg No</th>
                  <th className="p-3">Public Authority</th>
                  <th className="p-3">Subject Matter</th>
                  <th className="p-3">Turnaround</th>
                  <th className="p-3">Statutory SLA</th>
                  <th className="p-3">Decision</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                {rtis.map((r) => (
                  <tr key={r.regNo} className="hover:bg-slate-900/40 transition-colors">
                    <td className="p-3 font-mono font-bold text-blue-400">{r.regNo}</td>
                    <td className="p-3 font-semibold text-white">{r.authority}</td>
                    <td className="p-3 text-slate-300">{r.subject}</td>
                    <td className="p-3 font-bold text-slate-200">{r.turnaround}</td>
                    <td className="p-3">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${r.slaColor}`}>
                        {r.slaStatus}
                      </span>
                    </td>
                    <td className="p-3 font-medium text-slate-200">{r.decision}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 5: Ministerial Assurances */}
      {activeTab === 'assurances' && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Tamil Nadu Legislative Assembly (TNLA) Ministerial Assurances
          </h3>
          <p className="text-xs text-slate-400">
            Rule 164 TNLA Follow-Through: Tracking floor commitments through the Committee on Government Assurances.
          </p>
          <div className="grid grid-cols-1 gap-4">
            {assurances.map((a) => (
              <div key={a.code} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-mono font-bold text-blue-400">{a.code}</span>
                    <span className="text-xs text-slate-400 ml-2">Question: {a.mla}</span>
                    <h4 className="text-sm font-bold text-white mt-1">{a.statement}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">Minister: {a.minister} ({a.dept}) • Date: {a.date}</p>
                  </div>
                  <div>
                    <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${a.statusColor}`}>
                      {a.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 6: Provenance & Safeguards */}
      {activeTab === 'safeguards' && (
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Shield className="w-4 h-4 text-blue-400" />
              Bitemporal Data Integrity & SHA-256 Provenance
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Every data point in CIVICLENS TN is preserved with bitemporal coordinates:
              <strong> Valid Time</strong> (when the governance fact or expenditure occurred in reality) and
              <strong> Transaction Time</strong> (when the fact was ingested into the system ledger). This protects the platform against retroactive silent edits and guarantees historical reproducibility for academic researchers and investigative journalists.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1">
                <span className="font-bold text-blue-400">DPDPA 2023 & DPDP Rules 2025</span>
                <p className="text-slate-400">
                  Automated PII scrubbing masks PAN, Aadhaar, bank account numbers, and phone numbers before ingestion.
                  Statutory data principal rights (access, correction, erasure) are tracked via formal audit logs.
                </p>
              </div>
              <div className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1">
                <span className="font-bold text-blue-400">BNS 2023 Sec 356 Right of Reply</span>
                <p className="text-slate-400">
                  Mandatory fair-hearing notices are logged before adverse findings are published. Public entities and contractors are given documented rebuttal windows recorded on an immutable ledger.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
