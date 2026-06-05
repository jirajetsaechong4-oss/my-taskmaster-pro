import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import json
import os
import uuid
import hashlib
import random

# ==========================================
# 1. ตั้งค่าระบบ (REBIRTH EDITION)
# ==========================================
st.set_page_config(page_title="REBIRTH HQ", layout="wide", page_icon="💀")
DB_FILE = "rebirth_db.json"
today_date = date.today()
today_str = str(today_date)

GOGGINS_QUOTES = [
    "เวลาของคุณกำลังหมดลงทุกวินาที จะนั่งโง่ๆ หรือจะลุกไปสร้างตำนาน!",
    "ความเจ็บปวดสร้างความยิ่งใหญ่ ความสบายสร้างความกระจอก!",
    "คนอื่นหยุดเมื่อเหนื่อย แต่เราหยุดเมื่อเสร็จ!",
    "เมื่อคุณคิดว่าไม่ไหวแล้ว คุณเพิ่งใช้พลังไปแค่ 40% STAY HARD!",
    "จงทำในสิ่งที่คุณเกลียดทุกวัน เพื่อให้จิตใจมันด้านชา!"
]

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    
    defaults = {"users": {}, "missions": {}, "cookie_jar": {}, "mirror": {}, "callus": {}, "haters": {}}
    for k, v in defaults.items():
        if k not in data: data[k] = v
    return data

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()

# ==========================================
# 2. ระบบคัดกรอง (ฆ่าร่างเก่า สมัครร่างใหม่)
# ==========================================
if "current_user" not in st.session_state:
    st.session_state.current_user = None

with st.sidebar:
    st.title("💀 จุดเกิดใหม่ (Rebirth)")
    
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือก:", ["รายงานตัว (Login)", "ฆ่าร่างเก่า (Register)"])
        email_input = st.text_input("อีเมล:")
        pass_input = st.text_input("รหัสผ่าน:", type="password")
        
        if auth_mode == "ฆ่าร่างเก่า (Register)":
            name_input = st.text_input("ฉายานักรบ:")
            birth_date = st.date_input("วันเกิด (เพื่อคำนวณวันตาย):", min_value=date(1940, 1, 1), max_value=today_date)
            if st.button("เกิดใหม่เป็นคนจริง"):
                if email_input and pass_input and name_input:
                    if email_input in db["users"]:
                        st.error("วิญญาณดวงนี้มีอยู่แล้ว!")
                    else:
                        db["users"][email_input] = {
                            "password": hash_password(pass_input), "username": name_input,
                            "birthdate": str(birth_date), "level": 1, "exp": 0, "streak": 0, 
                            "iron_will": 0, "last_login": today_str, "cleared_yesterday": True,
                            "hell_week_active": False, "hell_week_end": ""
                        }
                        db["missions"][email_input] = []
                        db["cookie_jar"][email_input] = []
                        db["mirror"][email_input] = []
                        db["callus"][email_input] = []
                        db["haters"][email_input] = []
                        save_db(db)
                        st.success("ร่างเก่าตายไปแล้ว ล็อกอินเพื่อเริ่มนรกขุมใหม่!")
                else:
                    st.warning("กรอกให้ครบ!")
                    
        elif auth_mode == "รายงานตัว (Login)":
            if st.button("บุก!"):
                if email_input in db["users"] and db["users"][email_input]["password"] == hash_password(pass_input):
                    user_data = db["users"][email_input]
                    
                    # เช็คการตายจากวันก่อนหน้า
                    if user_data["last_login"] != today_str:
                        if not user_data["cleared_yesterday"]:
                            if user_data.get("hell_week_active", False):
                                user_data["level"] = 1 # HELL WEEK PENALTY (รีเซ็ตเวล 1)
                                user_data["exp"] = 0
                                user_data["hell_week_active"] = False
                            else:
                                user_data["exp"] -= 50
                                if user_data["exp"] < 0:
                                    user_data["level"] = max(1, user_data["level"] - 1)
                                    user_data["exp"] = 0
                            user_data["streak"] = 0
                        
                        # เช็ควันหมดอายุ Hell Week
                        if user_data.get("hell_week_active") and today_str > user_data["hell_week_end"]:
                            user_data["hell_week_active"] = False
                            
                        user_data["last_login"] = today_str
                        user_data["cleared_yesterday"] = False
                        save_db(db)
                        
                    st.session_state.current_user = email_input
                    st.rerun()
                else:
                    st.error("ข้อมูลผิด รึแกความจำเสื่อม!")
    else:
        u_data = db["users"][st.session_state.current_user]
        st.error(f"💀 นักรบ: {u_data['username']}")
        st.warning(f"🔥 ความต่อเนื่อง: {u_data['streak']} วัน")
        st.info(f"🩸 Iron Will (แต้มความถึก): {u_data.get('iron_will', 0)}")
        st.progress(u_data["exp"] / 100, text=f"Lv.{u_data['level']} | EXP: {u_data['exp']}/100")
        
        if u_data.get("hell_week_active"):
            st.error(f"🔥 HELL WEEK ทำงานอยู่! พลาด=กลับเวล 1 (หมดเขต: {u_data['hell_week_end']})")
            
        if st.button("🚪 ถอยทัพ"):
            st.session_state.current_user = None
            st.rerun()

