import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import requests
import uuid
import hashlib
import random

# ==========================================
# 1. ตั้งค่าระบบ (THE CHRONICLES V.15.3)
# ==========================================
st.set_page_config(page_title="THE BRAIN WAR", layout="wide", page_icon="🧠")

# ⚠️ เอาลิงก์ของมึงมาใส่ตรงนี้เหมือนเดิม ห้ามลืมเครื่องหมาย " "
FIREBASE_URL = "https://mytaskpro-f7328-default-rtdb.asia-southeast1.firebasedatabase.app/" 

today_date = date.today()
today_str = str(today_date)

PUNISHMENTS = [
    "ไปดันพื้น 50 ทีเดี๋ยวนี้! ห้ามพักจนกว่าจะครบ!",
    "แพลงก์ 2 นาที! เอาความเจ็บปวดล้างสมองซะ!",
    "ลุกไปอาบน้ำเย็นจัด 5 นาทีเดี๋ยวนี้ ไป!",
    "กระโดดตบ 100 ครั้ง สลัดความขี้เกียจทิ้งไป!",
    "ห้ามจับมือถือ 1 ชั่วโมงนับจากนี้! นั่งทบทวนความกากของตัวเอง!"
]

LAZY_VOICES = [
    "🤡 เสียงขี้แพ้: 'พักเถอะมึง วันนี้เหนื่อยมาเยอะแล้ว...'",
    "🤡 เสียงขี้แพ้: 'พรุ่งนี้ค่อยทำก็ได้น่า ไม่มีใครรู้หรอก...'",
    "🤡 เสียงขี้แพ้: 'มึงทำไปก็สู้พวกคนรวยไม่ได้หรอก เลิกเถอะ...'",
    "🤡 เสียงขี้แพ้: 'เล่นเกมแป๊บเดียวเอง ไม่เสียเวลาหรอกน่า...'"
]

SAVAGE_VOICES = [
    "🦍 เสียงนักรบ: 'หุบปากไอ้สวะ! ร่างกายนี้กูเป็นคนคุม ลุยต่อ!'",
    "🦍 เสียงนักรบ: 'มึงจะฟังสวะนั่น หรือจะลุกมาสร้างตำนานวะ!'",
    "🦍 เสียงนักรบ: 'พรุ่งนี้พ่อง! มึงต้องทำเดี๋ยวนี้ ตายก็ต้องเสร็จ!'",
    "🦍 เสียงนักรบ: 'ความสบายคือยาพิษ ลุกขึ้นมาสู้ดิวะไอ้หน้าโง่!'"
]

AMBUSH_TASKS = [
    "กฎก้าวสุดท้าย! ไปแพลงก์ 1 นาทีก่อนนอน!",
    "คิดว่ารอดแล้วหรอ? วิดพื้น 20 ที!",
    "เขียนเป้าหมายพรุ่งนี้ 3 ข้อใส่กระดาษเดี๋ยวนี้!",
    "ยืนสมาธิ 5 นาที ห้ามขยับ!"
]

ANTI_SIMP_SLAPS = ["เขาไม่เอามึงหรอก ไปวิดพื้น 30 ที!", "เอาเวลาเพ้อไปหาเงินซะ!", "เลิกเป็นทาสอารมณ์โง่ๆ ได้แล้ว!"]

