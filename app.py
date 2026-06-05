import streamlit as st
import pandas as pd
from datetime import date, datetime
import json
import os
import uuid
import hashlib

# ==========================================
# 1. ตั้งค่าระบบเบื้องต้น
# ==========================================
st.set_page_config(page_title="Discipline & Focus HQ", layout="wide", page_icon="🎯")
DB_FILE = "focus_hq_db.json"
today = str(date.today())

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    
    # โครงสร้างฐานข้อมูลสำหรับคนมีวินัย
    defaults = {
        "users": {}, "squad_tasks": [], "private_tasks": {}, 
        "habits": {}, "deep_work": {}, "reflections": {}, "contracts": []
    }
    for k, v in defaults.items():
        if k not in data: data[k] = v
        
    return data

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()

# ฟังก์ชันแจก EXP
def add_exp(email, amount):
    db["users"][email]["exp"] += amount
    if db["users"][email]["exp"] >= 100:
        db["users"][email]["level"] += 1
        db["users"][email]["exp"] -= 100
        st.balloons()
        st.success(f"🎉 LEVEL UP! ตอนนี้คุณเลเวล {db['users'][email]['level']} แล้ว!")

# ==========================================
# 2. ระบบเข้าสู่ระบบ (Authentication)
# ==========================================
if "current_user" not in st.session_state:
    st.session_state.current_user = None

with st.sidebar:
    st.title("🔐 เข้าสู่ระบบ")
    
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือกทำรายการ:", ["เข้าสู่ระบบ", "สมัครสมาชิกใหม่"])
        email_input = st.text_input("📧 อีเมล:")
        pass_input = st.text_input("🔑 รหัสผ่าน:", type="password")
        
        if auth_mode == "สมัครสมาชิกใหม่":
            name_input = st.text_input("👤 ชื่อผู้ใช้:")
            if st.button("สมัครสมาชิก"):
                if email_input and pass_input and name_input:
                    if email_input in db["users"]:
                        st.error("อีเมลนี้ถูกใช้แล้ว!")
                    else:
                        db["users"][email_input] = {
                            "password": hash_password(pass_input), 
                            "username": name_input,
                            "level": 1, "exp": 0
                        }
                        # สร้างพื้นที่ส่วนตัว
                        db["private_tasks"][email_input] = []
                        db["habits"][email_input] = []
                        db["deep_work"][email_input] = 0
                        db["reflections"][email_input] = []
                        save_db(db)
                        st.success("สร้างโปรไฟล์สำเร็จ! เข้าสู่ระบบได้เลย")
                else:
                    st.warning("กรอกข้อมูลให้ครบครับ")
                    
        elif auth_mode == "เข้าสู่ระบบ":
            if st.button("เข้าสู่ระบบ"):
                if email_input in db["users"] and db["users"][email_input]["password"] == hash_password(pass_input):
                    st.session_state.current_user = email_input
                    st.rerun()
                else:
                    st.error("ข้อมูลไม่ถูกต้อง!")
    else:
        user_data = db["users"][st.session_state.current_user]
        st.success(f"สวัสดี, {user_data['username']}")
        st.progress(user_data["exp"] / 100, text=f"Lv.{user_data['level']} | EXP: {user_data['exp']}/100")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.current_user = None
            st.rerun()

if st.session_state.current_user is None:
    st.title("🎯 Discipline & Focus HQ")
    st.info("👈 ศูนย์บัญชาการสำหรับคนเอาจริง ล็อกอินเพื่อเริ่มฝึกวินัย")
    st.stop()

user_email = st.session_state.current_user
username = db["users"][user_email]["username"]

# ==========================================
# 3. หน้าต่างการทำงานหลัก
# ==========================================
st.title(f"⚡ ศูนย์บัญชาการของ: {username}")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📢 กลุ่ม & สถิติ", "🔒 งานส่วนตัว", "🌱 สร้างวินัย & โฟกัส", "🧠 ทบทวนตัวเอง", "🗄️ ประวัติ"])

