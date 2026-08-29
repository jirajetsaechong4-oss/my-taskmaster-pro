import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import requests
import uuid
import hashlib
import random
import re

# ==========================================
# 1. ตั้งค่าระบบ (DISCIPLINE ARC - V31 THE DUAL WAR ROOM)
# ==========================================
st.set_page_config(page_title="DISCIPLINE ARC", layout="wide", page_icon="⚙️", initial_sidebar_state="expanded")

# 🛡️ THE SHIELD: ป้องกัน AttributeError แบบ 100%
if "current_user" not in st.session_state: st.session_state["current_user"] = None
if "punishment_active" not in st.session_state: st.session_state["punishment_active"] = False
if "punishment_task" not in st.session_state: st.session_state["punishment_task"] = ""
if "slap_awake_active" not in st.session_state: st.session_state["slap_awake_active"] = False
if "active_slap_message" not in st.session_state: st.session_state["active_slap_message"] = ""
if "locked_in_active" not in st.session_state: st.session_state["locked_in_active"] = False

# ==========================================
# --- PREMIUM UI SYSTEM (AURORA COMMAND :: MODERN DASHBOARD THEME)
# --- CSS + FontAwesome ทั้งหมดฝังอยู่ในไฟล์นี้ไฟล์เดียว
# ==========================================
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Prompt:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* ==================================================
       0. DESIGN TOKENS — AURORA COMMAND NEXUS
       ================================================== */
    :root{
        /* Surfaces (Frosted Glass) */
        --bg-0:#05070D; --bg-1:#080C18;
        --glass:        rgba(20,27,46,.58);
        --glass-2:      rgba(20,27,46,.36);
        --glass-3:      rgba(255,255,255,.035);
        --surface:      rgba(18,25,40,.72);
        --surface-2:    rgba(18,25,40,.42);
        --surface-3:    rgba(255,255,255,.035);

        /* Strokes & Text */
        --stroke:        rgba(148,163,184,.14);
        --stroke-strong: rgba(148,163,184,.22);
        --stroke-hi:     rgba(56,189,248,.45);
        --txt:#F2F7FF;  --txt-2:#B6C2D7; --muted:#78869E;

        /* Accents */
        --accent:#38BDF8; --accent-2:#818CF8; --violet:#A855F7;
        --cyan:#22D3EE;  --pink:#F472B6;    --emerald:#10B981;
        --danger:#F43F5E; --warn:#F59E0B; --ok:#22C55E; --orange:#FB923C;

        /* Radii */
        --r-xl:24px; --r-lg:18px; --r-md:13px; --r-sm:9px;

        /* Soft Multi-Layer Shadows */
        --sh-1: 0 1px 2px rgba(0,0,0,.45);
        --sh-2: 0 1px 1px rgba(0,0,0,.30), 0 8px 24px -8px rgba(0,0,0,.55), 0 20px 40px -20px rgba(0,0,0,.45);
        --sh-3: 0 1px 1px rgba(0,0,0,.30), 0 14px 40px -10px rgba(0,0,0,.60), 0 32px 80px -28px rgba(56,189,248,.35);
        --sh-glow-blue:   0 0 0 1px rgba(56,189,248,.30), 0 8px 28px -6px rgba(56,189,248,.55);
        --sh-glow-violet: 0 0 0 1px rgba(168,85,247,.30), 0 8px 28px -6px rgba(168,85,247,.55);
        --sh-glow-red:    0 0 0 1px rgba(244,63,94,.30),  0 8px 28px -6px rgba(244,63,94,.55);
        --sh-glow-gold:   0 0 0 1px rgba(245,158,11,.30), 0 8px 28px -6px rgba(245,158,11,.55);
        --sh-glow-green:  0 0 0 1px rgba(34,197,94,.30),  0 8px 28px -6px rgba(34,197,94,.55);

        /* Motion */
        --ease: cubic-bezier(.22,.61,.36,1);
        --ease-out: cubic-bezier(.16,1,.3,1);

        /* Font stack: Latin (Plus Jakarta Sans) + Thai (Prompt) */
        --font: 'Plus Jakarta Sans','Inter','Prompt','IBM Plex Sans Thai','Segoe UI',Tahoma,sans-serif;
        --mono: 'JetBrains Mono','Courier New',Courier,monospace;
    }

    /* ==================================================
       1. GLOBAL CANVAS & TYPOGRAPHY
       ================================================== */
    .stApp{
        background:
            radial-gradient(1300px 720px at 8% -10%,  rgba(56,189,248,.18), transparent 60%),
            radial-gradient(1100px 600px at 95% 0%,  rgba(168,85,247,.18), transparent 58%),
            radial-gradient(1000px 700px at 50% 110%, rgba(244,63,94,.10), transparent 60%),
            radial-gradient(700px 500px  at 0% 100%,  rgba(34,197,94,.08),  transparent 60%),
            linear-gradient(180deg,#05070D 0%,#080D1A 45%,#05080E 100%);
        background-attachment: fixed;
        color: var(--txt);
        font-family: var(--font);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
        font-feature-settings: "ss01","cv11";
    }
    .stApp::before{
        content:''; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.55;
        background-image:
            linear-gradient(rgba(148,163,184,.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(148,163,184,.04) 1px, transparent 1px);
        background-size: 48px 48px;
        -webkit-mask-image: radial-gradient(ellipse 90% 60% at 50% 0%, #000 18%, transparent 78%);
                mask-image: radial-gradient(ellipse 90% 60% at 50% 0%, #000 18%, transparent 78%);
    }
    .stApp::after{
        content:''; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.25;
        background: radial-gradient(circle at 50% -10%, rgba(56,189,248,.18), transparent 55%);
        mix-blend-mode: screen;
    }
    [data-testid="stHeader"]{ background: transparent; backdrop-filter: blur(10px) saturate(140%); -webkit-backdrop-filter: blur(10px) saturate(140%); border-bottom: 1px solid rgba(148,163,184,.10); }
    .block-container, .stMainBlockContainer{ padding-top: 2.4rem; padding-bottom: 4rem; max-width: 1580px; }

    body, .stApp, .stMarkdown, p, span, div, label,
    button, input, textarea, select, [data-baseweb]{ font-family: var(--font); }
    i.fa, i.fas, i.far, i.fab, i[class^="fa-"], i[class*=" fa-"]{
        font-family: "Font Awesome 6 Free","Font Awesome 6 Brands" !important;
        font-style: normal;
    }

    /* Hierarchy */
    h1,h2,h3,h4,h5{ font-family: var(--font); letter-spacing: -.022em; color: #F4F8FF; line-height: 1.18; }
    h1{ font-weight: 800; font-size: 2.4rem; }
    h2{ font-weight: 800; font-size: 1.78rem; }
    h3{ font-weight: 800; font-size: 1.3rem;  color: #EEF4FF; }
    h4{ font-weight: 700; font-size: 1.06rem; }
    h5{ font-weight: 700; font-size: .96rem; }
    .stMarkdown p{ color: var(--txt-2); line-height: 1.72; }
    hr{
        border: 0; height: 1px; margin: 1.9rem 0;
        background: linear-gradient(90deg, transparent, rgba(148,163,184,.30), transparent);
    }
    ::selection{ background: rgba(56,189,248,.32); color: #fff; }

    /* Slim Modern Scrollbar (Global) */
    ::-webkit-scrollbar{ width: 8px; height: 8px; }
    ::-webkit-scrollbar-track{ background: rgba(255,255,255,.025); border-radius: 99px; }
    ::-webkit-scrollbar-thumb{
        background: linear-gradient(180deg, rgba(56,189,248,.65), rgba(129,140,248,.55));
        border-radius: 99px;
        border: 2px solid transparent;
        background-clip: padding-box;
        transition: background .25s var(--ease);
    }
    ::-webkit-scrollbar-thumb:hover{
        background: linear-gradient(180deg, #7dd3fc, #C4B5FD);
        background-clip: padding-box;
        box-shadow: 0 0 12px rgba(56,189,248,.55);
    }
    /* Sidebar Scrollbar */
    section[data-testid="stSidebar"] ::-webkit-scrollbar{ width: 6px; }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-track{ background: transparent; }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb{
        background: linear-gradient(180deg, rgba(56,189,248,.45), rgba(168,85,247,.40));
        border-radius: 99px;
    }

    /* ==================================================
       2. SURFACES / CARDS / CONTAINERS (Glassmorphism)
       ================================================== */
    .glass-panel {
        position: relative; overflow: hidden;
        background: var(--glass);
        -webkit-backdrop-filter: blur(20px) saturate(160%);
                backdrop-filter: blur(20px) saturate(160%);
        border: 1px solid rgba(255,255,255,.07);
        padding: 22px 24px;
        border-radius: var(--r-lg);
        margin-bottom: 18px;
        box-shadow: var(--sh-2);
        transition: transform .35s var(--ease-out), box-shadow .35s var(--ease-out), border-color .35s var(--ease-out);
    }
    .glass-panel::before{
        content:''; position:absolute; inset:0; border-radius: inherit; pointer-events:none;
        background: linear-gradient(140deg, rgba(255,255,255,.06), transparent 38%);
        opacity: .9;
    }
    .glass-panel:hover{
        transform: translateY(-3px);
        border-color: var(--stroke-hi);
        box-shadow: var(--sh-3);
    }

    /* st.container(border=True) -> การ์ดพรีเมียม */
    div[data-testid="stVerticalBlockBorderWrapper"]{
        position: relative; overflow: hidden;
        background: var(--glass-2);
        -webkit-backdrop-filter: blur(16px) saturate(150%);
                backdrop-filter: blur(16px) saturate(150%);
        border: 1px solid rgba(255,255,255,.07) !important;
        border-radius: var(--r-lg) !important;
        box-shadow: var(--sh-2);
        transition: transform .32s var(--ease-out), box-shadow .32s var(--ease-out), border-color .32s var(--ease-out);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::before{
        content:''; position:absolute; inset:0; border-radius: inherit; pointer-events:none;
        background: linear-gradient(140deg, rgba(255,255,255,.05), transparent 35%);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover{
        transform: translateY(-3px);
        border-color: var(--stroke-hi) !important;
        box-shadow: var(--sh-3);
    }
    /* ตัวบอกสีการ์ด (ซ่อน) */
    .card-tag{ display: none !important; }
    div[data-testid="stElementContainer"]:has(.card-tag),
    .element-container:has(.card-tag){ display: none !important; margin: 0 !important; height: 0 !important; }

    /* ==================================================
       3. SECTION HEADERS (FontAwesome)
       ================================================== */
    .sec-head{
        display: flex; align-items: center; gap: 16px;
        margin: 6px 0 20px 0; padding: 18px 22px;
        background:
          linear-gradient(110deg, rgba(56,189,248,.10), rgba(18,25,40,.35) 55%),
          var(--glass);
        -webkit-backdrop-filter: blur(18px) saturate(150%);
                backdrop-filter: blur(18px) saturate(150%);
        border: 1px solid rgba(255,255,255,.07);
        border-left: 4px solid var(--sec,#38BDF8);
        border-radius: var(--r-lg);
        box-shadow: var(--sh-1);
        transition: transform .25s var(--ease-out), border-color .25s var(--ease-out);
    }
    .sec-head:hover{ transform: translateX(2px); border-color: var(--sec,#38BDF8); }
    .sec-ico{
        flex: 0 0 48px; height: 48px; width: 48px; display: grid; place-items: center;
        border-radius: 14px; font-size: 1.18rem; color: var(--sec,#38BDF8);
        background: linear-gradient(140deg, rgba(255,255,255,.08), rgba(255,255,255,.02));
        border: 1px solid var(--sec,#38BDF8);
        box-shadow: 0 0 0 4px color-mix(in srgb, var(--sec,#38BDF8) 12%, transparent),
                    0 0 24px -6px var(--sec,#38BDF8);
    }
    .sec-txt h3{ margin: 0; font-size: 1.24rem; font-weight: 800; letter-spacing: -.012em; color: #F2F7FF; }
    .sec-txt p{ margin: 3px 0 0 0; font-size: .86rem; color: var(--muted); line-height: 1.45; }

    /* ==================================================
       4. CYBER TERMINAL (Dual Auto Planner)
       ================================================== */
    .cyber-terminal {
        position: relative;
        background: linear-gradient(180deg, rgba(2,6,23,.92), rgba(6,11,25,.88));
        border: 1px solid rgba(56,189,248,.34);
        border-left: 4px solid #38BDF8;
        padding: 20px 22px;
        font-family: var(--mono);
        border-radius: var(--r-lg);
        box-shadow:
            inset 0 0 32px rgba(56,189,248,.06),
            0 0 0 1px rgba(56,189,248,.12),
            0 12px 30px -16px rgba(56,189,248,.45);
        color: #38bdf8;
        margin-top: 14px;
    }
    .cyber-terminal.combat{
        border-color: rgba(244,63,94,.34); border-left-color: #F43F5E; color: #FB7185;
        box-shadow:
            inset 0 0 32px rgba(244,63,94,.06),
            0 0 0 1px rgba(244,63,94,.12),
            0 12px 30px -16px rgba(244,63,94,.45);
    }
    .cyber-terminal h4{
        color: #f8fafc; margin: 0 0 12px 0; font-size: .86rem;
        border-bottom: 1px dashed rgba(255,255,255,.16);
        padding-bottom: 11px; text-transform: uppercase; letter-spacing: .18em;
        font-family: var(--font);
    }
    .cyber-phase{ margin: 16px 0 9px 0; font-weight: 800; font-size: .9rem; letter-spacing: .08em; font-family: var(--font); }
    .cyber-phase.hab{ color: #38bdf8; }
    .cyber-phase.com{ color: #f59e0b; }
    .cyber-item{
        border-left: 2px dashed rgba(148,163,184,.35);
        padding: 4px 0 4px 14px; margin-bottom: 7px; position: relative;
        color: #DCE6F5; font-size: .85rem;
    }
    .cyber-item::before{ content: '>'; position: absolute; left: -7px; top: 3px; font-weight: 800; background: #040914; padding: 0 2px; }
    .cyber-item.hab::before{ color: #38bdf8; }
    .cyber-item.com::before{ color: #ef4444; }

    /* ==================================================
       5. BIG NUMBER METRIC CARDS
       ================================================== */
    .metric-card{
        position: relative; overflow: hidden; height: 100%;
        background:
            linear-gradient(160deg, rgba(255,255,255,.07) 0%, rgba(15,22,36,.72) 44%),
            var(--glass);
        -webkit-backdrop-filter: blur(20px) saturate(160%);
                backdrop-filter: blur(20px) saturate(160%);
        border: 1px solid rgba(255,255,255,.08);
        border-top: 3px solid var(--m,#38BDF8);
        border-radius: var(--r-xl);
        padding: 22px 24px 20px 24px;
        box-shadow: var(--sh-2);
        transition: transform .35s var(--ease-out), box-shadow .35s var(--ease-out), border-color .35s var(--ease-out);
    }
    .metric-card::before{
        content:''; position:absolute; inset:0; border-radius: inherit; pointer-events:none;
        background: linear-gradient(140deg, rgba(255,255,255,.08), transparent 38%);
    }
    .metric-card::after{
        content:''; position:absolute; top: -50%; right: -18%; width: 220px; height: 220px; border-radius: 50%;
        background: radial-gradient(circle, var(--m,#38BDF8), transparent 68%);
        opacity: .22; filter: blur(18px); pointer-events:none;
    }
    .metric-card:hover{
        transform: translateY(-5px);
        border-color: color-mix(in srgb, var(--m,#38BDF8) 50%, transparent);
        box-shadow: 0 1px 1px rgba(0,0,0,.30), 0 18px 50px -14px rgba(0,0,0,.65), 0 0 30px -6px color-mix(in srgb, var(--m,#38BDF8) 35%, transparent);
    }
    .metric-top{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; position: relative; z-index: 1; }
    .metric-ico{
        height: 40px; width: 40px; display: grid; place-items: center; border-radius: 12px; font-size: .98rem;
        color: var(--m,#38BDF8);
        background: linear-gradient(140deg, color-mix(in srgb, var(--m,#38BDF8) 18%, transparent), transparent);
        border: 1px solid color-mix(in srgb, var(--m,#38BDF8) 40%, transparent);
        box-shadow: 0 0 18px -4px color-mix(in srgb, var(--m,#38BDF8) 50%, transparent);
    }
    .metric-label{
        font-size: .74rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: var(--muted);
    }
    .metric-value{
        font-size: 2.95rem; font-weight: 800; line-height: 1; letter-spacing: -.038em;
        background: linear-gradient(120deg, #FFFFFF 8%, var(--m,#38BDF8) 92%);
        -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
        position: relative; z-index: 1;
    }
    .metric-unit{ font-size: .95rem; font-weight: 700; color: #AAB7CC; -webkit-text-fill-color: #AAB7CC; margin-left: 6px; }
    .metric-foot{ display: flex; align-items: center; gap: 10px; margin-top: 14px; flex-wrap: wrap; position: relative; z-index: 1; }
    .metric-delta{
        display: inline-flex; align-items: center; gap: 6px;
        font-size: .74rem; font-weight: 800; padding: 5px 11px; border-radius: 999px;
        letter-spacing: .02em;
    }
    .md-up  { background: rgba(34,197,94,.14);  color: #4ADE80; border: 1px solid rgba(34,197,94,.40);  }
    .md-down{ background: rgba(244,63,94,.14);  color: #FB7185; border: 1px solid rgba(244,63,94,.40);  }
    .md-flat{ background: rgba(148,163,184,.13); color: #A3B0C4; border: 1px solid rgba(148,163,184,.30); }
    .metric-sub{ font-size: .75rem; color: var(--muted); }

    /* st.metric ดั้งเดิม (สำรอง) */
    [data-testid="stMetric"]{
        background: var(--glass-2);
        -webkit-backdrop-filter: blur(14px) saturate(150%);
                backdrop-filter: blur(14px) saturate(150%);
        border: 1px solid rgba(255,255,255,.07);
        border-radius: var(--r-lg); padding: 18px 20px; box-shadow: var(--sh-2);
    }
    [data-testid="stMetricValue"]{
        font-size: 2.4rem; font-weight: 800; letter-spacing: -.03em;
        background: linear-gradient(120deg, #FFFFFF, #38BDF8);
        -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    }
    [data-testid="stMetricLabel"] p{
        font-size: .78rem !important; text-transform: uppercase; letter-spacing: .10em;
        font-weight: 700; color: var(--muted) !important;
    }

    /* ==================================================
       6. HERO / KPI STRIP / CHIPS / ROWS
       ================================================== */
    .hero{
        position: relative; overflow: hidden;
        background:
            linear-gradient(120deg, rgba(56,189,248,.16) 0%, rgba(129,140,248,.12) 38%, rgba(18,25,40,.62) 78%),
            var(--glass);
        -webkit-backdrop-filter: blur(22px) saturate(160%);
                backdrop-filter: blur(22px) saturate(160%);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: var(--r-xl);
        padding: 30px 34px; margin-bottom: 22px; box-shadow: var(--sh-3);
    }
    .hero::before{
        content:''; position:absolute; inset:0; border-radius: inherit; pointer-events:none;
        background: linear-gradient(140deg, rgba(255,255,255,.07), transparent 40%);
    }
    .hero::after{
        content:''; position:absolute; top: -65%; right: -6%; width: 460px; height: 460px; border-radius: 50%;
        background: radial-gradient(circle, rgba(56,189,248,.28), transparent 65%);
        filter: blur(24px); pointer-events: none;
    }
    .hero-eyebrow{
        font-size: .72rem; font-weight: 800; letter-spacing: .28em; text-transform: uppercase; color: #7DD3FC;
        display: flex; align-items: center; gap: 10px; position: relative; z-index: 1;
    }
    .hero-title{
        margin: 10px 0 6px 0; font-size: 2.18rem; font-weight: 800; letter-spacing: -.038em; line-height: 1.12;
        background: linear-gradient(100deg, #FFFFFF 10%, #93C5FD 55%, #C4B5FD 95%);
        -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
        position: relative; z-index: 1;
    }
    .hero-sub{ margin: 0; color: var(--txt-2); font-size: .95rem; position: relative; z-index: 1; }
    .hero-chips{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; position: relative; z-index: 1; }
    .chip{
        display: inline-flex; align-items: center; gap: 8px;
        padding: 8px 14px; border-radius: 999px;
        font-size: .78rem; font-weight: 700; letter-spacing: .01em;
        background: rgba(255,255,255,.045);
        border: 1px solid rgba(148,163,184,.18);
        color: var(--txt-2);
        transition: transform .22s var(--ease-out), background .22s var(--ease-out), border-color .22s var(--ease-out);
    }
    .chip:hover{ transform: translateY(-2px); background: rgba(255,255,255,.07); border-color: var(--stroke-hi); }
    .chip.c-blue  { color: #7DD3FC; border-color: rgba(56,189,248,.40);  background: rgba(56,189,248,.10);  }
    .chip.c-gold  { color: #FCD34D; border-color: rgba(245,158,11,.40);  background: rgba(245,158,11,.10);  }
    .chip.c-red   { color: #FDA4AF; border-color: rgba(244,63,94,.40);   background: rgba(244,63,94,.10);   }
    .chip.c-green { color: #86EFAC; border-color: rgba(34,197,94,.40);   background: rgba(34,197,94,.10);   }
    .chip.c-violet{ color: #D8B4FE; border-color: rgba(168,85,247,.40);  background: rgba(168,85,247,.10);  }

    .row-item{
        display: flex; align-items: center; gap: 12px;
        background: var(--glass-3);
        -webkit-backdrop-filter: blur(8px);
                backdrop-filter: blur(8px);
        border: 1px solid rgba(148,163,184,.16);
        border-left: 3px solid var(--ri,#64748B);
        padding: 12px 14px; border-radius: var(--r-md); margin-bottom: 9px;
        transition: transform .25s var(--ease-out), background .25s var(--ease-out), border-left-width .25s var(--ease-out);
    }
    .row-item:hover{ background: rgba(255,255,255,.07); transform: translateX(3px); border-left-width: 5px; }
    .row-item i{ color: var(--ri,#64748B); font-size: .9rem; width: 16px; text-align: center; }
    .row-item b{ font-weight: 600; color: #E8EEF9; font-size: .92rem; }
    .row-item.done b{ color: var(--muted); text-decoration: line-through; }
    .row-empty{
        display: flex; align-items: center; gap: 10px; padding: 14px 16px; border-radius: var(--r-md);
        background: rgba(34,197,94,.08); border: 1px dashed rgba(34,197,94,.40);
        color: #86EFAC; font-size: .88rem; font-weight: 600;
    }

    /* ==================================================
       7. BANNERS / BADGES / PULSING DOTS
       ================================================== */
    .subject-banner {
        position: relative; overflow: hidden;
        background: linear-gradient(120deg, rgba(30,41,59,.85) 0%, rgba(10,15,26,.92) 100%);
        -webkit-backdrop-filter: blur(16px) saturate(150%);
                backdrop-filter: blur(16px) saturate(150%);
        padding: 22px 28px;
        border-radius: var(--r-lg);
        border: 1px solid rgba(255,255,255,.07);
        border-left: 5px solid #38BDF8;
        color: white; margin-bottom: 14px;
        box-shadow: var(--sh-2);
    }
    .subject-banner::after{ content: ''; position: absolute; top: 0; right: 0; width: 220px; height: 100%; background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.18)); transform: skewX(-22deg); pointer-events: none; }
    .subject-banner h3{ margin: 0 0 4px 0; font-weight: 800; color: #ffffff; text-transform: uppercase; letter-spacing: .09em; font-size: 1.18rem; }
    .subject-banner h4{ margin: 0; }
    .subject-banner p{ margin: 0; color: #B6C2D7; font-size: .90em; }

    /* Sleek Pill Badges */
    .badge{
        display: inline-flex; align-items: center; gap: 5px;
        padding: 5px 11px; border-radius: 999px;
        font-size: .72em; font-weight: 800; letter-spacing: .03em; white-space: nowrap;
        margin: 0 4px 4px 0;
        transition: transform .2s var(--ease-out);
    }
    .badge:hover{ transform: translateY(-1px); }
    .b-red   { background: rgba(244, 63, 94, 0.14);  color: #FB7185; border: 1px solid rgba(244, 63, 94, 0.45);  }
    .b-blue  { background: rgba(56, 189, 248, 0.14); color: #7DD3FC; border: 1px solid rgba(56, 189, 248, 0.45); }
    .b-gold  { background: rgba(245, 158, 11, 0.14); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.45); }
    .b-gray  { background: rgba(148, 163, 184, 0.12); color: #A3B0C4; border: 1px solid rgba(148, 163, 184, 0.35); }
    .b-green { background: rgba(34, 197, 94, 0.14);  color: #86EFAC; border: 1px solid rgba(34, 197, 94, 0.45);  }
    .b-purple{ background: rgba(168, 85, 247, 0.14); color: #D8B4FE; border: 1px solid rgba(168, 85, 247, 0.45); }

    /* Pulsing Dot (ใช้ร่วมกับ badge ผ่าน ::before เพิ่มเติม) */
    @keyframes pulse-dot {
        0%   { box-shadow: 0 0 0 0   rgba(56,189,248,.55); }
        70%  { box-shadow: 0 0 0 8px rgba(56,189,248,0);  }
        100% { box-shadow: 0 0 0 0   rgba(56,189,248,0);  }
    }
    .b-pulse::before{
        content: ''; width: 7px; height: 7px; border-radius: 50%;
        background: currentColor;
        box-shadow: 0 0 0 0 currentColor;
        animation: pulse-dot 1.8s var(--ease) infinite;
        margin-right: 2px;
    }
    .b-pulse-green::before  { animation-name: pulse-dot; color: #4ADE80; }
    .b-pulse-red::before    { color: #FB7185; }
    .b-pulse-gold::before   { color: #FCD34D; }
    .b-pulse-violet::before { color: #C4B5FD; }

    /* Death Mark Animation */
    @keyframes pulse-red {
        0%   { box-shadow: 0 0 0 0 rgba(244,63,94,.50); }
        70%  { box-shadow: 0 0 0 12px rgba(244,63,94,0); }
        100% { box-shadow: 0 0 0 0 rgba(244,63,94,0); }
    }
    .b-death{
        background: linear-gradient(100deg, #7f1d1d, #9f1239);
        color: #FECDD3; border: 1px solid #F43F5E; text-transform: uppercase;
        animation: pulse-red 2.2s var(--ease) infinite;
    }

    /* ==================================================
       8. TASK CARDS - DYNAMIC PRIORITY (ผูกกับ .card-tag ที่ซ่อนไว้)
       ================================================== */
    .task-card-ui { border-radius: var(--r-lg); }
    .task-title{ font-size: 1.06rem; font-weight: 700; color: #F2F7FF; line-height: 1.55; }
    .task-meta{ margin-bottom: 8px; }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.task-priority-1){
        border-left: 4px solid #F43F5E !important;
        background: linear-gradient(100deg, rgba(244,63,94,.12), rgba(18,25,40,.42) 46%);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.task-priority-2){
        border-left: 4px solid #FB923C !important;
        background: linear-gradient(100deg, rgba(251,146,60,.12), rgba(18,25,40,.42) 46%);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.task-priority-3){
        border-left: 4px solid #F59E0B !important;
        background: linear-gradient(100deg, rgba(245,158,11,.10), rgba(18,25,40,.42) 46%);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.task-priority-4){
        border-left: 4px solid #22C55E !important;
        background: linear-gradient(100deg, rgba(34,197,94,.10), rgba(18,25,40,.42) 46%);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sq-card){
        border-left: 4px solid #A855F7 !important;
        background: linear-gradient(100deg, rgba(168,85,247,.12), rgba(18,25,40,.42) 46%);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.qa-card){
        border-left: 4px solid #10B981 !important;
        background: linear-gradient(100deg, rgba(16,185,129,.12), rgba(18,25,40,.42) 46%);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.skill-card){
        border-left: 4px solid #F59E0B !important;
        background: linear-gradient(100deg, rgba(245,158,11,.12), rgba(18,25,40,.42) 46%);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.death-mark){
        border: 1px solid rgba(244,63,94,.55) !important;
        border-left: 5px solid #F43F5E !important;
        background: linear-gradient(100deg, rgba(244,63,94,.18), rgba(18,25,40,.58) 52%);
        animation: pulse-red 2.4s var(--ease) infinite;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.task-card-ui):hover{ transform: translateY(-3px); }

    /* คลาสเดิม (สำรองไว้ ไม่ตัดทิ้ง) */
    .sq-card {
        background: linear-gradient(100deg, rgba(168,85,247,.12), rgba(18,25,40,.42) 46%);
        border-left: 4px solid #A855F7; padding: 15px 20px; border-radius: var(--r-lg);
        margin-bottom: 12px; transition: transform .3s var(--ease-out), box-shadow .3s var(--ease-out);
        border-top: 1px solid var(--stroke); border-right: 1px solid var(--stroke);
    }
    .qa-card {
        background: linear-gradient(100deg, rgba(16,185,129,.12), rgba(18,25,40,.42) 46%);
        border-left: 4px solid #10B981; padding: 15px 20px; border-radius: var(--r-lg);
        margin-bottom: 12px; transition: transform .3s var(--ease-out), box-shadow .3s var(--ease-out);
        border-top: 1px solid var(--stroke); border-right: 1px solid var(--stroke);
    }
    .task-card-ui.death-mark{
        border: 1px solid rgba(244,63,94,.55); border-left: 5px solid #F43F5E;
        animation: pulse-red 2.4s var(--ease) infinite;
    }

    /* แถบความคืบหน้างานย่อย */
    .mini-track{
        margin-top: 14px; width: 100%;
        background: rgba(255,255,255,.06);
        border-radius: 99px; height: 8px; overflow: hidden;
        box-shadow: inset 0 1px 2px rgba(0,0,0,.30);
    }
    .mini-fill{
        height: 100%; border-radius: 99px;
        background: linear-gradient(90deg, #0EA5E9, #38BDF8, #818CF8);
        box-shadow: 0 0 14px rgba(56,189,248,.65);
        transition: width .5s var(--ease-out);
    }
    .mini-label{ font-size: .74rem; color: var(--muted); margin-top: 6px; font-weight: 700; letter-spacing: .03em; }

    /* Mentor Quotes */
    .mentor-quote {
        background: linear-gradient(110deg, rgba(2,6,23,.65), rgba(6,11,25,.50));
        padding: 14px 18px; border-radius: var(--r-md); font-style: italic;
        margin: 10px 0 12px 0; font-size: .92em;
        border: 1px solid rgba(148,163,184,.18); border-left: 3px solid rgba(148,163,184,.55);
        color: #D6E0F0;
    }

    /* ==================================================
       9. BUTTONS (Dynamic Hover + Soft Glow)
       ================================================== */
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button,
    .stPopover > button, [data-testid="stPopover"] button{
        position: relative; overflow: hidden;
        border-radius: var(--r-md) !important;
        border: 1px solid rgba(148,163,184,.20) !important;
        background: rgba(255,255,255,.05) !important;
        color: #E8EEF9 !important;
        font-weight: 700 !important; font-size: .90rem !important; letter-spacing: .01em;
        padding: .6rem 1.1rem !important;
        box-shadow: var(--sh-1);
        transition: transform .25s var(--ease-out), background .25s var(--ease-out), border-color .25s var(--ease-out), box-shadow .25s var(--ease-out), color .25s var(--ease-out) !important;
    }
    .stButton > button::before, .stFormSubmitButton > button::before, .stDownloadButton > button::before,
    .stPopover > button::before, [data-testid="stPopover"] button::before{
        content: ''; position: absolute; inset: 0; pointer-events: none; border-radius: inherit;
        background: linear-gradient(120deg, rgba(255,255,255,.10), transparent 50%);
        opacity: 0; transition: opacity .25s var(--ease-out);
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover,
    .stPopover > button:hover, [data-testid="stPopover"] button:hover{
        background: rgba(56,189,248,.14) !important;
        border-color: var(--stroke-hi) !important;
        color: #fff !important;
        transform: translateY(-3px);
        box-shadow: var(--sh-glow-blue);
    }
    .stButton > button:hover::before, .stFormSubmitButton > button:hover::before, .stDownloadButton > button:hover::before,
    .stPopover > button:hover::before, [data-testid="stPopover"] button:hover::before{ opacity: 1; }
    .stButton > button:active, .stFormSubmitButton > button:active,
    .stPopover > button:active, [data-testid="stPopover"] button:active{ transform: translateY(0); box-shadow: var(--sh-1); }
    .stButton > button:focus:not(:active),
    .stPopover > button:focus:not(:active), [data-testid="stPopover"] button:focus:not(:active){
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,.28) !important;
    }

    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"]{
        background: linear-gradient(100deg, #0EA5E9 0%, #4F7FF7 52%, #8B5CF6 100%) !important;
        border: 1px solid rgba(255,255,255,.18) !important;
        color: #fff !important; font-weight: 800 !important;
        box-shadow: 0 10px 26px -12px rgba(79,127,247,.85), inset 0 1px 0 rgba(255,255,255,.18);
    }
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover{
        filter: brightness(1.10) saturate(1.05);
        transform: translateY(-3px);
        box-shadow: 0 18px 36px -12px rgba(79,127,247,.95), inset 0 1px 0 rgba(255,255,255,.22);
    }
    .stButton > button:disabled, .stPopover > button:disabled, [data-testid="stPopover"] button:disabled{ opacity: .42 !important; transform: none !important; box-shadow: none !important; }

    /* ==================================================
       10. INPUTS / SELECTS / RADIOS (Focus Ring Glow)
       ================================================== */
    .stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input{
        background: rgba(9,14,25,.65) !important;
        -webkit-backdrop-filter: blur(8px);
                backdrop-filter: blur(8px);
        border-radius: var(--r-md) !important;
        border: 1px solid rgba(148,163,184,.18) !important;
        color: #E8EEF9 !important; font-size: .92rem !important;
        padding: .58rem .85rem !important;
        transition: border-color .2s var(--ease-out), box-shadow .2s var(--ease-out), background .2s var(--ease-out) !important;
    }
    .stTextInput input:hover, .stTextArea textarea:hover, .stNumberInput input:hover{
        border-color: var(--stroke-strong) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus,
    .stDateInput input:focus{
        border-color: var(--stroke-hi) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,.18) !important;
        background: rgba(9,14,25,.82) !important;
    }
    [data-baseweb="input"], [data-baseweb="textarea"]{
        background: rgba(9,14,25,.65) !important;
        border-radius: var(--r-md) !important;
        border-color: rgba(148,163,184,.18) !important;
        transition: border-color .2s var(--ease-out), box-shadow .2s var(--ease-out) !important;
    }
    [data-baseweb="input"]:hover, [data-baseweb="textarea"]:hover{ border-color: var(--stroke-strong) !important; }
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within{
        border-color: var(--stroke-hi) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,.18) !important;
    }
    ::placeholder{ color: rgba(148,163,184,.55) !important; }

    /* Hard fallback: guarantee dark glass styling on every raw text/number field,
       including ones nested inside st.form (Streamlit forms can otherwise leak
       the browser's default light input chrome through). Uses bare element
       selectors (not input[type="text"]) because Streamlit's text inputs often
       omit the type attribute entirely, which would silently defeat an
       attribute-based selector. Checkbox/radio/range keep native styling. */
    input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="button"]):not([type="submit"]),
    textarea{
        background: rgba(9,14,25,.65) !important;
        -webkit-backdrop-filter: blur(8px);
                backdrop-filter: blur(8px);
        border-radius: var(--r-md) !important;
        border: 1px solid rgba(148,163,184,.18) !important;
        color: #E8EEF9 !important; font-size: .92rem !important;
        padding: .58rem .85rem !important;
        transition: border-color .2s var(--ease-out), box-shadow .2s var(--ease-out), background .2s var(--ease-out) !important;
    }
    input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="button"]):not([type="submit"]):hover,
    textarea:hover{
        border-color: var(--stroke-strong) !important;
    }
    input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="button"]):not([type="submit"]):focus,
    textarea:focus{
        border-color: var(--stroke-hi) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,.18) !important;
        background: rgba(9,14,25,.82) !important;
    }

    [data-baseweb="select"] > div{
        background: rgba(9,14,25,.65) !important;
        border-radius: var(--r-md) !important;
        border: 1px solid rgba(148,163,184,.18) !important;
        transition: border-color .2s var(--ease-out), box-shadow .2s var(--ease-out) !important;
    }
    [data-baseweb="select"] > div:hover{ border-color: var(--stroke-hi) !important; }
    [data-baseweb="select"] > div:focus-within{
        border-color: var(--stroke-hi) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,.18) !important;
    }
    [data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"]{
        background: rgba(8,12,24,.96) !important;
        border: 1px solid rgba(148,163,184,.20) !important;
        border-radius: var(--r-md) !important;
        box-shadow: var(--sh-3) !important;
        -webkit-backdrop-filter: blur(18px) saturate(150%);
                backdrop-filter: blur(18px) saturate(150%);
    }
    [role="option"]:hover{ background: rgba(56,189,248,.14) !important; color: #fff; }
    [role="option"][aria-selected="true"]{
        background: linear-gradient(100deg, rgba(56,189,248,.22), rgba(139,92,246,.18)) !important;
        color: #fff !important;
    }

    /* Date picker calendar */
    [data-baseweb="calendar"]{
        background: rgba(8,12,24,.96) !important;
        border: 1px solid rgba(148,163,184,.20) !important;
        border-radius: var(--r-md) !important;
    }
    [data-baseweb="calendar"] button:hover{ background: rgba(56,189,248,.16) !important; }

    .stTextInput label, .stTextArea label, .stNumberInput label, .stSelectbox label,
    .stDateInput label, .stRadio label, .stCheckbox label, .stMultiSelect label, .stSlider label{
        font-size: .82rem !important; font-weight: 700 !important; color: #B6C2D7 !important;
        letter-spacing: .01em;
    }
    .stRadio [role="radiogroup"]{ gap: 8px; flex-wrap: wrap; }
    .stRadio [role="radiogroup"] > label{
        background: rgba(255,255,255,.035); border: 1px solid var(--stroke);
        border-radius: 999px; padding: 6px 14px 6px 10px; margin: 0; transition: all .2s var(--ease-out);
    }
    .stRadio [role="radiogroup"] > label:hover{
        background: rgba(56,189,248,.10); border-color: var(--stroke-hi);
    }
    .stCheckbox label, .stRadio label{ color: #D6E0F0 !important; }

    /* ==================================================
       11. TABS
       ================================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; padding: 8px; border-radius: var(--r-lg); flex-wrap: wrap;
        background: rgba(12,18,31,.68);
        -webkit-backdrop-filter: blur(14px) saturate(150%);
                backdrop-filter: blur(14px) saturate(150%);
        border: 1px solid rgba(255,255,255,.07);
        box-shadow: var(--sh-1);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent; border-radius: var(--r-md); padding: 10px 18px; height: auto;
        color: var(--muted); font-weight: 700; font-size: .88rem; border: 1px solid transparent;
        transition: all .25s var(--ease-out);
    }
    .stTabs [data-baseweb="tab"]:hover{ color: #E8EEF9; background-color: rgba(255,255,255,.05); transform: translateY(-1px); }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(100deg, rgba(56,189,248,.22), rgba(139,92,246,.22)) !important;
        border: 1px solid rgba(56,189,248,.45) !important;
        color: white !important; font-weight: 800 !important;
        box-shadow: 0 8px 22px -12px rgba(56,189,248,.85), inset 0 1px 0 rgba(255,255,255,.10);
    }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{ display: none !important; }
    .stTabs [data-baseweb="tab-panel"]{ padding-top: 22px; }

    /* ==================================================
       12. SIDEBAR (Clean & Refined)
       ================================================== */
    section[data-testid="stSidebar"]{
        background:
            radial-gradient(700px 420px at 0% 0%, rgba(56,189,248,.10), transparent 65%),
            linear-gradient(180deg, rgba(9,14,24,.985) 0%, rgba(7,11,20,.99) 100%);
        border-right: 1px solid rgba(148,163,184,.14);
        box-shadow: 22px 0 60px -36px rgba(0,0,0,.95);
    }
    section[data-testid="stSidebar"] > div:first-child{
        background: transparent;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
        padding-top: 1.4rem; padding-bottom: 2.5rem;
    }
    section[data-testid="stSidebar"] hr{
        margin: 1.15rem 0;
        background: linear-gradient(90deg, transparent, rgba(148,163,184,.20), transparent);
    }
    .side-brand{
        display: flex; align-items: center; gap: 13px; padding: 16px;
        border-radius: var(--r-lg); margin-bottom: 14px;
        background:
            linear-gradient(120deg, rgba(56,189,248,.18), rgba(139,92,246,.14) 70%, transparent),
            rgba(20,27,46,.42);
        -webkit-backdrop-filter: blur(16px) saturate(150%);
                backdrop-filter: blur(16px) saturate(150%);
        border: 1px solid rgba(255,255,255,.08);
        box-shadow: var(--sh-1);
        transition: transform .25s var(--ease-out), box-shadow .25s var(--ease-out);
    }
    .side-brand:hover{ transform: translateY(-2px); box-shadow: var(--sh-2); }
    .side-brand-ico{
        height: 46px; width: 46px; display: grid; place-items: center; border-radius: 14px;
        font-size: 1.22rem; color: #fff;
        background: linear-gradient(135deg, #0EA5E9, #8B5CF6);
        box-shadow: 0 8px 22px -8px rgba(56,189,248,.9), inset 0 1px 0 rgba(255,255,255,.18);
    }
    .side-brand h2{
        margin: 0; font-size: 1.06rem; font-weight: 800; letter-spacing: .14em; line-height: 1.2;
        background: linear-gradient(100deg, #fff, #93C5FD);
        -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    }
    .side-brand span{ font-size: .68rem; color: var(--muted); letter-spacing: .12em; text-transform: uppercase; font-weight: 700; }
    .side-label{
        display: flex; align-items: center; gap: 8px; margin: 20px 0 10px 0;
        font-size: .68rem; font-weight: 800; letter-spacing: .22em; text-transform: uppercase; color: var(--muted);
    }
    .side-label::after{
        content: ''; flex: 1; height: 1px;
        background: linear-gradient(90deg, rgba(148,163,184,.28), transparent);
    }
    .side-card{
        background: var(--glass-3);
        -webkit-backdrop-filter: blur(8px);
                backdrop-filter: blur(8px);
        border: 1px solid rgba(148,163,184,.16);
        border-left: 3px solid var(--sc,#38BDF8);
        border-radius: var(--r-md); padding: 13px 15px; margin-bottom: 10px;
        transition: transform .25s var(--ease-out), border-color .25s var(--ease-out), background .25s var(--ease-out);
    }
    .side-card:hover{
        background: rgba(255,255,255,.05);
        transform: translateX(2px);
    }
    .side-card .sc-label{
        font-size: .66rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; color: var(--muted);
        display: flex; align-items: center; gap: 7px;
    }
    .side-card .sc-value{ font-size: .96rem; font-weight: 700; color: #E8EEF9; margin-top: 5px; line-height: 1.45; }
    .side-card .sc-note{ font-size: .78rem; color: #B6C2D7; margin-top: 5px; font-style: italic; line-height: 1.5; }

    /* ==================================================
       13. EXPANDER / POPOVER / ALERTS / PROGRESS / FORM / DATAFRAME
       ================================================== */
    [data-testid="stExpander"]{
        border: 1px solid rgba(148,163,184,.16) !important;
        border-radius: var(--r-md) !important;
        background: rgba(255,255,255,.022) !important;
        overflow: hidden; box-shadow: var(--sh-1);
    }
    [data-testid="stExpander"] summary{
        font-weight: 700 !important; font-size: .90rem !important;
        padding: 12px 16px !important;
        transition: background .2s var(--ease-out), color .2s var(--ease-out);
    }
    [data-testid="stExpander"] summary:hover{
        color: #38BDF8 !important; background: rgba(56,189,248,.06);
    }
    [data-testid="stExpander"] details[open] summary{ border-bottom: 1px solid var(--stroke); }

    [data-testid="stPopoverBody"]{
        background: rgba(8,12,24,.96) !important;
        border: 1px solid rgba(148,163,184,.20) !important;
        border-radius: var(--r-lg) !important;
        box-shadow: var(--sh-3) !important;
        -webkit-backdrop-filter: blur(18px) saturate(160%);
                backdrop-filter: blur(18px) saturate(160%);
    }

    [data-testid="stAlert"], [data-testid="stAlertContainer"], .stAlert{
        border-radius: var(--r-md) !important;
        box-shadow: var(--sh-1);
        border: 1px solid rgba(148,163,184,.16) !important;
    }
    [data-testid="stAlert"] p{ font-size: .90rem; }

    .stProgress > div > div > div{
        background: rgba(255,255,255,.07) !important;
        border-radius: 99px !important; height: 9px !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,.30);
    }
    .stProgress > div > div > div > div{
        background: linear-gradient(90deg, #0EA5E9, #38BDF8, #818CF8) !important;
        border-radius: 99px !important;
        box-shadow: 0 0 16px rgba(56,189,248,.55);
    }

    [data-testid="stForm"]{
        border: 1px solid rgba(148,163,184,.16) !important;
        border-radius: var(--r-lg) !important;
        background: rgba(255,255,255,.025) !important;
        padding: 20px 22px !important;
        box-shadow: var(--sh-1);
        -webkit-backdrop-filter: blur(8px);
                backdrop-filter: blur(8px);
    }
    [data-testid="stDataFrame"], [data-testid="stTable"], [data-testid="stArrowVegaLiteChart"], .stPlotlyChart{
        border: 1px solid rgba(148,163,184,.16);
        border-radius: var(--r-lg); overflow: hidden;
        background: var(--glass-2);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
                backdrop-filter: blur(12px) saturate(150%);
        box-shadow: var(--sh-2); padding: 6px;
    }
    [data-testid="stToast"]{
        border-radius: var(--r-md) !important;
        border: 1px solid rgba(148,163,184,.20) !important;
        background: rgba(8,12,24,.95) !important;
        -webkit-backdrop-filter: blur(16px) saturate(150%);
                backdrop-filter: blur(16px) saturate(150%);
    }

    /* ==================================================
       14. RESPONSIVE
       ================================================== */
    @media (max-width: 1100px){
        .hero-title{ font-size: 1.78rem; }
        .metric-value{ font-size: 2.4rem; }
        .block-container{ padding-left: 1.1rem; padding-right: 1.1rem; }
    }
    @media (max-width: 720px){
        .hero{ padding: 22px 22px; }
        .hero-title{ font-size: 1.55rem; }
        .metric-value{ font-size: 2.05rem; }
        .sec-head{ padding: 14px 16px; gap: 12px; }
        .sec-ico{ height: 40px; width: 40px; }
    }

    /* ==================================================
       15. LAST-RESORT OVERRIDES (exact aria-label targeting)
       Two fields inside st.form blocks (weakness_fuel_form,
       hater_form) were observed rendering with the browser's
       native light input chrome despite the rules above.
       aria-label is set by Streamlit from the widget's label
       text, so this reaches the exact element regardless of
       DOM ancestry/portal placement.
       ================================================== */
    input[aria-label="ความอ่อนแอที่มึงเคยทำพลาด:"],
    input[aria-label="คำดูถูกที่ฝังใจ:"]{
        background: rgba(9,14,25,.65) !important;
        border: 1px solid rgba(148,163,184,.18) !important;
        border-radius: 13px !important;
        color: #E8EEF9 !important;
        padding: .58rem .85rem !important;
    }
    input[aria-label="ความอ่อนแอที่มึงเคยทำพลาด:"]:focus,
    input[aria-label="คำดูถูกที่ฝังใจ:"]:focus{
        border-color: rgba(56,189,248,.45) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,.18) !important;
        background: rgba(9,14,25,.82) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1.5 UI COMPONENTS (ตัวช่วยเรนเดอร์ดีไซน์พรีเมียม)
# ==========================================
def ui_section(icon, title, subtitle="", accent="#38BDF8"):
    """หัวข้อหลักพร้อมไอคอน FontAwesome + แถบเน้นสี"""
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"<div class='sec-head' style='--sec:{accent};'>"
        f"<div class='sec-ico'><i class='{icon}'></i></div>"
        f"<div class='sec-txt'><h3>{title}</h3>{sub_html}</div></div>",
        unsafe_allow_html=True
    )

def ui_metric(icon, label, value, delta=None, accent="#38BDF8", unit="", sub=""):
    """การ์ดตัวเลขขนาดใหญ่ (Big Number Metric Card)"""
    delta_html = ""
    if delta is not None and str(delta).strip() != "":
        d_txt = str(delta).strip()
        if d_txt.startswith("-"): d_cls, d_ico = "md-down", "fa-solid fa-arrow-trend-down"
        elif d_txt.startswith("0"): d_cls, d_ico = "md-flat", "fa-solid fa-minus"
        else: d_cls, d_ico = "md-up", "fa-solid fa-arrow-trend-up"
        delta_html = f"<span class='metric-delta {d_cls}'><i class='{d_ico}'></i>{d_txt}</span>"
    sub_html = f"<span class='metric-sub'>{sub}</span>" if sub else ""
    unit_html = f"<span class='metric-unit'>{unit}</span>" if unit else ""
    foot_html = f"<div class='metric-foot'>{delta_html}{sub_html}</div>" if (delta_html or sub_html) else ""
    st.markdown(
        f"<div class='metric-card' style='--m:{accent};'>"
        f"<div class='metric-top'><span class='metric-ico'><i class='{icon}'></i></span>"
        f"<span class='metric-label'>{label}</span></div>"
        f"<div class='metric-value'>{value}{unit_html}</div>{foot_html}</div>",
        unsafe_allow_html=True
    )

def ui_card_tag(css_class):
    """ตัวบอกสีการ์ด (ซ่อนไว้) ให้ CSS จับคู่กับ st.container(border=True)"""
    st.markdown(f"<span class='card-tag {css_class}'></span>", unsafe_allow_html=True)

def ui_row(icon, text, color="#64748B", done=False, extra=""):
    """แถวรายการในแผงสรุป"""
    cls = "row-item done" if done else "row-item"
    st.markdown(f"<div class='{cls}' style='--ri:{color};'><i class='{icon}'></i><b>{text}</b>{extra}</div>", unsafe_allow_html=True)

def ui_empty(text, icon="fa-solid fa-circle-check"):
    """กล่องสถานะว่าง/เคลียร์หมดแล้ว"""
    st.markdown(f"<div class='row-empty'><i class='{icon}'></i>{text}</div>", unsafe_allow_html=True)

# ==========================================
# 2. ฟังก์ชันพื้นฐานทั้งหมด (HELPER FUNCTIONS)
# ==========================================
FIREBASE_URL = "https://mytaskpro-f7328-default-rtdb.asia-southeast1.firebasedatabase.app"
FIREBASE_SECRET = "Wv2Ha7WZrDLwnpJyKMt29z9I0MGb0kxitoOaaoGe"

def get_current_thai_time():
    tz_thai = timezone(timedelta(hours=7))
    return datetime.now(tz_thai)

now_thai = get_current_thai_time()
today_date = now_thai.date()
today_str = str(today_date)
yesterday_date = today_date - timedelta(days=1)
yesterday_str = str(yesterday_date)

THAI_DAYS = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
THAI_MONTHS = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

def thai_date_format(date_str):
    if not date_str or date_str == "": return ""
    try:
        if isinstance(date_str, date) or isinstance(date_str, datetime): d = date_str
        else: d = datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
        return f"{THAI_DAYS[d.weekday()]} {d.day} {THAI_MONTHS[d.month]} {d.year}"
    except: return str(date_str)

def safe_date_parse(date_str):
    if not date_str or str(date_str).strip() == "" or str(date_str) == "None": return today_date
    try: return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
    except: return today_date

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

def get_stable_index(id_str, list_len):
    if list_len == 0: return 0
    return int(hashlib.md5(id_str.encode('utf-8')).hexdigest(), 16) % list_len

def clean_quote(text):
    return re.sub(r'^\d+\.\s*', '', text)

def get_safe_email(email):
    return email.replace(".", "-").replace("@", "-")

def get_title(level):
    if level < 3: return "🤡 ไอ้ขี้แพ้ที่รอการพิสูจน์"
    elif level < 7: return "⚙️ ผู้ทุบทำลายขีดจำกัด (Limit Breaker)"
    elif level < 12: return "🦍 นักรบผู้คุมปีศาจในใจ (Mind Master)"
    else: return "👑 ปรมาจารย์แห่งวินัยเหล็ก (Discipline God)"

def get_priority_score(task_type):
    if not task_type: return 4
    if "🔴 ด่วนสุด" in task_type or "🔥 งานฉุกเฉิน" in task_type: return 1
    if "🟡 ปานกลาง" in task_type: return 2
    if "🟢 ชิลๆ" in task_type: return 3
    return 4

def get_priority_badge(task_type):
    if not task_type: return "<span class='badge b-gray'>⚪ ไม่ระบุความสำคัญ</span>"
    if "ด่วนสุด" in task_type or "ฉุกเฉิน" in task_type: return f"<span class='badge b-red'>🚨 {task_type}</span>"
    if "ปานกลาง" in task_type: return f"<span class='badge b-gold'>🟡 {task_type}</span>"
    return f"<span class='badge b-green'>🟢 {task_type}</span>"

def get_deadline_score(dl_str):
    if not dl_str or dl_str == "": return 999999
    try: return (datetime.strptime(str(dl_str).strip(), "%Y-%m-%d").date() - today_date).days
    except: return 999999

def format_days_left(dl_str):
    days = get_deadline_score(dl_str)
    if days == 999999: return ""
    if days > 0: return f"⏳ เหลือ {days} วัน"
    if days == 0: return f"🚨 เสร็จวันนี้!"
    return f"💀 เลยกำหนด {-days} วัน"

def get_badge_html(dl_str, dl_type, is_must_do=False):
    if is_must_do: return f"<span class='badge b-death blink-text'>🩸 MUST DO TODAY!</span>"
    if not dl_str or dl_str == "": return "<span class='badge b-gray'>⚪ ไม่มีกำหนดเวลา</span>"
    days = get_deadline_score(dl_str)
    txt = format_days_left(dl_str)
    if "Deadline" in dl_type: css = "b-red" if days <= 2 else "b-gray"
    else: css = "b-blue" if days <= 2 else "b-gray"
    icon = "🔴" if "Deadline" in dl_type else "🎯"
    if days < 0: css = "b-red"; icon = "💀"
    return f"<span class='badge {css}'>{icon} {txt}</span>"

def is_overdue_check(dl_str):
    return get_deadline_score(dl_str) < 0

def get_task_css_class(item, base_type="task"):
    dl_str = item.get("deadline", "")
    is_overdue = is_overdue_check(dl_str) if dl_str != "" else False
    is_must_do = item.get("is_must_do", False)
    prio_str = item.get("priority", item.get("ประเภท", ""))

    prio_css = "task-priority-3"
    if "ด่วนสุด" in prio_str: prio_css = "task-priority-1"
    elif "ฉุกเฉิน" in prio_str: prio_css = "task-priority-2"
    elif "ปานกลาง" in prio_str: prio_css = "task-priority-3"
    elif "ชิลๆ" in prio_str: prio_css = "task-priority-4"

    classes = ["task-card-ui", prio_css]
    if base_type == "study": classes.append("study")
    if is_must_do: classes.append("death-mark")
    elif is_overdue: classes.append("overdue")

    return " ".join(classes)

def get_subtask_progress_html(item):
    subs = item.get("subtasks", [])
    if not subs: return ""
    total_s = len(subs)
    done_s = len([s for s in subs if s.get("done")])
    prog_percent = int((done_s / total_s) * 100) if total_s > 0 else 0
    return f"""
    <div class='mini-track'><div class='mini-fill' style='width:{prog_percent}%;'></div></div>
    <div class='mini-label'><i class="fa-solid fa-bars-progress"></i> คืบหน้า: {done_s}/{total_s} ({prog_percent}%)</div>
    """

def calculate_task_rewards(task, current_streak, mentor_name):
    score = get_priority_score(task.get("ประเภท", ""))
    base_exp = 40 if score == 1 else 20 if score == 2 else 10
    bonus_exp = 100 if task.get("is_boss") else 0
    if task.get("bounty"): bonus_exp += 50
    if task.get("subtasks"): bonus_exp += len(task["subtasks"]) * 10
    raw_total_exp = base_exp + bonus_exp
    multiplier = 1.5 if current_streak >= 30 else 1.2 if current_streak >= 7 else 1.1 if current_streak >= 3 else 1.0
    final_exp = int(raw_total_exp * multiplier)
    fail_reduce = 10 if score == 1 else 5 if score == 2 else 2
    if task.get("is_boss"): fail_reduce += 15
    if task.get("bounty"): fail_reduce += 5
    if task.get("is_must_do"): fail_reduce += 10
    if mentor_name == "Toji" and task.get("is_boss"): final_exp = int(final_exp * 1.3)
    if mentor_name == "Zenitsu" and st.session_state.get("locked_in_active", False) and score == 1: fail_reduce *= 2
    if mentor_name == "Future You" and score == 1: final_exp += 20
    return final_exp, fail_reduce

def get_skill_tier_info(exp):
    if exp < 100: return "🟤 ทองแดง (Bronze)", "#b45309"
    elif exp < 300: return "⚪ เหล็กกล้า (Iron)", "#94a3b8"
    elif exp < 600: return "🟡 ทองคำ (Gold)", "#f59e0b"
    elif exp < 1000: return "🟣 แพลตตินัม (Platinum)", "#a855f7"
    else: return "💠 เพชร (Diamond)", "#06b6d4"
# ==========================================
# 🚀 4. ฟังก์ชัน AI DATA LINK (สร้าง PROMPT สำเร็จรูป)
# ==========================================
def generate_ai_export_payload(tasks):
    payload = f"📅 STATUS REPORT: {thai_date_format(today_str)}\n"
    payload += "="*60 + "\n"
    payload += "SYSTEM CONTEXT: ฉันต้องการให้คุณทำหน้าที่เป็น 'Personal Tactical AI Agent' ช่วยวิเคราะห์และวางแผนตารางชีวิตให้ฉัน โดยอิงจากทรัพยากรเวลาที่มีจำกัด และภารกิจที่ค้างอยู่ด้านล่างนี้ ช่วยจัด Time-boxing เรียงลำดับความสำคัญ และแนะนำเทคนิคการโฟกัสให้ที\n\n"
    payload += "-"*60 + "\n\n"

    for t in tasks:
        if t.get("is_habit"): t_type = "⛓️ วินัยเหล็ก"
        elif t.get("is_sidequest"): t_type = "🎯 เควสย่อย"
        elif t.get("is_study"): t_type = "📖 การเรียน"
        else: t_type = "🔪 ภารกิจหลัก"

        t_name = t.get("ภารกิจ", "Unknown")
        t_prio = t.get("ประเภท", "ไม่ระบุ")
        t_dead = t.get("deadline", "ไม่มีกำหนด")
        t_desc = t.get("รายละเอียด", "")
        t_must = "[🔥 MUST DO TODAY]" if t.get("is_must_do") else ""

        payload += f"[{t_type}] {t_name} {t_must}\n"
        if not t.get("is_habit") and not t.get("is_sidequest"):
            payload += f"   - ความสำคัญ: {t_prio}\n"
            if str(t_dead).strip(): payload += f"   - Deadline: {t_dead}\n"
        if str(t_desc).strip():
            payload += f"   - รายละเอียด: {t_desc}\n"

        subs = t.get("subtasks", [])
        if subs:
            payload += "   - งานย่อย (Subtasks):\n"
            for s in subs:
                done_mark = "[x]" if s.get("done") else "[ ]"
                payload += f"     * {done_mark} {s.get('name')}\n"
        payload += "\n"

    return payload

def load_db():
    if FIREBASE_URL == "" or FIREBASE_URL is None:
        st.error("🚨 ใส่ลิงก์ Firebase ก่อน!")
        st.stop()
    try:
        res = requests.get(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}")
        if res.status_code == 200 and res.json() is not None:
            data = res.json()
            if not isinstance(data, dict): data = {}
            defaults = {
                "users": {}, "missions": {}, "study_missions": {}, "command_log": {}, "accountability_mirror": {},
                "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, "haters": {}, "finance": {}, "iron_habits": {},
                "daily_wins": {}, "exams": {}, "beat_yesterday": {}, "limit_breaks": {}, "weakness_fuel": {},
                "sanctuary": {}, "skill_forge": {}, "judgment_history": {}, "subjects": {},
                "qa_vault": {}, "side_quests": {}
            }
            for k, v in defaults.items():
                if k not in data or data[k] is None: data[k] = v
            return data
    except Exception as e:
        pass
    return {
        "users": {}, "missions": {}, "study_missions": {}, "command_log": {}, "accountability_mirror": {}, "dopamine_fails": {},
        "excuses": {}, "cookie_jar": {}, "haters": {}, "finance": {}, "iron_habits": {}, "daily_wins": {}, "exams": {},
        "beat_yesterday": {}, "limit_breaks": {}, "weakness_fuel": {}, "sanctuary": {}, "skill_forge": {}, "judgment_history": {},
        "subjects": {}, "qa_vault": {}, "side_quests": {}
    }

def save_db(data):
    try: requests.put(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}", json=data)
    except Exception as e: st.error(f"🚨 เซฟข้อมูลลงฐานข้อมูลไม่สำเร็จ! Error: {e}")

# 🛡️ โหลดฐานข้อมูลทันที!
db = load_db()

# ==========================================
# 3. ข้อมูลคำพูด (QUOTES & MENTORS) 50 ประโยค
# ==========================================
MENTORS = {
    "None": {
        "name": "ไม่มี (วิถีคนเถื่อน)", "icon": "⚔️", "desc": "พึ่งพาแค่สันดานดิบของตัวเอง ไม่มีสกิลบัฟอะไรทั้งนั้น!",
        "quotes": ["1. มึงจะยอมแพ้แค่นี้หรอวะ?", "2. โลกไม่จำคนเกือบสำเร็จ เอาให้สุด!", "3. ไม่มีใครมาช่วยมึงหรอก ลุกขึ้น!", "4. เจ็บจากการมีวินัย หรือเจ็บจากความล้มเหลว เลือกเอา!", "5. ความขี้เกียจมันวางยาพิษอนาคตมึง!", "6. โม้ไว้เยอะ ไหนล่ะผลงาน?", "7. ความสำเร็จสร้างจากเหงื่อและเลือด!", "8. ถ้าวันนี้มึงสบาย พรุ่งนี้มึงชิบหายแน่!", "9. มึงมีข้ออ้างหรือมีเป้าหมายวะ?", "10. หยุดไถมือถือแล้วไปทำงานเดี๋ยวนี้!", "11. พรสวรรค์สู้คนขยันไม่ได้หรอกโว้ย!", "12. มึงหลอกคนอื่นได้ แต่หลอกกระจกไม่ได้!", "13. กัดฟันทำไปดิวะ อย่าบ่น!", "14. คนอ่อนแอไม่มีที่ยืนในโลกความจริง!", "15. ถ้าไม่เริ่มวันนี้ แล้วจะเสร็จชาติไหน!", "16. อนาคตมึงอยู่ในกำมือมึงเอง อย่าให้มันพัง!", "17. เป้าหมายใหญ่แต่ความพยายามกระจอก มันไม่ได้!", "18. ทนเหนื่อยวันนี้ สบายวันหน้า!", "19. พิสูจน์ให้พวกที่ดูถูกมึงเห็นซะ!", "20. วินัยคือสะพานเชื่อมระหว่างเป้าหมายกับความสำเร็จ!", "21. ลุกไปลุยดิวะ นั่งรออะไรอยู่!", "22. เลิกพูดแล้วลงมือทำ!", "23. ร่างกายอาจจะเหนื่อย แต่ใจต้องไม่ยอมแพ้!", "24. หนทางเดียวที่จะรอดคือสู้จนตาย!", "25. ทำให้มันจบๆ ไป จะได้ไปพัก!", "26. อย่าให้ความขี้เกียจมาชนะใจมึงได้!", "27. บีบคั้นตัวเองเข้าไป เลือดกลบปากก็ต้องทน!", "28. วันนี้ยังหายใจอยู่ ก็ห้ามหยุดพยายาม!", "29. แค่งานแค่นี้มึงจะตายหรอวะ?", "30. ไม่มีอะไรได้มาง่ายๆ จำไว้!", "31. พวกขี้แพ้มักจะมีข้ออ้างเสมอ มึงเป็นไหม?", "32. ชนะใจตัวเองให้ได้ก่อนไปชนะคนอื่น!", "33. พรุ่งนี้ไม่มีจริง ทำเดี๋ยวนี้!", "34. ถ้าใจมึงได้ ร่างกายมันก็ตามไปเอง!", "35. เหยียบความกลัวให้จมดินแล้วเดินหน้า!", "36. ฝันให้ไกล แล้วไปให้ถึงด้วยมือมึงเอง!", "37. ล้มกี่ครั้งก็ช่างมัน ลุกขึ้นมาให้ได้แล้วกัน!", "38. มึงน่ะเก่งกว่าที่ตัวเองคิด ลุยเลย!", "39. อย่าให้คำด่าของคนอื่นมากำหนดชีวิตมึง!", "40. สร้างผลงานให้พวกมันหุบปาก!", "41. วินัยเหล็กคืออาวุธของคนจริง!", "42. ไม่เจ็บปวดก็ไม่เติบโต!", "43. เสียเหงื่อวันนี้ ดีกว่าเสียน้ำตาวันหน้า!", "44. ทุกวินาทีมีค่า อย่าทิ้งไปเฉยๆ!", "45. ทำลายขีดจำกัดของตัวเองซะ!", "46. พลังใจคือสิ่งเดียวที่ทำให้มึงไปต่อได้!", "47. ร้องไห้ได้ แต่อย่ายอมแพ้!", "48. พึ่งพาตัวเองให้รอดก่อน!", "49. ชะตาชีวิตมึง มึงขีดเอง!", "50. วันนี้ต้องดีกว่าเมื่อวาน ลุย!"]
    },
    "Jesus": {
        "name": "พระเยซู (Grace)", "icon": "✝️", "desc": "ยอมรับความพ่ายแพ้ลดค่าปรับลง 50% เริ่มต้นใหม่ได้เสมอ",
        "quotes": ["1. บรรดาผู้เหน็ดเหนื่อยและแบกภาระหนัก จงมาหาเราเถิด", "2. เราจะไม่ละทิ้งเจ้า หรือทอดทิ้งเจ้าเลย", "3. จงเข้มแข็งและกล้าหาญเถิด", "4. สันติสุขของเรา เรามอบให้แก่ท่าน อย่ากลัวเลย", "5. ท่านทำทุกสิ่งได้ โดยพระองค์ผู้ประทานกำลัง", "6. ล้มลงเจ็ดครั้ง ก็ลุกขึ้นใหม่ได้", "7. ความรักอดทนนานและกระทำคุณให้", "8. จงฝากความกังวลไว้กับพระองค์", "9. แอกของเราก็พอเหมาะ ภาระของเราก็เบา", "10. อย่ากระวนกระวายถึงวันพรุ่งนี้เลย", "11. เราเป็นความสว่างของโลก", "12. ผู้ที่เชื่อในเราจะมีชีวิตนิรันดร์", "13. จงรักเพื่อนบ้านเหมือนรักตนเอง", "14. แสวงหาแผ่นดินของพระเจ้าก่อน", "15. สันติสุขจงมีแก่ท่าน", "16. จงวางใจในพระยาห์เวห์ด้วยสุดใจ", "17. พระเจ้าทรงเป็นที่ลี้ภัยและเป็นกำลัง", "18. พระคุณของเราก็มีพอสำหรับเจ้า", "19. ผู้ที่รอคอยพระเจ้าจะได้รับกำลังใหม่", "20. จงชื่นชมยินดีเสมอ", "21. อธิษฐานอย่างสม่ำเสมอ", "22. จงขอบพระคุณในทุกกรณี", "23. ความเชื่อก้าวข้ามภูเขาได้", "24. เราอยู่กับเจ้าทั้งหลายเสมอไป", "25. จงเป็นเกลือแห่งแผ่นดินโลก", "26. จงเป็นความสว่างของโลก", "27. บำเหน็จของท่านในสวรรค์นั้นยิ่งใหญ่นัก", "28. จงตื่นตัวและระวังระไว", "29. จงดำเนินชีวิตในความรัก", "30. ผลของพระวิญญาณคือความรัก ความชื่นชมยินดี", "31. สันติสุข สอดส่อง ความปรานี", "32. ความดี ความสัตย์ซื่อ ความสุภาพอ่อนโยน", "33. การรู้จักบังคับตน", "34. จงสวมยุทธภัณฑ์ทั้งชุดของพระเจ้า", "35. ดาบของพระวิญญาณคือพระวจนะของพระเจ้า", "36. จงต่อสู้กับมาร แล้วมันจะหนีไป", "37. เข้าใกล้พระเจ้า แล้วพระองค์จะเข้าใกล้ท่าน", "38. พระเจ้าทรงต่อสู้คนที่หยิ่งจองหอง", "39. ประทานพระคุณแก่คนที่ถ่อมใจ", "40. จงโยนความกังวลทั้งหมดของท่านให้พระองค์", "41. เพราะพระองค์ทรงห่วงใยท่าน", "42. จงมีสติสัมปชัญญะ ระวังระวังให้ดี", "43. ศัตรูของท่านคือมาร", "44. เดินวนเวียนดุจสิงห์คำราม", "45. จงต่อต้านมันด้วยความเชื่อที่มั่นคง", "46. พระเจ้าแห่งพระคุณทั้งสิ้น", "47. จะทรงให้ท่านทั้งหลายตั้งมั่นคง", "48. ทรงให้มีกำลัง และทรงให้มีรากฐานที่มั่นคง", "49. ขออานุภาพจงมีแด่พระองค์ตลอดไป", "50. อาเมน ลุกขึ้นเถิดและก้าวต่อไป"]
    },
    "Zenitsu": {
        "name": "เซนอิทสึ (Godspeed)", "icon": "⚡", "desc": "ทำงานด่วนในโหมด Locked In ลดความกาก 2 เท่า!",
        "quotes": ["1. ฉันไม่ได้มาที่นี่เพื่อคุยเล่น ฉันมาเพื่อจบเรื่องนี้!", "2. เตรียมรับมือกับความเร็วเสียงได้เลย!", "3. โฟกัสแค่สิ่งเดียว ทำให้ทะลุขีดจำกัด!", "4. ฟาดฟันความขี้เกียจด้วยสายฟ้า!", "5. ฉันจะปกป้องสิ่งที่สำคัญด้วยชีวิต!", "6. ปราณอัสนี กระบวนท่าที่ 1 ฟ้าผ่าชั่วพริบตา!", "7. หกเลี้ยว! ฟาดมันให้ยับ!", "8. ความกลัวนี่แหละที่จะทำให้เราเร็วกว่าเดิม!", "9. อย่าลังเล พุ่งออกไปเลย!", "10. หลับตาแล้วเพ่งสมาธิให้ถึงขีดสุด!", "11. หายใจเข้าลึกๆ แล้วปลดปล่อยพลังทั้งหมด!", "12. เสียงของแกมันน่ารำคาญ ฉันจะตัดมันทิ้งซะ!", "13. ถ้ามัวแต่หนี แล้วใครจะจัดการเรื่องนี้ล่ะ!", "14. ฉันทำได้แค่ท่าเดียว เพราะงั้นต้องขัดเกลาให้ถึงที่สุด!", "15. ทะลวงมันเข้าไป อย่าหยุดจนกว่าจะสำเร็จ!", "16. Godspeed! ไม่มีอะไรเร็วกว่านี้อีกแล้ว!", "17. ฉันจะแบกรับความหวังของทุกคนเอง!", "18. แม้จะตัวสั่น แต่ขาก็ยังต้องก้าวไปข้างหน้า!", "19. อย่าให้ปู่ต้องผิดหวังในตัวฉัน!", "20. ฉันไม่ใช่คนขี้ขลาดอีกต่อไปแล้ว!", "21. ดาบของฉันจะฟาดฟันทุกอุปสรรคให้ขาดสะบั้น!", "22. มองเห็นแล้ว เส้นด้ายแห่งช่องโหว่!", "23. จะไม่ยอมแพ้ แม้จะต้องแลกด้วยชีวิต!", "24. สายฟ้าที่ฟาดลงมา จะทำลายทุกความลังเล!", "25. โฟกัสไปที่จุดเดียว แล้วระเบิดพลังออกมา!", "26. ฉันจะต้องแข็งแกร่งขึ้น เพื่อปกป้องเธอ!", "27. ไม่ว่าศัตรูจะเก่งแค่ไหน ฉันก็จะฟาดมันให้ร่วง!", "28. เสียงหัวใจเต้นรัว นี่แหละคือสัญญาณของการเอาจริง!", "29. ความเร็วของฉัน เหนือกว่าการรับรู้ของแกแน่นอน!", "30. อย่าประมาทคนที่กำลังเอาจริงเด็ดขาด!", "31. สายฟ้าแลบ! จบเกม!", "32. ฉันจะไม่ยอมตาย จนกว่าจะทำตามสัญญาได้!", "33. พลังที่ซ่อนอยู่ จงตื่นขึ้นมาเดี๋ยวนี้!", "34. แค่พริบตาเดียว ทุกอย่างก็จะจบลง!", "35. ความตั้งใจของฉัน แน่วแน่ดั่งสายฟ้า!", "36. ไม่มีใครหยุดฉันได้ในโหมดนี้!", "37. เตรียมตัวรับความเจ็บปวดซะ!", "38. ดาบนิจิรินของฉัน จะสะบั้นทุกความเกียจคร้าน!", "39. ฉันทำได้ ฉันต้องทำได้!", "40. อย่าให้ความกลัวครอบงำจิตใจ!", "41. หายใจเพ่งจิตรวมปราณ แล้วพุ่งชน!", "42. ความเร็วคืออาวุธที่อันตรายที่สุด!", "43. ฉันจะพิสูจน์ให้ทุกคนเห็นว่าฉันทำได้!", "44. สายฟ้าจะผ่าลงทัณฑ์พวกคนบาป!", "45. ฉันจะไม่วิ่งหนีอีกต่อไปแล้ว!", "46. ทิ้งความลังเลไว้ข้างหลัง แล้วเดินหน้าต่อไป!", "47. ร่างกายมันขยับไปเอง สัญชาตญาณล้วนๆ!", "48. พลังนี้เพื่อปกป้อง ไม่ใช่เพื่อทำลาย!", "49. โฟกัส! โฟกัส! โฟกัส!", "50. ฉันนี่แหละ คือสายฟ้าที่จะฟาดฟันทุกสิ่ง!"]
    },
    "Yuji": {
        "name": "ยูจิ (Cog)", "icon": "⚙️", "desc": "ติ๊กงานย่อย 1 ข้อ ลดความกาก 2 เท่า",
        "quotes": ["1. ฉันอาจจะไม่เก่งที่สุด แต่ฉันจะเป็นฟันเฟืองที่ไม่หยุดหมุน!", "2. กูไม่รู้ตอนจบจะเป็นไง แต่จะสู้จนหมดลม!", "3. ความตายไม่ใช่ข้ออ้างให้ยอมแพ้!", "4. เจ็บแค่ไหนก็ต้องกัดฟันเดินหน้า!", "5. จะไม่ให้การเสียสละสูญเปล่า!", "6. ก้าวเล็กๆ นี่แหละจะเปลี่ยนโลก!", "7. ฉันจะช่วยทุกคน เท่าที่ทำได้!", "8. ถ้าไม่ทำตอนนี้ แล้วจะไปทำตอนไหน!", "9. พลังไสยเวทอาจไม่มี แต่แรงกายฉันเหลือเฟือ!", "10. ประกายทมิฬ! อัดมันให้กระเด็น!", "11. ฉันจะไม่ยอมแพ้ต่อโชคชะตาบ้าๆ นี่!", "12. ต้องแข็งแกร่งขึ้น เพื่อไม่ให้เสียใครไปอีก!", "13. รับผิดชอบในสิ่งที่ตัวเองเลือก!", "14. ความทรงจำที่มีค่า จะปกป้องมันไว้เอง!", "15. แม้จะต้องเป็นภาชนะของปีศาจ ฉันก็จะทน!", "16. สู้เพื่อการตายที่ถูกต้อง!", "17. กำปั้นนี้ จะซัดทุกความอยุติธรรม!", "18. ไม่ใช่แค่เพื่อตัวเอง แต่เพื่อคนรอบข้างด้วย!", "19. จะไม่ยอมให้ใครต้องมาตายต่อหน้าอีกแล้ว!", "20. ความเจ็บปวดนี้ จะเปลี่ยนเป็นพลัง!", "21. ลุกขึ้นมา! ร่างกายฉัน ลุกขึ้นมาเดี๋ยวนี้!", "22. จะฟันฝ่าความมืดมิดนี้ไปให้ได้!", "23. ไม่ว่าต้องเจอกับอะไร ฉันก็จะรับหน้าเอง!", "24. เป็นฟันเฟืองที่แข็งแกร่งที่สุดในระบบ!", "25. ความหวังยังมีอยู่เสมอ ตราบใดที่ยังไม่ยอมแพ้!", "26. ต่อกรกับคำสาป ด้วยกำลังทั้งหมดที่มี!", "27. จะไม่เสียใจทีหลัง กับสิ่งที่ตัดสินใจลงไป!", "28. วิ่งต่อไป อย่าหยุดจนกว่าจะถึงเป้าหมาย!", "29. แบกรับความคาดหวัง แล้วก้าวไปข้างหน้า!", "30. ถึงจะล้มลง ก็จะคลานต่อไปให้ถึงที่สุด!", "31. พลังใจของมนุษย์ ไม่แพ้คำสาปหรอกนะ!", "32. ฉันนี่แหละ จะเป็นคนจบเรื่องราวนี้เอง!", "33. หมัดคู่ใจ จะเบิกทางไปสู่อนาคต!", "34. ไม่ต้องมีเหตุผลมากมาย แค่ทำในสิ่งที่ควรทำ!", "35. ความมุ่งมั่นของฉัน ไม่มีวันดับสลาย!", "36. จะปกป้องรอยยิ้มของทุกคนเอาไว้!", "37. เตรียมตัวรับแรงกระแทกได้เลย!", "38. ไร้ซึ่งความกลัว มีแต่ความกล้าหาญ!", "39. จะสู้จนกว่าหยดเลือดสุดท้ายจะหยดลงพื้น!", "40. แม้จะต้องเผชิญกับศัตรูที่แข็งแกร่งกว่า ก็จะไม่ถอย!", "41. วิญญาณที่ไม่ยอมแพ้ จะสถิตอยู่ในตัวฉัน!", "42. ข้ามผ่านขีดจำกัดของตัวเองไปให้ได้!", "43. ความทรงจำของคุณปู่ จะเป็นพลังให้ฉัน!", "44. จะเป็นคนดี ที่ช่วยเหลือผู้อื่นเสมอ!", "45. ยิ้มรับความท้าทาย แล้วบดขยี้มันซะ!", "46. พลังแห่งมิตรภาพ จะเอาชนะทุกสิ่ง!", "47. ฉันไม่ใช่คนเดียวที่สู้อยู่ ยังมีเพื่อนๆ อีกมากมาย!", "48. จะเป็นฟันเฟืองที่สำคัญ ขาดไม่ได้!", "49. ลุยเข้าไปให้สุดกำลัง! โฮก!!!", "50. ฉันคือ อิตาโดริ ยูจิ จำชื่อนี้ไว้ให้ดี!"]
    },
    "Gojo": {
        "name": "โกโจ (Limitless)", "icon": "🤞", "desc": "หนี้เลือดถูกจำกัดสูงสุด 100 ที/วัน",
        "quotes": ["1. เรื่องแค่นี้เอง ไม่เป็นไรหรอก เพราะฉันน่ะเก่งที่สุดแล้ว!", "2. ขีดจำกัดมันมีไว้ให้พวกกระจอก!", "3. เหนื่อยหรอ? โทษทีนะ ฉันไม่รู้จัก!", "4. จะยอมแพ้ทำไม ชัยชนะรออยู่ตรงหน้าแล้ว สบายๆ!", "5. ปล่อยให้พวกอ่อนแอหาข้ออ้างไปเถอะ เราแค่ชนะพอ!", "6. ควบคุมตัวเองให้อยู่เหนือทุกอุปสรรค!", "7. มุเก็น (ไร้ขีดจำกัด) กางออก!", "8. กางอาณาเขต พรมแดนไร้เขต! แกจบแค่นี้แหละ", "9. ไสยเวทหมุนกลับ อาคะ (แดง) บดขยี้มันซะ", "10. ไสยเวทหมุนตาม อาโอะ (น้ำเงิน) ดูดกลืนทุกสิ่ง", "11. ท่าไม้ตาย มุราซากิ (ม่วง)! หายไปซะ!", "12. โทษทีนะ พอดีฉันเป็นพวกสมบูรณ์แบบน่ะ", "13. ก็บอกแล้วไงว่าฉันเก่งที่สุด เข้าใจยากตรงไหน?", "14. ระดับมันต่างกันเกินไป อย่าฝืนเลยไอ้น้อง", "15. แค่มองตาฉัน แกก็แพ้แล้ว", "16. อาจารย์มาแล้ว ไม่ต้องห่วง!", "17. การสอนลูกศิษย์ให้เก่งกว่าตัวเอง คือหน้าที่ของฉัน", "18. ความแข็งแกร่งของฉัน มันไร้ขอบเขต", "19. จะโจมตีมาทางไหนก็ไร้ผล มุเก็นกันไว้หมดแล้ว", "20. สนุกหน่อยสิ อย่าเพิ่งรีบตายล่ะ", "21. ตาที่หก (Rokugan) มองทะลุทุกสิ่ง", "22. จะเปลี่ยนแปลงวงการไสยเวทเน่าๆ นี้ให้ดู", "23. เพราะมีฉันอยู่ โลกนี้ถึงยังสมดุล", "24. ยิ้มเข้าไว้ โลกมันไม่ได้เลวร้ายขนาดนั้น", "25. ทำตัวสบายๆ ชิลๆ เดี๋ยวก็ชนะเอง", "26. พรสวรรค์มันต่างกัน ยอมรับซะเถอะ", "27. ฉันจะแบกรับโลกใบนี้ไว้เอง ไหวอยู่แล้ว", "28. อย่าให้ความเศร้ามากลืนกินนายได้ล่ะ", "29. แข็งแกร่งขึ้นซะ จะได้ไม่โดนทิ้งไว้ข้างหลัง", "30. ปล่อยวางบ้าง อย่าตึงเกินไป", "31. พลังที่แท้จริง ไม่ได้มาจากการบีบบังคับ", "32. เป็นตัวของตัวเองให้ดีที่สุดก็พอ", "33. ก้าวข้ามฉันไปให้ได้สิ เหล่าลูกศิษย์ของฉัน", "34. ความตายไม่ใช่จุดจบ แต่มันคือการเริ่มต้นใหม่", "35. ฉันจะไม่ยอมแพ้ต่อโชคชะตาเด็ดขาด", "36. จะสร้างอนาคตที่ทุกคนยิ้มได้", "37. เชื่อมั่นในตัวเอง แล้วลุยเลย!", "38. ไม่มีอุปสรรคไหนที่ฉันข้ามไม่ได้", "39. ฉันคือจุดสูงสุดของยุคนี้ จำไว้ให้ดี", "40. แม้จะต้องสู้คนเดียว ฉันก็ไม่หวั่น", "41. ความเหงาของผู้ที่แข็งแกร่งที่สุด นายไม่เข้าใจหรอก", "42. ทำทุกอย่างด้วยความมั่นใจเกินร้อย", "43. ชัยชนะมันเป็นของฉันตั้งแต่เกิดแล้ว", "44. อย่ามาขวางทางฉัน ถ้าไม่อยากเจ็บตัว", "45. โลกนี้มันช่างน่าเบื่อจริงๆ เลยนะ", "46. หาอะไรสนุกๆ ทำแก้เซ็งดีกว่า", "47. ถึงเวลาโชว์เทพแล้ว จับตาดูให้ดี!", "48. พลังที่ไร้ขีดจำกัด สู่ความเป็นไปได้ที่ไม่มีสิ้นสุด", "49. ทะลวงมิติแหวกกฎเกณฑ์ ฉันทำได้หมด", "50. ฉันคือ โกโจ ซาโตรุ ผู้ที่แข็งแกร่งที่สุดในปฐพี!"]
    },
    "Toji": {
        "name": "โทจิ (Assassin)", "icon": "🐛", "desc": "งาน Boss +30% EXP แต่พลาดโดน x2!",
        "quotes": ["1. ข้ออ้างหรือพรสวรรค์กูไม่สน กูสนแค่ผลลัพธ์!", "2. เงินและอำนาจเป็นของคนที่ลงมือทำ!", "3. โลกนี้มีแค่คนล่า กับคนที่ถูกล่า มึงจะเป็นอะไร?", "4. อย่าบ่นว่าโลกไม่ยุติธรรม มึงแค่กระจอก!", "5. ค่าตัวกูแพง ผลงานกูก็สมราคา!", "6. ไร้พลังเวทแล้วไง? สองมือเนี่ยแหละขยี้ทุกอย่าง!", "7. กูคือ ลิง ที่จะบดขยี้ผู้ใช้คุณไสยให้หมด!", "8. ดาบปลดวิญญาณ ฟันทะลุทุกการป้องกัน!", "9. อาวุธระดับพิเศษ อยู่ในคลังของกูหมดแล้ว", "10. สัญญาสวรรค์ แลกพลังเวทกับร่างกายที่เหนือมนุษย์", "11. ประสาทสัมผัสกู ไวกว่าพวกมึงเป็นร้อยเท่า", "12. จะลอบฆ่าใคร กูไม่เคยพลาด", "13. ความปรานีไม่มีในพจนานุกรมของกู", "14. ผู้แข็งแกร่งคือผู้รอดชีวิต นั่นคือกฎของโลก", "15. อย่ามาขวางทางหาเงินของกู ไอ้สวะ", "16. กูทำทุกอย่างเพื่อผลประโยชน์ของตัวเอง", "17. ตระกูลเซนอิงหรอ? กูทิ้งมันมาตั้งนานแล้ว", "18. พวกมึงมันก็แค่ เหยื่อ ของกูเท่านั้นแหละ", "19. เตรียมตัวตายได้เลย ไม่ทรมานหรอก (มั้ง)", "20. ความเร็วของกู มึงมองตามไม่ทันหรอก", "21. พละกำลังเพียวๆ นี่แหละ ของจริง", "22. อาศัยสัญชาตญาณดิบ ล้วนๆ", "23. ไม่ต้องมีแผน อะไรทั้งนั้น พุ่งเข้าไปฆ่าก็พอ", "24. ปืนพกสั้น จัดการพวกกากๆ ได้สบาย", "25. โซ่หมื่นลี้ จับมึงไว้ไม่ให้หนีไปไหน", "26. แมลงวันหัวเขียว เก็บอาวุธให้กู", "27. กูไม่สนหรอกว่ามึงจะเป็นใคร เก่งแค่ไหน", "28. จ่ายเงินมา แล้วงานจะเสร็จเรียบร้อย", "29. ชีวิตคนเรามันสั้น ใช้ให้คุ้มค่าซะ", "30. อย่าประมาทกูเด็ดขาด ถ้าไม่อยากตายโง่ๆ", "31. กลิ่นคาวเลือด มันช่างหอมหวานเสียจริง", "32. การต่อสู้คือศิลปะ ที่กูถนัดที่สุด", "33. บดขยี้ความหวังของพวกมึง ให้แหลกสลาย", "34. กูคือฝันร้าย ที่จะตามหลอกหลอนพวกมึง", "35. ความมืดมิด คือเพื่อนซี้ของกู", "36. แฝงตัวในเงามืด แล้วโจมตีทีเผลอ", "37. จุดอ่อนของพวกมึง กูเห็นหมดแล้ว", "38. แทงทะลุหัวใจ จบเกมอย่างสวยงาม", "39. กูไม่ต้องการความช่วยเหลือจากใคร", "40. ยืนหยัดด้วยลำแข้งของตัวเอง นี่แหละลูกผู้ชาย", "41. ฝากดูแลลูกกูด้วยล่ะ... เมกุมิ", "42. ความพ่ายแพ้ครั้งนี้ กูจะจดจำไว้", "43. แม้ความตายจะมาเยือน กูก็ไม่กลัว", "44. ใช้ชีวิตบนเส้นด้าย สนุกดีออก", "45. อันตรายแค่ไหน กูก็พร้อมลุยเสมอ", "46. หัวใจที่เย็นชา ดั่งน้ำแข็ง", "47. ไร้ซึ่งความรู้สึก ไร้ซึ่งความผูกพัน", "48. ทำตามสัญชาตญาณนักล่า อย่างเต็มรูปแบบ", "49. ฟุชิงุโระ โทจิ ชื่อนี้มึงต้องจดจำไปจนวันตาย", "50. เตรียมรับมือกับความโหดร้ายของโลกใบนี้ซะ!"]
    },
    "Subaru": {
        "name": "ซุบารุ (Return by Death)", "icon": "⏪", "desc": "เลื่อน Deadline เป็นวันนี้ จ่าย 10 EXP",
        "quotes": ["1. กูรู้ว่ากูมันกาก แต่กูก็จะกัดฟันทำให้ได้!", "2. ถ้าหนีตอนนี้ ทุกอย่างจะสูญเปล่า ไม่มีทางหรอก!", "3. ล้มกี่ร้อยครั้งก็ช่าง ขอแค่ครั้งสุดท้ายยืนได้ก็พอ!", "4. เพื่อเป้าหมาย ตายกี่สิบหนก็จะคลานกลับมาทำ!", "5. ความสิ้นหวังหรอ? กูชินกับมันแล้ว เข้ามาเลย!", "6. กูเริ่มจากติดลบ แต่กูจะปีนขึ้นไปให้ได้!", "7. เอมิเลียตัน ฉันจะปกป้องเธอเอง!", "8. เรม ขอบใจนะที่เชื่อมั่นในตัวฉันเสมอ", "9. กลับจากความตาย (Return by Death)! กูจะแก้ไขมัน!", "10. ความทรงจำที่มีแต่ฉันที่จำได้ มันช่างเจ็บปวด", "11. แต่ฉันจะไม่ยอมให้ความตายของทุกคนต้องสูญเปล่า", "12. กูมันอ่อนแอ ไร้พลังเวท แต่กูมีสมองและลูกบ้า!", "13. ใช้ข้อมูลจากลูปที่แล้ว วางแผนให้รัดกุมที่สุด!", "14. บาปแห่งความเย่อหยิ่ง กูจะบดขยี้มันซะ!", "15. แม่มดแห่งความริษยา ปล่อยกูไปสักทีเถอะ!", "16. ฉันคือ นัตสึกิ ซุบารุ อัศวินของเอมิเลีย!", "17. จะทลายกำแพงแห่งโชคชะตา นี้ให้ดู", "18. ต่อให้ต้องแบกรับความเจ็บปวดทั้งหมดไว้คนเดียว", "19. เพื่อรอยยิ้มของทุกคน ฉันยอมทนได้!", "20. ความมืดมิดในใจ ฉันจะเอาชนะมันให้ได้!", "21. อย่าดูถูกมนุษย์ธรรมดาอย่างกูนะเว้ย!", "22. ปาฏิหาริย์ ฉันจะสร้างมันขึ้นมาด้วยมือของฉันเอง!", "23. ไม่ว่าจะกี่ลูป ฉันก็จะไม่ยอมแพ้!", "24. น้ำตาที่ไหลออกมา จะเป็นพลังผลักดันให้ก้าวต่อไป", "25. ความผิดพลาดสอนให้เราแข็งแกร่งขึ้น", "26. ฉันเกลียดตัวเองที่อ่อนแอ แต่ฉันก็จะพยายามเปลี่ยนแปลง!", "27. ขอบคุณที่สอนให้ฉันรู้จักความรักนะ เรม", "28. เสียงเรียกร้องของหัวใจ บอกให้ฉันสู้ต่อ!", "29. ดาบที่มองไม่เห็น ฉันจะหลบมันให้พ้น!", "30. เอาชนะวาฬขาว ด้วยพลังของทุกคนร่วมกัน!", "31. เบียทริซ ออกมาเถอะ ฉันจะจับมือเธอไว้เอง!", "32. คำสัญญาที่ให้ไว้ จะต้องรักษาให้ได้!", "33. อนาคตที่สดใส รอเราอยู่ข้างหน้า!", "34. กูจะไม่ยอมให้เรื่องเลวร้ายแบบนี้เกิดขึ้นอีก!", "35. ทุกความตาย มีความหมายซ่อนอยู่เสมอ", "36. ใช้ความตายเป็นบทเรียน เพื่อก้าวไปสู่ความสำเร็จ", "37. จิตใจที่บอบช้ำ แต่ไม่เคยแตกสลาย", "38. ความกล้าหาญที่แท้จริง คือการเผชิญหน้ากับความกลัว", "39. ฉันจะเขียนตอนจบของเรื่องราวนี้ด้วยตัวเอง!", "40. แม้โลกทั้งใบจะหันหลังให้ฉัน ฉันก็จะสู้ต่อไป!", "41. อุปสรรคมีไว้ให้พุ่งชน ไม่ใช่ให้หลบหนี", "42. ความหวังอันริบหรี่ แต่ก็ยังคงส่องสว่างอยู่ในใจ", "43. ฉันจะแสดงให้เห็น ว่าคนธรรมดาก็สร้างปาฏิหาริย์ได้!", "44. เสียงหัวใจที่เต้นอย่างรุนแรง บ่งบอกถึงการมีชีวิต", "45. ฉันจะไม่ยอมตาย จนกว่าจะทำเป้าหมายให้สำเร็จ!", "46. พลังใจที่ไม่มีวันหมด นี่แหละคืออาวุธที่แข็งแกร่งที่สุด", "47. จะจดจำทุกความรู้สึกไว้ เพื่อเป็นแรงผลักดัน", "48. ความรักคือพลังที่ทำให้มนุษย์ทำสิ่งที่เป็นไปไม่ได้", "49. ขอบคุณที่อยู่เคียงข้างฉันมาตลอดนะ ทุกคน", "50. นัตสึกิ ซุบารุ จะไม่ยอมให้ชีวิตนี้ต้องสูญเปล่าแน่นอน!"]
    },
    "Ippo": {
        "name": "อิปโป (Dempsey Roll)", "icon": "🥊", "desc": "หากทำวินัย 100% Streak จะไม่ขาดแม้พลาดงาน",
        "quotes": ["1. ซ้อมพื้นฐานซ้ำๆ จนฝังในสายเลือด!", "2. ไม่เก่งเท่าคนอื่น แต่ความพยายามต้องไม่แพ้ใคร!", "3. เหงื่อตอนซ้อม จะเป็นพลังตอนลงสนาม!", "4. แย็บหมื่นครั้ง ก็ล้มศัตรูได้!", "5. อย่ายอมแพ้จนกว่าระฆังจะดัง! ก้าวเท้าออกไป!", "6. ความกลัวมีทุกคน แต่ความกล้าแยกผู้ชนะออกจากผู้แพ้!", "7. ท่าไม้ตาย Dempsey Roll เริ่มทำงาน!", "8. ก้าวซ้ายไปข้างหน้า แล้วเหวี่ยงหมัดขวาเต็มแรง!", "9. สวิงหมัด ซ้ายขวา ต่อเนื่องไม่หยุด!", "10. ประธานค่ายคาโมงาวะ สอนผมมาดี!", "11. ทาคาซามูระซัง คือไอดอลของผม!", "12. หมัดฮุก คตทสึ! กระแทกซี่โครงให้หัก!", "13. กาเซลพั้นช์! เสยปลายคางให้ร่วง!", "14. พีคกะบู สไตล์! ป้องกันให้แน่นหนา!", "15. สายตาจับจ้องไปที่คู่ต่อสู้ อย่าละสายตา!", "16. อ่านจังหวะ แล้วสวนกลับทันที!", "17. ความหนักแน่นของหมัด มาจากร่างกายส่วนล่าง!", "18. วิ่งรอบสวนสาธารณะ สร้างความอึด!", "19. ตีลูกปิงปอง ฝึกสายตาและปฏิกิริยาตอบสนอง!", "20. ชกกระสอบทราย ให้หนักหน่วงที่สุด!", "21. ล่อเป้ากับประธาน ให้เป๊ะทุกจังหวะ!", "22. ก้าวเดินสายแชมป์เปี้ยน มันไม่ง่ายเลย", "23. แต่ผมจะทำให้ได้ เพื่อตอบแทนทุกคนที่เชียร์ผม!", "24. บนสังเวียน มีแค่ผมกับคู่ต่อสู้เท่านั้น", "25. ตัดขาดจากโลกภายนอก โฟกัสแค่การต่อสู้", "26. เสียงเชียร์ของคนดู คือพลังใจชั้นยอด!", "27. มิยาตะคุง ฉันจะตามนายให้ทัน!", "28. เซนโดซัง มาสู้กันให้รู้ผลไปเลย!", "29. โวลคุง ฉันจะไม่ยอมแพ้นายหรอกนะ!", "30. ดาเตะซัง ผมจะสืบทอดเจตนารมณ์ของคุณเอง!", "31. ความพ่ายแพ้ สอนให้รู้ว่าผมยังอ่อนหัด", "32. เอาความเจ็บใจ มาเป็นแรงผลักดันให้ซ้อมหนักขึ้น!", "33. แผลแตก เลือดไหล ก็หยุดผมไม่ได้!", "34. กัดฟันแน่น แล้วสู้จนหยดสุดท้าย!", "35. จิตวิญญาณแห่งนักมวย ลุกโชนอยู่ในอก!", "36. นักชกมืออาชีพ ต้องมีความรับผิดชอบ!", "37. ดูแลร่างกายให้พร้อมเสมอ สำหรับแมตช์ต่อไป!", "38. ศึกษาเทคนิคของคู่แข่ง เพื่อหาจุดอ่อน!", "39. สร้างกล้ามเนื้อ ให้แข็งแกร่งดั่งเหล็กกล้า!", "40. ความเร็ว ความแม่นยำ ความหนักหน่วง ต้องมีครบ!", "41. จิตใจที่สงบ จะทำให้มองเห็นทุกการเคลื่อนไหว", "42. ระเบิดพลังออกมา ในจังหวะที่เหมาะสมที่สุด!", "43. หมัดน็อคเอาท์ คือเป้าหมายสูงสุด!", "44. แบกรับความฝันของทุกคน ขึ้นไปบนเวที!", "45. ฉันรักมวยสากลที่สุดเลย!", "46. ก้าวเท้า ซ้าย ขวา ซ้าย ขวา ไปเรื่อยๆ!", "47. อย่าปล่อยให้ความท้อแท้ เข้ามาครอบงำจิตใจ!", "48. พรุ่งนี้ต้องดีกว่าวันนี้ แน่นอน!", "49. มาคุโนอุจิ อิปโป พร้อมลุยแล้วครับ!", "50. ขอบคุณทุกคน ที่สนับสนุนผมมาตลอด!"]
    },
    "Future You": {
        "name": "นักรบจากอนาคตอีก 20 ปี", "icon": "⏳", "desc": "เคลียร์งานด่วนรับโบนัส +20 แต่ถ้าดองงานกาก x2!",
        "quotes": ["1. กูคือตัวมึงในอีก 20 ปีข้างหน้า อยากเป็นไอ้ขี้แพ้หรือคนสำเร็จ เลือก!", "2. เหงื่อมึงวันนี้ คือเงินล้านของกู ลุยดิ!", "3. จะฆ่าอนาคตตัวเองด้วยความขี้เกียจชั่วคราวหรอ ตื่น!", "4. เวลาที่เสียไปกับการไถฟีด มันเอากลับคืนมาไม่ได้!", "5. กูไม่อยากให้มึงเสียใจเหมือนพวกลูซเซอร์ ทำเดี๋ยวนี้!", "6. อนาคตไม่ได้ถูกกำหนดด้วยโชค แต่มันสร้างจากตอนนี้!", "7. อย่าให้กูต้องมานั่งเสียดายเวลา ที่มึงทิ้งไปวันๆ", "8. มึงรู้ไหมว่าถ้ามึงตั้งใจตั้งแต่ตอนนี้ ชีวิตกูจะสบายแค่ไหน?", "9. เลิกผลัดวันประกันพรุ่งซะที กูเบื่อที่จะรอแล้ว!", "10. ความล้มเหลวของมึงในวันนี้ คือบทเรียนอันล้ำค่าของกู", "11. แต่อย่าล้มบ่อยเกินไปล่ะ กูขี้เกียจตามเช็ดตามล้าง", "12. ลงทุนกับตัวเองให้มากๆ ความรู้คืออาวุธที่ดีที่สุด", "13. สร้างคอนเนคชั่นไว้ด้วย โลกนี้มันไม่ได้อยู่คนเดียว", "14. รักษาสุขภาพให้ดีๆ กูไม่อยากแก่ไปแล้วมีแต่โรคภัยเบียดเบียน", "15. เก็บเงินออมเงินซะบ้าง กูไม่อยากเป็นคนแก่ที่ไม่มีจะกิน", "16. กล้าที่จะเสี่ยง อย่ามัวแต่กลัวความล้มเหลว", "17. ออกจาก Comfort Zone ไปเผชิญหน้ากับโลกกว้าง", "18. เรียนรู้ภาษาใหม่ๆ เพิ่มโอกาสให้ชีวิต", "19. อ่านหนังสือให้เยอะๆ เปิดโลกทัศน์ให้กว้างไกล", "20. ตั้งเป้าหมายให้ชัดเจน แล้วพุ่งชนมันให้เต็มแรง", "21. วินัยคือสะพานเชื่อมระหว่างความฝันกับความจริง", "22. อย่าปล่อยให้ความขี้เกียจ มาทำลายอนาคตที่สดใส", "23. เชื่อมั่นในตัวเอง มึงทำได้ดีกว่าที่คิดเสมอ", "24. รักษาความสัมพันธ์กับครอบครัวและเพื่อนฝูงให้ดี", "25. หาเวลาพักผ่อนบ้าง อย่าตึงจนเกินไป", "26. แต่เวลาทำงานก็ต้องทำให้สุด อย่าเหยียบขี้ไก่ไม่ฝ่อ", "27. เรียนรู้ที่จะให้อภัย ทั้งตัวเองและผู้อื่น", "28. ปล่อยวางเรื่องที่ควบคุมไม่ได้ โฟกัสแค่สิ่งที่ทำได้", "29. ใช้ชีวิตให้มีความสุข ในทุกๆ วัน", "30. อย่าเอาตัวเองไปเปรียบเทียบกับใคร ทุกคนมีเส้นทางของตัวเอง", "31. กตัญญูต่อผู้มีพระคุณ", "32. ช่วยเหลือสังคม เมื่อมีโอกาส", "33. สร้างมรดกทิ้งไว้ให้คนรุ่นหลัง", "34. ให้ชีวิตของมึง เป็นแรงบันดาลใจให้ผู้อื่น", "35. อย่าลืมความฝันในวัยเด็ก ทำให้มันเป็นจริงซะ", "36. ฟังเสียงหัวใจตัวเอง แล้วทำตามมัน", "37. อย่าปล่อยให้คนอื่น มากราบบังคับชีวิตมึง", "38. จงเป็นผู้กำกับชีวิตตัวเอง ไม่ใช่แค่ตัวประกอบ", "39. สร้างอนาคตที่มึงภาคภูมิใจ ด้วยสองมือของมึงเอง", "40. กูเชื่อมั่นในตัวมึงนะ ไอ้หนู", "41. มึงคือความหวังเดียวของกู อย่าทำให้กูผิดหวังล่ะ", "42. สู้ให้เต็มที่ เพื่อชีวิตที่ดียิ่งขึ้น", "43. ทุกการกระทำ มีผลตามมาเสมอ เลือกให้ดี", "44. ชีวิตนี้มีแค่ครั้งเดียว ใช้มันให้คุ้มค่าที่สุด", "45. อย่าให้ความเสียใจ มากัดกินจิตใจในภายหลัง", "46. ทำวันนี้ให้ดีที่สุด เพื่อพรุ่งนี้ที่สดใส", "47. กูรอความสำเร็จของมึงอยู่นะ รีบๆ ตามมาล่ะ", "48. ความพยายาม ไม่เคยทรยศใคร จำไว้", "49. ทะยานสู่ความสำเร็จ ไปให้สุดขอบฟ้า", "50. ขอบคุณนะ ที่ไม่ยอมแพ้ และสู้มาจนถึงตอนนี้!"]
    }
}

PUNISHMENTS = ["1. ไปดันพื้น 50 ทีเดี๋ยวนี้!", "2. แพลงก์ 2 นาที!", "3. ลุกไปอาบน้ำเย็นจัด 5 นาทีเดี๋ยวนี้ ไป!", "4. กระโดดตบ 100 ครั้ง สลัดความขี้เกียจทิ้งไป!", "5. ห้ามจับมือถือ 1 ชั่วโมงนับจากนี้! นั่งสมาธิทบทวนความกากของตัวเอง!", "6. สควอช (ลุกนั่ง) 60 ที เอาให้ขาเบิร์น!", "7. เดินไปตะโกนใส่กำแพงว่า 'กูจะไม่ยอมกลับไปกระจอกอีก!' 10 รอบ!", "8. Burpee 30 ครั้ง ห้ามหยุดพัก! ลุย!", "9. วิดพื้นจนกว่าจะหมดแรง (Failure) เพื่อจำความรู้สึกของการยอมแพ้!", "10. เก็บกวาดห้องหรือโต๊ะทำงานเดี๋ยวนี้!", "11. วิ่งรอบบ้าน 10 รอบ ห้ามเดินเด็ดขาด!", "12. ลุกนั่ง (Sit-up) 50 ครั้ง", "13. ยืนขาเดียว หลับตา 3 นาที", "14. คัดลายมือคำว่า 'วินัย' 100 จบ", "15. งดขนมหวานและน้ำอัดลม 1 สัปดาห์", "16. ตื่นเช้ากว่าเดิม 1 ชั่วโมง เป็นเวลา 3 วันติด!", "17. อ่านหนังสือที่มีประโยชน์ 1 บท", "18. ยกของหนักๆ เดินไปมา 5 นาที!", "19. ทำความสะอาดห้องน้ำให้สะอาดเอี่ยมอ่อง!", "20. ล้างจานทุกใบในบ้าน", "21. ซักผ้าด้วยมือ 1 กะละมัง", "22. นั่งคุกเข่า สำนึกผิด 10 นาที", "23. ห้ามดูทีวี/ซีรีส์/อนิเมะ 1 วันเต็ม!", "24. ปิดการแจ้งเตือนโซเชียลมีเดียทุกแอป 24 ชั่วโมง!", "25. เขียนเรียงความ 1 หน้ากระดาษ อธิบายว่าทำไมถึงหลุดวินัย", "26. เดินขึ้นลงบันได 20 รอบ", "27. กระโดดเชือก 500 ครั้ง", "28. โหนบาร์ (Pull-up) ให้ได้มากที่สุดเท่าที่จะทำได้!", "29. ทำ High Knees (วิ่งยกเข่าสูง) 3 นาที ต่อเนื่อง!", "30. ทำ Mountain Climbers 100 ครั้ง เร่งจังหวะให้เร็วที่สุด!", "31. ยืนกางแขน ถือหนังสือหนักๆ ไว้ข้างละเล่ม นาน 2 นาที!", "32. ดื่มน้ำเปล่ารวดเดียว 2 แก้ว", "33. กินผักใบเขียวที่ไม่ชอบ 1 จานเต็มๆ!", "34. ห้ามบ่น ห้ามสบถ เป็นเวลา 24 ชั่วโมง!", "35. ยิ้มให้กับตัวเองในกระจก 1 นาที ฝืนใจทำให้ได้!", "36. พูดคำว่า 'ขอบคุณ' กับสิ่งรอบตัว 10 อย่าง!", "37. บริจาคเงิน (จำนวนตามเหมาะสม) ให้กับองค์กรการกุศล", "38. ทิ้งของที่ไม่จำเป็นในห้อง 3 ชิ้น", "39. จัดตารางเวลาชีวิตของวันพรุ่งนี้ให้ละเอียดถยิบ!", "40. เขียนเป้าหมายระยะสั้น 3 ข้อ แล้วแปะไว้ที่หน้าคอม!", "41. โทรไปหาคนที่เคารพ แล้วบอกว่า 'ผมจะตั้งใจทำให้ดีที่สุด'!", "42. ถอดแอปพลิเคชันที่กินเวลาทิ้งไป 1 แอป เป็นเวลา 1 สัปดาห์!", "43. ทำ Plank Jacks 50 ครั้ง", "44. ทำ Wall Sit (นั่งพิงกำแพงลม) 2 นาที", "45. ทำ Lunges สลับขา 40 ครั้ง", "46. งดพูดคุยเรื่องไร้สาระกับเพื่อน 1 วัน!", "47. ตั้งใจเรียน/ทำงานอย่างเต็มที่ 100% เป็นเวลา 2 ชั่วโมง", "48. เขียนข้อดีของตัวเอง 5 ข้อ", "49. กอดตัวเอง แล้วบอกว่า 'เริ่มใหม่ได้เสมอ'!", "50. วิดพื้นเพิ่มอีก 10 ที เป็นโบนัสของการทำโทษ!"]

WARRIOR_OATHS = ["1. โลกนี้ไม่มีที่ยืนให้คนอ่อนแอ! ถ้าขี้เกียจ ก็เตรียมดูคนอื่นแซงหน้าไปเลย!", "2. ข้ออ้างมีไว้สำหรับไอ้กระจอก! วันนี้มึงจะสร้างผลงาน หรือข้ออ้าง เลือกเอา!", "3. ความสบายวันนี้ คือความชิบหายวันหน้า! บดขยี้ความขี้เกียจซะ!", "4. เวลาไม่เคยรอใคร ไถมือถือโง่ๆ คือฆ่าอนาคตตัวเอง!", "5. มึงบอกอยากสำเร็จ แต่การกระทำเหมือนคนรอวันตาย! ตื่น ไปทำเดี๋ยวนี้!", "6. วินัยคือการทำตอนที่มึงโคตรไม่อยากทำต่างหาก!", "7. เป้าหมายใหญ่ แต่พยายามกระจอก! เปลี่ยนแปลงตัวเองเดี๋ยวนี้!", "8. คนบอกพรุ่งนี้ค่อยทำ คือคนที่ไม่มีวันพรุ่งนี้ให้สำเร็จ!", "9. หยาดเหงื่อวันนี้ คือความสำเร็จในวันพรุ่งนี้!", "10. ฉันจะไม่ยอมแพ้ ต่อให้อุปสรรคจะใหญ่แค่ไหนก็ตาม!", "11. ทุกก้าวที่เดินไปข้างหน้า คือการเข้าใกล้เป้าหมายอีกก้าว!", "12. ความล้มเหลวไม่ใช่จุดจบ แต่มันคือจุดเริ่มต้นของความสำเร็จ!", "13. ฉันจะแข็งแกร่งขึ้น ทั้งร่างกายและจิตใจ!", "14. ไม่มีใครมากำหนดชีวิตฉันได้ นอกจากตัวฉันเอง!", "15. ความสำเร็จ ไม่ได้มาเพราะโชคช่วย แต่มาจากการลงมือทำ!", "16. ฉันจะทำลายทุกขีดจำกัด ของตัวเองให้พินาศ!", "17. เสียงนกเสียงกา จะไม่ทำให้ฉันหวั่นไหว!", "18. ฉันโฟกัสแค่เป้าหมายเท่านั้น สิ่งเร้าอื่นไม่มีผล!", "19. วินัยเหล็ก จะหล่อหลอมให้ฉันเป็นยอดคน!", "20. ฉันจะสู้จนกว่าจะหมดลมหายใจ เพื่อสิ่งที่ฝัน!", "21. ความเกียจคร้าน คือศัตรูตัวฉกาจ ฉันจะฆ่ามันให้ตาย!", "22. ทุกๆ วัน ฉันต้องพัฒนาตัวเองให้ดีขึ้น 1%!", "23. ความเจ็บปวดในวันนี้ คือความแข็งแกร่งในวันพรุ่งนี้!", "24. ฉันจะไม่ยอมให้ใคร มาดูถูกความพยายามของฉัน!", "25. โลกใบนี้ เป็นของคนที่กล้าลงมือทำเท่านั้น!", "26. ความฝันมันจะไม่มีวันเป็นจริง ถ้าฉันเอาแต่นอน!", "27. ฉันจะใช้ชีวิต ให้คุ้มค่าทุกวินาที!", "28. พรุ่งนี้ต้องดีกว่าวันนี้ นี่คือสัจธรรมของฉัน!", "29. พลังใจของฉัน ยิ่งใหญ่กว่าอุปสรรคใดๆ!", "30. ฉันจะพิสูจน์ให้ทุกคนเห็น ว่าฉันทำได้!", "31. ความสำเร็จ มันรอฉันอยู่แค่เอื้อมมือ!", "32. ฉันจะไม่หยุดเดิน จนกว่าจะถึงเส้นชัย!", "33. เหงื่อทุกหยด น้ำตาแห่งความเหนื่อยล้า จะกลายเป็นเพชรเม็ดงาม!", "34. ฉันคือผู้สร้างโชคชะตาของตัวเอง ไม่ใช่ผู้ถูกกระทำ!", "35. ความมุ่งมั่นของฉัน ร้อนแรงดั่งเปลวเพลิง!", "36. ฉันจะเหยียบย่ำความกลัว แล้วก้าวเดินต่อไปอย่างสง่างาม!", "37. อุปสรรค คือแบบทดสอบความแข็งแกร่งของจิตใจฉัน!", "38. ฉันจะไม่ยอมอ่อนข้อ ให้กับความอ่อนแอของตัวเอง!", "39. ฉันมีศักยภาพที่ซ่อนอยู่ และฉันจะระเบิดมันออกมา!", "40. ทุกความท้าทาย คือโอกาสในการเรียนรู้และเติบโต!", "41. ฉันจะสร้างประวัติศาสตร์ หน้าใหม่ให้กับชีวิตของฉัน!", "42. ความสำเร็จของฉัน จะเป็นแรงบันดาลใจให้กับผู้อื่น!", "43. ฉันจะไม่ยอมเป็นแค่ คนธรรมดาที่ไม่มีใครจดจำ!", "44. ฉันจะทิ้งร่องรอยแห่งความยิ่งใหญ่ ไว้บนโลกใบนี้!", "45. จิตวิญญาณแห่งนักรบ ไหลเวียนอยู่ในสายเลือดของฉัน!", "46. ฉันพร้อมที่จะเผชิญหน้า กับทุกสิ่งที่จะเข้ามาในวันนี้!", "47. พลังแห่งความเชื่อมั่น จะนำพาฉันไปสู่ชัยชนะ!", "48. ฉันคือผู้กุมชะตาชีวิต ของตัวฉันเองแต่เพียงผู้เดียว!", "49. วันนี้ ฉันจะสร้างตำนานบทใหม่!", "50. ลุยเลย! ตัวฉันในอนาคตกำลังรอคอยความสำเร็จนี้อยู่!"]

WARRIOR_CONSEQUENCES = ["1. กูจะต้องทนเห็นคนที่พยายามน้อยกว่ากู ได้ดีกว่ากู!", "2. พรุ่งนี้กูก็จะตื่นมาเป็นไอ้ขี้แพ้คนเดิม ที่เก่งแต่ปาก!", "3. ความฝันที่กูโม้ไว้ ก็จะเป็นแค่อากาศธาตุ!", "4. กูจะกลายเป็นภาระของครอบครัวและคนที่รักกู!", "5. ชีวิตกูก็จะย่ำอยู่กับที่ ไม่มีวันเงยหน้าอ้าปากได้!", "6. กูจะต้องก้มหัวให้คนที่กูเกลียดไปตลอดชีวิต!", "7. อนาคตที่กูวาดฝันไว้ จะพังทลายลงด้วยมือของกูเอง!", "8. กูจะต้องเสียใจและเกลียดตัวเองในอีก 5 ปีข้างหน้า!", "9. กูจะไม่มีวันภูมิใจในตัวเองได้เลย ตลอดชีวิต!", "10. ความเจ็บปวดจากความล้มเหลว จะตามหลอกหลอนกูไปจนตาย!", "11. คนที่เคยดูถูกกู จะหัวเราะเยาะกูได้เต็มปาก!", "12. โอกาสดีๆ จะหลุดลอยไปตกอยู่ในมือของคนอื่น!", "13. กูจะต้องทนทำงานที่ไม่ได้รัก ไปตลอดชีวิต!", "14. ความยากจนและความขัดสน จะกลายเป็นเพื่อนสนิทกู!", "15. ลูกหลานกู จะต้องเกิดมาเจอกับความลำบาก!", "16. กูจะสูญเสียความน่าเชื่อถือ ไม่มีใครเชื่อคำพูดกูอีก!", "17. กูจะต้องทนเห็นคนที่กูรัก ต้องตกระกำลำบากเพราะความขี้เกียจของกู!", "18. กูจะกลายเป็น ตัวตลก ในสายตาของสังคม!", "19. ความอิจฉาริษยา จะกัดกินจิตใจกู จนเน่าเฟะ!", "20. กูจะไม่มีวันได้สัมผัส กับคำว่า ความสำเร็จ อย่างแท้จริง!", "21. กูจะต้องแก่ตายไป อย่างโดดเดี่ยวและไร้ค่า!", "22. ประวัติศาสตร์ จะจารึกชื่อกูไว้ในฐานะ คนขี้แพ้!", "23. กูจะสูญเสียเวลาอันมีค่า ที่ไม่สามารถย้อนกลับคืนมาได้!", "24. สุขภาพกูจะย่ำแย่ เพราะไม่ได้ดูแลตัวเองอย่างดี!", "25. ความสัมพันธ์กับคนรอบข้าง จะพังทลายลง!", "26. กูจะถูกสังคมทอดทิ้ง ให้อยู่เบื้องหลัง!", "27. กูจะไม่มีวัน ได้เติมเต็มศักยภาพของตัวเอง!", "28. กูจะต้องทนอยู่กับ ความรู้สึกผิด ไปจนวันตาย!", "29. โลกนี้ จะไม่รับรู้ถึงการมีอยู่ของกูเลย!", "30. กูจะกลายเป็น แค่ฝุ่นผงในจักรวาล ไม่มีค่าอะไร!", "31. ความสามารถกูจะถดถอย ลงเรื่อยๆ ตามกาลเวลา!", "32. กูจะถูกเด็กรุ่นใหม่ แซงหน้าไปอย่างง่ายดาย!", "33. กูจะต้องพึ่งพาจมูกคนอื่นหายใจ ไปตลอดชีวิต!", "34. กูจะไม่มีสิทธิ์ เลือกทางเดินชีวิตของตัวเองได้!", "35. กูจะต้องยอมรับ สภาพความเป็นอยู่ที่เลวร้าย อย่างหลีกเลี่ยงไม่ได้!", "36. กูจะสูญเสีย อิสรภาพ ทางการเงินและเวลา!", "37. ความคิดสร้างสรรค์กู จะถูกแช่แข็งและตายจากไป!", "38. กูจะกลายเป็น หุ่นยนต์ ที่ทำตามคำสั่งของคนอื่น!", "39. กูจะไม่มีวัน ได้ค้นพบความหมายที่แท้จริงของชีวิต!", "40. รอยยิ้มของกู จะหายไปจากใบหน้าอย่างถาวร!", "41. กูจะต้องทนฟัง คำด่าทอและคำวิจารณ์ จากคนรอบข้าง!", "42. กูจะสูญเสีย ความเคารพในตัวเอง ไปอย่างหมดสิ้น!", "43. กูจะกลายเป็น ภาระของโลกใบนี้!", "44. ชีวิตกู จะเต็มไปด้วยความเสียดายและคำว่า รู้งี้!", "45. กูจะไม่มีวัน ได้ชื่นชมผลงานของตัวเองอย่างภาคภูมิใจ!", "46. กูจะต้องใช้ชีวิต ด้วยความหวาดระแวงและกังวลอยู่เสมอ!", "47. กูจะสูญเสีย เสน่ห์และความมั่นใจในตัวเอง!", "48. กูจะกลายเป็น คนแปลกหน้า สำหรับตัวเองในที่สุด!", "49. ความหวังทุกอย่าง จะดับวูบลงอย่างไม่มีวันหวนกลับ!", "50. กูจะตายไป พร้อมกับความว่างเปล่าในจิตใจ!"]

ETERNAL_ECHOES = ["1. มึงบอกว่าไม่อยากกากอีกแล้ว มึงทำตัวให้คู่ควรกับคำพูดรึยัง!?", "2. โลกไม่สนหรอกว่ามึงจะเหนื่อย โลกสนแค่ว่ามึงทำสำเร็จหรือเปล่า!", "3. ทุกวินาทีที่ขี้เกียจ คือการกลับไปเป็นขี้แพ้!", "4. จะเก่งได้ไงถ้ามึงเอาแต่หาข้ออ้าง ลุกขึ้นมา!", "5. Pain is temporary, quitting lasts forever!", "6. They don't know you son! Show them what you're made of!", "7. Stay hard! อย่าให้ปีศาจในหัวมึงชนะได้!", "8. มึงหลอกคนอื่นได้ แต่มึงหลอกตัวเองหน้ากระจกไม่ได้หรอกนะ!", "9. อย่าให้ความกลัว ขโมยความฝันของมึงไป!", "10. ความสำเร็จสร้างด้วยมือ ไม่ใช่ด้วยน้ำลาย!", "11. ถ้ามึงไม่สร้างฝันของตัวเอง คนอื่นก็จะจ้างมึงไปสร้างฝันของเขา!", "12. ล้มได้ ร้องไห้ได้ แต่มึงห้ามยอมแพ้เด็ดขาด!", "13. หนทางที่ยากลำบาก มักจะนำไปสู่จุดหมายที่งดงามเสมอ!", "14. ความอดทนมันขมขื่น แต่ผลของมันช่างหอมหวาน!", "15. พิสูจน์ตัวเองด้วยผลงาน ไม่ใช่ด้วยคำแก้ตัว!", "16. ยิ่งเหนื่อย ยิ่งต้องพยายาม เพราะชัยชนะอยู่ใกล้แค่เอื้อม!", "17. จงเป็นเวอร์ชั่นที่ดีที่สุด ของตัวมึงเองในทุกๆ วัน!", "18. อนาคตของมึง ซ่อนอยู่ในกิจวัตรประจำวันของมึงนั่นแหละ!", "19. อย่าลดขนาดความฝัน แต่จงเพิ่มขนาดความพยายาม!", "20. ผู้ชนะไม่เคยล้มเลิก ผู้ล้มเลิกไม่เคยชนะ!", "21. เริ่มต้นจากศูนย์ ดีกว่าไม่เริ่มต้นอะไรเลย!", "22. ความกล้าหาญ คือการก้าวไปข้างหน้า แม้จะรู้สึกกลัวก็ตาม!", "23. เชื่อมั่นในตัวเอง แล้วทุกอย่างจะเป็นไปได้!", "24. อุปสรรคมีไว้ให้ข้าม ไม่ใช่มีไว้ให้หยุด!", "25. จงทำวันนี้ให้ดีที่สุด เหมือนไม่มีวันพรุ่งนี้ให้แก้ตัว!", "26. ความพยายามอยู่ที่ไหน ความสำเร็จอยู่ที่นั่น คำนี้ยังใช้ได้เสมอ!", "27. เหงื่อของมึงในวันนี้ จะกลายเป็นรอยยิ้มในวันพรุ่งนี้!", "28. อย่าเอาชีวิตมึง ไปเปรียบเทียบกับใคร มึงมีเส้นทางของมึงเอง!", "29. จงเรียนรู้จากความผิดพลาด แล้วทำให้มันดีขึ้นในครั้งต่อไป!", "30. ความสำเร็จ ไม่ได้วัดกันที่ความฉลาด แต่วัดกันที่ความขยัน!", "31. อย่าปล่อยให้คำวิจารณ์ของคนอื่น มาทำลายความตั้งใจของมึง!", "32. จงเป็นแรงบันดาลใจ ให้กับคนที่กำลังมองดูมึงอยู่!", "33. ความยิ่งใหญ่ ไม่ได้เกิดขึ้นในชั่วข้ามคืน มันต้องใช้เวลาและความพยายาม!", "34. เมื่อมึงคิดจะยอมแพ้ ให้นึกถึงเหตุผลที่มึงเริ่มต้น!", "35. จงแข็งแกร่งดั่งหินผา และอ่อนโยนดั่งสายน้ำ!", "36. ความมีวินัย คือกุญแจสำคัญ สู่ความสำเร็จในทุกๆ เรื่อง!", "37. อย่ากลัวความล้มเหลว เพราะมันคือส่วนหนึ่งของความสำเร็จ!", "38. จงก้าวออกจาก Comfort Zone แล้วมึงจะค้นพบโลกใบใหม่!", "39. ทุกๆ วันคือโอกาสใหม่ ในการเริ่มต้นทำสิ่งดีๆ!", "40. จงทำในสิ่งที่มึงรัก แล้วมึงจะไม่รู้สึกว่าต้องทำงานเลย!", "41. ความมุ่งมั่นของมึง จะทำลายทุกกำแพงที่ขวางกั้น!", "42. จงเป็นแสงสว่าง ในความมืดมิดให้กับตัวเองและผู้อื่น!", "43. ความหวัง คือพลังที่ทำให้มนุษย์ก้าวต่อไปได้เสมอ!", "44. จงเชื่อว่ามึงทำได้ แล้วมึงจะหาทางทำให้มันสำเร็จจนได้!", "45. อย่าปล่อยให้ความฝัน เป็นเพียงแค่ความฝัน จงลงมือทำให้มันเป็นจริง!", "46. พลังที่ซ่อนอยู่ในตัวมึง มันยิ่งใหญ่กว่าที่มึงคิดไว้มาก!", "47. จงขอบคุณทุกอุปสรรค ที่เข้ามาทำให้มึงแข็งแกร่งขึ้น!", "48. ชีวิตนี้สั้นนัก จงใช้มันอย่างคุ้มค่า และมีความหมาย!", "49. มึงคือสถาปนิก ผู้ออกแบบชีวิตของมึงเอง!", "50. ลุยให้สุดขีดจำกัด แล้วมึงจะพบว่าตัวเองเจ๋งแค่ไหน!"]

# ==========================================
# 4. ระบบล็อกอิน & แถบด้านข้าง
# ==========================================
safe_email = st.session_state.get("current_user")

with st.sidebar:
    st.markdown(
        "<div class='side-brand'>"
        "<div class='side-brand-ico'><i class='fa-solid fa-gears'></i></div>"
        "<div><h2>DISCIPLINE ARC</h2><span>Iron Will Command Center</span></div>"
        "</div>", unsafe_allow_html=True
    )
    st.markdown(
        f"<div class='chip c-blue' style='width:100%; justify-content:center;'>"
        f"<i class='fa-regular fa-calendar-days'></i> {thai_date_format(today_str)}</div>",
        unsafe_allow_html=True
    )

    if safe_email is None:
        st.markdown("<div class='side-label'><i class='fa-solid fa-right-to-bracket'></i> ทางเข้าสนามรบ</div>", unsafe_allow_html=True)
        auth_mode = st.radio("เลือกโหมด:", ["⚡ ล็อกอิน", "➕ สร้างไอดีใหม่"], key="auth_mode_radio")
        st.divider()
        if auth_mode == "➕ สร้างไอดีใหม่":
            name_input = st.text_input("ชื่อนักรบ:", key="txt_reg_name")
            email_input = st.text_input("อีเมล (ID):", key="txt_reg_email")
            if st.button("เข้าสู่ Discipline Arc!", key="btn_register_submit"):
                if email_input and name_input:
                    new_safe_email = get_safe_email(email_input)
                    if new_safe_email in db.get("users", {}): st.error("อีเมล/ID นี้มีในระบบแล้ว!")
                    else:
                        db["users"][new_safe_email] = {
                            "username": name_input, "level": 1, "exp": 0, "streak": 0, "blood_debt": 0, "in_cage": False, "ghost_exp": 0,
                            "ambush_task": "", "failure_prob": 10, "last_login": today_str, "cleared_yesterday": True, "judged_today": "",
                            "target_name": "เป้าหมายสูงสุดของชีวิต", "target_date": str(today_date + timedelta(days=90)),
                            "daily_oath_date": "", "anime_mentor": "None", "mentor_date": ""
                        }
                        save_db(db); st.success("🔥 ลงทะเบียนสำเร็จ! ล็อกอินเลย!")
                else: st.warning("กรอกข้อมูลให้ครบ!")

        elif auth_mode == "⚡ ล็อกอิน":
            if not db.get("users"): st.warning("ยังไม่มีนักรบในระบบ ไปสร้างไอดีก่อน!")
            else:
                user_options = {f"{data.get('username', 'Unknown Warrior')}": email for email, data in db["users"].items() if isinstance(data, dict)}
                selected_display = st.selectbox("เลือกบัญชีของคุณ:", list(user_options.keys()), key="sb_login_user")

                if st.button("🔥 เริ่มต้นวันใหม่ (Login)", key="btn_login_submit"):
                    login_email = user_options[selected_display]
                    user_data = db["users"][login_email]

                    if "target_name" not in user_data: user_data["target_name"] = "เป้าหมายสูงสุด"; user_data["target_date"] = str(today_date + timedelta(days=90))
                    if "anime_mentor" not in user_data: user_data["anime_mentor"] = "None"

                    if user_data.get("last_login") != today_str:
                        user_data["ghost_exp"] = user_data.get("ghost_exp", 0) + 25
                        if user_data.get("judged_today") != yesterday_str and not user_data.get("cleared_yesterday", False):
                            penalty = 150
                            if user_data.get("anime_mentor") == "Jesus": penalty = int(penalty * 0.5); st.toast("✝️ พระคุณค้ำจุน", icon="🕊️")
                            else: user_data["streak"] = 0
                            user_data["blood_debt"] = user_data.get("blood_debt", 0) + penalty
                            user_data["failure_prob"] = min(100, user_data.get("failure_prob", 10) + 20)

                        user_data["last_login"] = today_str; user_data["cleared_yesterday"] = False
                        save_db(db)
                    st.session_state["current_user"] = login_email
                    safe_rerun()
    else:
        u_data = db["users"][safe_email]

        st_echo = clean_quote(random.choice(ETERNAL_ECHOES))
        st.markdown("<div class='side-label'><i class='fa-solid fa-crosshairs'></i> เป้าหมายสูงสุด</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='subject-banner' style='padding:16px 18px; border-left-color:#F43F5E; "
            f"background:linear-gradient(120deg, rgba(69,10,10,.85) 0%, rgba(5,8,14,.95) 100%);'>"
            f"<h4 style='color:#FB7185; margin:0 0 6px 0; font-size:.72rem; letter-spacing:.16em; text-transform:uppercase;'>"
            f"<i class='fa-solid fa-bullseye'></i> ULTIMATE TARGET</h4>"
            f"<b style='font-size:1.02rem; color:#fff;'>{u_data.get('target_name', '')}</b>"
            f"<p style='color:#FDA4AF; font-style:italic; margin-top:7px; font-size:.82rem;'>\"{st_echo}\"</p></div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='side-label'><i class='fa-solid fa-id-badge'></i> ตัวตนนักรบ</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='side-card' style='--sc:#F43F5E;'>"
            f"<div class='sc-label'><i class='fa-solid fa-user-ninja'></i> ตัวตน</div>"
            f"<div class='sc-value'>{u_data['username']}</div></div>"
            f"<div class='side-card' style='--sc:#38BDF8;'>"
            f"<div class='sc-label'><i class='fa-solid fa-shield-halved'></i> ฉายา</div>"
            f"<div class='sc-value'>{get_title(u_data['level'])}</div></div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='side-label'><i class='fa-solid fa-dna'></i> Soul Resonance</div>", unsafe_allow_html=True)
        if u_data.get("mentor_date") != today_str:
            u_data["anime_mentor"] = random.choice(list(MENTORS.keys())); u_data["mentor_date"] = today_str; save_db(db)
            st.toast(f"🎲 โชคชะตาส่ง {MENTORS[u_data['anime_mentor']]['name']} มาคุมมึง!", icon="🔮")

        current_mentor = u_data.get("anime_mentor", "None")
        m_info = MENTORS[current_mentor]
        st.markdown(
            f"<div class='side-card' style='--sc:#22C55E;'>"
            f"<div class='sc-label'><i class='fa-solid fa-hand-fist'></i> เมนเทอร์ประจำวัน</div>"
            f"<div class='sc-value'>{m_info['icon']} {m_info['name']}</div>"
            f"<div class='sc-note'>{m_info['desc']}</div></div>",
            unsafe_allow_html=True
        )

        st.divider()
        st.markdown("<div class='side-label'><i class='fa-solid fa-hand-back-fist'></i> เรียกสติ</div>", unsafe_allow_html=True)
        if st.button("🔥 ขอกำลังใจด่ากูหน่อย! (SLAP ME!)", type="primary", use_container_width=True, key="btn_sidebar_slap"):
            st.session_state["active_slap_message"] = clean_quote(random.choice(m_info["quotes"]))
            safe_rerun()

        if st.session_state.get("active_slap_message"):
            st.markdown(
                f"<div class='side-card' style='--sc:#F59E0B; background:rgba(245,158,11,.08);'>"
                f"<div class='sc-label'><i class='fa-solid fa-comment-dots'></i> {m_info['icon']} {m_info['name']}</div>"
                f"<div class='sc-note' style='color:#FCD34D; font-size:.88rem;'>\"{st.session_state.get('active_slap_message')}\"</div></div>",
                unsafe_allow_html=True
            )
            if st.button("✅ รับทราบ! ลุย!", use_container_width=True, key="btn_ack_slap"):
                st.session_state["active_slap_message"] = ""
                safe_rerun()
        st.divider()

        st.markdown("<div class='side-label'><i class='fa-solid fa-lock'></i> โหมดโฟกัส</div>", unsafe_allow_html=True)
        locked_in = st.toggle("🔒 LOCKED IN (โฟกัสขั้นสุด)", key="tg_locked_in")
        st.session_state["locked_in_active"] = locked_in

        if not locked_in:
            current_streak = u_data.get("streak", 0)
            if current_streak >= 30: buff_txt, buff_col, buff_ico = "วินัยระดับพระเจ้า (EXP x 1.5)", "#F59E0B", "fa-solid fa-crown"
            elif current_streak >= 7: buff_txt, buff_col, buff_ico = "วินัยเหล็ก (EXP x 1.2)", "#38BDF8", "fa-solid fa-fire"
            elif current_streak >= 3: buff_txt, buff_col, buff_ico = "เริ่มก่อร่างสร้างวินัย (EXP x 1.1)", "#22C55E", "fa-solid fa-bolt"
            else: buff_txt, buff_col, buff_ico = "ไร้วินัย (ไม่มีโบนัส)", "#78869E", "fa-solid fa-skull"

            st.markdown("<div class='side-label'><i class='fa-solid fa-chart-line'></i> สถานะพลัง</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='side-card' style='--sc:#F59E0B;'>"
                f"<div class='sc-label'><i class='fa-solid fa-fire-flame-curved'></i> ความต่อเนื่อง</div>"
                f"<div class='sc-value' style='font-size:1.5rem; font-weight:900;'>{u_data['streak']} "
                f"<span style='font-size:.8rem; color:#AAB7CC; font-weight:700;'>วัน</span></div></div>"
                f"<div class='side-card' style='--sc:{buff_col};'>"
                f"<div class='sc-label'><i class='{buff_ico}'></i> BUFF ปัจจุบัน</div>"
                f"<div class='sc-value' style='color:{buff_col};'>{buff_txt}</div></div>",
                unsafe_allow_html=True
            )

            needs_save = False
            while u_data["exp"] >= 100:
                u_data["level"] += 1; u_data["exp"] -= 100; needs_save = True
                st.toast(f"🔥 LEVEL UP! Lv.{u_data['level']}", icon="⚙️")
            while u_data["exp"] < 0:
                if u_data["level"] > 1: u_data["level"] -= 1; u_data["exp"] += 100
                else: u_data["exp"] = 0
                needs_save = True
            if needs_save: save_db(db)
            st.progress(max(0.0, min(1.0, u_data["exp"] / 100)), text=f"Lv.{u_data['level']} | EXP: {u_data['exp']}/100")
            st.divider()

        if st.button("🚪 ออกจากระบบ", key="btn_logout", use_container_width=True):
            st.session_state["current_user"] = None
            safe_rerun()

# 🛡️ IF NOT LOGGED IN, STOP HERE
if safe_email is None:
    st.markdown(
        "<div class='hero'>"
        "<div class='hero-eyebrow'><i class='fa-solid fa-gears'></i> DISCIPLINE ARC · IRON WILL SYSTEM</div>"
        "<h1 class='hero-title'>ห้องบัญชาการวินัยเหล็ก</h1>"
        "<p class='hero-sub'>ระบบติดตามวินัย ภารกิจ การเรียน และการพิพากษาตัวเองประจำวัน</p>"
        "<div class='hero-chips'>"
        "<span class='chip c-blue'><i class='fa-solid fa-arrow-left'></i> ล็อกอินที่แถบด้านซ้าย</span>"
        "<span class='chip c-violet'><i class='fa-solid fa-brain'></i> Dual Auto Planner</span>"
        "<span class='chip c-gold'><i class='fa-solid fa-scale-balanced'></i> Judgment Feed</span>"
        "<span class='chip c-green'><i class='fa-solid fa-chart-line'></i> Analytics</span>"
        "</div></div>", unsafe_allow_html=True
    )
    c_land1, c_land2, c_land3 = st.columns(3)
    with c_land1: ui_metric("fa-solid fa-list-check", "ระบบภารกิจ", "12", accent="#38BDF8", unit="โมดูล", sub="งาน · เรียน · เควสย่อย · วินัย")
    with c_land2: ui_metric("fa-solid fa-fire", "โหมดโฟกัส", "LOCKED", accent="#A855F7", sub="ตัดสิ่งรบกวนทั้งหมด")
    with c_land3: ui_metric("fa-solid fa-gavel", "พิพากษารายวัน", "S–F", accent="#F59E0B", sub="ให้เกรดวินัยก่อนนอน")
    st.stop()

# ==========================================
# 5. APP MAIN LOGIC (USER DATA LOADED)
# ==========================================
user = db["users"][safe_email]
active_mentor = user.get("anime_mentor", "None")
active_quotes = MENTORS[active_mentor]["quotes"]
is_locked_in = st.session_state.get("locked_in_active", False)

if user.get("daily_oath_date") != today_str:
    st.markdown(
        "<div class='hero' style='text-align:center; background:linear-gradient(120deg, rgba(244,63,94,.16) 0%, rgba(127,29,29,.12) 45%, rgba(18,25,40,.55) 85%);'>"
        "<div class='hero-eyebrow' style='justify-content:center; color:#FB7185;'><i class='fa-solid fa-droplet'></i> DAILY OATH PROTOCOL</div>"
        "<h1 class='hero-title' style='font-size:2.8rem; background:linear-gradient(100deg,#fff,#FB7185);"
        " -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;'>🩸 ดึงสติรับวันใหม่!</h1>"
        "<p class='hero-sub'>สาบานก่อนเริ่มวัน แล้วค่อยเข้าสู่ห้องบัญชาการ</p></div>",
        unsafe_allow_html=True
    )
    oath_text = clean_quote(random.choice(WARRIOR_OATHS))
    st.error(f"### ⚔️ เสียงจากแม่ทัพเหล็ก:\n\n> **\"{oath_text}\"**")
    st.warning("มึงจะยอมแพ้ตั้งแต่ยังไม่เริ่ม แล้วกลับไปซุกผ้าห่ม หรือจะลุกขึ้นมาสู้เพื่อชีวิตตัวเอง?")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔥 กูขอสาบานว่าจะไม่ยอมเป็นไอ้ขี้แพ้!", use_container_width=True, type="primary", key="btn_take_daily_oath"):
            user["daily_oath_date"] = today_str; save_db(db); safe_rerun()
    st.stop()

# CHECK DB STRUCTURE
list_keys = ["missions", "study_missions", "command_log", "accountability_mirror", "dopamine_fails", "excuses", "cookie_jar", "haters", "iron_habits", "limit_breaks", "weakness_fuel", "sanctuary", "skill_forge", "subjects", "qa_vault", "side_quests"]
for k in list_keys:
    if safe_email not in db[k] or db[k][safe_email] is None: db[k][safe_email] = []
    elif isinstance(db[k][safe_email], dict): db[k][safe_email] = list(db[k][safe_email].values())

for k in ["finance", "exams", "beat_yesterday", "daily_wins", "judgment_history"]:
    if safe_email not in db[k] or db[k][safe_email] is None:
        if k == "finance": db[k][safe_email] = {"goal_name": "ยังไม่ได้ตั้ง", "goal_amount": 0.0, "current": 0.0, "ledger": []}
        elif k == "daily_wins": db[k][safe_email] = {"items": [], "logs": {}}
        else: db[k][safe_email] = {}

finance = db["finance"][safe_email]
if "ledger" not in finance: finance["ledger"] = []
current_streak = user.get("streak", 0)

# CHECK OVERDUE COMMAND LOG
overdue_count = 0
overdue_debt_accum = 0
overdue_tasks_names = []

for item in db["command_log"][safe_email]:
    if not isinstance(item, dict): continue
    if item.get("type") in ["task", "study", "exam"] and item.get("deadline") and item["deadline"] != "":
        if is_overdue_check(item["deadline"]) and item.get("last_penalized") != today_str:
            overdue_count += 1
            item["last_penalized"] = today_str
            penalty_val = 150 if item.get("is_must_do") else 50 if "Deadline" in item.get("deadline_type", "🔴") else 25
            overdue_debt_accum += penalty_val
            overdue_tasks_names.append(item.get("title", ""))

if overdue_count > 0:
    fail_prob_penalty = 10 * overdue_count
    if active_mentor == "Future You":
        fail_prob_penalty *= 2
    user["failure_prob"] = min(100, user.get("failure_prob", 10) + fail_prob_penalty)
    user["blood_debt"] = user.get("blood_debt", 0) + overdue_debt_accum
    user["in_cage"] = True; save_db(db)
    if not is_locked_in: st.error(f"🚨 **มึงโดนลงโทษ {overdue_debt_accum} ที!** ข้อหา: ดองงานในสมุดบัญชาการจนเลยเวลา! ({', '.join(overdue_tasks_names)})")

# PREPARE ACTIVE TASKS
raw_m = [m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False) and m.get("skip_today_date") != today_str]
raw_s = [s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว") and not s.get("รอตรวจ", False) and s.get("skip_today_date") != today_str]
raw_h = [h for h in db["iron_habits"][safe_email] if isinstance(h, dict) and h.get("last_done_date") != today_str]
raw_sq = [sq for sq in db["side_quests"][safe_email] if isinstance(sq, dict) and not sq.get("done")]

for h in raw_h: h["ภารกิจ"] = h["name"]; h["is_habit"] = True
for sq in raw_sq: sq["ภารกิจ"] = sq["task"]; sq["is_sidequest"] = True; sq["ประเภท"] = "🟡 ปานกลาง"

all_active_tasks = raw_m + raw_s + raw_h + raw_sq
all_active_tasks.sort(key=lambda x: (
    0 if x.get("is_must_do") else 1,
    int(x.get("user_order", 99)),
    get_priority_score(x.get("ประเภท", "")),
    get_deadline_score(x.get("deadline", ""))
))

# LOCKED IN MODE
if is_locked_in:
    st.markdown(
        "<div class='hero' style='text-align:center;'>"
        "<div class='hero-eyebrow' style='justify-content:center;'><i class='fa-solid fa-lock'></i> SINGLE TARGET PROTOCOL</div>"
        "<h1 class='hero-title' style='font-size:3rem;'>LOCKED IN MODE</h1>"
        "<p class='hero-sub'>ตัดทุกอย่างออก เหลือแค่เป้าหมายเดียวตรงหน้า</p></div>",
        unsafe_allow_html=True
    )
    st.divider()
    if not all_active_tasks: st.success("🎉 ไม่มีงานค้างแล้ว! ปิดโหมด Locked In ได้เลย")
    else:
        top_task = all_active_tasks[0]
        icon = "⛓️" if top_task.get("is_habit") else "🎯" if top_task.get("is_sidequest") else "📖" if top_task.get("is_study") else "🔪"
        must_do_label = " 🩸 **[ชี้เป็นชี้ตาย!]**" if top_task.get("is_must_do") else ""
        st.markdown(f"## {icon} เป้าหมายปัจจุบัน:{must_do_label} **{top_task.get('ภารกิจ')}**")
        st.caption("มึงไม่เห็นงานอื่น และระบบอื่นๆ จนกว่ามึงจะทำไอ้งานนี้เสร็จ!")

        display_hype = clean_quote(active_quotes[get_stable_index(str(top_task.get("id", "")) + "hype", len(active_quotes))])
        hype_color = "#38bdf8" if active_mentor == "Jesus" else "#f59e0b" if active_mentor == "Zenitsu" else "#ef4444"
        st.markdown(f"<div class='mentor-quote' style='border-left: 5px solid {hype_color};'>{MENTORS[active_mentor]['icon']} <b>{MENTORS[active_mentor]['name']}:</b> {display_hype}</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if top_task.get("is_habit"):
                if st.button("🔥 ก้าวข้ามมันไป! (ทำสำเร็จ)", use_container_width=True, type="primary", key="btn_locked_habit_done"):
                    for h in db["iron_habits"][safe_email]:
                        if h.get("id") == top_task.get("id"):
                            h["streak"] = h.get("streak", 0) + 1 if h.get("last_done_date") == yesterday_str else 1
                            h["last_done_date"] = today_str; h["total_done"] = h.get("total_done", 0) + 1
                    user["exp"] += 10; save_db(db); safe_rerun()
            elif top_task.get("is_sidequest"):
                if st.button("✅ พิชิตเควสย่อย!", use_container_width=True, type="primary", key="btn_locked_sq_done"):
                    for sq in db["side_quests"][safe_email]:
                        if sq.get("id") == top_task.get("id"):
                            sq["done"] = True; sq["done_date"] = today_str
                    user["exp"] += 5; save_db(db); safe_rerun()
            elif top_task.get("subtasks"):
                st.warning("ซอยขั้นตอนไว้ ลุยทีละข้อ!")
                target_list = db["study_missions"][safe_email] if top_task.get("is_study") else db["missions"][safe_email]
                for task in target_list:
                    if task.get("id") == top_task.get("id"):
                        all_done = True
                        for i, stask in enumerate(task["subtasks"]):
                            is_locked = stask.get("done", False) and stask.get("done_date", "") != today_str
                            checked = st.checkbox(stask['name'], value=stask.get("done", False), disabled=is_locked, key=f"locked_sub_{i}")
                            if not is_locked and checked != stask.get("done", False):
                                task["subtasks"][i]["done"] = checked; task["subtasks"][i]["done_date"] = today_str if checked else ""; save_db(db); safe_rerun()
                            if not checked: all_done = False
                        if all_done:
                            if st.button("✅ พิชิตงานใหญ่!", use_container_width=True, type="primary", key="btn_locked_task_done"):
                                task["เสร็จแล้ว"] = True; task["done_date"] = today_str
                                exp_gain, fail_reduce = calculate_task_rewards(task, current_streak, active_mentor)
                                user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
            else:
                if st.button("✅ จัดการเรียบร้อย!", use_container_width=True, type="primary", key="btn_locked_single_done"):
                    target_list = db["study_missions"][safe_email] if top_task.get("is_study") else db["missions"][safe_email]
                    for task in target_list:
                        if task.get("id") == top_task.get("id"):
                            task["เสร็จแล้ว"] = True; task["done_date"] = today_str
                            exp_gain, fail_reduce = calculate_task_rewards(task, current_streak, active_mentor)
                            user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
    st.stop()

# ==========================================
# 🎯 TOP CONTROLS
# ==========================================
try: t_date = datetime.strptime(str(user.get("target_date", str(today_date))).strip(), "%Y-%m-%d").date()
except: t_date = today_date + timedelta(days=90)
days_left = (t_date - today_date).days

# --- HERO COMMAND BAR ---
_hero_mentor = MENTORS[active_mentor]
st.markdown(
    f"<div class='hero'>"
    f"<div class='hero-eyebrow'><i class='fa-solid fa-gauge-high'></i> COMMAND CENTER · {thai_date_format(today_str)}</div>"
    f"<h1 class='hero-title'>{user['username']}</h1>"
    f"<p class='hero-sub'>{get_title(user['level'])} &nbsp;·&nbsp; เป้าหมายสูงสุด: <b style='color:#E8EEF9;'>{user.get('target_name','-')}</b></p>"
    f"<div class='hero-chips'>"
    f"<span class='chip c-blue'><i class='fa-solid fa-star'></i> Level {user['level']} · {user['exp']}/100 EXP</span>"
    f"<span class='chip c-gold'><i class='fa-solid fa-fire'></i> Streak {current_streak} วัน</span>"
    f"<span class='chip c-violet'><i class='fa-solid fa-hand-fist'></i> {_hero_mentor['icon']} {_hero_mentor['name']}</span>"
    f"<span class='chip c-red'><i class='fa-solid fa-hourglass-half'></i> เหลือ {days_left} วัน ก่อนถึงเส้นตาย</span>"
    f"<span class='chip c-green'><i class='fa-solid fa-list-check'></i> งานค้างวันนี้ {len(all_active_tasks)} รายการ</span>"
    f"</div></div>", unsafe_allow_html=True
)

# --- KPI STRIP ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    ui_metric("fa-solid fa-shield-halved", "ระดับวินัย", f"Lv.{user['level']}", accent="#38BDF8", sub=f"EXP {user['exp']}/100")
with k2:
    ui_metric("fa-solid fa-fire-flame-curved", "ความต่อเนื่อง", current_streak, accent="#F59E0B", unit="วัน",
              sub="ยิ่งยาว EXP ยิ่งคูณ")
with k3:
    ui_metric("fa-solid fa-triangle-exclamation", "โอกาสหลุดวินัย", f"{user.get('failure_prob', 10)}", accent="#F43F5E", unit="%",
              sub="ทำงานสำเร็จเพื่อกดให้ต่ำลง")
with k4:
    ui_metric("fa-solid fa-droplet", "หนี้เลือดค้างชำระ", f"{user.get('blood_debt', 0)}", accent="#A855F7", unit="ที",
              sub="วิดพื้นเพื่อปลดล็อกกรง")

st.write("")
if st.button("💥 กูเริ่มเหนื่อยและอยากสบาย (Slap Me Awake!)", use_container_width=True, type="secondary", key="btn_trigger_slap_awake"):
    st.session_state["slap_awake_active"] = True
    safe_rerun()

colTop1, colTop2, colTop3 = st.columns([1, 1, 3])
with colTop1:
    if st.button("🎰 วงล้อชดใช้กรรม", type="primary", use_container_width=True, key="btn_trigger_punish_wheel"):
        st.session_state["punishment_active"] = True
        st.session_state["punishment_task"] = random.choice(PUNISHMENTS)
        safe_rerun()
with colTop2:
    if st.button("⚡ ปลุกวินัย", use_container_width=True, key="btn_boost_discipline"): st.toast("🔥 อย่าถอย! ลุยดิวะ!", icon="⚙️")
with colTop3:
    with st.popover("⚙️ ตั้งเป้าหมายสูงสุด"):
        new_t_name = st.text_input("เป้าหมายสูงสุด:", user.get("target_name", ""), key="txt_top_target_name")
        new_t_date = st.date_input("วันกำหนด (Deadline):", t_date, key="dt_top_target_date")
        if st.button("บันทึกเป้าหมาย", key="btn_save_top_target"): user["target_name"] = new_t_name; user["target_date"] = str(new_t_date); save_db(db); safe_rerun()
    st.caption(f"เหลือเวลาอีก **{days_left}** วัน ที่มึงต้องพิสูจน์ตัวเอง!")

if user.get("in_cage"): st.error("🚨 **มึงอยู่ในกรง!** วิดพื้นจ่ายหนี้เลือดเพื่อออกมาทำตามแผนซะ!")
st.divider()

# ==========================================
# 🔥 สรุปวินัยเหล็กประจำวัน (THE IRON SUMMARY)
# ==========================================
st.markdown("## 🔥 สรุปวินัยเหล็กประจำวัน (THE IRON SUMMARY)")
st.info("เป้าหมายมีไว้พุ่งชน ไม่ต้องสนเวลา! ว่างตอนไหน ฟาดให้เรียบตามลิสต์นี้! หมดข้ออ้าง!")

col_sum1, col_sum2, col_sum3 = st.columns(3)
with col_sum1:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 🔪 งาน & 📖 เรียน")
    has_tasks = False
    for task in all_active_tasks:
        if not task.get("is_habit") and not task.get("is_sidequest"):
            has_tasks = True
            icon = "📖" if task.get("is_study") else "🔪"
            must_do = " <span class='badge b-death'>🩸 MUST DO</span>" if task.get("is_must_do") else ""
            prio = task.get("ประเภท", "")
            bl = "border-left: 3px solid #64748b;"
            if "ด่วนสุด" in prio: bl = "border-left: 3px solid #ef4444;"
            elif "ฉุกเฉิน" in prio: bl = "border-left: 3px solid #f97316;"
            elif "ปานกลาง" in prio: bl = "border-left: 3px solid #eab308;"
            elif "ชิลๆ" in prio: bl = "border-left: 3px solid #22c55e;"
            if task.get("is_must_do"): bl = "border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.1);"
            st.markdown(f"<div style='background:rgba(255,255,255,0.03); padding:10px; margin-bottom:8px; border-radius:8px; {bl}'>{icon} <b>{task.get('ภารกิจ', '')}</b>{must_do}</div>", unsafe_allow_html=True)
    if not has_tasks: st.success("✅ กวาดงานเรียบ!")
    st.markdown("</div>", unsafe_allow_html=True)

with col_sum2:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### ⛓️ วินัยเหล็ก & 🎯 เควสย่อย")
    has_habits = False
    for task in all_active_tasks:
        if task.get("is_habit"):
            has_habits = True
            st.markdown(f"<div style='background:rgba(255,255,255,0.03); padding:10px; border-left:3px solid #38BDF8; margin-bottom:8px; border-radius:8px;'>⛓️ <b>{task.get('ภารกิจ', '')}</b></div>", unsafe_allow_html=True)
        elif task.get("is_sidequest"):
            has_habits = True
            st.markdown(f"<div style='background:rgba(255,255,255,0.03); padding:10px; border-left:3px solid #A855F7; margin-bottom:8px; border-radius:8px;'>🎯 <b>{task.get('ภารกิจ', '')}</b></div>", unsafe_allow_html=True)
    if not has_habits: st.success("✅ รักษาวินัยครบถ้วน!")
    st.markdown("</div>", unsafe_allow_html=True)

with col_sum3:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 🏅 ชัยชนะรายวัน")
    win_items_summary = db["daily_wins"][safe_email].get("items", [])
    if not win_items_summary: st.caption("ยังไม่มีลิสต์ชัยชนะ")
    for d_win in win_items_summary:
        log_status = db["daily_wins"][safe_email].get("logs", {}).get(today_str, {}).get(d_win["id"])
        if log_status == "win": st.markdown(f"<div style='background:rgba(34,197,94,0.15); padding:10px; border-left:3px solid #22C55E; margin-bottom:8px; border-radius:8px; box-shadow: 0 0 10px rgba(34,197,94,0.2);'>✅ <del>{d_win['name']}</del></div>", unsafe_allow_html=True)
        elif log_status == "lose": st.markdown(f"<div style='background:rgba(239,68,68,0.15); padding:10px; border-left:3px solid #EF4444; margin-bottom:8px; border-radius:8px; box-shadow: 0 0 10px rgba(239,68,68,0.2);'>❌ <del>{d_win['name']}</del></div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:10px; border-left:3px solid #F59E0B; margin-bottom:8px; border-radius:8px;'>⏳ <b>{d_win['name']}</b></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. DUAL REALITY DASHBOARD
# ==========================================
colLeft, colRight = st.columns([1.2, 2.8])

with colLeft:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 🗑️ ขยะในจิตใจ (Distractions)")
    fail_prob = user.get('failure_prob', 10)
    st.markdown(f"**📉 โอกาสหลุดวงโคจรวินัย: {fail_prob}%**")
    st.progress(fail_prob / 100)
    if st.button("💀 กดยอมแพ้ให้สิ่งเร้า", use_container_width=True, key="btn_surrender_distraction"):
        db["dopamine_fails"][safe_email].append(today_str); user["exp"] = 0; user["blood_debt"] = user.get("blood_debt", 0) + 50; user["in_cage"] = True; user["failure_prob"] = min(100, user["failure_prob"] + 20); save_db(db); safe_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("#### 🩸 เชื้อเพลิงความแค้น")
    with st.form("weakness_fuel_form", clear_on_submit=True):
        w_text = st.text_input("ความอ่อนแอที่มึงเคยทำพลาด:", key="txt_weakness_input")
        if st.form_submit_button("🔥 เผาความกากเป็นพลัง!"):
            if w_text: db["weakness_fuel"][safe_email].append({"id": str(uuid.uuid4()), "text": w_text}); save_db(db); safe_rerun()

    if db.get("weakness_fuel", {}).get(safe_email):
        random_weakness = random.choice(db["weakness_fuel"][safe_email])
        w_disp = random_weakness.get("text", "") if isinstance(random_weakness, dict) else random_weakness
        st.error(f"🩸 **มึงเคยกากแบบนี้:**\n\n\"{w_disp}\"")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("#### 🗣️ THE HATER'S WALL")
    with st.form("hater_form", clear_on_submit=True):
        h_text = st.text_input("คำดูถูกที่ฝังใจ:", key="txt_hater_input")
        if st.form_submit_button("ฝังความแค้น"):
            if h_text: db["haters"][safe_email].append(h_text); save_db(db); safe_rerun()
    if db.get("haters", {}).get(safe_email): st.warning(f"🤬 \"{random.choice(db['haters'][safe_email])}\"")
    st.markdown("</div>", unsafe_allow_html=True)

with colRight:
    st.markdown("## ⚙️ DISCIPLINE ZONE")

    # 🛡️ V31: TABS UPDATE (THE DUAL AUTO-PLANNER)
    tab_planner_ai, tab_missions, tab_study, tab_sidequests, tab_forge, tab_subjects, tab_planner, tab_qa, tab_mirror, tab_habits, tab_daily_wins, tab_sanctuary = st.tabs([
        "🧠 DUAL PLANNER", "🔪 งาน", "📖 เรียน", "🎯 เควสย่อย", "⚒️ ตีเหล็ก", "🗂️ คลังวิชา", "📝 บัญชาการ", "❓ Q&A", "🪞 กระจก", "⛓️ วินัย", "🏅 ชัยชนะ", "🔥 พักใจ"
    ])

    user_subj_names = [s["name"] for s in db["subjects"].get(safe_email, []) if isinstance(s, dict)]
    subj_options = ["- ไม่ระบุ -"] + user_subj_names

    # ----------------------------------------------------
    # TAB 1: 🧠 THE DUAL AUTO-PLANNER (V31 SEPARATED)
    # ----------------------------------------------------
    # ----------------------------------------------------
    # TAB 1: 🧠 THE DUAL AUTO-PLANNER & AI DATA LINK
    # ----------------------------------------------------
    with tab_planner_ai:
        
        # 📡 AI DATA LINK (ส่งออกข้อมูลให้ AI ภายนอก)
        st.markdown("<div class='glass-panel' style='border-left: 4px solid #A855F7; padding:18px; margin-bottom:25px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#A855F7; margin-top:0; margin-bottom:10px;'><i class='fa-solid fa-satellite-dish'></i> AI DATA LINK (ระบบเชื่อมต่อ AI เอเจนท์ส่วนตัว)</h4>", unsafe_allow_html=True)
        st.write("ดาวน์โหลดภารกิจค้างทั้งหมดของวันนี้เป็นไฟล์ `.txt` เพื่อเอาไปแปะให้ ChatGPT, Claude หรือ AI เอเจนท์ของมึงช่วยวิเคราะห์และวางแผนตารางเวลาแบบเจาะลึก!")
        
        export_payload = generate_ai_export_payload(all_active_tasks)
        
        c_dl1, c_dl2 = st.columns([1, 3])
        with c_dl1:
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ (TXT)",
                data=export_payload,
                file_name=f"Discipline_Plan_{today_str}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with c_dl2:
            with st.expander("👁️ ดูตัวอย่างข้อมูลที่จะส่งให้ AI (Preview Prompt)"):
                st.code(export_payload, language="markdown")
        st.markdown("</div>", unsafe_allow_html=True)

        # (โค้ดเก่าส่วน st.markdown("### 🧠 THE DUAL AUTO-PLANNER...") ของมึงจะอยู่ต่อจากตรงนี้)
    with tab_planner_ai:
        st.markdown("### 🧠 THE DUAL AUTO-PLANNER (ห้องบัญชาการรบแยกส่วน)")
        st.write("แยกระบบคำนวณระหว่าง 'การสร้างวินัย' และ 'การสะสางงานค้าง' เพื่อการประเมินที่โหดและตรงจุดที่สุด!")

        col_plan1, col_plan2 = st.columns(2)

        # --- LEFT: HABIT PLANNER ---
        with col_plan1:
            st.markdown("<div class='glass-panel' style='border-top: 4px solid #38bdf8;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#38bdf8; text-align:center;'>⛓️ กองบัญชาการวินัย (HABITS)</h4>", unsafe_allow_html=True)
            time_habit = st.number_input("⏳ เวลาฝึกวินัย (นาที):", min_value=5, max_value=300, value=30, step=5, key="t_hab")
            mode_habit = st.selectbox("โหมดการฝึกวินัย:", ["🏃 วอร์มอัป (ชิลๆ - 5 นาที/ข้อ)", "🔥 เอาจริง (มาตรฐาน - 10 นาที/ข้อ)", "💀 ทรมานร่าง (รีดขีดจำกัด - 15 นาที/ข้อ)"], key="m_hab")
            btn_hab = st.button("⛓️ ประมวลผลตารางวินัย", use_container_width=True, key="btn_plan_hab")

            if btn_hab:
                habits_sim = [h for h in db["iron_habits"][safe_email] if isinstance(h, dict) and h.get("last_done_date") != today_str]
                st.markdown("<div class='cyber-terminal'>", unsafe_allow_html=True)
                st.markdown("<h4>SYSTEM LOG: DISCIPLINE OVERVIEW</h4>", unsafe_allow_html=True)

                if not habits_sim:
                    st.success("✅ วินัยมึงครบแล้วสำหรับวันนี้! ไปลุยงานหลักซะ!")
                else:
                    time_per_habit = 5 if "วอร์มอัป" in mode_habit else 15 if "ทรมาน" in mode_habit else 10
                    total_needed = len(habits_sim) * time_per_habit

                    st.write(f"**เวลาที่มี:** {time_habit} นาที | **เวลาที่ต้องใช้ทั้งหมด:** {total_needed} นาที")
                    st.markdown("<div class='cyber-phase hab'>[ PROTOCOL: HABIT EXECUTION ]</div>", unsafe_allow_html=True)

                    t_left = time_habit
                    for h in habits_sim:
                        if t_left >= time_per_habit:
                            st.markdown(f"<div class='cyber-item hab'>{h.get('name')} (~{time_per_habit} นาที)</div>", unsafe_allow_html=True)
                            t_left -= time_per_habit
                        else:
                            st.markdown(f"<div class='cyber-item' style='color:#ef4444;'><s>{h.get('name')}</s> [FAILED: INSUFFICIENT TIME]</div>", unsafe_allow_html=True)

                    st.markdown("<br><div class='cyber-phase hab'>[ COMMANDER'S REVIEW ]</div>", unsafe_allow_html=True)
                    if time_habit < total_needed:
                        st.markdown("<span style='color:#ef4444; font-weight:bold;'>🚨 สภาพ! เวลาแค่นี้มึงยังไม่พอขัดเกลาวินัยพื้นฐานเลย! โคตรน่าสมเพช มึงห้ามหาข้ออ้างเด็ดขาด!</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color:#38bdf8;'>เวลาพอถมเถ! ยัดตารางนี้เข้าไปในหัวมึง แล้วทำมันให้จบๆ ไปซะ!</span>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # --- RIGHT: TASK PLANNER ---
        with col_plan2:
            st.markdown("<div class='glass-panel' style='border-top: 4px solid #ef4444;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#ef4444; text-align:center;'>🔪 กองบัญชาการรบ (TASKS & QUESTS)</h4>", unsafe_allow_html=True)
            time_task = st.number_input("⏳ เวลาสางงานค้าง (นาที):", min_value=10, max_value=1440, value=120, step=10, key="t_tsk")
            mode_task = st.selectbox("โหมดความตาย:", ["🍅 Pomodoro (50/10)", "🌊 Deep Work (90/15)", "🦅 Spartan Time (120/10)", "🩸 Hell Week (180/5)", "💀 Brutal (ไม่พัก)"], key="m_tsk")
            btn_tsk = st.button("💀 ประมวลผลแผนฆ่างาน", type="primary", use_container_width=True, key="btn_plan_tsk")

            if btn_tsk:
                tasks_sim = []
                for m in db["missions"][safe_email]:
                    if isinstance(m, dict) and not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False) and m.get("skip_today_date") != today_str:
                        tasks_sim.append({"name": m.get('ภารกิจ'), "type": "งาน", "must_do": m.get("is_must_do", False), "score": get_priority_score(m.get("ประเภท", "")), "dl_score": get_deadline_score(m.get("deadline", ""))})
                for s in db["study_missions"][safe_email]:
                    if isinstance(s, dict) and not s.get("เสร็จแล้ว") and not s.get("รอตรวจ", False) and s.get("skip_today_date") != today_str:
                        tasks_sim.append({"name": s.get('ภารกิจ'), "type": "เรียน", "must_do": s.get("is_must_do", False), "score": get_priority_score(s.get("ประเภท", "")), "dl_score": get_deadline_score(s.get("deadline", ""))})
                for sq in db["side_quests"][safe_email]:
                    if isinstance(sq, dict) and not sq.get("done"):
                        tasks_sim.append({"name": sq.get('task'), "type": "เควสย่อย", "must_do": False, "score": 2, "dl_score": 999})

                st.markdown("<div class='cyber-terminal combat'>", unsafe_allow_html=True)
                st.markdown("<h4>SYSTEM LOG: COMBAT PROTOCOL</h4>", unsafe_allow_html=True)

                if not tasks_sim:
                    st.success("✅ โล่ง! ไม่มีงานค้างในระบบ!")
                else:
                    tasks_sim.sort(key=lambda x: (0 if x["must_do"] else 1, x["dl_score"], x["score"]))
                    st.write(f"**เวลาที่มี:** {time_task} นาที | **โหมด:** {mode_task}")
                    st.markdown("<div class='cyber-phase com'>[ PROTOCOL: MISSION EXECUTION ]</div>", unsafe_allow_html=True)

                    t_left = time_task
                    dropped_must_do = False
                    dropped_overdue = False

                    for task in tasks_sim:
                        is_overdue = task["dl_score"] < 0

                        if t_left <= 0:
                            if task["must_do"]: dropped_must_do = True
                            if is_overdue: dropped_overdue = True
                            st.markdown(f"<div class='cyber-item' style='color:#64748b;'><s>[{task['type']}] {task['name']}</s> (ABORTED: NO TIME)</div>", unsafe_allow_html=True)
                            continue

                        # Estimate time
                        est_time = 45 if task["must_do"] else 30 if task["score"]==1 or is_overdue else 20 if task["score"]==2 else 15 if task["type"]!="เควสย่อย" else 10
                        if t_left < est_time: est_time = t_left

                        warning = " <span style='color:#ef4444;'>[!! MUST DO !!]</span>" if task["must_do"] else " <span style='color:#f59e0b;'>[OVERDUE]</span>" if is_overdue else ""
                        st.markdown(f"<div class='cyber-item com'>[{task['type']}] {task['name']}{warning} (~{est_time} นาที)</div>", unsafe_allow_html=True)
                        t_left -= est_time

                    st.markdown("<br><div class='cyber-phase com'>[ COMMANDER'S REVIEW ]</div>", unsafe_allow_html=True)

                    if dropped_must_do:
                        st.markdown("<span style='color:#ef4444; font-weight:bold; font-size:1.1em;'>🚨 [CRITICAL FAILURE] ไอ้เวร! มึงดองงานจนเวลาไม่พอทำงานชี้เป็นชี้ตาย (MUST DO)! มึงเตรียมตัวตายตอนพิพากษาได้เลย!</span><br><br>", unsafe_allow_html=True)
                    elif dropped_overdue:
                        st.markdown("<span style='color:#f59e0b; font-weight:bold;'>⚠️ [WARNING] งานดองข้ามชาติมึงก็ยังสะสางไม่หมด! พรุ่งนี้มึงต้องตื่นมาจัดการมันให้ได้!</span><br><br>", unsafe_allow_html=True)

                    brutal_text = ""
                    if "Pomodoro" in mode_task: brutal_text = "ลุกขึ้นมาขยับตัวตอนพักด้วย! อย่าเสือกหยิบมือถือมาไถให้เสียสมาธิ!"
                    elif "Deep" in mode_task: brutal_text = "90 นาทีนี้คือโลกที่มีแค่มึงกับเป้าหมาย ใครทักมาไม่ต้องตอบ ตัดขาดจากโลกภายนอกซะ!"
                    elif "Spartan" in mode_task: brutal_text = "120 นาทีไม่มีคำว่าปรานี ลุกไปเยี่ยวคือแพ้! บีบคั้นสมองมึงออกมาให้หมด!"
                    elif "Hell" in mode_task: brutal_text = "180 นาทีรวด! ถ้ามึงไม่ตาย มึงก็รอด! กัดฟันทำไปซะไอ้ลูกหมา!"
                    else: brutal_text = "พักคือข้ออ้างของคนอ่อนแอ! ลุยจนกว่าตาจะลาย ทำจนกว่างานจะเสร็จ มึงห้ามลุกไปไหน!"

                    st.markdown(f"<span style='color:#e2e8f0;'>{brutal_text}</span>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 2: 🔪 งาน
    # ----------------------------------------------------
    with tab_missions:
        st.markdown("### 🔪 งานที่ต้องบดขยี้วันนี้")
        raw_active_missions = [m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว")]
        todo_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False)]
        todo_missions.sort(key=lambda x: (
            0 if x.get("is_must_do") else 1,
            int(x.get("user_order", 99)),
            get_priority_score(x.get("ประเภท", "")),
            get_deadline_score(x.get("deadline", ""))
        ))

        if todo_missions:
            with st.expander("🎯 วางแผนลำดับงาน (Q-Order)"):
                with st.form("set_order_form"):
                    new_orders = {}
                    for m in todo_missions:
                        col_q, col_n = st.columns([1, 5])
                        new_orders[m["id"]] = col_q.number_input("คิว", min_value=1, max_value=99, value=int(m.get("user_order", 99)), step=1, key=f"q_{m['id']}", label_visibility="collapsed")
                        col_n.write(f"{'🩸 [MUST DO] ' if m.get('is_must_do') else ''}{'💀 [BOSS] ' if m.get('is_boss') else ''}{m['ภารกิจ']}")
                    if st.form_submit_button("🔒 ล็อคผังชีวิต!"):
                        for m in db["missions"][safe_email]:
                            if isinstance(m, dict) and m.get("id") in new_orders: m["user_order"] = int(new_orders[m["id"]])
                        save_db(db); st.success("✅ อัปเดตผังเรียบร้อย!"); safe_rerun()

            for m in todo_missions:
                css_class = get_task_css_class(m, "task")
                st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)

                c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6])

                dl_type = m.get("deadline_type", "🔴 Deadline")
                dl_str = m.get("deadline", "")
                is_overdue = is_overdue_check(dl_str) if dl_str != "" else False

                badge_html = get_badge_html(dl_str, dl_type, is_must_do=m.get("is_must_do", False))
                prio_badge = get_priority_badge(m.get('ประเภท',''))

                is_frozen = (m.get("skip_today_date") == today_str)
                if m.get("skip_today_date") != "" and not is_frozen: m["skip_today_date"] = ""; save_db(db)
                frozen_badge = "<span class='badge b-red'>❄️🚨 เกราะแตก!</span>" if is_frozen and is_overdue else "<span class='badge b-blue'>❄️ แช่แข็ง</span>" if is_frozen else ""

                subj_tag = f"<span class='badge b-gray'>🗂️ {m.get('subject')}</span>" if m.get("subject") and m.get("subject") != "- ไม่ระบุ -" else ""
                q_tag = f"<span class='badge b-gold'>Q{m.get('user_order', 99)}</span>" if int(m.get('user_order', 99)) != 99 else ""
                type_icon = "💀 BOSS" if m.get("is_boss") else "🔪" if m.get("subtasks") else "⚡"

                inline_prog = get_subtask_progress_html(m)

                c1.markdown(f"<div style='margin-bottom:8px;'>{prio_badge} {q_tag} {subj_tag}</div><div style='font-size:1.1em;'>{type_icon} <b>{m['ภารกิจ']}</b> {badge_html} {frozen_badge}</div>{inline_prog}", unsafe_allow_html=True)

                m_id = str(m.get("id", f"unk_m_{m.get('ภารกิจ', '')}"))
                csq_text = clean_quote(WARRIOR_CONSEQUENCES[get_stable_index(m_id + 'conseq', len(WARRIOR_CONSEQUENCES))])
                c1.markdown(f"<div class='mentor-quote' style='border-left: 3px solid #ff4b4b;'>🩸 <b>ถ้ากูไม่ทำ:</b> {m.get('consequence', '') or csq_text}</div>", unsafe_allow_html=True)

                with c1.popover("✏️ แก้ไขงาน"):
                    new_t = st.text_input("ชื่อภารกิจ:", value=m["ภารกิจ"], key=f"ed_m_name_{m['id']}")
                    new_s = st.selectbox("วิชา:", subj_options, index=subj_options.index(m.get("subject", "- ไม่ระบุ -")) if m.get("subject", "- ไม่ระบุ -") in subj_options else 0, key=f"ed_m_sub_{m['id']}")
                    new_p = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"], index=["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"].index(m.get("ประเภท", "🟡 ปานกลาง")) if m.get("ประเภท", "🟡 ปานกลาง") in ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"] else 2, key=f"ed_m_pri_{m['id']}")
                    new_d = st.text_area("รายละเอียด:", value=m.get("รายละเอียด", ""), key=f"ed_m_det_{m['id']}")
                    new_must_do = st.checkbox("🩸 ชี้เป็นชี้ตาย! (พลาดคือพัง)", value=m.get("is_must_do", False), key=f"ed_m_mustdo_{m['id']}")

                    curr_subtasks_str = "\n".join([stk['name'] for stk in m.get("subtasks", [])])
                    new_sub_str = st.text_area("ซอยงานย่อย (Enter เพื่อแยกข้อ):", value=curr_subtasks_str, key=f"ed_m_subs_{m['id']}")

                    new_dl_t = st.radio("ประเภท Deadline:", ["🔴 Deadline (ครูสั่ง/ห้ามพลาด)", "🎯 เป้าหมายส่วนตัว (อยากเสร็จ)", "⚪ ไม่มีกำหนด"], index=0 if "Deadline" in m.get("deadline_type", "🔴") else 1 if "เป้าหมาย" in m.get("deadline_type", "") else 2, key=f"ed_m_dlt_{m['id']}")
                    new_dl_d = ""
                    if "ไม่มีกำหนด" not in new_dl_t:
                        parsed_dt = safe_date_parse(m.get("deadline", ""))
                        new_dl_d = str(st.date_input("วันกำหนด:", value=parsed_dt, key=f"ed_m_dt_{m['id']}"))

                    if st.button("💾 เซฟการแก้ไข", key=f"save_ed_m_{m['id']}", use_container_width=True):
                        m["ภารกิจ"] = new_t; m["subject"] = new_s; m["ประเภท"] = new_p; m["รายละเอียด"] = new_d
                        m["deadline_type"] = new_dl_t; m["deadline"] = new_dl_d; m["is_must_do"] = new_must_do

                        old_subs = {stk['name']: stk['done'] for stk in m.get("subtasks", [])}
                        new_subs_list = []
                        for line in new_sub_str.split('\n'):
                            line = line.strip()
                            if line: new_subs_list.append({"name": line, "done": old_subs.get(line, False), "done_date": ""})
                        m["subtasks"] = new_subs_list
                        save_db(db); st.success("อัปเดตแล้ว!"); safe_rerun()

                with st.expander("📝 ดูรายละเอียดและเนื้องาน"):
                    if m.get("รายละเอียด"): st.write(m["รายละเอียด"])
                    all_done = True
                    if m.get("subtasks"):
                        st.markdown("**📌 งานย่อยที่ต้องเคลียร์ (ทำแค่อันเดียวก็รอดพิพากษา *ถ้ายังไม่เลยกำหนด*):**")
                        for i, stask in enumerate(m["subtasks"]):
                            is_locked = stask.get("done", False) and stask.get("done_date", "") != today_str
                            can_interact = not is_locked and (not is_frozen or is_overdue)
                            checked = st.checkbox(f"{stask['name']} {'🔒 ('+thai_date_format(stask.get('done_date', ''))+')' if is_locked else ''}", value=stask.get("done", False), disabled=not can_interact, key=f"st_{m['id']}_{i}")
                            if can_interact and checked != stask.get("done", False):
                                m["subtasks"][i]["done"] = checked; m["subtasks"][i]["done_date"] = today_str if checked else ""
                                save_db(db); safe_rerun()
                            if not checked: all_done = False
                        total_subs = len(m["subtasks"]); done_subs = len([s for s in m["subtasks"] if s.get("done")])
                        st.progress(done_subs / total_subs if total_subs > 0 else 0)

                if active_mentor == "Subaru" and is_overdue:
                    if user.get("exp", 0) >= 10:
                        if c1.button("⏪ Return by Death (-10 EXP)", key=f"rbd_{m['id']}", type="primary"): user["exp"] -= 10; m["deadline"] = today_str; save_db(db); safe_rerun()
                    else: c1.caption("⏪ ต้องการ 10 EXP")

                if is_frozen:
                    if c4.button("🔥 ปลดล็อก", key=f"unfrz_{m['id']}", use_container_width=True): m["skip_today_date"] = ""; save_db(db); safe_rerun()
                else:
                    if c4.button("❄️ แช่แข็ง", key=f"frz_{m['id']}", use_container_width=True): m["skip_today_date"] = today_str; save_db(db); safe_rerun()

                if all_done and (not is_frozen or is_overdue):
                    if c2.button("✅ สำเร็จ", key=f"m_{m['id']}"):
                        m["เสร็จแล้ว"] = True; m["done_date"] = today_str
                        exp_gain, fail_reduce = calculate_task_rewards(m, current_streak, active_mentor)
                        user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                    if c3.button("📤 ส่งตรวจ", key=f"pend_{m['id']}"): m["รอตรวจ"] = True; save_db(db); safe_rerun()
                else: c2.caption("❄️ แช่แข็ง" if is_frozen and not is_overdue else "🔒 งานย่อยคาอยู่")
                if c5.button("🗑️", key=f"del_m_{m['id']}"): db["missions"][safe_email].remove(m); save_db(db); safe_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        else: st.success("✅ วันนี้เคลียร์แผนผังงานหมดแล้ว!")

        pending_missions = [m for m in raw_active_missions if m.get("รอตรวจ", False)]
        if pending_missions:
            st.divider(); st.markdown("### ⏳ งานที่รอรีวิวผลงาน")
            for m in pending_missions:
                c1, c2, c3 = st.columns([5, 2, 2])
                c1.caption(f"⏳ {'💀 ' if m.get('is_boss') else ''}{m['ภารกิจ']}")
                if c2.button("✅ ตรวจผ่าน", key=f"appr_{m['id']}"):
                    m["เสร็จแล้ว"] = True; m["รอตรวจ"] = False; m["done_date"] = today_str
                    exp_gain, fail_reduce = calculate_task_rewards(m, current_streak, active_mentor)
                    user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                if c3.button("⏪ ดึงกลับมาทำ", key=f"revert_{m['id']}"): m["รอตรวจ"] = False; save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 3: 📖 เรียน
    # ----------------------------------------------------
    with tab_study:
        st.markdown("### 📖 วิชาที่ต้องบรรลุในวันนี้")
        raw_active_study = [s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว")]
        todo_study = [s for s in raw_active_study if not s.get("รอตรวจ", False)]
        todo_study.sort(key=lambda x: (
            0 if x.get("is_must_do") else 1,
            int(x.get("user_order", 99)),
            get_priority_score(x.get("ประเภท", "")),
            get_deadline_score(x.get("deadline", ""))
        ))

        if todo_study:
            with st.expander("🎯 วางแผนลำดับวิชาเรียน (Q-Order)"):
                with st.form("set_study_order_form"):
                    new_s_orders = {}
                    for s in todo_study:
                        col_q, col_n = st.columns([1, 5])
                        new_s_orders[s["id"]] = col_q.number_input("คิว", min_value=1, max_value=99, value=int(s.get("user_order", 99)), step=1, key=f"q_s_{s['id']}", label_visibility="collapsed")
                        col_n.write(f"{'💀 [BOSS] ' if s.get('is_boss') else ''}{s['ภารกิจ']}")
                    if st.form_submit_button("🔒 ล็อคผังเรียน!"):
                        for s in db["study_missions"][safe_email]:
                            if isinstance(s, dict) and s.get("id") in new_s_orders: s["user_order"] = int(new_s_orders[s["id"]])
                        save_db(db); st.success("✅ อัปเดตผังเรียนเรียบร้อย!"); safe_rerun()

            for s in todo_study:
                css_class = get_task_css_class(s, "study")
                st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)

                c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6])

                dl_type = s.get("deadline_type", "🔴 Deadline")
                dl_str = s.get("deadline", "")
                is_overdue = is_overdue_check(dl_str) if dl_str != "" else False

                badge_html = get_badge_html(dl_str, dl_type, is_must_do=s.get("is_must_do", False))
                prio_badge = get_priority_badge(s.get('ประเภท',''))

                is_frozen = (s.get("skip_today_date") == today_str)
                if s.get("skip_today_date") != "" and not is_frozen: s["skip_today_date"] = ""; save_db(db)
                frozen_badge = "<span class='badge b-red'>❄️🚨 แช่แข็งแตก!</span>" if is_frozen and is_overdue else "<span class='badge b-blue'>❄️ แช่แข็ง</span>" if is_frozen else ""

                subj_tag = f"<span class='badge b-gray'>🗂️ {s.get('subject')}</span>" if s.get("subject") and s.get("subject") != "- ไม่ระบุ -" else ""
                q_tag = f"<span class='badge b-gold'>Q{s.get('user_order', 99)}</span>" if int(s.get('user_order', 99)) != 99 else ""
                type_icon = "💀 BOSS" if s.get("is_boss") else "📖" if s.get("subtasks") else "⚡"

                inline_prog = get_subtask_progress_html(s)

                c1.markdown(f"<div style='margin-bottom:8px;'>{prio_badge} {q_tag} {subj_tag}</div><div style='font-size:1.1em;'>{type_icon} <b>{s['ภารกิจ']}</b> {badge_html} {frozen_badge}</div>{inline_prog}", unsafe_allow_html=True)

                s_id = str(s.get("id", f"unk_s_{s.get('ภารกิจ', '')}"))
                csq_s_text = clean_quote(WARRIOR_CONSEQUENCES[get_stable_index(s_id + 'conseq', len(WARRIOR_CONSEQUENCES))])
                c1.markdown(f"<div class='mentor-quote' style='border-left: 3px solid #ff4b4b;'>🩸 <b>ถ้ากูไม่ทำ:</b> {s.get('consequence', '') or csq_s_text}</div>", unsafe_allow_html=True)

                with c1.popover("✏️ แก้ไขเป้าหมาย"):
                    new_t = st.text_input("ชื่อภารกิจ:", value=s["ภารกิจ"], key=f"ed_s_name_{s['id']}")
                    new_s = st.selectbox("วิชา:", subj_options, index=subj_options.index(s.get("subject", "- ไม่ระบุ -")) if s.get("subject", "- ไม่ระบุ -") in subj_options else 0, key=f"ed_s_sub_{s['id']}")
                    new_p = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"], index=["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"].index(s.get("ประเภท", "🟡 ปานกลาง")) if s.get("ประเภท", "🟡 ปานกลาง") in ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"] else 2, key=f"ed_s_pri_{s['id']}")
                    new_d = st.text_area("รายละเอียด:", value=s.get("รายละเอียด", ""), key=f"ed_s_det_{s['id']}")
                    new_must_do = st.checkbox("🩸 ชี้เป็นชี้ตาย! (พลาดคือพัง)", value=s.get("is_must_do", False), key=f"ed_s_mustdo_{s['id']}")

                    curr_subtasks_str = "\n".join([stk['name'] for stk in s.get("subtasks", [])])
                    new_sub_str = st.text_area("ซอยบทเรียน (Enter เพื่อแยกข้อ):", value=curr_subtasks_str, key=f"ed_s_subs_{s['id']}")

                    new_dl_t = st.radio("ประเภท Deadline:", ["🔴 Deadline (ครูสั่ง/ห้ามพลาด)", "🎯 เป้าหมายส่วนตัว (อยากเสร็จ)", "⚪ ไม่มีกำหนด"], index=0 if "Deadline" in s.get("deadline_type", "🔴") else 1 if "เป้าหมาย" in s.get("deadline_type", "") else 2, key=f"ed_s_dlt_{s['id']}")
                    new_dl_d = ""
                    if "ไม่มีกำหนด" not in new_dl_t:
                        parsed_dt = safe_date_parse(s.get("deadline", ""))
                        new_dl_d = str(st.date_input("วันกำหนด:", value=parsed_dt, key=f"ed_s_dt_{s['id']}"))

                    if st.button("💾 เซฟการแก้ไข", key=f"save_ed_s_{s['id']}", use_container_width=True):
                        s["ภารกิจ"] = new_t; s["subject"] = new_s; s["ประเภท"] = new_p; s["รายละเอียด"] = new_d
                        s["deadline_type"] = new_dl_t; s["deadline"] = new_dl_d; s["is_must_do"] = new_must_do

                        old_subs = {stk['name']: stk['done'] for stk in s.get("subtasks", [])}
                        new_subs_list = []
                        for line in new_sub_str.split('\n'):
                            line = line.strip()
                            if line: new_subs_list.append({"name": line, "done": old_subs.get(line, False), "done_date": ""})
                        s["subtasks"] = new_subs_list
                        save_db(db); st.success("อัปเดตแล้ว!"); safe_rerun()

                with st.expander("📝 ดูขอบเขต/รายละเอียด"):
                    if s.get("รายละเอียด"): st.write(s["รายละเอียด"])
                    all_done = True
                    if s.get("subtasks"):
                        st.markdown("**📌 บทเรียนที่ต้องเก็บ (เรียนบทเดียวก็รอดพิพากษา *ถ้ายังไม่เลยกำหนด*):**")
                        for i, stask in enumerate(s["subtasks"]):
                            is_locked = stask.get("done", False) and stask.get("done_date", "") != today_str
                            can_interact = not is_locked and (not is_frozen or is_overdue)
                            checked = st.checkbox(f"{stask['name']} {'🔒 ('+thai_date_format(stask.get('done_date', ''))+')' if is_locked else ''}", value=stask.get("done", False), disabled=not can_interact, key=f"st_stud_{s['id']}_{i}")
                            if can_interact and checked != stask.get("done", False):
                                s["subtasks"][i]["done"] = checked; s["subtasks"][i]["done_date"] = today_str if checked else ""
                                save_db(db); safe_rerun()
                            if not checked: all_done = False
                        total_subs = len(s["subtasks"]); done_subs = len([stk for stk in s["subtasks"] if stk.get("done")])
                        st.progress(done_subs / total_subs if total_subs > 0 else 0)

                if is_frozen:
                    if c4.button("🔥 ปลดแช่แข็ง", key=f"unfrz_stud_{s['id']}", use_container_width=True): s["skip_today_date"] = ""; save_db(db); safe_rerun()
                else:
                    if c4.button("❄️ แช่แข็ง", key=f"frz_stud_{s['id']}", use_container_width=True): s["skip_today_date"] = today_str; save_db(db); safe_rerun()

                if all_done and (not is_frozen or is_overdue):
                    if c2.button("✅ ติวสำเร็จ", key=f"stud_win_{s['id']}", use_container_width=True):
                        s["เสร็จแล้ว"] = True; s["done_date"] = today_str
                        exp_gain, fail_reduce = calculate_task_rewards(s, current_streak, active_mentor)
                        user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                    if c3.button("📤 ส่งอนุมัติ", key=f"pend_stud_{s['id']}", use_container_width=True): s["รอตรวจ"] = True; save_db(db); safe_rerun()
                else: c2.caption("❄️ แช่แข็ง" if is_frozen and not is_overdue else "🔒 บทเรียนคาอยู่")
                if c5.button("🗑️", key=f"del_stud_{s['id']}"): db["study_missions"][safe_email].remove(s); save_db(db); safe_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        else: st.success("📚 ติวทบทวนเนื้อหาครบหมดแล้วใน Roadmap!")

        pending_study = [s for s in raw_active_study if s.get("รอตรวจ", False)]
        if pending_study:
            st.divider(); st.markdown("### ⏳ วิชาที่รออนุมัติ")
            for s in pending_study:
                c1, c2, c3 = st.columns([5, 2, 2])
                c1.caption(f"⏳ {s['ภารกิจ']}")
                if c2.button("✅ ผ่าน", key=f"appr_stud_{s['id']}"):
                    s["เสร็จแล้ว"] = True; s["รอตรวจ"] = False; s["done_date"] = today_str
                    exp_gain, fail_reduce = calculate_task_rewards(s, current_streak, active_mentor)
                    user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                if c3.button("⏪ กลับมาอ่าน", key=f"revert_stud_{s['id']}"): s["รอตรวจ"] = False; save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 4: 🎯 เควสย่อยส่วนตัว (SIDE QUESTS)
    # ----------------------------------------------------
    with tab_sidequests:
        st.markdown("### 🎯 เควสย่อยส่วนตัว (Side Quests)")
        st.write("งานจิปาถะส่วนตัว เช่น 'วันนี้ต้องลงโปรแกรม', 'ตอบเมล' ไม่ใช่งานใหญ่ แต่ถ้าละเลยโดนหักคะแนนพิพากษา!")

        with st.form("add_sq_form", clear_on_submit=True):
            col_sq1, col_sq2 = st.columns([4, 1])
            sq_name = col_sq1.text_input("ชื่อเควสย่อย:", placeholder="เช่น ลงโปรแกรม ROS 2, ซื้อปากกา")
            if col_sq2.form_submit_button("บรรจุเควส", use_container_width=True):
                if sq_name:
                    db["side_quests"][safe_email].append({"id": str(uuid.uuid4()), "task": sq_name, "done": False, "done_date": ""})
                    save_db(db); safe_rerun()

        active_sq = [sq for sq in db["side_quests"][safe_email] if isinstance(sq, dict) and not sq.get("done")]
        if not active_sq:
            st.info("ไม่มีเควสย่อยค้างอยู่")
        else:
            for sq in active_sq:
                st.markdown("<div class='sq-card'>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([6, 1.5, 0.5])
                col1.markdown(f"🎯 **{sq['task']}**")

                if col2.button("✅ เสร็จสิ้น", key=f"sq_done_{sq['id']}", use_container_width=True):
                    sq["done"] = True; sq["done_date"] = today_str
                    user["exp"] += 5
                    save_db(db); safe_rerun()
                if col3.button("🗑️", key=f"sq_del_{sq['id']}"):
                    db["side_quests"][safe_email].remove(sq)
                    save_db(db); safe_rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 5: ⚒️ โรงตีเหล็ก (THE ADVANCED FORGE V2)
    # ----------------------------------------------------
    with tab_forge:
        st.markdown("### ⚒️ โรงตีเหล็ก V2 (The Advanced Skill Forge)")
        st.write("ปลดล็อกขีดจำกัด! สะสม EXP พัฒนาระดับขั้น (Tiers) ดึงทักษะมาโฟกัสพร้อมกันได้แค่ 2 อย่าง!")

        forge_data = db["skill_forge"].get(safe_email, [])
        active_skills = [sk for sk in forge_data if sk.get("status") == "active"]
        dormant_skills = [sk for sk in forge_data if sk.get("status") == "dormant"]

        with st.expander("➕ เพิ่มทักษะที่อยากเรียนรู้ (Add Skill)"):
            with st.form("forge_add_form", clear_on_submit=True):
                sk_name = st.text_input("ชื่อทักษะ (เช่น เขียนโปรแกรม Python):", key="txt_sk_name")
                sk_why = st.text_input("แรงผลักดัน (ทำไมต้องเก่งเรื่องนี้?):", key="txt_sk_why")
                if st.form_submit_button("บรรจุลงคลังเหล็ก"):
                    if sk_name:
                        db["skill_forge"][safe_email].append({"id": str(uuid.uuid4()), "name": sk_name, "why": sk_why, "status": "dormant", "exp_gained": 0, "date_added": today_str})
                        save_db(db); safe_rerun()

        st.divider()
        st.markdown(f"#### 🔥 ทักษะที่กำลังฝังราก (Active Focus: {len(active_skills)}/2)")
        if not active_skills: st.info("ยังไม่มีทักษะที่ดึงมาฝึก ไปดึงจากคลังสิวะ!")
        for sk in active_skills:
            st.markdown("<div class='glass-panel' style='border-left: 5px solid #F59E0B;'>", unsafe_allow_html=True)
            col1, col2 = st.columns([5, 3])

            sk_exp = sk.get('exp_gained', 0)
            tier_name, tier_color = get_skill_tier_info(sk_exp)

            col1.markdown(f"<h4 style='margin-bottom:0;'>⚡ {sk['name']}</h4>", unsafe_allow_html=True)
            col1.caption(f"🔥 {sk.get('why', '-')}")
            col1.markdown(f"<b style='color:{tier_color};'>{tier_name}</b> | 👑 Lv.{(sk_exp // 100) + 1} | รวม {sk_exp} EXP", unsafe_allow_html=True)
            col1.progress((sk_exp % 100) / 100.0)

            col2.markdown("**โหมดการฝึกฝน:**")
            t1, t2, t3 = col2.columns(3)
            if t1.button("🏃 เบาๆ\n(+10 EXP)", key=f"t1_{sk['id']}", use_container_width=True): sk["exp_gained"]=sk_exp+10; user["exp"]+=2; save_db(db); safe_rerun()
            if t2.button("🔥 เอาจริง\n(+30 EXP)", key=f"t2_{sk['id']}", use_container_width=True): sk["exp_gained"]=sk_exp+30; user["exp"]+=5; save_db(db); safe_rerun()
            if t3.button("💀 ขีดสุด\n(+50 EXP)", key=f"t3_{sk['id']}", use_container_width=True): sk["exp_gained"]=sk_exp+50; user["exp"]+=10; save_db(db); safe_rerun()

            if col2.button("🧊 พักทักษะนี้ (เข้าคลัง)", key=f"rest_{sk['id']}", use_container_width=True): sk["status"] = "dormant"; save_db(db); safe_rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 🧊 คลังทักษะรอการฝึก (Dormant Vault)")
        if not dormant_skills: st.info("คลังว่างเปล่า")
        for sk in dormant_skills:
            with st.container(border=True):
                col1, col2, col3 = st.columns([5, 2, 1])
                sk_exp = sk.get('exp_gained', 0)
                tier_name, tier_color = get_skill_tier_info(sk_exp)

                col1.write(f"🧊 **{sk['name']}** (<span style='color:{tier_color};'>{tier_name}</span> Lv.{(sk_exp // 100) + 1})", unsafe_allow_html=True)
                col1.caption(f"เหตุผล: {sk.get('why', '-')}")
                if col2.button("⚡ สวมใส่เพื่อฝึก (Equip)", key=f"equip_{sk['id']}", use_container_width=True):
                    if len(active_skills) >= 2: st.error("🚨 กฎเหล็ก: โฟกัสพร้อมกันได้แค่ 2 อย่าง!")
                    else: sk["status"] = "active"; save_db(db); safe_rerun()
                if col3.button("🗑️", key=f"del_sk_{sk['id']}"): db["skill_forge"][safe_email].remove(sk); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 6: 🗂️ คลังแสงวิชา (ACADEMIC ARSENAL)
    # ----------------------------------------------------
    with tab_subjects:
        st.markdown("### 🗂️ คลังแสงรายวิชา (Academic Arsenal)")
        st.write("จัดการทุกอย่างแบบแยกตามวิชา ดูงานค้าง ดูตารางสอบ และจดบันทึกช่วยจำ")

        with st.expander("➕ เพิ่มรายวิชาใหม่"):
            with st.form("add_subject_form", clear_on_submit=True):
                sub_name = st.text_input("ชื่อรายวิชา (เช่น คณิตศาสตร์, ROS 2):", key="txt_new_sub_name")
                sub_goal = st.text_input("เป้าหมาย (เช่น เกรด 4, ผ่านระดับ B1):", key="txt_new_sub_goal")
                if st.form_submit_button("บันทึกเข้าคลังแสง"):
                    if sub_name:
                        db["subjects"][safe_email].append({"id": str(uuid.uuid4()), "name": sub_name, "goal": sub_goal, "date_added": today_str})
                        save_db(db); st.success("สร้างรายวิชาเรียบร้อย!"); safe_rerun()

        user_subjects = [s for s in db["subjects"].get(safe_email, []) if isinstance(s, dict)]
        if not user_subjects:
            st.info("ยังไม่มีรายวิชาในคลังแสง ไปสร้างซะ!")
        else:
            all_pending_logs = [i for i in db["command_log"][safe_email] if isinstance(i, dict)]
            all_active_m = [m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว")]
            all_active_s = [s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว")]

            for subj in user_subjects:
                subj_name = subj.get("name", "")
                st.markdown(f"""
                <div class='subject-banner'>
                    <h3>📚 {subj_name}</h3>
                    <p>🎯 เป้าหมาย: <b>{subj.get('goal', 'ไม่ได้ตั้งเป้า')}</b></p>
                </div>
                """, unsafe_allow_html=True)

                col_del_1, col_del_2 = st.columns([8, 1])
                if col_del_2.button("🗑️ ลบวิชานี้", key=f"del_subj_{subj['id']}", use_container_width=True):
                    db["subjects"][safe_email].remove(subj); save_db(db); safe_rerun()

                related_tasks = []
                related_notes = []

                for log in all_pending_logs:
                    if log.get("subject") == subj_name:
                        if log.get("type") == "note": related_notes.append({"source": "planner", "data": log})
                        else: related_tasks.append({"source": "planner", "data": log})

                for m in all_active_m:
                    if m.get("subject") == subj_name: related_tasks.append({"source": "mission", "data": m})
                for s in all_active_s:
                    if s.get("subject") == subj_name: related_tasks.append({"source": "study", "data": s})

                if not related_tasks and not related_notes:
                    st.write("✅ โล่ง! ไม่มีข้อมูลในวิชานี้")
                else:
                    col_view1, col_view2 = st.columns(2)

                    with col_view1:
                        st.markdown("<h5 style='color:#ff4b4b;'>🚨 ภารกิจค้าง & เตรียมสอบ</h5>", unsafe_allow_html=True)
                        if not related_tasks: st.caption("- ไม่มีภารกิจ")
                        else:
                            related_tasks.sort(key=lambda x: get_deadline_score(x["data"].get("deadline", "")))
                            for wrapper in related_tasks:
                                item = wrapper["data"]
                                dl = item.get("deadline", "")
                                dl_type = item.get("deadline_type", "🔴 Deadline")
                                is_must_do = item.get("is_must_do", False)
                                badge_html = get_badge_html(dl, dl_type, is_must_do=is_must_do)
                                prio_badge = get_priority_badge(item.get('priority', item.get('ประเภท', '')))

                                icon = "🔪" if wrapper["source"] == "mission" or item.get("type") == "task" else "📖" if wrapper["source"] == "study" or item.get("type") == "study" else "⚠️"
                                title = item.get("ภารกิจ") if "ภารกิจ" in item else item.get("title", "")

                                css_wrapper = get_task_css_class(item, wrapper["source"] if wrapper["source"] in ["task", "study"] else "task")
                                st.markdown(f"<div class='{css_wrapper}' style='padding:10px;'>", unsafe_allow_html=True)
                                with st.expander(f"{icon} {title}"):
                                    st.markdown(f"{prio_badge} {badge_html}", unsafe_allow_html=True)
                                    st.write(item.get("รายละเอียด") or item.get("detail") or "ไม่มีรายละเอียด")
                                    subs = item.get("subtasks", [])
                                    if subs:
                                        st.markdown("**งานย่อย:**")
                                        for sub in subs: st.write(f"- {'✅' if sub.get('done') else '⬜'} {sub.get('name')}")
                                st.markdown("</div>", unsafe_allow_html=True)

                    with col_view2:
                        st.markdown("<h5 style='color:#38bdf8;'>📝 โน้ตความรู้ / บันทึกช่วยจำ</h5>", unsafe_allow_html=True)
                        if not related_notes: st.caption("- ไม่มีบันทึก")
                        else:
                            for wrapper in related_notes:
                                note = wrapper["data"]
                                prio_badge = get_priority_badge(note.get('priority', ''))
                                css_wrapper = get_task_css_class(note, "task")
                                st.markdown(f"<div class='{css_wrapper}' style='padding:10px;'>", unsafe_allow_html=True)
                                with st.expander(f"📝 {note.get('title', '')}"):
                                    st.markdown(prio_badge, unsafe_allow_html=True)
                                    st.write(note.get("detail", "ไม่มีรายละเอียด"))
                                st.markdown("</div>", unsafe_allow_html=True)
                st.write("")
# ----------------------------------------------------
    # TAB 7: 📝 สมุดบัญชาการ (COMMAND LOG)
    # ----------------------------------------------------
    with tab_planner:
        st.markdown("### 📝 สมุดบัญชาการ (Command Log)")
        st.write("ที่จดรวมทุกอย่าง! (แยกประเภทชัดเจน และแก้ไขได้ทุกเมื่อ)")
        
        pl_type = st.radio("ประเภทการบันทึก:", ["📝 โน้ตทั่วไป (ไม่มี Deadline)", "🔪 เตรียมงาน", "📖 เตรียมเรียน", "⚠️ ตารางสอบ (บังคับ Deadline)"], horizontal=True, key="rad_pl_type")
        
        col_f1, col_f2 = st.columns([3, 1])
        pl_title = col_f1.text_input("หัวข้อเรื่อง:", key="txt_pl_title")
        pl_subject = col_f2.selectbox("🗂️ ผูกกับรายวิชา:", subj_options, key="sb_pl_subject")
        pl_detail = st.text_area("รายละเอียด / ขอบเขตเนื้อหา:", key="txt_pl_detail")
        
        pl_priority = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"], index=2, key="sb_pl_prio")
        pl_subtasks_str = ""
        pl_date = None
        pl_dl_type = "⚪ ไม่มีกำหนด"
        is_must_do_planner = False
        
        if "งาน" in pl_type or "เรียน" in pl_type:
            pl_subtasks_str = st.text_area("🔪 ซอยข้อย่อย (Enter ขึ้นบรรทัดใหม่ / เว้นว่างถ้าเป็นงานชิ้นเดียวจบ):", key="txt_pl_subtasks")
            is_must_do_planner = st.checkbox("🩸 ชี้เป็นชี้ตาย! (MUST DO TODAY)", key="chk_pl_mustdo")
            pl_dl_type = st.radio("ประเภทเป้าหมายเวลา:", ["🔴 Deadline (ครูสั่ง/ห้ามพลาด)", "🎯 เป้าหมายส่วนตัว (อยากเสร็จ)", "⚪ ไม่มีกำหนด"], horizontal=True, key="rad_dl_type")
            if "ไม่มีกำหนด" not in pl_dl_type: pl_date = st.date_input("กำหนดวัน:", key="dt_pl_deadline")
        elif "สอบ" in pl_type:
            pl_dl_type = "🔴 Deadline (ครูสั่ง/ห้ามพลาด)"
            pl_date = st.date_input("วันที่สอบ (ห้ามพลาด):", key="dt_pl_exam_date")

        if st.button("💾 บันทึกลงสมุดบัญชาการ", type="primary", key="btn_save_command_log"):
            if pl_title:
                item_type = "note"
                if "งาน" in pl_type: item_type = "task"
                elif "เรียน" in pl_type: item_type = "study"
                elif "สอบ" in pl_type: item_type = "exam"
                
                final_dl = str(pl_date) if pl_date and item_type != "note" and "ไม่มีกำหนด" not in pl_dl_type else ""
                subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in pl_subtasks_str.split('\n') if s.strip()] if item_type in ["task", "study"] else []
                
                db["command_log"][safe_email].append({
                    "id": str(uuid.uuid4()), "type": item_type, "title": pl_title, "detail": pl_detail, "priority": pl_priority, 
                    "subtasks": subtasks, "deadline": final_dl, "deadline_type": pl_dl_type, "is_must_do": is_must_do_planner, "date_added": today_str, "subject": pl_subject
                })
                save_db(db); st.success("บันทึกสำเร็จ!"); safe_rerun()
            else: st.warning("ใส่ชื่อหัวข้อด้วยสิวะ!")
                    
        planner_items = db["command_log"].get(safe_email, [])
        if planner_items:
            exams = [i for i in planner_items if i.get("type") == "exam"]
            tasks_study = [i for i in planner_items if i.get("type") in ["task", "study"]]
            notes = [i for i in planner_items if i.get("type") == "note"]
            
            if exams:
                st.divider()
                st.markdown("#### ⚠️ ตารางสอบ (Exams)")
                for exam in sorted(exams, key=lambda x: x.get("deadline", "9999-12-31")):
                    css_class = get_task_css_class(exam, "task")
                    st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
                    c1, c2 = st.columns([5, 1])
                    subj_tag = f"<span class='badge b-gray'>🗂️ {exam.get('subject')}</span>" if exam.get("subject") and exam.get("subject") != "- ไม่ระบุ -" else ""
                    badge_html = get_badge_html(exam.get('deadline', ''), "🔴 Deadline")
                    prio_badge = get_priority_badge(exam.get('priority', ''))
                    
                    c1.markdown(f"**{exam['title']}** {subj_tag} | 📅 วันสอบ: {thai_date_format(exam.get('deadline', '-'))} {badge_html} {prio_badge}", unsafe_allow_html=True)
                    
                    with c1.popover("✏️ แก้ไขสอบ"):
                        new_t = st.text_input("หัวข้อ:", value=exam['title'], key=f"ed_e_t_{exam['id']}")
                        new_s = st.selectbox("วิชา:", subj_options, index=subj_options.index(exam.get("subject", "- ไม่ระบุ -")) if exam.get("subject", "- ไม่ระบุ -") in subj_options else 0, key=f"ed_e_s_{exam['id']}")
                        new_p = st.selectbox("ความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"], index=["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"].index(exam.get("priority", "🟡 ปานกลาง")) if exam.get("priority", "🟡 ปานกลาง") in ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"] else 2, key=f"ed_e_p_{exam['id']}")
                        new_d = st.text_area("รายละเอียด:", value=exam.get("detail", ""), key=f"ed_e_d_{exam['id']}")
                        parsed_dt = safe_date_parse(exam.get("deadline", ""))
                        new_dt = str(st.date_input("วันสอบ:", value=parsed_dt, key=f"ed_e_dt_{exam['id']}"))
                        
                        if st.button("💾 เซฟการแก้ไข", key=f"sv_e_{exam['id']}", use_container_width=True):
                            exam['title'] = new_t; exam['subject'] = new_s; exam['priority'] = new_p; exam['detail'] = new_d; exam['deadline'] = new_dt; save_db(db); safe_rerun()
                            
                    with c1.expander("📝 ดูรายละเอียด"): st.write(exam.get("detail", "ไม่มีรายละเอียด"))
                    if c2.button("🗑️", key=f"del_exm_{exam['id']}"): planner_items.remove(exam); save_db(db); safe_rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            
            if tasks_study:
                st.divider()
                st.markdown("#### ⏳ งานและการเรียนที่เตรียมไว้ (ดึงเข้าหน้าหลักได้เลย)")
                active_m_slots = len([m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว") and not m.get("subtasks")])
                active_s_slots = len([s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว") and not s.get("subtasks")])
                
                tasks_study.sort(key=lambda x: (0 if x.get("is_must_do") else 1, get_priority_score(x.get("priority", "")), get_deadline_score(x.get("deadline", ""))))
                for item in tasks_study:
                    css_class = get_task_css_class(item, item.get("type", "task"))
                    st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([5, 2, 1])
                    
                    dl_str = item.get("deadline", "")
                    dl_type = item.get("deadline_type", "🔴 Deadline")
                    is_must_do = item.get("is_must_do", False)
                    
                    icon = "🔪 [งาน]" if item.get("type") == "task" else "📖 [เรียน]"
                    subj_tag = f"<span class='badge b-gray'>🗂️ {item.get('subject')}</span>" if item.get("subject") and item.get("subject") != "- ไม่ระบุ -" else ""
                    badge_html = get_badge_html(dl_str, dl_type, is_must_do=is_must_do)
                    prio_badge = get_priority_badge(item.get('priority', '🟡 ปานกลาง'))
                    
                    c1.markdown(f"<div style='margin-bottom:8px;'>{prio_badge} {subj_tag}</div><div style='font-size:1.1em;'><b>{icon} {item['title']}</b> {badge_html}</div>", unsafe_allow_html=True)
                    
                    with c1.popover("✏️ แก้ไขงาน/เรียน"):
                        new_t = st.text_input("หัวข้อ:", value=item['title'], key=f"ed_pl_t_{item['id']}")
                        new_s = st.selectbox("วิชา:", subj_options, index=subj_options.index(item.get("subject", "- ไม่ระบุ -")) if item.get("subject", "- ไม่ระบุ -") in subj_options else 0, key=f"ed_pl_s_{item['id']}")
                        new_p = st.selectbox("ความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"], index=["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"].index(item.get("priority", "🟡 ปานกลาง")) if item.get("priority", "🟡 ปานกลาง") in ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"] else 2, key=f"ed_pl_p_{item['id']}")
                        new_d = st.text_area("รายละเอียด:", value=item.get("detail", ""), key=f"ed_pl_d_{item['id']}")
                        new_must_do = st.checkbox("🩸 ชี้เป็นชี้ตาย!", value=item.get("is_must_do", False), key=f"ed_pl_mustdo_{item['id']}")
                        
                        curr_subtasks = "\n".join([stk['name'] for stk in item.get("subtasks", [])])
                        new_subs = st.text_area("งานย่อย (Enter เพื่อแยก):", value=curr_subtasks, key=f"ed_pl_subs_{item['id']}")
                        
                        new_dl_t = st.radio("ประเภท Deadline:", ["🔴 Deadline (ครูสั่ง/ห้ามพลาด)", "🎯 เป้าหมายส่วนตัว (อยากเสร็จ)", "⚪ ไม่มีกำหนด"], index=0 if "Deadline" in item.get("deadline_type", "🔴") else 1 if "เป้าหมาย" in item.get("deadline_type", "") else 2, key=f"ed_pl_dlt_{item['id']}")
                        new_dl_d = ""
                        if "ไม่มีกำหนด" not in new_dl_t:
                            parsed_dt = safe_date_parse(item.get("deadline", ""))
                            new_dl_d = str(st.date_input("วันกำหนด:", value=parsed_dt, key=f"ed_pl_dt_{item['id']}"))
                            
                        if st.button("💾 เซฟการแก้ไข", key=f"sv_pl_{item['id']}", use_container_width=True):
                            item['title'] = new_t; item['subject'] = new_s; item['priority'] = new_p; item['detail'] = new_d
                            item['deadline_type'] = new_dl_t; item['deadline'] = new_dl_d; item['is_must_do'] = new_must_do
                            item['subtasks'] = [{"name": line.strip(), "done": False, "done_date": ""} for line in new_subs.split('\n') if line.strip()]
                            save_db(db); safe_rerun()
                    
                    with c1.expander("📝 ดูรายละเอียดและงานย่อย"):
                        st.write(item.get("detail", "ไม่มีรายละเอียด"))
                        if item.get("subtasks"):
                            st.markdown("**งานย่อย:**")
                            for s in item["subtasks"]: st.write(f"- {s.get('name', '')}")
                    
                    if item.get("type") == "task":
                        if not item.get("subtasks") and active_m_slots >= 3: c2.button("⚡ โควตางานเดี่ยวเต็ม", key=f"pull_{item['id']}", disabled=True)
                        else:
                            if c2.button("⚡ ดึงเข้าหน้างาน", key=f"pull_{item['id']}", type="primary"):
                                final_task_name = f"[{item['subject']}] {item['title']}" if item.get('subject') and item.get('subject') != "- ไม่ระบุ -" else item['title']
                                db["missions"][safe_email].append({
                                    "id": item["id"], "วันที่": today_str, "ภารกิจ": final_task_name, "รายละเอียด": item.get("detail", ""), 
                                    "ประเภท": item.get("priority", "🟡 ปานกลาง"), "bounty": False, "is_boss": False, "custom_order": 99, "user_order": 99, 
                                    "is_queued": False, "skip_today_date": "", "deadline": item.get("deadline", ""), "deadline_type": item.get("deadline_type", "🔴 Deadline"), 
                                    "is_must_do": item.get("is_must_do", False),
                                    "subtasks": item.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False, "subject": item.get("subject", "- ไม่ระบุ -")
                                })
                                planner_items.remove(item); save_db(db); safe_rerun()
                    else:
                        if not item.get("subtasks") and active_s_slots >= 3: c2.button("📖 โควตาเรียนเดี่ยวเต็ม", key=f"pull_{item['id']}", disabled=True)
                        else:
                            if c2.button("📖 ดึงเข้าหน้าเรียน", key=f"pull_{item['id']}", type="primary"):
                                final_task_name = f"[{item['subject']}] {item['title']}" if item.get('subject') and item.get('subject') != "- ไม่ระบุ -" else item['title']
                                db["study_missions"][safe_email].append({
                                    "id": item["id"], "วันที่": today_str, "ภารกิจ": final_task_name, "รายละเอียด": item.get("detail", ""), 
                                    "ประเภท": item.get("priority", "🟡 ปานกลาง"), "bounty": False, "is_boss": False, "custom_order": 99, "user_order": 99, 
                                    "is_queued": False, "skip_today_date": "", "deadline": item.get("deadline", ""), "deadline_type": item.get("deadline_type", "🔴 Deadline"), 
                                    "is_must_do": item.get("is_must_do", False),
                                    "subtasks": item.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False, "is_study": True, "subject": item.get("subject", "- ไม่ระบุ -")
                                })
                                planner_items.remove(item); save_db(db); safe_rerun()
                                
                    if c3.button("🗑️ ลบทิ้ง", key=f"del_pl_{item['id']}"): planner_items.remove(item); save_db(db); safe_rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            if notes:
                st.divider()
                st.markdown("#### 📝 โน้ตทั่วไป (General Notes) - ไม่มี Deadline")
                for note in reversed(notes):
                    css_class = get_task_css_class(note, "task")
                    st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
                    subj_tag = f"<span class='badge b-gray'>🗂️ {note.get('subject')}</span>" if note.get("subject") and note.get("subject") != "- ไม่ระบุ -" else ""
                    prio_badge = get_priority_badge(note.get('priority', ''))
                    
                    with st.expander(f"📝 {note['title']} | (บันทึกเมื่อ: {thai_date_format(note.get('date_added', '-'))})"):
                        st.markdown(f"{prio_badge} {subj_tag}", unsafe_allow_html=True)
                        
                        with st.popover("✏️ แก้ไขโน้ต"):
                            new_title = st.text_input("แก้หัวข้อ:", value=note['title'], key=f"txt_ed_title_{note['id']}")
                            new_s = st.selectbox("วิชา:", subj_options, index=subj_options.index(note.get("subject", "- ไม่ระบุ -")) if note.get("subject", "- ไม่ระบุ -") in subj_options else 0, key=f"ed_n_sub_{note['id']}")
                            new_p = st.selectbox("ความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"], index=["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"].index(note.get("priority", "🟡 ปานกลาง")) if note.get("priority", "🟡 ปานกลาง") in ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"] else 2, key=f"ed_n_pri_{note['id']}")
                            new_content = st.text_area("แก้เนื้อหา:", value=note.get('detail', ''), height=150, key=f"txt_ed_det_{note['id']}")
                            
                            c1, c2 = st.columns([1, 1])
                            if c1.button("💾 บันทึกการแก้ไข", key=f"sv_n_{note['id']}", use_container_width=True):
                                note['title'] = new_title; note['subject'] = new_s; note['priority'] = new_p; note['detail'] = new_content; save_db(db); st.success("อัปเดตเรียบร้อย!"); safe_rerun()
                            if c2.button("🗑️ ลบทิ้ง", key=f"del_n_{note['id']}", use_container_width=True): planner_items.remove(note); save_db(db); safe_rerun()
                            
                        st.write("---")
                        st.write(note.get("detail", "ไม่มีเนื้อหา"))
                    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 8: ❓ คลังปัญญา (Q&A VAULT)
    # ----------------------------------------------------
    with tab_qa:
        st.markdown("### ❓ คลังปัญญา (Q&A Vault)")
        st.write("สงสัยอะไร? เจอคำตอบแล้วใช่ไหม? บันทึกมันไว้ที่นี่เพื่ออัปเกรดความรู้ของมึงซะ!")
        
        with st.form("add_qa_form", clear_on_submit=True):
            qa_q = st.text_input("คำถาม / เรื่องที่สงสัย (เช่น Error นี้แก้ยังไง?):", placeholder="พิมพ์คำถามที่นี่...")
            qa_a = st.text_area("คำตอบ / วิธีแก้ (สิ่งที่ได้เรียนรู้):", placeholder="พิมพ์คำตอบ หรือโน้ตกันลืมที่นี่...", height=100)
            if st.form_submit_button("บันทึกคลังปัญญา", use_container_width=True):
                if qa_q and qa_a:
                    db["qa_vault"][safe_email].append({"id": str(uuid.uuid4()), "q": qa_q, "a": qa_a, "date": today_str})
                    user["exp"] += 2
                    save_db(db); st.success("✅ อัปเกรดความรู้สำเร็จ! (+2 EXP)"); safe_rerun()
                else:
                    st.warning("กรอกให้ครบทั้งคำถามและคำตอบดิวะ!")

        st.divider()
        qa_list = db["qa_vault"].get(safe_email, [])
        if not qa_list:
            st.info("คลังปัญญายังว่างเปล่า... โลกนี้ไม่มีอะไรให้มึงสงสัยเลยหรอ?")
        else:
            for qa in reversed(qa_list):
                if not isinstance(qa, dict): continue
                st.markdown("<div class='qa-card'>", unsafe_allow_html=True)
                with st.expander(f"❓ {qa['q']} (บันทึกเมื่อ: {thai_date_format(qa.get('date', ''))})"):
                    st.markdown(f"**💡 คำตอบ:**\n\n{qa['a']}")
                    if st.button("🗑️ ลบทิ้ง", key=f"del_qa_{qa['id']}"):
                        db["qa_vault"][safe_email].remove(qa)
                        save_db(db); safe_rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 9: 🪞 กระจกแห่งความรับผิดชอบ
    # ----------------------------------------------------
    with tab_mirror:
        st.markdown("### 🪞 กระจกแห่งความรับผิดชอบ (Accountability Mirror)")
        mirror_notes = db["accountability_mirror"].get(safe_email, [])
        with st.form("mirror_add_form", clear_on_submit=True):
            st.markdown("**เขียน Post-it แปะกระจก**")
            note_text = st.text_area("ความจริงหรือเป้าหมาย (เช่น 'กูแม่งขี้เกียจตอนเช้า' หรือ 'ต้องลุกไปวิ่ง'):", height=100, key="txt_mirror_text")
            note_type = st.radio("ประเภท:", ["🔥 ความจริงอันน่าเกลียด (Brutal Truth)", "🎯 เป้าหมายที่ต้องบดขยี้ (Goal)"], horizontal=True, key="rad_mirror_type")
            if st.form_submit_button("แปะกระจกเดี๋ยวนี้!"):
                if note_text:
                    db["accountability_mirror"][safe_email].append({"id": str(uuid.uuid4()), "text": note_text, "is_goal": "Goal" in note_type, "date_added": today_str})
                    save_db(db); safe_rerun()
        st.divider()
        if mirror_notes:
            cols = st.columns(3)
            for idx, note in enumerate(reversed(mirror_notes)):
                col = cols[idx % 3]
                bg_color, border_color, icon = ("rgba(34,197,94,0.1)", "#22c55e", "🎯") if note.get('is_goal') else ("rgba(239,68,68,0.1)", "#ef4444", "🔥")
                with col:
                    st.markdown(f"<div style='background-color: {bg_color}; border-left: 5px solid {border_color}; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'><b>{icon} {thai_date_format(note.get('date_added', '-'))}</b><br><p style='margin-top: 8px;'>{note.get('text', '')}</p></div>", unsafe_allow_html=True)
                    if st.button("🗑️ ดึงออก", key=f"del_mirror_{note['id']}", use_container_width=True): db["accountability_mirror"][safe_email].remove(note); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 10: ⛓️ วินัยเหล็ก
    # ----------------------------------------------------
    with tab_habits:
        st.markdown("### ⛓️ วินัยเหล็ก (THE IRON HABITS)")
        with st.expander("➕ เพิ่มวินัยเหล็กใหม่"):
            with st.form("habit_form", clear_on_submit=True):
                h_name = st.text_input("ชื่อวินัย (เช่น นั่งสมาธิ 10 นาที, ดื่มน้ำ):", key="txt_h_name")
                h_detail = st.text_input("คติเตือนใจ / ทำไปทำไม?:", key="txt_h_detail")
                h_conseq = st.text_input("🩸 ผลของการหลุดวินัย:", key="txt_h_conseq")
                if st.form_submit_button("บรรจุวินัยเหล็ก"):
                    if h_name:
                        db["iron_habits"][safe_email].append({"id": str(uuid.uuid4()), "name": h_name, "รายละเอียด": h_detail, "consequence": h_conseq.strip(), "last_done_date": "", "total_done": 0, "user_order": 99, "streak": 0})
                        save_db(db); safe_rerun()
        
        todo_habits = [h for h in db["iron_habits"][safe_email] if isinstance(h, dict) and h.get("last_done_date") != today_str]
        
        if todo_habits:
            with st.expander("🎯 วางแผนลำดับวินัย (Q-Order)"):
                with st.form("set_habit_order_form"):
                    new_h_orders = {}
                    for h in todo_habits:
                        col_q, col_n = st.columns([1, 5])
                        new_h_orders[h["id"]] = col_q.number_input("คิว", min_value=1, max_value=99, value=int(h.get("user_order", 99)), step=1, key=f"q_h_{h['id']}", label_visibility="collapsed")
                        col_n.write(f"⛓️ {h['name']}")
                    if st.form_submit_button("🔒 ล็อคคิววินัย! (เซฟแผน)"):
                        for h in db["iron_habits"][safe_email]:
                            if isinstance(h, dict) and h.get("id") in new_h_orders: h["user_order"] = int(new_h_orders[h["id"]])
                        save_db(db); st.success("✅ อัปเดตผังวินัยเรียบร้อย!"); safe_rerun()
                    
        if db["iron_habits"][safe_email]:
            st.divider()
            for h in db["iron_habits"][safe_email]:
                if not isinstance(h, dict): continue 
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 3, 1])
                    h_streak = h.get("streak", 0)
                    streak_badge = f"<span class='badge b-gold'>🔥 Streak: {h_streak} วัน!</span>" if h_streak > 0 else "<span class='badge b-gray'>❄️ ไม่มี Streak</span>"
                    c1.markdown(f"⛓️ {'🎯 **[Q' + str(h.get('user_order', 99)) + ']** ' if int(h.get('user_order', 99)) != 99 else ''}**{h['name']}**  *({streak_badge} | รวม {h.get('total_done', 0)} ครั้ง)*", unsafe_allow_html=True)
                    
                    with c1.expander("📝 ดูรายละเอียด"):
                        if h.get("รายละเอียด"): st.write(f"💡 **เป้าหมาย:** {h['รายละเอียด']}")
                        h_id = str(h.get("id", f"unk_h_{h.get('name', '')}"))
                        
                        csq_h_text = clean_quote(WARRIOR_CONSEQUENCES[get_stable_index(h_id + 'conseq', len(WARRIOR_CONSEQUENCES))])
                        h_hype = clean_quote(active_quotes[get_stable_index(h_id + 'habit_hype', len(active_quotes))])
                        
                        st.markdown(f"<div class='mentor-quote' style='border-left: 3px solid #ff4b4b;'>🩸 <b>ถ้าหลุดวินัย:</b> {h.get('consequence', '') or csq_h_text}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='mentor-quote' style='border-left: 3px solid #f59e0b;'>{MENTORS[active_mentor]['icon']} <b>{MENTORS[active_mentor]['name']}:</b> {h_hype}</div>", unsafe_allow_html=True)

                    if h.get("last_done_date") == today_str: c2.success("✅ รักษาวินัยได้แล้ววันนี้!")
                    else:
                        if c2.button("🔥 กูทำสำเร็จ!", key=f"h_done_{h.get('id', h.get('name', ''))}", use_container_width=True):
                            h["streak"] = h.get("streak", 0) + 1 if h.get("last_done_date") == yesterday_str else 1
                            h["last_done_date"] = today_str; h["total_done"] = h.get("total_done", 0) + 1
                            user["exp"] += 10 if current_streak >= 30 else 7 if current_streak >= 7 else 5
                            user["failure_prob"] = max(0, user.get("failure_prob",10) - (5 if current_streak >= 30 else 3 if current_streak >= 7 else 2))
                            save_db(db); safe_rerun()
                    if c3.button("🗑️", key=f"del_h_{h.get('id', h.get('name', ''))}"): db["iron_habits"][safe_email].remove(h); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 11: 🏅 ชัยชนะรายวัน
    # ----------------------------------------------------
    with tab_daily_wins:
        st.markdown("### 🏅 ชัยชนะรายวัน (Daily Wins)")
        win_items = db["daily_wins"][safe_email].get("items", [])
        
        with st.expander("➕ เพิ่มเป้าหมายแห่งชัยชนะ"):
            with st.form("add_daily_win_form", clear_on_submit=True):
                new_win = st.text_input("เรื่องที่ต้องชนะตัวเองทุกวัน (เช่น ไม่ลืมกินข้าวเช้า):", key="txt_new_daily_win")
                if st.form_submit_button("บันทึกเป้าหมาย"):
                    if new_win:
                        win_items.append({"id": str(uuid.uuid4()), "name": new_win})
                        db["daily_wins"][safe_email]["items"] = win_items; save_db(db); st.success("เพิ่มเป้าหมายสำเร็จ!"); safe_rerun()
                        
        if win_items:
            today_logs = db["daily_wins"][safe_email].get("logs", {}).get(today_str, {})
            win_count = sum(1 for v in today_logs.values() if v == "win")
            st.progress(win_count / len(win_items) if len(win_items) > 0 else 0, text=f"พลังแห่งชัยชนะวันนี้: {win_count}/{len(win_items)}")
            
            for item in win_items:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([4, 1.5, 1.5, 0.5])
                    status = today_logs.get(item["id"])
                    if status == "win": col1.markdown(f"✅ **<span style='color:#4bff4b;'>{item['name']}</span>**", unsafe_allow_html=True); col2.write("🏆 ชนะแล้ว!")
                    elif status == "lose": col1.markdown(f"❌ **<span style='color:#ff4b4b; text-decoration: line-through;'>{item['name']}</span>**", unsafe_allow_html=True); col2.write("💀 แพ้ราบคาบ")
                    else:
                        col1.markdown(f"**{item['name']}**")
                        if col2.button("✅ ชนะ", key=f"win_{item['id']}", use_container_width=True): db["daily_wins"][safe_email]["logs"].setdefault(today_str, {})[item["id"]] = "win"; user["exp"] += 5; save_db(db); safe_rerun()
                        if col3.button("❌ แพ้", key=f"lose_{item['id']}", use_container_width=True): db["daily_wins"][safe_email]["logs"].setdefault(today_str, {})[item["id"]] = "lose"; user["blood_debt"] = user.get("blood_debt", 0) + 10; save_db(db); safe_rerun()
                    if col4.button("🗑️", key=f"del_dwin_{item['id']}"): win_items.remove(item); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 12: 🔥 พักใจ
    # ----------------------------------------------------
    with tab_sanctuary:
        st.markdown("## 🔥 แคมป์ไฟพักใจ (The Sanctuary)")
        with st.form("sanctuary_form", clear_on_submit=True):
            sanc_text = st.text_area("โยนความรู้สึกหนักๆ ของมึงลงในกองไฟ...", height=150, key="txt_sanc_text")
            if st.form_submit_button("🔥 ปล่อยวางมันลง"):
                if sanc_text: db["sanctuary"][safe_email].append({"id": str(uuid.uuid4()), "วันที่": today_str, "ข้อความ": sanc_text}); save_db(db); st.success("รับฟังแล้ว... พักซะ"); safe_rerun()
        st.divider()
        if db.get("sanctuary", {}).get(safe_email):
            for note in reversed(db["sanctuary"][safe_email][-10:]):
                if isinstance(note, dict):
                    with st.container(border=True):
                        st.caption(f"📅 วันที่บันทึก: {thai_date_format(note.get('วันที่', ''))}"); st.write(f"💭 {note.get('ข้อความ', '')}")
                        if active_mentor == "Jesus": 
                            j_quote = clean_quote(random.choice(MENTORS['Jesus']['quotes']))
                            st.markdown(f"<p style='color: #38bdf8; font-style: italic; font-size: 0.9em;'>✝️ \"{j_quote}\"</p>", unsafe_allow_html=True)


# ==========================================
# 💰 อัปเกรดระบบการเงิน (ULTIMATE FINANCE TRACKER)
# ==========================================
st.divider()
st.markdown("### 💰 คลังทุนสร้างฝัน (Ultimate Finance Tracker)")

c_fin1, c_fin2 = st.columns([2, 1])
with c_fin1:
    st.write(f"**เป้าหมายหลัก:** {finance.get('goal_name', 'ยังไม่ตั้ง')}")
    total_ledger = sum([float(t.get("amount", 0.0)) for t in finance.get("ledger", []) if t.get("type") in ["income", "savings"]]) - sum([float(t.get("amount", 0.0)) for t in finance.get("ledger", []) if t.get("type") == "expense"])
    finance["current"] = max(0.0, float(total_ledger)) 
    
    cur = float(finance.get('current', 0.0))
    tgt = float(finance.get('goal_amount', 1.0))
    st.progress(max(0.0, min(cur / tgt if tgt > 0 else 1.0, 1.0)), text=f"ยอดคงเหลือ: {cur:,.2f} / {tgt:,.2f} บาท")
    
with c_fin2:
    with st.popover("⚙️ ตั้งเป้าหมาย/เพิ่มธุรกรรม"):
        new_g_name = st.text_input("ชื่อเป้าหมายเงิน:", value=finance.get('goal_name', ''), key="txt_fin_goal_name")
        new_g_amt = st.number_input("ยอดเป้าหมาย:", value=float(finance.get('goal_amount', 0.0)), step=100.0, key="num_fin_goal_amt")
        if st.button("บันทึกเป้าหมาย", key="btn_save_fin_goal"): 
            finance['goal_name'] = new_g_name; finance['goal_amount'] = float(new_g_amt); save_db(db); safe_rerun()
        st.divider()
        tx_name = st.text_input("รายการ (เช่น ค่าข้าว, แม่ให้เงิน):", key="txt_tx_name")
        tx_type = st.radio("ประเภท:", ["🟢 รายรับ / เงินออม", "🔴 รายจ่าย"], horizontal=True, key="rad_tx_type")
        tx_amt = st.number_input("จำนวนเงิน:", min_value=0.0, step=10.0, key="num_tx_amt")
        if st.button("📝 บันทึกลงสมุดบัญชี", type="primary", key="btn_save_ledger"):
            if tx_name and tx_amt > 0:
                finance["ledger"].append({"id": str(uuid.uuid4()), "date": today_str, "name": tx_name, "type": "income" if "รายรับ" in tx_type else "expense", "amount": float(tx_amt)})
                save_db(db); st.success("บันทึกยอดสำเร็จ!"); safe_rerun()

# ==========================================
# 6. หหนี้เลือด & ⚖️ THE JUDGMENT FEED (AUTOMATED)
# ==========================================
st.divider()
c_bot1, c_bot2 = st.columns(2)
with c_bot1:
    my_exp = ((user.get("level",1) - 1) * 100) + user.get("exp",0)
    st.metric("พลังร่างวินัยสูงสุด", f"{user.get('ghost_exp',0)} EXP")
    st.metric("พลังในปัจจุบัน", f"{my_exp} EXP", delta=f"{my_exp - user.get('ghost_exp',0)} (เปรียบเทียบ)")
with c_bot2:
    st.markdown("### 🩸 หนี้เลือด")
    st.metric("ต้องวิดพื้นชดใช้", f"{user.get('blood_debt', 0)} ที")
    if user.get("blood_debt", 0) > 0:
        if st.button("วิดพื้นใช้หนี้หมดแล้ว! (ปลดล็อก)", key="btn_pay_debt"): user["blood_debt"] = 0; user["in_cage"] = False; save_db(db); safe_rerun()

st.divider()
st.markdown("<h2>⚖️ THE JUDGMENT FEED (พิพากษาก่อนนอน)</h2>", unsafe_allow_html=True)
if user.get("ambush_task", "") != "":
    st.error(f"🚨 **โดนซุ่มโจมตีวินัย!** คำสั่ง: **{user['ambush_task']}**")
    if st.button("🔥 ทำเสร็จแล้ว!", key="btn_clear_ambush"): user["ambush_task"] = ""; user["exp"] += 20; save_db(db); safe_rerun()
elif user.get("judged_today") == today_str: 
    st.success(f"🔥 จบวันเรียบร้อย! วันนี้มึงประทับตราคำพิพากษาไปแล้ว ไปนอนซะ!")
else:
    if user.get("in_cage") or user.get("blood_debt", 0) > 0: 
        st.error("❌ ติดหนี้เลือดอยู่! ไปวิดพื้นชดใช้กรรมให้หมดก่อนมาขอรับคำพิพากษา!")
    else:
        expected_today = []
        completed_today = []
        progressed_today = [] 
        
        # 1. เช็คงานหลักและเรียน
        all_m_and_s = [m for m in db["missions"][safe_email] if isinstance(m, dict)] + [s for s in db["study_missions"][safe_email] if isinstance(s, dict)]
        for item in all_m_and_s:
            if item.get("เสร็จแล้ว") and item.get("done_date") == today_str: 
                completed_today.append(item)
            elif not item.get("เสร็จแล้ว") and not item.get("รอตรวจ", False):
                
                is_overdue = is_overdue_check(item.get("deadline", ""))
                made_progress_today = False
                
                if item.get("subtasks"):
                    for sub in item["subtasks"]:
                        if sub.get("done") and sub.get("done_date") == today_str:
                            made_progress_today = True
                            break
                            
                if is_overdue:
                    expected_today.append(item)
                elif made_progress_today:
                    progressed_today.append(item) 
                elif item.get("is_must_do") or item.get("skip_today_date") != today_str: 
                    expected_today.append(item)
                    
        # 2. เช็ควินัยเหล็ก
        for h in db["iron_habits"][safe_email]:
            if isinstance(h, dict):
                if h.get("last_done_date") == today_str: completed_today.append(h)
                else: expected_today.append(h)
                
        # 3. เช็คเควสย่อย
        for sq in db["side_quests"][safe_email]:
            if isinstance(sq, dict):
                if sq.get("done") and sq.get("done_date") == today_str: completed_today.append(sq)
                elif not sq.get("done"): expected_today.append(sq)

        done_count = len(completed_today) + len(progressed_today)
        missed_count = len(expected_today)
        total_load = done_count + missed_count
        score_percent = int((done_count / total_load * 100)) if total_load > 0 else 100
        
        if total_load == 0 or score_percent == 100: grade, grade_color = "S", "#f59e0b"
        elif score_percent >= 80: grade, grade_color = "A", "#38bdf8"
        elif score_percent >= 60: grade, grade_color = "B", "#22c55e"
        elif score_percent >= 40: grade, grade_color = "C", "#f97316"
        else: grade, grade_color = "F", "#ef4444"

        evaluations = {
            "S": "ไร้ที่ติ! ความสมบูรณ์แบบคือสิ่งที่คู่ควรกับผู้ที่มุ่งมั่น จงรักษามันไว้!",
            "A": "ทำได้ดีมากไอ้น้อง! แม้จะแอบหลุดไปบ้าง แต่มึงพิสูจน์แล้วว่ามึงเอาจริง!",
            "B": "ผ่านเกณฑ์ แต่มึงรู้ตัวใช่ไหมว่ามึงยังทำได้ดีกว่านี้? อย่าเพิ่งพอใจแค่นี้!",
            "C": "เกือบจะเน่า! มึงมัวแต่หาข้ออ้างใช่ไหม? พรุ่งนี้ถ้ายังเป็นแบบนี้ กูจะเหยียบมึงจมดิน!",
            "F": "ขยะสังคม! น่าสมเพชที่สุด! วันนี้มึงปล่อยให้ความขี้เกียจข่มขืนจิตใจมึงเต็มประตู!"
        }
        
        st.markdown(f"<div style='background-color:rgba(0,0,0,0.5); padding:20px; border: 2px solid {grade_color}; border-radius: 10px; text-align:center; box-shadow: 0 0 15px {grade_color}40;'>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color: {grade_color}; font-size: 4.5em; margin-bottom:0; text-shadow: 2px 2px 10px rgba(0,0,0,0.8);'>GRADE: {grade}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3>วินัยสัมฤทธิ์ผล: {score_percent}%</h3>", unsafe_allow_html=True)
        st.caption(f"เสร็จสมบูรณ์: {len(completed_today)} | ก้าวหน้า (ทำ Subtask แล้ว): {len(progressed_today)} | พัง/ดอง/เลยกำหนด: {len(expected_today)}")
        st.divider()
        st.markdown(f"<h4 style='color:{grade_color};'>🗣️ คำตัดสินจาก {MENTORS[active_mentor]['name']}:</h4>", unsafe_allow_html=True)
        st.write(f"> **\"{evaluations[grade]}\"**")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("⚖️ ยอมรับคำพิพากษาและจบวัน! (End Day)", use_container_width=True, type="primary", key="btn_accept_judgment"):
            missed_must_do = len([m for m in expected_today if m.get("is_must_do")])
            
            if grade == "S": user["exp"] += 50; user["streak"] += 1; user["failure_prob"] = max(0, user.get("failure_prob",10) - 10)
            elif grade == "A": user["exp"] += 30; user["streak"] += 1; user["failure_prob"] = max(0, user.get("failure_prob",10) - 5)
            elif grade == "B": user["exp"] += 10; user["failure_prob"] = max(0, user.get("failure_prob",10) - 2)
            elif grade == "C": user["exp"] -= 10; user["streak"] = 0 if active_mentor != "Ippo" else user["streak"]; user["failure_prob"] = min(100, user.get("failure_prob",10) + 10)
            elif grade == "F": 
                user["exp"] -= 30; user["streak"] = 0 if active_mentor != "Ippo" else user["streak"]
                user["blood_debt"] += 50; user["failure_prob"] = min(100, user.get("failure_prob",10) + 20)
                user["in_cage"] = True
            
            if missed_must_do > 0:
                user["blood_debt"] += (missed_must_do * 150)
                user["failure_prob"] = min(100, user.get("failure_prob", 10) + (missed_must_do * 30))
                user["in_cage"] = True
                
            db["judgment_history"][safe_email][today_str] = {"grade": grade, "score": score_percent, "done": done_count, "missed": missed_count, "mentor": active_mentor}
            user["judged_today"] = today_str; user["cleared_yesterday"] = True
            save_db(db); st.balloons(); safe_rerun()

# ==========================================
# 8. 📜 ประวัติศาสตร์เส้นทางวินัย (HISTORY LOG)
# ==========================================
st.divider()
st.markdown("## 📜 ประวัติศาสตร์เส้นทางวินัย (HISTORY LOG)")
tab_h_judgement, tab_h_finance, tab_h_journey, tab_h_cookie, tab_h_fail, tab_h_stats = st.tabs([
    "⚖️ ประวัติคำพิพากษา", "💰 บัญชีการเงิน", "🗺️ บันทึกเดินทาง", "🏆 โหลความภูมิใจ", "🤡 ความกาก & ข้ออ้าง", "📊 สถิติความก้าวหน้า"
])

with tab_h_judgement:
    st.markdown("### ⚖️ สมุดบันทึกคำพิพากษา (Judgment History)")
    judgements = db.get("judgment_history", {}).get(safe_email, {})
    if not judgements: st.info("ยังไม่เคยผ่านการพิพากษาเลยไอ้หนู!")
    else:
        for j_date in sorted(judgements.keys(), reverse=True):
            j_data = judgements[j_date]
            g = j_data.get("grade", "F")
            g_color = "#e2d141" if g == "S" else "#38bdf8" if g == "A" else "#22c55e" if g == "B" else "#f59e0b" if g == "C" else "#ef4444"
            st.markdown(f"<div style='padding: 15px; border-left: 5px solid {g_color}; background: rgba(255,255,255,0.03); margin-bottom: 8px; border-radius:8px;'><b>{thai_date_format(j_date)}</b> | เกรด: <span style='color:{g_color}; font-weight:bold; font-size:1.2em;'>{g}</span> ({j_data.get('score', 0)}%) | สำเร็จ {j_data.get('done', 0)} พลาด {j_data.get('missed', 0)}</div>", unsafe_allow_html=True)

with tab_h_finance:
    st.markdown("### 💰 สมุดบัญชีการเงิน (Financial Ledger)")
    if not finance.get("ledger"): st.info("ยังไม่มีบันทึกการเงิน")
    else:
        for tx in reversed(finance["ledger"]):
            color = "#22c55e" if tx.get("type") in ["income", "savings"] else "#ef4444"
            icon = "🟢" if tx.get("type") in ["income", "savings"] else "🔴"
            st.markdown(f"<div style='border-left: 4px solid {color}; margin-bottom: 8px; background:rgba(255,255,255,0.03); padding: 12px; border-radius:8px;'>{icon} <b>{thai_date_format(tx.get('date', ''))}</b> : {tx.get('name', 'ไม่ระบุ')} <span style='color:{color}; float:right; font-weight:bold;'>{'+' if icon == '🟢' else '-'}{float(tx.get('amount', 0)):,.2f} ฿</span></div>", unsafe_allow_html=True)

with tab_h_journey:
    st.markdown("### 🗺️ ประวัติภารกิจที่พิชิตแล้ว")
    completed_m = sorted([m for m in db["missions"].get(safe_email, []) if isinstance(m, dict) and m.get("เสร็จแล้ว")], key=lambda x: str(x.get("วันที่", "")), reverse=True)
    completed_s = sorted([s for s in db["study_missions"].get(safe_email, []) if isinstance(s, dict) and s.get("เสร็จแล้ว")], key=lambda x: str(x.get("วันที่", "")), reverse=True)
    all_completed = completed_m + completed_s
    
    if not all_completed: st.info("ยังไม่มีภารกิจที่ทำสำเร็จ ไปลุยซะ!")
    for idx, item in enumerate(all_completed):
        c1, c2 = st.columns([10, 1])
        c1.info(f"✅ **[{thai_date_format(item.get('done_date', item.get('วันที่', '-')))}]** | {'📖 เรียน' if item.get('is_study') else '🔪 งาน'} | {item.get('ภารกิจ', '')}")
        if c2.button("🗑️", key=f"del_hm_{idx}_{item.get('id', idx)}"):
            (db["study_missions"] if item.get("is_study") else db["missions"])[safe_email].remove(item); save_db(db); safe_rerun()

with tab_h_cookie:
    st.markdown("### 🏆 โหลความภูมิใจ (Cookie Jar)")
    with st.form("cookie_form", clear_on_submit=True):
        win_text = st.text_input("ความสำเร็จที่อยากเก็บไว้เป็นความทรงจำ:", key="txt_cookie_win")
        if st.form_submit_button("เก็บเข้าโหล!"):
            if win_text: db["cookie_jar"][safe_email].append({"id": str(uuid.uuid4()), "วันที่": today_str, "ชัยชนะ": win_text}); user["exp"] += int(5 * (1.5 if current_streak>=30 else 1.2 if current_streak>=7 else 1.0)); save_db(db); st.success("✅ เก็บความสำเร็จ!"); safe_rerun()

    if not db["cookie_jar"].get(safe_email): st.info("ยังไม่มีความภูมิใจสะสมไว้")
    for idx, c in enumerate(reversed(db["cookie_jar"].get(safe_email, []))):
        c1, c2 = st.columns([10, 1])
        if isinstance(c, dict):
            c1.success(f"🏆 **[{thai_date_format(c.get('วันที่', '-'))}]** {c.get('ชัยชนะ', '')}")
            if c2.button("🗑️", key=f"del_cj_{idx}_{c.get('id', idx)}"): db["cookie_jar"][safe_email].remove(c); save_db(db); safe_rerun()
        else: 
            c1.success(f"🏆 {c}")
            if c2.button("🗑️", key=f"del_cj_old_{idx}"): db["cookie_jar"][safe_email].remove(c); save_db(db); safe_rerun()

with tab_h_fail:
    st.markdown("### 🩸 เชื้อเพลิงความแค้น (ความกากในอดีต)")
    if not db["weakness_fuel"].get(safe_email): st.info("ยังไม่มีประวัติความกาก")
    for idx, w in enumerate(reversed(db["weakness_fuel"].get(safe_email, []))):
        c1, c2 = st.columns([10, 1])
        c1.error(f"🩸 **[เชื้อเพลิงความแค้น]** : {w.get('text', '') if isinstance(w, dict) else w}")
        if c2.button("🗑️", key=f"del_wf_{idx}"): db["weakness_fuel"][safe_email].remove(w); save_db(db); safe_rerun()

with tab_h_stats:
    st.markdown("### 📊 ลานประลองปัญญาและสถิติ (Analytics & Exams)")
    with st.form("exam_form", clear_on_submit=True):
        e_subj = st.text_input("ชื่อวิชา / เรื่องที่ทดสอบ:", key="txt_exam_subj")
        e_score = st.number_input("คะแนนที่ได้ล่าสุด:", min_value=0.0, step=0.1, key="num_exam_score")
        if st.form_submit_button("บันทึกคะแนนสอบ"):
            if e_subj:
                if e_subj not in db["exams"][safe_email]: db["exams"][safe_email][e_subj] = []
                history = db["exams"][safe_email][e_subj]
                if len(history) > 0:
                    last_score = history[-1]
                    if e_score > last_score: user["exp"] += int(30 * (1.5 if current_streak>=30 else 1.0))
                    elif e_score < last_score: user["blood_debt"] = user.get("blood_debt",0) + 50; user["failure_prob"] = min(100, user.get("failure_prob",10) + 10)
                db["exams"][safe_email][e_subj].append(e_score); save_db(db); safe_rerun()

    if db.get("exams", {}).get(safe_email):
        cols = st.columns(3); idx = 0
        for subj, scores in db["exams"][safe_email].items():
            if len(scores) > 0:
                latest = scores[-1]
                delta = round(latest - scores[-2], 2) if len(scores) > 1 else None
                cols[idx % 3].metric(label=f"📖 {subj}", value=latest, delta=delta); idx += 1
                
    st.divider()
    all_m = [m for m in db["missions"].get(safe_email, []) if isinstance(m, dict)] + [s for s in db["study_missions"].get(safe_email, []) if isinstance(s, dict)]
    total_m = len(all_m)
    done_m = len([m for m in all_m if m.get("เสร็จแล้ว")])
    win_rate = (done_m / total_m * 100) if total_m > 0 else 0
    win_count = len([c for c in db["cookie_jar"].get(safe_email, []) if isinstance(c, dict)])
    fail_count = len(db["weakness_fuel"].get(safe_email, []))
    
    c_stat1, c_stat2, c_stat3, c_stat4 = st.columns(4)
    c_stat1.metric("อัตราการรักษาวินัย", f"{win_rate:.1f}%")
    c_stat2.metric("บอสที่จัดการได้", f"{len([m for m in all_m if m.get('เสร็จแล้ว') and m.get('is_boss')])} ตัว")
    c_stat3.metric("เป้าหมายสำเร็จ", f"{done_m} / {total_m}")
    c_stat4.metric("รอยแผลความกาก", f"{fail_count} รอย")
    if win_count + fail_count > 0: 
        st.bar_chart(pd.DataFrame({"จำนวนครั้ง": [win_count, fail_count]}, index=["Discipline (ชนะใจ)", "Weakness (เคยกาก)"]))