def get_safe_email(email):
    return email.replace(".", "-").replace("@", "-")

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_db():
    if FIREBASE_URL == "ใส่ลิงก์FIREBASEของมึงตรงนี้" or FIREBASE_URL == "":
        st.error("🚨 ไอ้เวร! มึงยังไม่ได้เอาลิงก์ Firebase มาใส่ในโค้ด! กลับไปแก้เดี๋ยวนี้!")
        st.stop()
        
    try:
        res = requests.get(f"{FIREBASE_URL}/db.json")
        if res.status_code == 200 and res.json() is not None:
            data = res.json()
            defaults = {"users": {}, "missions": {}, "dark_room": {}, "anti_simp": {}, "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}}
            for k, v in defaults.items():
                if k not in data: data[k] = v
            return data
    except:
        pass
    
    return {"users": {}, "missions": {}, "dark_room": {}, "anti_simp": {}, "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}}

def save_db(data):
    try:
        requests.put(f"{FIREBASE_URL}/db.json", json=data)
    except:
        st.error("🚨 เซฟข้อมูลลงฐานข้อมูลอมตะไม่สำเร็จ! เช็คเน็ตมึงด้วย!")

db = load_db()

# ==========================================
# 2. OVERLAY นรก (I'M A BITCH BUTTON)
# ==========================================
if "punishment_active" in st.session_state:
    st.error("🚨 มึงกดปุ่มยอมรับความกระจอก! บททดสอบนรกเริ่มขึ้นแล้ว! 🚨")
    st.title(f"🔥 คำสั่ง: {st.session_state.punishment_task}")
    st.warning("หน้าเว็บทั้งหมดถูกล็อก! มึงไม่มีสิทธิ์ทำอย่างอื่นจนกว่ามึงจะชดใช้กรรมนี้เสร็จ!")
    if st.button("🩸 กูทำเสร็จแล้ว! (ชดใช้กรรม)"):
        del st.session_state.punishment_active
        st.rerun()
    st.stop() 

# ==========================================
# 3. ระบบกำเนิด (Login / Register)
# ==========================================
if "current_user" not in st.session_state:
    st.session_state.current_user = None

with st.sidebar:
    st.title("🧠 สมรภูมิในสมอง")
    
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือก:", ["ลุย (Login)", "เกิดใหม่ (Register)"])
        email_input = st.text_input("อีเมล:")
        pass_input = st.text_input("รหัสผ่าน:", type="password")
        
        if auth_mode == "เกิดใหม่ (Register)":
            name_input = st.text_input("ชื่อนักรบ:")
            deadline_name = st.text_input("ชื่อวันชี้ชะตา (เช่น วันสอบ/วันส่งโปรเจกต์):")
            deadline_date = st.date_input("กำหนดวันชี้ชะตา:")
            if st.button("ทิ้งความเป็นคนซะ!"):
                if email_input and pass_input and name_input and deadline_name:
                    safe_email = get_safe_email(email_input)
                    if safe_email in db["users"]:
                        st.error("อีเมลนี้ถูกใช้ไปแล้ว!")
                    else:
                        db["users"][safe_email] = {
                            "password": hash_password(pass_input), "username": name_input,
                            "level": 1, "exp": 0, "streak": 0, "blood_debt": 0, "in_cage": False,
                            "ghost_exp": 0, "ambush_task": "", "failure_prob": 10,
                            "deadline_name": deadline_name, "deadline_date": str(deadline_date),
                            "hater_letter": "ไอ้กระจอก มึงทำไม่ได้หรอกกูรู้!",
                            "last_login": today_str, "cleared_yesterday": True
                        }
                        for k in ["missions", "dark_room", "anti_simp", "dopamine_fails", "excuses", "cookie_jar"]:
                            db[k][safe_email] = []
                        save_db(db)
                        st.success("🔥 ลงทะเบียนวิญญาณอมตะสำเร็จ! ล็อกอินซะ!")
                else:
                    st.warning("กรอกให้ครบทุกช่องดิโว้ย!")
                    
        elif auth_mode == "ลุย (Login)":
            if st.button("เปิดสมอง!"):
                safe_email = get_safe_email(email_input)
                if safe_email not in db["users"]:
                    st.error("❌ ไม่พบบัญชีนี้! มึงยังไม่ได้สมัคร หรือพิมพ์ผิด!")
                elif db["users"][safe_email]["password"] != hash_password(pass_input):
                    st.error("❌ รหัสผ่านผิด! ความจำเสื่อมรึไง!")
                else:
                    user_data = db["users"][safe_email]
                    if user_data["last_login"] != today_str:
                        user_data["ghost_exp"] += 25 
                        if not user_data.get("cleared_yesterday", False):
                            user_data["exp"] = 0; user_data["level"] = max(1, user_data["level"] - 1)
                            user_data["streak"] = 0; user_data["blood_debt"] += 100
                            user_data["failure_prob"] = min(100, user_data["failure_prob"] + 20)
                        user_data["last_login"] = today_str
                        user_data["cleared_yesterday"] = False
                        save_db(db)
                    st.session_state.current_user = safe_email
                    st.rerun()
    else:
        safe_email = st.session_state.current_user
        u_data = db["users"][safe_email]
        st.error(f"⚔️ นักรบ: {u_data['username']}")
        st.warning(f"🔥 สถิติไม่แพ้: {u_data['streak']} วัน")
        st.progress(u_data["exp"] / 100, text=f"Lv.{u_data['level']} | พลังงาน: {u_data['exp']}/100")
        if st.button("🚪 ถอยทัพ (ปิดเว็บ)"):
            st.session_state.current_user = None
            st.rerun()

if st.session_state.current_user is None:
    st.title("🧠 THE BRAIN WAR (สงครามสองอนาคต)")
    st.info("👈 ล็อกอินเข้ามา ฐานข้อมูลนี้เก็บวิญญาณมึงไว้เป็นอมตะแล้ว!")
    st.stop()

safe_email = st.session_state.current_user

# ===== 🛡️ FIREBASE SHIELD =====
for k in ["missions", "dark_room", "anti_simp", "dopamine_fails", "excuses", "cookie_jar"]:
    if safe_email not in db[k] or db[k][safe_email] is None:
        db[k][safe_email] = []
# ===============================

user = db["users"][safe_email]

# ==========================================
# 4. ปุ่มสับหน้า & COUNTDOWN TO REGRET
# ==========================================
colTop1, colTop2 = st.columns([1, 4])
with colTop1:
    if st.button("🚨 I'M A BITCH 🚨\n(กูเริ่มขี้เกียจ)", type="primary", use_container_width=True):
        st.session_state.punishment_active = True
        st.session_state.punishment_task = random.choice(PUNISHMENTS)
        st.rerun()
        
with colTop2:
    try:
        target_date = datetime.strptime(user["deadline_date"], "%Y-%m-%d").date()
        days_left = (target_date - today_date).days
        st.markdown(f"### ⏳ COUNTDOWN TO REGRET: {user['deadline_name']}")
        st.error(f"เหลือเวลาอีกแค่ **{days_left} วัน** เท่านั้น! เวลาที่มึงเอาแต่เพ้อ คือเวลาที่มึงกำลังส่งตัวเองลงนรก!")
    except:
        pass

if user.get("in_cage"):
    st.error("🚨 **มึงอยู่ในกรง!** จ่ายหนี้เลือดให้หมดถึงจะปลดล็อกตัวเองได้!")

# ==========================================
# 5. DUAL REALITY DASHBOARD
# ==========================================
st.divider()
colLeft, colRight = st.columns(2)

with colLeft:
    st.markdown("## 🗑️ THE BITCH ZONE")
    st.caption("ที่อยู่ของไอ้ร่างขยะที่มึงต้องฆ่า!")
    st.warning(random.choice(LAZY_VOICES))
    
    st.markdown("### 🤡 The Excuses Log")
    st.metric("📉 โอกาสล้มเหลวในอนาคต", f"{user['failure_prob']}%")
    if user['failure_prob'] > 50:
        st.error("สภาพนี้มึงเตรียมตัวเป็นไอ้ขี้แพ้ตอนอายุ 20 ได้เลย!")
        
    with st.form("excuse_form", clear_on_submit=True):
        exc_text = st.text_input("ข้ออ้างขยะๆ วันนี้คืออะไร?:")
        if st.form_submit_button("บันทึกข้ออ้าง"):
            if exc_text:
                db["excuses"][safe_email].append({"วันที่": today_str, "ข้ออ้าง": exc_text})
                user["failure_prob"] = min(100, user["failure_prob"] + 10)
                save_db(db); st.rerun()
                
    st.markdown("### 🕸️ Dopamine Trap & Anti-Simp")
    with st.form("simp_form", clear_on_submit=True):
        simp_text = st.text_input("เพ้อหาใคร? สารภาพมา!:")
        if st.form_submit_button("กูเพ้อเจ้อ"):
            db["anti_simp"][safe_email].append(simp_text)
            user["blood_debt"] += 30; user["failure_prob"] = min(100, user["failure_prob"] + 5)
            save_db(db); st.toast(random.choice(ANTI_SIMP_SLAPS), icon="🖐️"); st.rerun()
            
    if st.button("💀 แท่นประหาร: กูแพ้ให้เกม/โซเชียล/หนังโป๊"):
        db["dopamine_fails"][safe_email].append(today_str)
        user["exp"] = 0; user["blood_debt"] += 50; user["in_cage"] = True
        user["failure_prob"] = min(100, user["failure_prob"] + 20)
        save_db(db); st.rerun()

with colRight:
    st.markdown("## ⚔️ THE SAVAGE ZONE")
    st.caption("ที่อยู่ของมหาบุรุษมึงในวัย 20 ปี!")
    st.success(random.choice(SAVAGE_VOICES))
    
    st.markdown("### 🪵 The Daily Siege (ตารางรบ)")
    with st.form("mission_form", clear_on_submit=True):
        m_name = st.text_input("ท่อนซุงที่มึงต้องแบกวันนี้:")
        if st.form_submit_button("เพิ่มภารกิจ"):
            if m_name:
                db["missions"][safe_email].append({"id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": m_name, "เสร็จแล้ว": False})
                save_db(db); st.rerun()
                
    active_missions = [m for m in db["missions"][safe_email] if not m.get("เสร็จแล้ว")]
    if active_missions:
        for m in active_missions:
            c1, c2 = st.columns([3, 1])
            c1.write(f"❌ **{m['ภารกิจ']}**")
            if c2.button("✅ Tick!", key=f"m_{m['id']}"):
                m["เสร็จแล้ว"] = True
                user["exp"] += 20
                user["failure_prob"] = max(0, user["failure_prob"] - 5)
                if user["exp"] >= 100:
                    user["level"] += 1; user["exp"] -= 100
                save_db(db); st.rerun()
    else:
        st.success("✅ ท่อนซุงวันนี้แบกหมดแล้ว!")

    st.markdown("### 🍪 คลังแสงความสำเร็จ (Cookie Jar)")
    with st.form("cookie_form", clear_on_submit=True):
        c_victory = st.text_area("วันนี้มึงชนะความอ่อนแอเรื่องอะไร?:")
        if st.form_submit_button("ยัดใส่คลังแสง"):
            if c_victory:
                db["cookie_jar"][safe_email].append({"วันที่": today_str, "ชัยชนะ": c_victory})
                save_db(db); st.rerun()
    if db["cookie_jar"][safe_email]:
        st.info(f"🏆 ชัยชนะล่าสุด: {db['cookie_jar'][safe_email][-1]['ชัยชนะ']}")

# ==========================================
# 6. หนี้เลือด & วิญญาณร่างทอง
# ==========================================
st.divider()
c_bot1, c_bot2 = st.columns(2)
with c_bot1:
    st.markdown("### 👻 ร่างทอง (Ghost)")
    my_exp = ((user["level"] - 1) * 100) + user["exp"]
    st.metric("พลังร่างทอง (มันไม่เคยหยุดเดิน)", f"{user['ghost_exp']} EXP")
    st.metric("พลังของมึง", f"{my_exp} EXP", delta=f"{my_exp - user['ghost_exp']} ตามหลังร่างทอง" if my_exp < user['ghost_exp'] else "นำอยู่!")

with c_bot2:
    st.markdown("### 🩸 หนี้เลือด (Blood Debt)")
    st.metric("หนี้วิดพื้นที่ต้องจ่าย", f"{user.get('blood_debt', 0)} ที")
    if user.get("blood_debt", 0) > 0:
        if st.button("กูวิดพื้นใช้หนี้หมดแล้ว! (ปลดกรง)"):
            user["blood_debt"] = 0; user["in_cage"] = False
            save_db(db); st.rerun()

# ==========================================
# 7. THE JUDGMENT FEED 
# ==========================================
st.divider()
st.markdown("## ⚖️ THE JUDGMENT FEED (พิพากษาก่อนนอน)")

if user.get("ambush_task", "") != "":
    st.error(f"🚨 **โดนซุ่มโจมตี! (กฎก้าวสุดท้าย)** 🚨\n\nคำสั่ง: **{user['ambush_task']}**")
    if st.button("🔥 กูทำเสร็จแล้ว! (ข้ามศพกูไปก่อนเถอะ)"):
        user["ambush_task"] = ""
        user["exp"] += 20; save_db(db); st.rerun()
        
elif user.get("cleared_yesterday"):
    st.success("🔥 พิพากษาเสร็จสิ้น! มึงรอดไปได้อีกหนึ่งวัน!")
else:
    if active_missions:
        st.error("❌ มึงกำลังหักหลังตัวเอง! งานใน The Daily Siege ยังไม่เสร็จ!")
    elif user.get("in_cage") or user.get("blood_debt", 0) > 0:
        st.error("❌ มึงติดหนี้เลือด/ติดกรงอยู่! ไปรับกรรมซะก่อน!")
    else:
        st.warning("ตอบคำถามกูก่อนปิดเว็บ: วันนี้มึงใส่เต็ม 100% หรือมึงใช้พลังแค่ 40%?")
        j_col1, j_col2 = st.columns(2)
        
        with j_col1:
            if st.button("📉 สู้ไม่เต็มที่ (แค่ 40%)"):
                st.error("👁️ สภาพมึงตอนอายุ 20 คือไอ้ขี้แพ้ตาโบ๋ นั่งมองคนอื่นประสบความสำเร็จ! มึงโดนริบ 30 EXP!")
                user["exp"] -= 30
                user["cleared_yesterday"] = True
                user["failure_prob"] = min(100, user["failure_prob"] + 10)
                save_db(db)
                
        with j_col2:
            if st.button("🔥 กูใช้พลังทั้งหมด 100%!"):
                if random.random() < 0.2: 
                    user["ambush_task"] = random.choice(AMBUSH_TASKS)
                    save_db(db); st.rerun()
                else:
                    user["cleared_yesterday"] = True
                    user["streak"] += 1; user["exp"] += 25
                    save_db(db); st.balloons(); st.rerun()

# ==========================================
# 8. 📜 พงศาวดารความทรงจำ (HISTORY LOG)
# ==========================================
st.divider()
st.markdown("## 📜 พงศาวดารความทรงจำ (HISTORY LOG)")
st.caption("อดีตคือกระจกสะท้อนสันดาน! มาดูกันว่าที่ผ่านมามึงเป็นนักรบหรือไอ้กระจอก!")

tab1, tab2, tab3 = st.tabs(["🍪 คลังแสง (ความสำเร็จ)", "🤡 บัญชีหนังหมา (ข้ออ้าง)", "🪵 ภารกิจทั้งหมด"])

with tab1:
    if db["cookie_jar"][safe_email]:
        for item in reversed(db["cookie_jar"][safe_email]):
            st.success(f"🏆 **[{item.get('วันที่', 'ไม่ระบุ')}]** : {item.get('ชัยชนะ', '')}")
    else:
        st.write("ยังไม่มีความสำเร็จอะไรเลย ไปทำซะ!")

with tab2:
    if db["excuses"][safe_email]:
        for item in reversed(db["excuses"][safe_email]):
            st.error(f"🤡 **[{item.get('วันที่', 'ไม่ระบุ')}]** : {item.get('ข้ออ้าง', '')}")
    else:
        st.write("ดีมาก! ยังไม่มีข้ออ้างขยะๆ ให้รกหูรกตา!")

with tab3:
    if db["missions"][safe_email]:
        for item in reversed(db["missions"][safe_email]):
            status = "✅ เสร็จแล้ว" if item.get("เสร็จแล้ว") else "❌ ยังดองอยู่"
            # ใช้สีแยกให้เห็นชัดๆ ว่าทำเสร็จหรือดองงาน
            if item.get("เสร็จแล้ว"):
                st.info(f"🔹 **[{item.get('วันที่', 'ไม่ระบุ')}]** {item.get('ภารกิจ', '')} 👉 {status}")
            else:
                st.warning(f"🔹 **[{item.get('วันที่', 'ไม่ระบุ')}]** {item.get('ภารกิจ', '')} 👉 {status}")
    else:
        st.write("ยังไม่มีประวัติการแบกซุง!")
