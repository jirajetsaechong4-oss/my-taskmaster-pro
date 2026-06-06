import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import json
import os
import uuid
import hashlib
import random

# ==========================================
# 1. ตั้งค่าระบบนรก (THE APOCALYPSE)
# ==========================================
st.set_page_config(page_title="THE APOCALYPSE HQ", layout="wide", page_icon="☢️")
DB_FILE = "apocalypse_db.json"
today_str = str(date.today())

HARDCORE_QUOTES = [
    "มึงจะหยุดพักตอนไหนก็ได้ แต่ร่างทองของมึงมันไม่เคยหยุดเดิน!",
    "โดพามีนขยะมันหลอกให้สมองมึงฟิน ทั้งที่ชีวิตมึงยังย่ำอยู่กับที่!",
    "เลิกเพ้อเจ้อหาคนที่เขาไม่เห็นค่ามึง แล้วไปวิดพื้นซะ!",
    "ความเจ็บปวดจากการมีวินัย ดีกว่าทรมานจากความเสียใจโว้ย!",
    "มึงไม่ใช่คนธรรมดาแล้ว มึงคือเครื่องจักร เครื่องจักรไม่มีข้ออ้าง!"
]

AMBUSH_TASKS = [
    "กฎก้าวสุดท้าย! ไปแพลงก์ 1 นาทีเดี๋ยวนี้!",
    "คิดว่ารอดแล้วหรอ? วิดพื้น 20 ที ก่อนนอน!",
    "ไปยืนสมาธินิ่งๆ กำหนดลมหายใจ 5 นาที ห้ามขยับ!",
    "จดเป้าหมายของพรุ่งนี้ใส่กระดาษ 3 ข้อเดี๋ยวนี้!",
    "ไปล้างหน้าด้วยน้ำเย็นจัดๆ แล้วค่อยมากดจบวัน!"
]

ANTI_SIMP_SLAPS = [
    "ตื่นไอ้เวร! เขาไม่เอามึงหรอก ไปวิดพื้น 30 ทีเดี๋ยวนี้!",
    "มึงเอาเวลาที่นั่งเพ้อ ไปสร้างตัวเองให้มันรวยก่อนดีกว่าไหมวะ?",
    "เหงาหรอ? ไปวิ่งให้หอบแดกจนไม่มีเวลาคิดเรื่องพวกนี้ซะ!",
    "เลิกเป็นไอ้ขี้แพ้เรียกร้องความสนใจได้แล้ว!"
]

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    
    defaults = {
        "users": {}, "missions": {}, "dark_room": {}, 
        "anti_simp": {}, "dopamine_fails": {}
    }
    for k, v in defaults.items():
        if k not in data: data[k] = v
    return data

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()

# ==========================================
# 2. ระบบกำเนิดเครื่องจักรสังหาร (Login)
# ==========================================
if "current_user" not in st.session_state:
    st.session_state.current_user = None