if st.session_state.current_user is None:
    st.title("💀 THE REBIRTH PROTOCOL")
    st.info("👈 ก้าวผ่านประตูนี้ เพื่อทิ้งความอ่อนแอไว้ข้างหลัง")
    st.stop()

email = st.session_state.current_user
user = db["users"][email]

# คำนวณนาฬิกามรณะ
birth_d = datetime.strptime(user["birthdate"], "%Y-%m-%d").date()
days_lived = (today_date - birth_d).days
total_days_80_years = 80 * 365
days_left = total_days_80_years - days_lived

# ==========================================
# 3. แดชบอร์ดนรกแตก
# ==========================================
st.title("🔥 ศูนบัญชาการนักรบ (STAY HARD)")
st.error(f'🗣️ "{random.choice(GOGGINS_QUOTES)}"')

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🕒 เวลา & ความแค้น", "🩸 ความด้านชา & กระจก", "⚔️ ภารกิจดิบ (กฎ 40%)", "🍪 โหลคุกกี้", "💀 จบวัน & โหมดนรก"])

# ----------------- 1. นาฬิกา & บัญชีแค้น -----------------
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🕒 นาฬิกามรณะ (Death Clock)")
        st.caption("สมมติว่าคุณมีอายุ 80 ปี นี่คือเวลาที่คุณเหลือบนโลก... อย่าเสียเวลา")
        st.metric("⏳ จำนวนวันที่เหลืออยู่", f"{days_left:,} วัน")
        st.progress(days_lived / total_days_80_years, text="หลอดพลังชีวิตของคุณที่หายไปแล้ว")
        
    with col2:
        st.markdown("### ☠️ บัญชีแค้น (Prove Them Wrong)")
        with st.form("hater_form", clear_on_submit=True):
            hater_msg = st.text_input("ใครเคยดูถูก หรือพูดจาเหยียดหยามคุณว่ายังไงบ้าง?:")
            if st.form_submit_button("จารึกลงบัญชีแค้น"):
                if hater_msg:
                    db["haters"][email].append(hater_msg)
                    save_db(db)
                    st.rerun()
        
        for h in db["haters"][email]:
            st.error(f"🤬 \"{h}\"")

# ----------------- 2. ด้านชา & กระจก -----------------
with tab2:
    cA, cB = st.columns(2)
    with cA:
        st.markdown("### 🩸 สร้างความด้านชา (Callus Your Mind)")
        st.caption("ทำสิ่งที่เกลียดเพื่อให้จิตใจแข็งแกร่ง (ได้แต้ม Iron Will)")
        with st.form("callus_form", clear_on_submit=True):
            c_task = st.text_input("วันนี้คุณทำสิ่งที่เกลียดอะไรไปแล้วบ้าง? (เช่น อาบน้ำเย็น, ตื่นตี 4):")
            if st.form_submit_button("ฉันเอาชนะความเกลียดได้!"):
                if c_task:
                    db["callus"][email].append({"วันที่": today_str, "สิ่งที่ทำ": c_task})
                    user["iron_will"] = user.get("iron_will", 0) + 1
                    user["exp"] += 15
                    save_db(db)
                    st.rerun()
        
        today_callus = [c for c in db["callus"][email] if c["วันที่"] == today_str]
        for c in today_callus:
            st.success(f"🩸 {c['สิ่งที่ทำ']}")

    with cB:
        st.markdown("### 🪞 กระจกสะท้อนความจริง")
        with st.form("mirror_form", clear_on_submit=True):
            excuse = st.text_input("ข้ออ้างในหัววันนี้คืออะไร?:")
            destroy = st.text_input("จะบดขยี้มันยังไง?:")
            if st.form_submit_button("ประกาศสงคราม!"):
                if excuse and destroy:
                    db["mirror"][email].append({"วันที่": today_str, "ข้ออ้าง": excuse, "การบดขยี้": destroy})
                    save_db(db)
                    st.rerun()
        
        today_mirrors = [m for m in db["mirror"][email] if m["วันที่"] == today_str]
        for m in today_mirrors:
            st.warning(f"🤡 ข้ออ้าง: {m['ข้ออ้าง']} ➡️ ⚔️ บดขยี้: {m['การบดขยี้']}")

