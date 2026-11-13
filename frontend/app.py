import os
import sys
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.database.session import SessionLocal
from backend.models.promise import PoliticalPromise
from frontend.services.api import api_client

if "view" not in st.session_state:
    st.session_state["view"] = st.query_params.get("view", "launch")

def enter_platform():
    st.session_state["view"] = "dashboard"
    st.query_params["view"] = "dashboard"

def return_to_launchpad():
    st.session_state["view"] = "launch"
    st.query_params["view"] = "launch"

current_view = st.session_state.get("view", "launch")

st.set_page_config(
    page_title="CivicLens TN — Public Accountability & Policy Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded" if current_view == "dashboard" else "collapsed"
)

is_healthy, health_data = api_client.get_health()
status_text = "API Online (Port 5000) • SQLite Active" if is_healthy else "Client Mode • SQLite Active"
status_dot_color = "#10b981" if is_healthy else "#f59e0b"

st.html("""
<style>
.stApp {
    background-color: #06070a !important;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Plus Jakarta Sans", sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #090d16 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

[data-testid="stSidebarNav"] a {
    border-radius: 10px !important;
    padding: 8px 14px !important;
    margin-bottom: 4px !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    color: #cbd5e1 !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebarNav"] a:hover {
    background-color: rgba(59, 130, 246, 0.15) !important;
    color: #60a5fa !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: rgba(59, 130, 246, 0.25) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-left: 3px solid #3b82f6 !important;
}

[data-testid="stSidebarNav"] a[href*="fixtures"],
[data-testid="stSidebarNav"] a[href*="helper"] {
    display: none !important;
}

.stDeployButton,
[data-testid="stDeployButton"],
[data-testid="stToolbarActions"],
.stAppDeployButton,
#MainMenu {
    display: none !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

.hero-container {
    background: linear-gradient(180deg, rgba(17, 24, 39, 0.85) 0%, rgba(10, 14, 23, 0.95) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 36px 32px 28px 32px;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    text-align: center;
    margin-bottom: 28px;
    position: relative;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(59, 130, 246, 0.12);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 9999px;
    padding: 5px 16px;
    font-size: 12.5px;
    font-weight: 600;
    color: #93c5fd;
    margin-bottom: 16px;
}

.hero-title {
    font-size: 46px;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #ffffff;
    margin-bottom: 8px;
    line-height: 1.15;
}

.hero-subtitle {
    font-size: 16.5px;
    color: #94a3b8;
    max-width: 680px;
    margin: 0 auto 24px auto;
    line-height: 1.55;
}

.stat-bar {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    max-width: 720px;
    margin: 0 auto;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.stat-item {
    text-align: center;
}

.stat-number {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
}

.stat-label {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

[data-testid="stPageLink-NavLink"] {
    background: rgba(18, 24, 38, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
    color: #f1f5f9 !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: center !important;
    min-height: 84px !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35) !important;
}

[data-testid="stPageLink-NavLink"]:hover {
    background: rgba(30, 41, 64, 0.95) !important;
    border-color: rgba(96, 165, 250, 0.5) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 28px rgba(59, 130, 246, 0.25) !important;
}

.result-card {
    background: rgba(15, 20, 32, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px;
    padding: 20px 22px;
    margin-bottom: 14px;
    backdrop-filter: blur(12px);
}

.party-tag {
    font-size: 12px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 6px;
    display: inline-block;
    margin-right: 8px;
}

.party-DMK { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
.party-AIADMK { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }
.party-BJP { background: rgba(249, 115, 22, 0.2); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.4); }
.party-PMK { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.4); }

.status-badge {
    font-size: 11.5px;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 9999px;
    display: inline-block;
    text-transform: capitalize;
}

.status-implemented { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
.status-policy_action { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
.status-announced { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }

/* Launch Screen Styles */
.orbit-stage {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none !important;
    z-index: 0;
    overflow: hidden;
}
.orbit-stage * {
    pointer-events: none !important;
}
.orbit-track {
    position: absolute;
    border-radius: 50%;
    border: 1px dashed rgba(255, 255, 255, 0.08);
}
.track-inner { width: 780px; height: 780px; }
.track-outer { width: 1080px; height: 1080px; }
.orbit-ring {
    position: absolute;
    width: 0;
    height: 0;
    top: 50%;
    left: 50%;
}
.orbit-cw { animation: spinCW 42s linear infinite; }
.orbit-ccw { animation: spinCCW 56s linear infinite; }
@keyframes spinCW { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes spinCCW { from { transform: rotate(0deg); } to { transform: rotate(-360deg); } }
.orbit-slot {
    position: absolute;
    top: 0;
    left: 0;
    transform: rotate(var(--angle)) translateY(var(--radius));
}
.orbit-card {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    background: rgba(18, 22, 32, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(12px);
    display: flex;
    align-items: center;
    justify-content: center;
}
.orbit-cw .orbit-card { animation: unspinCW 42s linear infinite; }
.orbit-ccw .orbit-card { animation: unspinCCW 56s linear infinite; }
@keyframes unspinCW {
    from { transform: translate(-50%, -50%) rotate(calc(-1 * var(--angle))); }
    to { transform: translate(-50%, -50%) rotate(calc(-360deg - var(--angle))); }
}
@keyframes unspinCCW {
    from { transform: translate(-50%, -50%) rotate(calc(-1 * var(--angle))); }
    to { transform: translate(-50%, -50%) rotate(calc(360deg - var(--angle))); }
}

div[class*="st-key-launch_card"],
.launch-hero-card {
    background: rgba(13, 17, 26, 0.94) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 28px !important;
    padding: 44px 38px 36px 38px !important;
    max-width: 620px !important;
    width: 100% !important;
    margin: 40px auto 0 auto !important;
    text-align: center !important;
    backdrop-filter: blur(28px) !important;
    box-shadow: 0 35px 80px rgba(0, 0, 0, 0.85) !important;
    position: relative !important;
    z-index: 10 !important;
    pointer-events: auto !important;
}

div[class*="st-key-launch_card"] * {
    pointer-events: auto !important;
}
.mascot-avatar {
    width: 72px;
    height: 72px;
    background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
    border-radius: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20px auto;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.85);
    position: relative;
}
.mascot-pulse {
    position: absolute;
    inset: -5px;
    border-radius: 26px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.7), rgba(168, 85, 247, 0.6));
    z-index: -1;
    filter: blur(12px);
}
.css-lens {
    width: 30px;
    height: 30px;
    border: 3px solid #0f172a;
    border-radius: 50%;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}
.css-lens-dot {
    width: 9px;
    height: 9px;
    background: #3b82f6;
    border-radius: 50%;
}
.css-lens-handle {
    position: absolute;
    width: 3.5px;
    height: 13px;
    background: #0f172a;
    bottom: -9px;
    right: -7px;
    transform: rotate(-45deg);
    border-radius: 2px;
}
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 9999px;
    padding: 6px 16px;
    font-size: 12px;
    color: #94a3b8;
}
.status-led {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 8px #10b981;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 9999px !important;
    padding: 14px 38px !important;
    font-size: 16.5px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5) !important;
    transition: all 0.25s ease !important;
    letter-spacing: -0.01em !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba(37, 99, 235, 0.7) !important;
}
</style>
""")