# ----------------- แถบที่ 1: กลุ่ม (Squad & Contracts) -----------------
with tab1:
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 📢 ประกาศงานกลุ่ม")
        with st.form("squad_form", clear_on_submit=True):
            s_name = st.text_input("ชื่องานกลุ่ม / โปรเจกต์:")
            s_date = st.date_input("กำหนดส่ง:")
            if st.form_submit_button("ประกาศงาน"):
                if s_name:
                    db["squad_tasks"].append({"id": str(uuid.uuid4()), "รายการ": s_name, "กำหนดส่ง": str(s_date), "ผู้ประกาศ": username, "เสร็จแล้ว": False})
                    save_db(db)
                    st.rerun()
                    
        squad_active = [t for t in db["squad_tasks"] if not t.get("เสร็จแล้ว")]
        if squad_active:
            for t in squad_active:
                st.info(f"📌 **{t['รายการ']}** (ส่ง: {t['กำหนดส่ง']}) - แจ้งโดย: {t['ผู้ประกาศ']}")
                if st.button(f"✅ เคลียร์งานนี้", key=f"sq_{t['id']}"):
                    t["เสร็จแล้ว"] = True
                    add_exp(user_email, 15) # เคลียร์งานกลุ่มได้ 15 EXP
                    save_db(db)
                    st.rerun()

    with c2:
        st.markdown("### ⚖️ กระดานสัญญาใจ (Accountability)")
        st.caption("ตั้งเป้าหมายโหดๆ พร้อมบทลงโทษถ้าทำไม่สำเร็จ ให้เพื่อนเป็นพยาน!")
        with st.form("contract_form", clear_on_submit=True):
            c_goal = st.text_input("ฉันขอสัญญาว่า จะทำ...")
            c_penalty = st.text_input("ถ้าทำไม่สำเร็จ ฉันจะ... (บทลงโทษ):")
            c_deadline = st.date_input("ภายในวันที่:")
            if st.form_submit_button("✍️ ลงนามสัญญา"):
                if c_goal and c_penalty:
                    db["contracts"].append({"id": str(uuid.uuid4()), "ผู้สัญญา": username, "เป้าหมาย": c_goal, "บทลงโทษ": c_penalty, "กำหนด": str(c_deadline)})
                    save_db(db)
                    st.rerun()
                    
        for c in db["contracts"]:
            st.error(f"🔥 **{c['ผู้สัญญา']}** สัญญาว่า: {c['เป้าหมาย']}\n\n⚠️ **บทลงโทษ:** {c['บทลงโทษ']} (ภายใน: {c['กำหนด']})")

# ----------------- แถบที่ 2: งานส่วนตัว -----------------
with tab2:
    st.markdown("### 🔒 แผนงานส่วนตัว (งาน, ยูทูป, การเรียน)")
    with st.form("priv_form", clear_on_submit=True):
        p_name = st.text_input("สิ่งที่ต้องทำให้สำเร็จ:")
        p_type = st.selectbox("หมวดหมู่:", ["ยูทูป/คอนเทนต์", "การเรียน/พัฒนาตนเอง", "โปรเจกต์ส่วนตัว", "อื่นๆ"])
        p_date = st.date_input("กำหนดวัน:")
        if st.form_submit_button("💾 เพิ่มเข้าแผนงาน"):
            if p_name:
                db["private_tasks"][user_email].append({"id": str(uuid.uuid4()), "รายการ": p_name, "หมวดหมู่": p_type, "กำหนดส่ง": str(p_date), "เสร็จแล้ว": False})
                save_db(db)
                st.rerun()

    priv_active = [t for t in db["private_tasks"][user_email] if not t.get("เสร็จแล้ว")]
    if priv_active:
        df_priv = pd.DataFrame(priv_active).set_index("id")
        edited_priv = st.data_editor(
            df_priv[["เสร็จแล้ว", "หมวดหมู่", "รายการ", "กำหนดส่ง"]],
            column_config={"เสร็จแล้ว": st.column_config.CheckboxColumn("✅ เสร็จแล้ว")},
            disabled=["หมวดหมู่", "รายการ", "กำหนดส่ง"], use_container_width=True
        )
        for task_id, row in edited_priv.iterrows():
            if row["เสร็จแล้ว"]:
                for t in db["private_tasks"][user_email]:
                    if t["id"] == task_id:
                        t["เสร็จแล้ว"] = True
                        add_exp(user_email, 10) # เคลียร์งานส่วนตัวได้ 10 EXP
                        save_db(db)
                        st.rerun()
    else:
        st.success("ไม่มีงานค้าง! คุณมีวินัยยอดเยี่ยมมาก")