# ----------------- 3. ภารกิจดิบ & กฎ 40% -----------------
with tab3:
    st.markdown("### ⚔️ ภารกิจวันนี้ (ห้ามมีคำว่าพรุ่งนี้)")
    
    with st.form("mission_form", clear_on_submit=True):
        m_name = st.text_input("ระบุภารกิจชี้ชะตา:")
        if st.form_submit_button("เพิ่มภารกิจ"):
            if m_name:
                db["missions"][email].append({"id": str(uuid.uuid4()), "ภารกิจ": m_name, "เสร็จแล้ว": False})
                save_db(db)
                st.rerun()
                
    active_missions = [m for m in db["missions"][email] if not m.get("เสร็จแล้ว")]
    
    if active_missions:
        for m in active_missions:
            with st.container():
                st.write(f"❌ **{m['ภารกิจ']}**")
                colA, colB = st.columns(2)
                
                # ปุ่มทำงานปกติ
                if colA.button("✅ เสร็จแบบปกติ", key=f"norm_{m['id']}"):
                    m["เสร็จแล้ว"] = True
                    user["exp"] += 10
                    if user["exp"] >= 100:
                        user["level"] += 1
                        user["exp"] -= 100
                    save_db(db)
                    st.rerun()
                    
                # ปุ่มกฎ 40%
                if colB.button("🛑 กฎ 40% (ฝืนทำต่ออีก 10% ก่อนจบ)", type="primary", key=f"hard_{m['id']}"):
                    m["เสร็จแล้ว"] = True
                    user["exp"] += 25 # โบนัสเยอะกว่ามาก
                    user["iron_will"] = user.get("iron_will", 0) + 1
                    if user["exp"] >= 100:
                        user["level"] += 1
                        user["exp"] -= 100
                    save_db(db)
                    st.toast("คุณมันปีศาจ! ฝืนขีดจำกัดสำเร็จ!", icon="🔥")
                    st.rerun()
                st.divider()
    else:
        st.success("✅ ภารกิจเคลียร์หมดแล้ว!")

# ----------------- 4. โหลคุกกี้ -----------------
with tab4:
    st.markdown("### 🍪 โหลคุกกี้แห่งชัยชนะ (Cookie Jar)")
    with st.form("cookie_form", clear_on_submit=True):
        c_victory = st.text_area("บันทึกความยากลำบากที่คุณเพิ่งชนะมาได้:")
        if st.form_submit_button("ยัดใส่โหล"):
            if c_victory:
                db["cookie_jar"][email].append({"วันที่": today_str, "ชัยชนะ": c_victory})
                save_db(db)
                st.rerun()
                
    if st.button("ขอกำลังใจให้ตัวเองหน่อย"):
        if db["cookie_jar"][email]:
            random_cookie = random.choice(db["cookie_jar"][email])
            st.success(f"💪 **อย่าลืมสิคุณคือคนที่:**\n\n\"{random_cookie['ชัยชนะ']}\" (เมื่อ {random_cookie['วันที่']})")
        else:
            st.error("โหลว่างเปล่า! ออกไปลุยเดี๋ยวนี้!")

# ----------------- 5. จบวัน & โหมดนรก -----------------
with tab5:
    st.markdown("### 💀 ยืนยันจบวัน (End of Day)")
    
    if user["cleared_yesterday"]:
        st.success("🔥 คุณรายงานตัวจบวันไปแล้ว! ไปพักซะ พรุ่งนี้ต้องลุยใหม่!")
    else:
        if active_missions:
            st.error("❌ ปุ่มถูกล็อก! ยังมีภารกิจค้างอยู่ กลับไปทำให้เสร็จ!!")
        else:
            if st.button("🔥 ยืนยันจบวัน! (รักษาสถิติ)"):
                user["cleared_yesterday"] = True
                user["streak"] += 1
                bonus = 20 if user.get("hell_week_active") else 10
                user["exp"] += bonus
                save_db(db)
                st.balloons()
                st.rerun()
                
    st.divider()
    st.markdown("### 🔥 HELL WEEK PROTOCOL (สัปดาห์นรก)")
    st.caption("เปิดโหมดนี้ 7 วัน: ได้ EXP สองเท่า แต่ถ้าพลาดจบวันไม่ทัน เลเวลจะกลับไปเป็น 1 ทันที!")
    
    if user.get("hell_week_active"):
        st.error(f"🔥 โหมดนรกกำลังทำงาน! สิ้นสุดวันที่: {user['hell_week_end']}")
    else:
        if st.button("🚨 เปิดโหมด HELL WEEK (คิดให้ดีก่อนกด)"):
            user["hell_week_active"] = True
            user["hell_week_end"] = str(today_date + timedelta(days=7))
            save_db(db)
            st.toast("ยินดีต้อนรับสู่นรก 7 วัน!", icon="💀")
            st.rerun()