if current_view != "dashboard":
    st.html("""
    <style>
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        margin-left: -9999px !important;
    }
    .block-container {
        max-width: 900px !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        margin: 0 auto !important;
    }
    iframe[data-testid="stIFrame"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
        pointer-events: none !important;
        z-index: 0 !important;
    }
    div[data-testid="stElementContainer"]:has(iframe[data-testid="stIFrame"]) {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
        pointer-events: none !important;
    }
    </style>
    """)

    components.html("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}
html, body {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
}
.ambient-glow {
    position: fixed;
    width: 700px;
    height: 700px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.18) 0%, rgba(99, 102, 241, 0.08) 40%, rgba(0, 0, 0, 0) 70%);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    filter: blur(80px);
}
.orbit-stage {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
    overflow: hidden;
}
.orbit-track {
    position: absolute;
    border-radius: 50%;
    pointer-events: none;
}
.track-inner {
    width: 780px;
    height: 780px;
    border: 1px dashed rgba(255, 255, 255, 0.08);
    box-shadow: 0 0 35px rgba(59, 130, 246, 0.04);
}
.track-outer {
    width: 1080px;
    height: 1080px;
    border: 1px dashed rgba(255, 255, 255, 0.05);
    box-shadow: 0 0 50px rgba(168, 85, 247, 0.03);
}
.orbit-ring {
    position: absolute;
    width: 0;
    height: 0;
    top: 50%;
    left: 50%;
    pointer-events: none;
}
.orbit-cw { animation: spinCW 42s linear infinite; }
.orbit-ccw { animation: spinCCW 56s linear infinite; }
@keyframes spinCW { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes spinCCW { from { transform: rotate(0deg); } to { transform: rotate(-360deg); } }
.orbit-slot {
    position: absolute;
    top: 0;
    left: 0;
    transform: rotate(var(--angle)) translateY(var(--radius));
}
.orbit-card {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    background: rgba(18, 22, 32, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(12px);
    display: flex;
    align-items: center;
    justify-content: center;
}
.orbit-cw .orbit-card { animation: unspinCW 42s linear infinite; }
.orbit-ccw .orbit-card { animation: unspinCCW 56s linear infinite; }
@keyframes unspinCW {
    from { transform: translate(-50%, -50%) rotate(calc(-1 * var(--angle))); }
    to { transform: translate(-50%, -50%) rotate(calc(-360deg - var(--angle))); }
}
@keyframes unspinCCW {
    from { transform: translate(-50%, -50%) rotate(calc(-1 * var(--angle))); }
    to { transform: translate(-50%, -50%) rotate(calc(360deg - var(--angle))); }
}
</style>
</head>
<body>
<div class="ambient-glow"></div>
<div class="orbit-stage">
<div class="orbit-track track-inner"></div>
<div class="orbit-track track-outer"></div>
<div class="orbit-ring orbit-cw">
<div class="orbit-slot" style="--angle: 0deg; --radius: 390px;"><div class="orbit-card"><svg viewBox="0 0 24 24" width="26" height="26" fill="#ffffff"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></div></div>
<div class="orbit-slot" style="--angle: 45deg; --radius: 390px;"><div class="orbit-card" style="border-color: rgba(239, 68, 68, 0.4);"><svg viewBox="0 0 36 36" width="30" height="30" fill="none"><circle cx="18" cy="18" r="6" fill="#f59e0b"/><path d="M18 5v3M18 28v3M5 18h3M28 18h3" stroke="#f59e0b" stroke-width="2.2" stroke-linecap="round"/><path d="M3 29l8-10 7 8 7-9 8 11H3z" fill="#dc2626"/></svg></div></div>
<div class="orbit-slot" style="--angle: 90deg; --radius: 390px;"><div class="orbit-card"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#e1306c"/><rect x="9.5" y="9.5" width="17" height="17" rx="5" stroke="#ffffff" stroke-width="1.8"/><circle cx="18" cy="18" r="4.2" stroke="#ffffff" stroke-width="1.8"/></svg></div></div>
<div class="orbit-slot" style="--angle: 135deg; --radius: 390px;"><div class="orbit-card" style="border-color: rgba(34, 197, 94, 0.4);"><svg viewBox="0 0 36 36" width="28" height="28" fill="none"><path d="M18 31c0-8 0-13 0-15" stroke="#22c55e" stroke-width="2.2"/><path d="M18 19c-7-2-11-7-10-13 5-1 11 4 10 13z" fill="#16a34a"/><path d="M18 18c7-2 11-7 10-13-5-1-11 4-10 13z" fill="#15803d"/></svg></div></div>
<div class="orbit-slot" style="--angle: 180deg; --radius: 390px;"><div class="orbit-card"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#FF0000"/><polygon points="15,13 23,18 15,23" fill="#ffffff"/></svg></div></div>
<div class="orbit-slot" style="--angle: 225deg; --radius: 390px;"><div class="orbit-card" style="border-color: rgba(249, 115, 22, 0.4);"><svg viewBox="0 0 36 36" width="28" height="28" fill="none"><path d="M18 6c-3 4-3 11 0 15 3-4 3-11 0-15z" fill="#f97316"/><path d="M18 11c-5-1-10 2-11 7 4 2 8 1 11-2z" fill="#fb923c"/><path d="M18 11c5-1 10 2 11 7-4 2-8 1-11-2z" fill="#fb923c"/></svg></div></div>
<div class="orbit-slot" style="--angle: 270deg; --radius: 390px;"><div class="orbit-card"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#1877F2"/><path d="M22.5 19.5h-3.2v10h-4.2v-10h-2.3v-3.8h2.3v-2.6c0-2.4 1.5-3.8 3.9-3.8 1.1 0 2.1.1 2.1.1v3h-1.3c-1.2 0-1.5.7-1.5 1.5v1.8h3.3l-.4 3.8z" fill="#ffffff"/></svg></div></div>
<div class="orbit-slot" style="--angle: 315deg; --radius: 390px;"><div class="orbit-card"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#0f172a"/><path d="M13 14V8a2 2 0 1 1 4 0v5M17 13V6a2 2 0 1 1 4 0v7M21 14V8a2 2 0 1 1 4 0v7M25 16v-4a2 2 0 1 1 4 0v9c0 6-4 10-10 10s-9-4-9-9v-3a2 2 0 1 1 4 0v2" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round"/></svg></div></div>
</div>
<div class="orbit-ring orbit-ccw">
<div class="orbit-slot" style="--angle: 0deg; --radius: 540px;"><div class="orbit-card"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#25D366"/><path d="M18 8a9.5 9.5 0 0 0-8.2 14.3L8 28l5.8-1.5A9.5 9.5 0 1 0 18 8z" fill="#ffffff"/></svg></div></div>
<div class="orbit-slot" style="--angle: 45deg; --radius: 540px;"><div class="orbit-card" style="border-color: rgba(239, 68, 68, 0.4);"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#ef4444"/><circle cx="18" cy="18" r="10" fill="#facc15"/></svg></div></div>
<div class="orbit-slot" style="--angle: 90deg; --radius: 540px;"><div class="orbit-card"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#229ED9"/><path d="M9 17.5l17.5-6.8c.8-.3 1.5.2 1.3 1.1l-3 14.1c-.2 1-.8 1.2-1.6.8l-4.5-3.3-2.2 2.1c-.2.2-.4.4-.8.4l.3-4.5 8.2-7.4c.4-.3-.1-.5-.5-.2L13.6 20.1l-4.3-1.4c-1-.3-1-1 .2-1.5z" fill="#ffffff"/></svg></div></div>
<div class="orbit-slot" style="--angle: 135deg; --radius: 540px;"><div class="orbit-card" style="border-color: rgba(234, 179, 8, 0.4);"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><path d="M18 10c-6 0-10 5-9 12 1 6 7 10 12 7 5-3 7-9 5-14-2-4-5-5-8-5z" fill="#eab308"/><path d="M20 5c3-1 8-1 9 2-3 2-6 1-9-2z" fill="#4d7c0f"/></svg></div></div>
<div class="orbit-slot" style="--angle: 180deg; --radius: 540px;"><div class="orbit-card"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#0A66C2"/><path d="M12 14.5h3.5V26H12V14.5zM13.8 9.5a2 2 0 1 1 0 4 2 2 0 0 1 0-4zM17.5 14.5H21v1.6h.1c.5-1 1.8-2 3.7-2 4 0 4.7 2.6 4.7 6V26H26v-5.2c0-1.2 0-2.8-1.7-2.8-1.7 0-2 1.3-2 2.7V26h-3.5V14.5z" fill="#ffffff"/></svg></div></div>
<div class="orbit-slot" style="--angle: 225deg; --radius: 540px;"><div class="orbit-card" style="border-color: rgba(220, 38, 38, 0.4);"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#dc2626"/><path d="M12 24c-3-4-2-10 3-13 5-3 11-2 13 2-3-2-8-2-10 1-2 2-3 6 0 9l-4 1z" fill="#facc15"/><path d="M25 12l-12 12M21 9l3 3-2 2-3-3 2-2z" stroke="#facc15" stroke-width="2"/></svg></div></div>
<div class="orbit-slot" style="--angle: 270deg; --radius: 540px;"><div class="orbit-card"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><rect width="36" height="36" rx="9" fill="#6366f1"/><path d="M10 10h16a2 2 0 0 1 2 2v13a3 3 0 0 1-3 3H11a3 3 0 0 1-3-3V12a2 2 0 0 1 2-2z" stroke="#ffffff" stroke-width="1.8"/></svg></div></div>
<div class="orbit-slot" style="--angle: 315deg; --radius: 540px;"><div class="orbit-card" style="border-color: rgba(56, 189, 248, 0.4);"><svg viewBox="0 0 36 36" width="26" height="26" fill="none"><path d="M18 5L7 9v9c0 7 5 12 11 14 6-2 11-7 11-14V9L18 5z" fill="#1e3a8a" stroke="#38bdf8" stroke-width="1.5"/><path d="M13 18l3.5 3.5 7-7" stroke="#38bdf8" stroke-width="2.2" stroke-linecap="round"/></svg></div></div>
</div>
</div>
</body>
</html>""", height=1, scrolling=False)

    with st.container(key="launch_card"):
        st.html("""<div class="mascot-avatar">
<div class="mascot-pulse"></div>
<div class="css-lens">
<div class="css-lens-dot"></div>
<div class="css-lens-handle"></div>
</div>
</div>
<h1 class="hero-title" style="font-size: 50px; margin-bottom: 10px; line-height: 1.15;">CivicLens TN.</h1>
<p class="hero-subtitle" style="font-size: 16px; margin-bottom: 26px; line-height: 1.55;">
AI-powered civic intelligence, manifesto promise tracking, and explainable multi-hop evidence graphs for Tamil Nadu.
</p>""")

        launch_btn_col1, launch_btn_col2, launch_btn_col3 = st.columns([1, 4, 1])
        with launch_btn_col2:
            st.button(
                "🚀 Enter CivicLens Platform →",
                key="enter_launch_key",
                type="primary",
                use_container_width=True,
                on_click=enter_platform
            )

        st.html(f"""<div style="text-align: center; margin-top: 20px;">
<span class="status-pill"><span class="status-led"></span><span>{status_text} • 1,065 Manifesto Promises Verified</span></span>
</div>""")

else:
    with st.sidebar:
        st.button("🪐 Return to Launchpad", use_container_width=True, on_click=return_to_launchpad)

        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-top: 14px; margin-bottom: 16px;">
            <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px;">
                🔍
            </div>
            <div>
                <h2 style="font-size: 17px; font-weight: 800; color: #ffffff; margin: 0; line-height: 1.1;">CivicLens TN</h2>
                <span style="font-size: 11.5px; color: #64748b;">v2.4 Production Suite</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 10px 12px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px; font-size: 12px; color: #cbd5e1;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: {status_dot_color}; box-shadow: 0 0 6px {status_dot_color};"></span>
                <span>{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 11px; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.05em; margin-bottom: 8px;'>Core Modules</p>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-badge">
            <span>🏛️ Government of Tamil Nadu Policy Intelligence Platform</span>
        </div>
        <h1 class="hero-title">CivicLens TN.</h1>
        <p class="hero-subtitle">
            AI-powered civic intelligence, manifesto promise tracking, and explainable multi-hop evidence graphs for Tamil Nadu public accountability.
        </p>
        <div class="stat-bar">
            <div class="stat-item">
                <div class="stat-number">1,065</div>
                <div class="stat-label">Manifesto Promises</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">₹3.65L Cr</div>
                <div class="stat-label">State Budget Tracked</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">234</div>
                <div class="stat-label">Assembly Constituencies</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    search_col1, search_col2 = st.columns([5, 1])
    with search_col1:
        search_query = st.text_input(
            "Search Platform",
            placeholder="Search welfare schemes, MLA questions, or manifesto commitments (e.g. laptop, women, DMK, agriculture)...",
            label_visibility="collapsed",
            key="main_search_input"
        )
    with search_col2:
        search_clicked = st.button("Explore →", use_container_width=True, type="primary")

    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    with quick_col1:
        if st.button("👩 Magalir Urimai (₹1000)", use_container_width=True):
            search_query = "women"
    with quick_col2:
        if st.button("🚌 Free Bus (Vidiyal)", use_container_width=True):
            search_query = "bus"
    with quick_col3:
        if st.button("🌾 Crop Loan Waiver", use_container_width=True):
            search_query = "agriculture"
    with quick_col4:
        if st.button("💻 Student Laptops", use_container_width=True):
            search_query = "laptop"

    if search_query:
        st.markdown(f"<h3 style='color: #f1f5f9; font-size: 20px; font-weight: 700; margin-top: 26px; margin-bottom: 14px;'>Matching Commitments for: <em>'{search_query}'</em></h3>", unsafe_allow_html=True)

        db = SessionLocal()
        try:
            search_term = f"%{search_query.strip()}%"
            matching_promises = db.query(PoliticalPromise).filter(
                (PoliticalPromise.normalized_text.ilike(search_term)) |
                (PoliticalPromise.original_text.ilike(search_term)) |
                (PoliticalPromise.primary_category.ilike(search_term))
            ).limit(8).all()

            if matching_promises:
                st.success(f"Found {len(matching_promises)} matching manifesto commitments across official records:")
                for item in matching_promises:
                    party_name = "DMK" if "DMK" in (item.manifesto_id or "") else ("AIADMK" if "AIADMK" in (item.manifesto_id or "") else "TN")
                    party_cls = f"party-{party_name}"
                    status_val = item.current_status or "announced"
                    status_cls = f"status-{status_val}"

                    st.markdown(f"""
                    <div class="result-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div>
                                <span class="party-tag {party_cls}">{party_name}</span>
                                <span style="font-size: 12px; color: #94a3b8;">Manifesto: {item.manifesto_id or 'TN Assembly'}</span>
                            </div>
                            <span class="status-badge {status_cls}">{status_val.replace('_', ' ').title()}</span>
                        </div>
                        <p style="font-size: 15px; color: #f1f5f9; line-height: 1.5; margin-bottom: 8px;">
                            {item.original_text or item.normalized_text}
                        </p>
                        <div style="display: flex; gap: 16px; font-size: 12px; color: #64748b;">
                            <span>📂 Sector: <strong style="color: #cbd5e1;">{item.primary_category or 'Welfare'}</strong></span>
                            <span>🎯 Beneficiary: <strong style="color: #cbd5e1;">{item.target_population or 'Citizens'}</strong></span>
                            <span style="margin-left: auto;">ID: <code style="color: #60a5fa;">{item.promise_id}</code></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.page_link("pages/2_Political_Promises.py", label="Open Full Promise Tracker Explorer →", icon="📜")
            else:
                st.info(f"No specific promises matched '{search_query}'. Try keywords like 'women', 'bus', 'pension', 'agriculture', or 'education'.")
        except Exception as e:
            st.error(f"Search query error: {e}")
        finally:
            db.close()

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffffff; font-size: 20px; font-weight: 700; margin-bottom: 14px;'>Platform Intelligence Modules</h3>", unsafe_allow_html=True)

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.page_link("pages/2_Political_Promises.py", label="📜 1,065 Political Promises\nTrack verified manifesto commitments across DMK, AIADMK, and BJP.", use_container_width=True)
    with row1_col2:
        st.page_link("pages/1_Budget_&_Schemes.py", label="⚖️ Budget & Schemes Analytics\nInspect ₹3.65L Cr allocations, department heads, and execution rates.", use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.page_link("pages/6_Claim_Verification.py", label="🔍 Multi-Hop Claim Verifier\nAuditable fact-checking engine with dialectical evidence proof paths.", use_container_width=True)
    with row2_col2:
        st.page_link("pages/9_Evidence_Graph_Explorer.py", label="🕸️ Evidence Graph Explorer\nInteractive network visualization linking promises, G.O.s, and funds.", use_container_width=True)

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        st.page_link("pages/4_Representatives.py", label="🏛️ MLAs & Legislative Activity\n234 Assembly constituencies, attendance records, and questions tabled.", use_container_width=True)
    with row3_col2:
        st.page_link("pages/8_Civic_Issue_Intelligence.py", label="🚨 Civic Issue Intelligence\nGeotagged municipal grievances across Chennai, Coimbatore, and Madurai.", use_container_width=True)

    row4_col1, row4_col2 = st.columns(2)
    with row4_col1:
        st.page_link("pages/10_Policy_Evaluation_Explorer.py", label="📊 Policy Outcome Scorecards\nLongitudinal analysis of Higher Education GER, MMR, and employment.", use_container_width=True)
    with row4_col2:
        st.page_link("pages/3_Tamil_News.py", label="📰 Tamil News & Media Bias\nTamil NLP pipeline for entity resolution, bias indicators, and news audit.", use_container_width=True)

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: rgba(18, 24, 38, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 22px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h4 style="font-size: 16px; font-weight: 700; color: #ffffff; margin-bottom: 4px;">🪐 Dual-Orbit Orbital Launchpad Available</h4>
            <p style="font-size: 13.5px; color: #94a3b8; margin: 0;">Experience the visual revolving orbit with social media apps and Tamil Nadu political party symbols.</p>
        </div>
        <a href="http://127.0.0.1:5000/launch" target="_blank" style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: #ffffff; padding: 10px 20px; border-radius: 9999px; text-decoration: none; font-size: 13.5px; font-weight: 700; white-space: nowrap;">
            Launch Standalone App →
        </a>
    </div>
    """, unsafe_allow_html=True)