# ----------------- แถบที่ 3: สร้างวินัย & โฟกัส -----------------
with tab3:
    cA, cB = st.columns(2)
    
    with cA:
        st.markdown("### 🌱 บันทึกนิสัยรายวัน (Habits)")
        st.caption("พิมพ์สิ่งที่ต้องการฝึกเป็นนิสัย แล้วกดเช็คอิน (+5 EXP)")
        with st.form("habit_form", clear_on_submit=True):
            h_name = st.text_input("นิสัยที่อยากสร้าง (เช่น อ่านหนังสือ 20 หน้า):")
            if st.form_submit_button("เพิ่มนิสัย"):
                if h_name:
                    db["habits"][user_email].append({"id": str(uuid.uuid4()), "ชื่อ": h_name, "ทำล่าสุด": ""})
                    save_db(db)
                    st.rerun()
                    
        for h in db["habits"][user_email]:
            col1, col2 = st.columns([3, 1])
            col1.write(f"🔹 {h['ชื่อ']}")
            if h["ทำล่าสุด"] == today:
                col2.success("เสร็จแล้ว")
            else:
                if col2.button("เช็คอิน", key=f"hb_{h['id']}"):
                    h["ทำล่าสุด"] = today
                    add_exp(user_email, 5)
                    save_db(db)
                    st.rerun()

    with cB:
        st.markdown("### ⏳ บันทึกชั่วโมง Deep Work")
        st.caption("การทำงานแบบไร้สิ่งรบกวน (ปิดมือถือ โฟกัส 100%)")
        st.metric("ชั่วโมงโฟกัสสะสมของคุณ", f"{db['deep_work'][user_email]} ชั่วโมง")
        
        with st.form("dw_form", clear_on_submit=True):
            dw_hours = st.number_input("วันนี้คุณทำ Deep Work ไปกี่ชั่วโมง?", min_value=0.5, step=0.5)
            if st.form_submit_button("บันทึกเวลา"):
                db["deep_work"][user_email] += dw_hours
                add_exp(user_email, int(dw_hours * 20)) # 1 ชม. ได้ 20 EXP
                save_db(db)
                st.toast(f"สุดยอด! โฟกัสไป {dw_hours} ชม.", icon="🧠")
                st.rerun()

# ----------------- แถบที่ 4: ทบทวนตัวเอง (Reflection) -----------------
with tab4:
    st.markdown("### 🧠 Daily Reflection (ทบทวนตัวเองก่อนนอน)")
    st.caption("คนสำเร็จมักทบทวนตัวเองเสมอ เพื่อพรุ่งนี้ที่ดีกว่า")
    
    with st.form("reflect_form", clear_on_submit=True):
        r_good = st.text_area("🌟 วันนี้ทำอะไรได้ดีบ้าง / สิ่งที่เรียนรู้:")
        r_improve = st.text_area("🛠️ สิ่งที่ต้องปรับปรุง / พรุ่งนี้จะทำให้ดีขึ้นยังไง:")
        if st.form_submit_button("บันทึกลงสมุด"):
            if r_good or r_improve:
                db["reflections"][user_email].append({"วันที่": today, "ข้อดี": r_good, "ปรับปรุง": r_improve})
                add_exp(user_email, 10)
                save_db(db)
                st.toast("บันทึกการเติบโตสำเร็จ!", icon="📈")
                st.rerun()
                
    st.markdown("#### 📖 บันทึกย้อนหลังของคุณ")
    for r in reversed(db["reflections"][user_email]):
        with st.expander(f"📅 บันทึกวันที่: {r['วันที่']}"):
            st.write(f"**ทำได้ดี:** {r['ข้อดี']}")
            st.write(f"**ต้องปรับปรุง:** {r['ปรับปรุง']}")

# ----------------- แถบที่ 5: ประวัติและสถิติ -----------------
with tab5:
    st.markdown("### 📊 สถิติความก้าวหน้า")
    
    # ดึงสถิติ Level ของทุกคนในกลุ่มมาโชว์
    st.markdown("#### 🏆 Leaderboard (จัดอันดับความมีวินัย)")
    leaderboard = [{"ชื่อ": v["username"], "เลเวล": v["level"], "EXP": v["exp"], "ชั่วโมงโฟกัส": db["deep_work"].get(k, 0)} for k, v in db["users"].items()]
    df_leaderboard = pd.DataFrame(leaderboard).sort_values(by=["เลเวล", "EXP"], ascending=[False, False])
    st.dataframe(df_leaderboard, hide_index=True, use_container_width=True)
    
    st.markdown("#### 🗄️ ประวัติงานที่ทำสำเร็จแล้ว")
    priv_hist = [t for t in db["private_tasks"][user_email] if t.get("เสร็จแล้ว")]
    if priv_hist:
        st.dataframe(pd.DataFrame(priv_hist)[["รายการ", "หมวดหมู่", "กำหนดส่ง"]], hide_index=True, use_container_width=True)