with st.sidebar:
    st.title("☢️ ประตูนรก (Apocalypse)")
    
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือก:", ["เปิดระบบ (Login)", "ล้างสมองเกิดใหม่ (Register)"])
        email_input = st.text_input("อีเมล:")
        pass_input = st.text_input("รหัสผ่าน:", type="password")
        
        if auth_mode == "ล้างสมองเกิดใหม่ (Register)":
            name_input = st.text_input("รหัสประจำตัว (ชื่อมึง):")
            if st.button("ทิ้งความเป็นคนซะ!"):
                if email_input and pass_input and name_input:
                    if email_input in db["users"]:
                        st.error("รหัสนี้มีคนใช้แล้ว!")
                    else:
                        db["users"][email_input] = {
                            "password": hash_password(pass_input), "username": name_input,
                            "level": 1, "exp": 0, "streak": 0, "blood_debt": 0, "in_cage": False,
                            "ghost_exp": 0, "ambush_task": "", 
                            "hater_letter": "ไอ้กระจอก มึงมันทำอะไรก็ไม่เคยสุดหรอก กูรอสมเพชมึงอยู่!",
                            "last_login": today_str, "cleared_yesterday": True
                        }
                        for k in ["missions", "dark_room", "anti_simp", "dopamine_fails"]:
                            db[k][email_input] = []
                        save_db(db)
                        st.success("สมองมึงถูกล้างแล้ว ล็อกอินซะไอ้เครื่องจักร!")
                else:
                    st.warning("กรอกให้ครบ!")
                    
        elif auth_mode == "เปิดระบบ (Login)":
            if st.button("เดินเครื่อง!"):
                if email_input in db["users"] and db["users"][email_input]["password"] == hash_password(pass_input):
                    user_data = db["users"][email_input]
                    
                    if user_data["last_login"] != today_str:
                        user_data["ghost_exp"] += 25 # ผีเดินหน้าทุกวัน
                        
                        if not user_data.get("cleared_yesterday", False):
                            user_data["exp"] = 0
                            user_data["level"] = max(1, user_data["level"] - 1)
                            user_data["streak"] = 0
                            user_data["blood_debt"] += 100 # อู้=หนี้เลือด 100
                            
                        user_data["last_login"] = today_str
                        user_data["cleared_yesterday"] = False
                        save_db(db)
                        
                    st.session_state.current_user = email_input
                    st.rerun()
                else:
                    st.error("รหัสผิด!")
    else:
        u_data = db["users"][st.session_state.current_user]
        st.error(f"⚙️ รหัส: {u_data['username']}")
        st.warning(f"🔥 เดินเครื่องต่อเนื่อง: {u_data['streak']} วัน")
        st.info(f"🩸 หนี้เลือดที่ต้องจ่าย: {u_data.get('blood_debt', 0)} ครั้ง")
        st.progress(u_data["exp"] / 100, text=f"Lv.{u_data['level']} | พลังงาน: {u_data['exp']}/100")
        
        if st.button("🚪 ปิดระบบ (หนีความจริง)"):
            st.session_state.current_user = None
            st.rerun()

if st.session_state.current_user is None:
    st.title("☢️ THE APOCALYPSE (ไร้รัก ไร้กิเลส)")
    st.info("👈 มึงกล้าพอก็ล็อกอินเข้ามา!")
    st.stop()

email = st.session_state.current_user
user = db["users"][email]

# ==========================================
# 3. แดชบอร์ดวันสิ้นโลก (Tabs)
# ==========================================
st.title("🔥 ศูนย์บัญชาการเครื่องจักร")
st.error(f'🗣️ "{random.choice(HARDCORE_QUOTES)}"')

if user.get("in_cage"):
    st.error("🚨 **มึงติดอยู่ในกรงไอ้ขี้แพ้!** ไปชดใช้หนี้เลือดให้หมดเดี๋ยวนี้ ถึงจะแหกกรงออกมาทำงานต่อได้!")

tab1, tab2, tab3, tab4 = st.tabs(["👻 ลานประหารกิเลส & ร่างทอง", "🩸 หนี้เลือด & กรงขัง", "⚔️ ภารกิจดิบ", "💀 จบวัน & ห้องมืด"])

# ----------------- 1. ลานประหาร & ร่างทอง -----------------
with tab1:
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown("### 💔 เครื่องสับความเพ้อเจ้อ (Anti-Simp)")
        with st.form("anti_simp_form", clear_on_submit=True):
            simp_text = st.text_input("กำลังคิดถึงเขา? เหงาหาคนคุย? สารภาพมา!:")
            if st.form_submit_button("กูเผลอเพ้อเจ้อ!"):
                if simp_text:
                    slap_word = random.choice(ANTI_SIMP_SLAPS)
                    db["anti_simp"][email].append({"วันที่": today_str, "ความเพ้อ": simp_text, "บทลงโทษ": slap_word})
                    user["blood_debt"] += 30
                    save_db(db)
                    st.toast("โดนตบเรียกสติไป 1 ที!", icon="🖐️")
                    st.rerun()
                    
        today_simp = [s for s in db["anti_simp"][email] if s["วันที่"] == today_str]
        for s in today_simp:
            st.error(f"🤡 เพ้อว่า: {s['ความเพ้อ']}\n\n💥 {s['บทลงโทษ']} (หนี้เลือด +30)")

        st.divider()
        st.markdown("### 🗑️ แท่นประหารโดพามีนขยะ")
        st.caption("TikTok, หนังโป๊, เกม, ของหวาน... ถ้ามึงเผลอเสพมัน กดปุ่มประหารตัวเองซะ!")
        if st.button("💀 กูแพ้กิเลส (แอบเสพโดพามีนขยะ)"):
            db["dopamine_fails"][email].append(today_str)
            user["exp"] = 0; user["level"] = max(1, user["level"] - 1)
            user["blood_debt"] += 50; user["in_cage"] = True
            save_db(db)
            st.rerun()

    with colB:
        st.markdown("### 👻 ร่างทอง (Ghost of Potential)")
        my_total_exp = ((user["level"] - 1) * 100) + user["exp"]
        ghost_total_exp = user.get("ghost_exp", 0)
        
        st.metric("พลังร่างทอง (Ghost EXP)", f"{ghost_total_exp} EXP")
        st.metric("พลังของมึงตอนนี้", f"{my_total_exp} EXP", delta=f"{my_total_exp - ghost_total_exp} ตามหลังร่างทอง" if my_total_exp < ghost_total_exp else "มึงนำอยู่!")
        
        st.divider()
        st.markdown("### ✉️ จดหมายจากศัตรู")
        st.warning(f"📝 **มันด่ามึงว่า:**\n\n\"{user.get('hater_letter', '')}\"")
        with st.expander("แก้ไขจดหมาย"):
            with st.form("hater_letter_form"):
                new_letter = st.text_area("ด่าตัวเองซะ:", value=user.get("hater_letter", ""))
                if st.form_submit_button("บันทึก"):
                    user["hater_letter"] = new_letter; save_db(db); st.rerun()

# ----------------- 2. หนี้เลือด & กรงขัง -----------------
with tab2:
    cA, cB = st.columns(2)
    with cA:
        st.markdown("### 🩸 หนี้เลือด (Blood Debt)")
        st.metric("🔥 หนี้เลือดที่ต้องชดใช้ด้วยหยาดเหงื่อ", f"{user.get('blood_debt', 0)} ครั้ง")
        
        with st.form("pay_debt_form", clear_on_submit=True):
            pay_amount = st.number_input("วันนี้มึงวิดพื้น/ซิทอัพชดใช้ไปกี่ครั้ง?:", min_value=1)
            if st.form_submit_button("กูจ่ายหนี้ด้วยเลือดแล้ว!"):
                if user.get("blood_debt", 0) > 0:
                    user["blood_debt"] = max(0, user["blood_debt"] - pay_amount)
                    save_db(db); st.rerun()
                else:
                    st.warning("มึงไม่ได้ติดหนี้ ไปทำอย่างอื่น!")

    with cB:
        st.markdown("### ⛓️ กรงขังไอ้ขี้แพ้")
        if user.get("in_cage"):
            st.error("🚨 มึงอยู่ในกรง! วิธีออก: จ่ายหนี้เลือดให้เหลือ 0 แล้วกดปุ่มนี้!")
            if user.get("blood_debt", 0) == 0:
                if st.button("🔓 กูชดใช้กรรมหมดแล้ว ปล่อยกู!"):
                    user["in_cage"] = False; save_db(db); st.rerun()
            else:
                st.warning("หนี้เลือดยังไม่หมด! มึงไม่มีสิทธิ์แหกกรง!")
        else:
            st.success("มึงยังมีอิสรภาพ จงใช้มันสร้างความยิ่งใหญ่!")

# ----------------- 3. ภารกิจดิบ -----------------
with tab3:
    st.markdown("### ⚔️ ภารกิจเครื่องจักร (สั่งการแล้วต้องจบ)")
    with st.form("mission_form", clear_on_submit=True):
        m_name = st.text_input("ป้อนคำสั่งภารกิจของวันนี้:")
        if st.form_submit_button("ป้อนคำสั่ง"):
            if m_name:
                db["missions"][email].append({"id": str(uuid.uuid4()), "ภารกิจ": m_name, "เสร็จแล้ว": False})
                save_db(db); st.rerun()
                
    active_missions = [m for m in db["missions"][email] if not m.get("เสร็จแล้ว")]
    if active_missions:
        for m in active_missions:
            st.write(f"❌ **{m['ภารกิจ']}**")
            c1, c2 = st.columns(2)
            if c1.button("✅ ประมวลผลเสร็จสิ้น", key=f"n_{m['id']}"):
                m["เสร็จแล้ว"] = True
                user["exp"] += 15
                if user["exp"] >= 100:
                    user["level"] += 1; user["exp"] -= 100
                save_db(db); st.rerun()
            if c2.button("🛑 ฝืนลิมิตเครื่องจักร (+EXPx2)", type="primary", key=f"h_{m['id']}"):
                m["เสร็จแล้ว"] = True
                user["exp"] += 30
                if user["exp"] >= 100:
                    user["level"] += 1; user["exp"] -= 100
                save_db(db); st.rerun()
            st.divider()
    else:
        st.success("✅ คำสั่งทั้งหมดถูกประมวลผลเสร็จสิ้น!")

# ----------------- 4. จบวัน & ห้องมืด -----------------
with tab4:
    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown("### 👁️ ห้องมืด (ความจริง)")
        with st.form("dark_room_form", clear_on_submit=True):
            insecurity = st.text_area("ปมด้อยหรือสันดานเสียของมึงคืออะไร?:")
            if st.form_submit_button("ยอมรับความกาก"):
                if insecurity:
                    db["dark_room"][email].append({"วันที่": today_str, "ข้อความ": insecurity})
                    save_db(db); st.rerun()
        if db["dark_room"][email]:
            st.warning(f"ล่าสุด: {db['dark_room'][email][-1]['ข้อความ']}")

    with col_2:
        st.markdown("### 💀 ยืนยันจบวัน (ปิดระบบ)")
        
        if user.get("ambush_task", "") != "":
            st.error(f"🚨 **โดนซุ่มโจมตี! (กฎก้าวสุดท้าย)** 🚨\n\nระบบสั่งให้มึง: **{user['ambush_task']}**")
            if st.button("🔥 กูทำเสร็จแล้ว! (ข้ามศพกูไปก่อนเถอะ)"):
                user["ambush_task"] = ""
                user["exp"] += 20; save_db(db); st.rerun()
                
        elif user.get("cleared_yesterday"):
            st.success("🔥 วันนี้มึงทำหน้าที่จบแล้ว ปิดหน้าจอแล้วไปนอน!")
            
        else:
            active_missions = [m for m in db["missions"][email] if not m.get("เสร็จแล้ว")]
            if active_missions:
                st.error("❌ งานมึงยังไม่เสร็จ! เครื่องจักรไม่มีสิทธิ์หยุด!")
            elif user.get("in_cage"):
                st.error("❌ มึงยังอยู่ในกรงไอ้ขี้แพ้! แหกกรงมาก่อน!")
            elif user.get("blood_debt", 0) > 0:
                st.error(f"❌ มึงยังติดหนี้เลือด {user['blood_debt']} ครั้ง! ไปชดใช้กรรมซะ!")
            else:
                if st.button("🔥 ประมวลผลสำเร็จทุกอย่าง (กดเพื่อจบวัน)"):
                    if random.random() < 0.2:
                        user["ambush_task"] = random.choice(AMBUSH_TASKS)
                        save_db(db); st.rerun()
                    else:
                        user["cleared_yesterday"] = True
                        user["streak"] += 1
                        user["exp"] += 15
                        save_db(db)
                        st.balloons()
                        st.rerun()