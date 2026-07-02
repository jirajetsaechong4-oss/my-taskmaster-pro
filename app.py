import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import requests
import uuid
import hashlib
import random

# ==========================================
# 1. ตั้งค่าระบบ (THE IMMORTAL SOUL V.37 - THE TIMELESS WARLORD)
# ==========================================
st.set_page_config(page_title="THE BRAIN WAR", layout="wide", page_icon="🧠")

# ⚠️ ลิงก์ Firebase ของมึง
FIREBASE_URL = "https://mytaskpro-f7328-default-rtdb.asia-southeast1.firebasedatabase.app/" 

# ⏱️ ฟังก์ชันจับเวลา Absolute Real-time (แก้ปัญหาเปิดแอปค้างข้ามคืนแล้วเวลาไม่เดิน)
def get_current_thai_time():
    tz_thai = timezone(timedelta(hours=7))
    return datetime.now(tz_thai)

now_thai = get_current_thai_time()
today_date = now_thai.date()
today_str = str(today_date)

# 🗺️ ซ่อมบัค: ประกาศ Dictionary ค่ายกลกระบวนทัพเป็น Global เพื่อให้ใช้ร่วมกันได้ทุกแท็บ
ROLE_MAP = {
    "Vanguard": "⚡ [ทัพหน้า - First Strike]", 
    "Main": "⚔️ [ทัพหลวง]", 
    "Support": "🏹 [ทัพหนุน]"
}

PUNISHMENTS = [
    "ไปดันพื้น 50 ทีเดี๋ยวนี้! ห้ามพักจนกว่าจะครบ!",
    "แพลงก์ 2 นาที! เอาความเจ็บปวดล้างสมองซะ!",
    "ลุกไปอาบน้ำเย็นจัด 5 นาทีเดี๋ยวนี้ ไป!",
    "กระโดดตบ 100 ครั้ง สลัดความขี้เกียจทิ้งไป!",
    "ห้ามจับมือถือ 1 ชั่วโมงนับจากนี้! นั่งทบทวนความกากของตัวเอง!",
    "สควอช (ลุกนั่ง) 60 ที เอาให้ขาเบิร์น!",
    "เดินไปตะโกนใส่กำแพงว่า 'กูจะไม่ยอมแพ้!' 10 รอบ!"
]

LAZY_VOICES = [
    "🤡 เสียงขี้แพ้: 'พักเถอะมึง วันนี้เหนื่อยมาเยอะแล้ว...'",
    "🤡 เสียงขี้แพ้: 'พรุ่งนี้ค่อยทำก็ได้น่า ไม่มีใครรู้หรอก...'",
    "🤡 เสียงขี้แพ้: 'เล่นเกมแป๊บเดียวเอง ไม่เสียเวลาหรอกน่า...'"
]

SAVAGE_VOICES = [
    "🦍 เสียงนักรบ: 'หุบปากไอ้สวะ! ร่างกายนี้กูเป็นคนคุม ลุยต่อ!'",
    "🦍 เสียงนักรบ: 'มึงจะฟังสวะนั่น หรือจะลุกมาสร้างตำนานวะ!'",
    "🦍 เสียงนักรบ: 'ความสบายคือยาพิษ ลุกขึ้นมาสู้ดิวะไอ้หน้าโง่!'"
]

AMBUSH_TASKS = [
    "กฎก้าวสุดท้าย! ไปแพลงก์ 1 นาทีก่อนนอน!",
    "คิดว่ารอดแล้วหรอ? วิดพื้น 20 ที!",
    "เขียนเป้าหมายพรุ่งนี้ 3 ข้อใส่กระดาษเดี๋ยวนี้!"
]

def get_safe_email(email): 
    return email.replace(".", "-").replace("@", "-")

def get_title(level):
    if level < 3: 
        return "🤡 ไอ้ลูกหมาขี้ขลาด"
    elif level < 7: 
        return "⚔️ นักรบฝึกหัดแบกซุง"
    elif level < 12: 
        return "🦍 แม่ทัพคุมโดพามีน"
    else: 
        return "👑 มหาจักรพรรดิผู้คุมชะตา"

def get_priority_score(task_type):
    if "🔴 ด่วนสุด" in task_type or "🔥 งานฉุกเฉิน" in task_type: 
        return 1
    if "🟡 ปานกลาง" in task_type: 
        return 2
    if "🟢 ชิลๆ" in task_type: 
        return 3
    return 4

# 🧠 ฟังก์ชันคำนวณน้ำหนักการจัดเรียงรบ (Tactical Sorting Scores)
def get_role_score(role):
    if role == "Vanguard": return 1
    if role == "Main": return 2
    return 3

def get_deadline_score(dl_str):
    if not dl_str or dl_str == "": return 999999
    try:
        dl_date = datetime.strptime(dl_str, "%Y-%m-%d").date()
        return (dl_date - today_date).days
    except:
        return 999999

# 🔥 คำนวณ EXP และ การลดโอกาสล้มเหลวแบบ Dynamic + พ่วงระบบคูณโบนัส Streak
def calculate_task_rewards(task, current_streak):
    score = get_priority_score(task.get("ประเภท", ""))
    
    # 1. คำนวณ Base EXP
    if score == 1:
        base_exp = 40
    elif score == 2:
        base_exp = 20
    else:
        base_exp = 10
    
    # 2. คำนวณ Bonus EXP
    bonus_exp = 0
    if task.get("is_boss"): 
        bonus_exp += 100
    if task.get("bounty"): 
        bonus_exp += 50
    if task.get("subtasks"):
        bonus_exp += len(task["subtasks"]) * 10  
        
    raw_total_exp = base_exp + bonus_exp
    
    # 🔥 The Savage Multiplier (คูณโบนัสความต่อเนื่อง)
    multiplier = 1.0
    if current_streak >= 30:
        multiplier = 1.5
    elif current_streak >= 7:
        multiplier = 1.2
    elif current_streak >= 3:
        multiplier = 1.1
        
    final_exp = int(raw_total_exp * multiplier)
    
    # 3. คำนวณอัตราลดโอกาสล้มเหลว
    if score == 1:
        fail_reduce = 10
    elif score == 2:
        fail_reduce = 5
    else:
        fail_reduce = 2
    
    if task.get("is_boss"): 
        fail_reduce += 15
    if task.get("bounty"): 
        fail_reduce += 5
    
    return final_exp, fail_reduce

def load_db():
    if FIREBASE_URL == "" or FIREBASE_URL is None:
        st.error("🚨 ไอ้เวร! ลิงก์ Firebase หายไปไหน กลับไปแก้เดี๋ยวนี้!")
        st.stop()
    try:
        res = requests.get(f"{FIREBASE_URL}/db.json")
        if res.status_code == 200 and res.json() is not None:
            data = res.json()
            defaults = {
                "users": {}, 
                "missions": {}, 
                "study_missions": {}, 
                "backlog": {}, 
                "dark_room": {}, 
                "anti_simp": {}, 
                "dopamine_fails": {}, 
                "excuses": {}, 
                "cookie_jar": {}, 
                "deadlines": {}, 
                "haters": {}, 
                "finance": {}, 
                "iron_habits": {},
                "exams": {}, 
                "beat_yesterday": {}, 
                "limit_breaks": {}
            }
            for k, v in defaults.items():
                if k not in data: 
                    data[k] = v
            return data
    except: 
        pass
    return {
        "users": {}, 
        "missions": {}, 
        "study_missions": {},
        "backlog": {}, 
        "dark_room": {}, 
        "anti_simp": {}, 
        "dopamine_fails": {}, 
        "excuses": {}, 
        "cookie_jar": {}, 
        "deadlines": {}, 
        "haters": {}, 
        "finance": {}, 
        "iron_habits": {},
        "exams": {}, 
        "beat_yesterday": {}, 
        "limit_breaks": {}
    }

def save_db(data):
    try: 
        requests.put(f"{FIREBASE_URL}/db.json", json=data)
    except: 
        st.error("🚨 เซฟข้อมูลลงฐานข้อมูลอมตะไม่สำเร็จ!")

db = load_db()

# ==========================================
# 2. OVERLAY นรก (PUNISHMENT ACTIVE)
# ==========================================
if "punishment_active" in st.session_state:
    st.error("🚨 วงล้อแห่งกรรมทำงาน! มึงต้องชดใช้ความกระจอกเดี๋ยวนี้! 🚨")
    st.title(f"🔥 คำสั่งทรมานร่างขยะ: {st.session_state.punishment_task}")
    if st.button("🩸 กูทำเสร็จแล้ว! (ชดใช้กรรมเรียบร้อย)"):
        del st.session_state.punishment_active
        st.rerun()
    st.stop() 

# ==========================================
# 3. ระบบล็อกอิน
# ==========================================
if "current_user" not in st.session_state: 
    st.session_state.current_user = None

with st.sidebar:
    st.title("🧠 สมรภูมิในสมอง")
    st.caption(f"🗓️ เวลาสมรภูมิ: {today_str}") # แสดงเวลาให้เห็นชัดเจน
    
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือกโหมด:", ["⚡ ล็อกอินด่วน", "➕ สร้างนักรบใหม่"])
        st.divider()
        
        if auth_mode == "➕ สร้างนักรบใหม่":
            st.info("ใช้สร้างไอดีครั้งแรกครั้งเดียว")
            name_input = st.text_input("ชื่อนักรบ:")
            email_input = st.text_input("อีเมล (ใช้เป็น ID):")
            if st.button("ทิ้งความเป็นคนซะ!"):
                if email_input and name_input:
                    safe_email = get_safe_email(email_input)
                    if safe_email in db.get("users", {}): 
                        st.error("อีเมล/ID นี้มีในระบบแล้ว!")
                    else:
                        db["users"][safe_email] = {
                            "username": name_input, 
                            "level": 1, 
                            "exp": 0, 
                            "streak": 0, 
                            "blood_debt": 0, 
                            "in_cage": False,
                            "ghost_exp": 0, 
                            "ambush_task": "", 
                            "failure_prob": 10,
                            "last_login": today_str, 
                            "cleared_yesterday": True,
                            "order_locked": False,
                            "target_name": "ทำ 10 ล้านวิว YouTube Shorts", 
                            "target_date": str(today_date + timedelta(days=90))
                        }
                        save_db(db)
                        st.success("🔥 ลงทะเบียนสำเร็จ! ไปที่ 'ล็อกอินด่วน' ได้เลย!")
                else: 
                    st.warning("กรอกชื่อกับอีเมลให้ครบ!")
                
        elif auth_mode == "⚡ ล็อกอินด่วน":
            if not db.get("users"): 
                st.warning("ยังไม่มีนักรบในระบบ ไปสร้างนักรบใหม่ก่อน!")
            else:
                user_options = {f"{data['username']}": email for email, data in db["users"].items()}
                selected_display = st.selectbox("เลือกบัญชีของคุณ:", list(user_options.keys()))
                
                if st.button("🔥 เปิดสมอง! (เข้าสู่ระบบ)"):
                    safe_email = user_options[selected_display]
                    user_data = db["users"][safe_email]
                    
                    if "target_name" not in user_data: 
                        user_data["target_name"] = "ทำ 10 ล้านวิว YouTube Shorts"
                        user_data["target_date"] = str(today_date + timedelta(days=90))

                    # ⏱️ ระบบข้ามวัน (Midnight Reset Mechanism)
                    if user_data["last_login"] != today_str:
                        user_data["ghost_exp"] += 25 
                        user_data["order_locked"] = False
                        unpaid_bounties = [m for m in db.get("missions", {}).get(safe_email, []) if m.get("bounty") and not m.get("เสร็จแล้ว")]
                        if unpaid_bounties or not user_data.get("cleared_yesterday", False):
                            penalty = 100 + (len(unpaid_bounties) * 100)
                            user_data["exp"] = 0
                            user_data["level"] = max(1, user_data["level"] - 1)
                            user_data["streak"] = 0
                            user_data["blood_debt"] += penalty
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
        st.info(f"🛡️ ฉายา: {get_title(u_data['level'])}")
        
        scars = len(db.get("dopamine_fails", {}).get(safe_email, []))
        st.markdown(f"🩻 **รอยแผลเป็นความพ่ายแพ้: {scars} รอย**")
        st.warning(f"🔥 สถิติไม่แพ้ (Streak): {u_data['streak']} วัน")
        
        current_streak = u_data.get("streak", 0)
        if current_streak >= 30:
            st.success("👑 BUFF: โบนัส EXP x 1.5 (ร่างทองคำ)")
        elif current_streak >= 7:
            st.success("🔥 BUFF: โบนัส EXP x 1.2 (นักรบคุ้มคลั่ง)")
        elif current_streak >= 3:
            st.success("⚡ BUFF: โบนัส EXP x 1.1 (เริ่มเข้าฝัก)")
        else:
            st.caption("💀 BUFF: ไม่มีโบนัส (กระจอก)")
        
        needs_save = False
        while u_data["exp"] >= 100:
            u_data["level"] += 1
            u_data["exp"] -= 100
            needs_save = True
            st.toast(f"🔥 LEVEL UP! มึงแกร่งขึ้นเป็น Lv.{u_data['level']}", icon="🦍")
        while u_data["exp"] < 0:
            if u_data["level"] > 1:
                u_data["level"] -= 1
                u_data["exp"] += 100
            else:
                u_data["exp"] = 0
            needs_save = True
            
        if needs_save:
            save_db(db)
            
        prog_val = max(0.0, min(1.0, u_data["exp"] / 100))
        st.progress(prog_val, text=f"Lv.{u_data['level']} | EXP: {u_data['exp']}/100")
        
        st.divider()
        monk_mode = st.toggle("🧘‍♂️ โหมดจำศีล (Monk Mode)")
        if st.button("🚪 ถอยทัพ (ออกจากระบบ)"):
            st.session_state.current_user = None
            st.rerun()

if st.session_state.current_user is None:
    st.title("🧠 THE BRAIN WAR")
    st.info("👈 เลือกชื่อตัวเองแล้วกดปุ่ม 'เปิดสมอง!' เพื่อเข้าใช้งาน!")
    st.stop()

safe_email = st.session_state.current_user

# คอนฟิกโครงสร้าง Database
for k in ["missions", "study_missions", "backlog", "dark_room", "anti_simp", "dopamine_fails", "excuses", "cookie_jar", "deadlines", "haters", "finance", "iron_habits", "exams", "beat_yesterday", "limit_breaks"]:
    if safe_email not in db[k] or db[k][safe_email] is None: 
        if k == "finance": 
            db[k][safe_email] = {"goal_name": "ยังไม่ได้ตั้ง", "goal_amount": 0, "current": 0}
        elif k in ["exams", "beat_yesterday"]: 
            db[k][safe_email] = {}
        else: 
            db[k][safe_email] = []

user = db["users"][safe_email]
finance = db["finance"][safe_email]
current_streak = user.get("streak", 0)

# ===== 🚨 CHECK OVERDUE BACKLOG =====
overdue_count = 0
for task in db["backlog"][safe_email]:
    try:
        if task.get("deadline") and task["deadline"] != "":
            dl_date = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
            if dl_date < today_date and task.get("last_penalized") != today_str:
                overdue_count += 1
                task["last_penalized"] = today_str
    except: 
        pass

if overdue_count > 0:
    user["failure_prob"] = min(100, user["failure_prob"] + (10 * overdue_count))
    user["blood_debt"] += (50 * overdue_count)
    user["in_cage"] = True
    save_db(db)
    st.error(f"🚨 ไอ้หน้าโง่! มึงมีงานดอง (หรือหลุดเป้าหมาย) เกินกำหนด {overdue_count} งาน! แท่นพิพากษายัดหนี้เลือดมึงแล้ว รีบไปเคลียร์ซะ!")

# ==========================================
# 🎯 ส่วนหัว: ปลุกพลัง & ระบบนับถอยหลังอนาคต (FUTURE COUNTDOWN)
# ==========================================
try: 
    t_date = datetime.strptime(user["target_date"], "%Y-%m-%d").date()
except: 
    t_date = today_date + timedelta(days=90)
days_left = (t_date - today_date).days

colTop1, colTop2, colTop3 = st.columns([1, 1, 3])
with colTop1:
    if st.button("🎰 วงล้อชดใช้กรรม\n(กูเริ่มขี้เกียจ)", type="primary", use_container_width=True):
        st.session_state.punishment_active = True
        st.session_state.punishment_task = random.choice(PUNISHMENTS)
        st.rerun()
with colTop2:
    if st.button("⚡ คาถาระเบิดพลัง\n(เรียกสติเดี่ยวนี้)", use_container_width=True):
        st.toast(f"🔊 ตื่นดิวะ! {random.choice(PUNISHMENTS)}", icon="🦍")
with colTop3:
    st.error(f"⏳ **นับถอยหลังชี้ชะตา:** {user.get('target_name', 'เป้าหมายสูงสุด')} ในอีก **{days_left}** วัน!")
    with st.popover("⚙️ ตั้งค่านับถอยหลัง"):
        new_t_name = st.text_input("เป้าหมายสูงสุด (เช่น 10ล้านวิว):", user.get("target_name", ""))
        new_t_date = st.date_input("วันกำหนดชี้ชะตา (Deadline ใหญ่):", t_date)
        if st.button("บันทึกเป้าหมายชี้ชะตา"):
            user["target_name"] = new_t_name
            user["target_date"] = str(new_t_date)
            save_db(db)
            st.rerun()

if user.get("in_cage"): 
    st.error("🚨 **มึงอยู่ในกรง!** วิดพื้นจ่ายหนี้เลือดซะ!")

# ==========================================
# 5. DUAL REALITY DASHBOARD
# ==========================================
st.divider()
if monk_mode:
    st.markdown("## 🧘‍♂️ MONK MODE ACTIVE: สมาธิขั้นสุด!")
    colLeft, colRight = st.columns([0.01, 1]) 
else: 
    colLeft, colRight = st.columns(2)

with colLeft:
    if not monk_mode:
        st.markdown("## 🗑️ THE BITCH ZONE (ฝั่งขยะ)")
        st.warning(random.choice(LAZY_VOICES))
        
        # 📊 อัปเกรดประสิทธิภาพ: หลอดพลังใจ (Mental Health Bar)
        fail_prob = user.get('failure_prob', 10)
        st.markdown(f"**📉 โอกาสพ่ายแพ้ต่อสิ่งเร้า: {fail_prob}%**")
        fail_color = "red" if fail_prob > 70 else "orange" if fail_prob > 40 else "green"
        st.progress(fail_prob / 100)
        st.caption("🚨 ถ้าระเบิดถึง 100% มึงเตรียมตัวรับกรรมอย่างสาสมได้เลย!")
            
        with st.form("excuse_form", clear_on_submit=True):
            exc_text = st.text_input("ข้ออ้างขยะๆ วันนี้คืออะไร?:")
            if st.form_submit_button("บันทึกข้ออ้าง"):
                if exc_text:
                    db["excuses"][safe_email].append({"วันที่": today_str, "ข้ออ้าง": exc_text})
                    user["failure_prob"] = min(100, user["failure_prob"] + 10)
                    save_db(db)
                    st.rerun()
                    
        if st.button("💀 แท่นประหาร: กูแพ้ให้สิ่งเร้าขยะ"):
            db["dopamine_fails"][safe_email].append(today_str)
            user["exp"] = 0
            user["blood_debt"] += 50
            user["in_cage"] = True
            user["failure_prob"] = min(100, user["failure_prob"] + 20)
            save_db(db)
            st.rerun()

        st.markdown("### 🩸 บัญชีแค้น (THE HATER'S WALL)")
        with st.form("hater_form", clear_on_submit=True):
            h_text = st.text_input("คำดูถูกที่มึงเจอ:")
            if st.form_submit_button("ฝังความแค้น"):
                if h_text: 
                    db["haters"][safe_email].append(h_text)
                    save_db(db)
                    st.rerun()
        if db["haters"][safe_email]: 
            st.error(f"🤬 คำดูถูก: \"{random.choice(db['haters'][safe_email])}\"")

with colRight:
    st.markdown("## ⚔️ THE SAVAGE ZONE (นักรบฝั่งขวา)")
    st.success(random.choice(SAVAGE_VOICES))
    
    tab_missions, tab_study, tab_habits, tab_backlog, tab_cookie, tab_academic = st.tabs([
        "🔥 ภารกิจวันนี้", 
        "📖 ภารกิจการเรียน", 
        "⛓️ วินัยเหล็ก", 
        "📝 สมุดจดงาน", 
        "🍪 โหลคุกกี้", 
        "📚 ลานประลองปัญญา"
    ])
    
    # ----------------------------------------------------
    # TAB 1: ภารกิจวันนี้ (Daily Missions)
    # ----------------------------------------------------
    with tab_missions:
        st.markdown("### 🪵 The Daily Siege (ตารางรบวันนี้)")
        
        raw_active_missions = [m for m in db["missions"][safe_email] if not m.get("เสร็จแล้ว")]
        active_single_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False) and not m.get("subtasks")]
        
        if len(active_single_missions) >= 3:
            st.error("🚨 **กฎเหล็กจอมทัพ:** โควตางานเดี่ยววันนี้เต็ม 3 Slot แล้ว! รีบเคลียร์ของเก่า หรือถ้าจะเพิ่มใหม่ต้องเป็นโครงงานใหญ่สับซุงเท่านั้น!")
        
        with st.expander("➕ เพิ่มงานด่วนวันนี้ (ไม่ผ่านสมุด)"):
            with st.form("mission_form", clear_on_submit=True):
                m_name = st.text_input("ชื่อภารกิจ:")
                m_is_boss = st.checkbox("💀 ตั้งเป็น THE BOSS FIGHT (งานกลืนกบประจำวัน! หนี=หนี้เลือด x3)")
                m_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด (คอขาดบาดตาย)", "🔥 งานฉุกเฉิน / Special Event", "🟡 ปานกลาง (ต้องเสร็จ)", "🟢 ชิลๆ (ทำตอนว่าง)"])
                m_bounty = st.checkbox("⚔️ ตั้งค่าหัว! (เดิมพันศักดิ์ศรี: พลาดโดนหนี้ 100 ที)")
                m_subtasks_text = st.text_area("🔪 สับท่อนซุง (ใส่ชื่อย่อยทีละบรรทัด, ไม่บังคับ):")
                
                m_dl_type = st.radio("⏰ ระบบเวลา (Dual Clock):", ["ไม่กำหนด (ชิลๆ)", "🗓️ Deadline ทางการ", "🎯 วันเป้าหมาย (กำหนดเอง)"], horizontal=True)
                m_deadline = st.date_input("เลือกวันที่:")
                
                if st.form_submit_button("เพิ่มภารกิจ"):
                    if m_name:
                        subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in m_subtasks_text.split('\n') if s.strip()]
                        
                        if not subtasks and len(active_single_missions) >= 3:
                            st.error("🤡 ตะบัดสัตย์! โควตางานเดี่ยวเต็มแล้ว ระบบบล็อกไม่ให้เพิ่ม บังคับให้สับข้อย่อยท่อนซุงซะ!")
                        else:
                            final_dl = str(m_deadline) if m_dl_type != "ไม่กำหนด (ชิลๆ)" else ""
                            
                            db["missions"][safe_email].append({
                                "id": str(uuid.uuid4()), 
                                "วันที่": today_str, 
                                "ภารกิจ": m_name, 
                                "ประเภท": m_type, 
                                "bounty": m_bounty, 
                                "is_boss": m_is_boss,
                                "custom_order": 99, 
                                "battle_role": "Main", 
                                "is_queued": False, 
                                "skip_today_date": "",
                                "subtasks": subtasks, 
                                "เสร็จแล้ว": False, 
                                "รอตรวจ": False,
                                "deadline": final_dl,
                                "deadline_type": m_dl_type
                            })
                            save_db(db)
                            st.rerun()
                    
        todo_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False)]
        pending_missions = [m for m in raw_active_missions if m.get("รอตรวจ", False)]
        
        # 🧠 V.37 อัปเกรด: AI จัดเรียงรบอัจฉริยะ (Role -> Deadline Proximity -> Priority)
        todo_missions.sort(key=lambda x: (
            get_role_score(x.get("battle_role", "Main")), 
            0 if x.get("is_boss") else 1, 
            get_deadline_score(x.get("deadline", "")),
            get_priority_score(x.get("ประเภท", ""))
        ))
        
        needs_queueing = [m for m in todo_missions if not m.get("is_queued", False)]
        
        if needs_queueing:
            with st.expander("⚔️🛡️ จัดค่ายกลกระบวนทัพรบประจำวัน (Tactical Battle Formation)", expanded=True):
                with st.form("lock_order_form"):
                    st.write("จอมทัพ! เลือกตำแหน่งเชิงยุทธศาสตร์ให้ทัพหนุนใหม่ (ทัพหน้าจะได้โบนัสจู่โจมชิงลงมือ First Strike +20 EXP!)")
                    updated_orders = {}
                    updated_roles = {}
                    for m in needs_queueing:
                        is_boss_str = "💀 [BOSS] " if m.get("is_boss") else ""
                        role_choice = st.selectbox(f"วางตำแหน่งทัพ: {is_boss_str}{m['ภารกิจ']}", 
                                                   ["⚡ ทัพหน้า (Vanguard - โบนัส First Strike +20 EXP)", 
                                                    "⚔️ ทัพหลวง (Main Force - เสาหลักของวัน)", 
                                                    "🏹 ทัพหนุน (Support - ทำเมื่อทัพหลักเสร็จ)"], 
                                                   key=f"setup_role_{m['id']}")
                        
                        if "ทัพหน้า" in role_choice:
                            updated_orders[m["id"]] = 1
                            updated_roles[m["id"]] = "Vanguard"
                        elif "ทัพหลวง" in role_choice:
                            updated_orders[m["id"]] = 2
                            updated_roles[m["id"]] = "Main"
                        else:
                            updated_orders[m["id"]] = 3
                            updated_roles[m["id"]] = "Support"
                    
                    if st.form_submit_button("🔒 ล็อกค่ายกลกระบวนทัพ! (ห้ามตระบัดสัตย์)"):
                        for m in db["missions"][safe_email]:
                            if m["id"] in updated_orders:
                                m["custom_order"] = updated_orders[m["id"]]
                                m["battle_role"] = updated_roles[m["id"]]
                                m["is_queued"] = True
                        save_db(db)
                        st.success("⚔️ จัดทัพเสร็จสิ้น! บัญญัติชะตากรรมเรียบร้อย!")
                        st.rerun()

        if todo_missions:
            for m in todo_missions:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6]) 
                    
                    task_mode_badge = "🔪 **[งานใหญ่]**" if m.get("subtasks") else "⚡ **[ม้วนเดียวจบ]**"
                    is_bounty = " ⚔️[เดิมพัน]" if m.get("bounty") else ""
                    is_boss = " 💀 **[BOSS]**" if m.get("is_boss") else ""
                    
                    # เรียกใช้ ROLE_MAP จาก Global scope อย่างถูกต้อง ไร้บัค
                    order_badge = f" | {ROLE_MAP.get(m.get('battle_role', 'Main'), '⚔️ [ทัพหลวง]')}"
                    
                    is_overdue = False
                    deadline_badge = ""
                    dl_str = m.get("deadline", "")
                    dl_type = m.get("deadline_type", "🗓️ Deadline ทางการ")
                    dl_icon = "🎯" if "เป้าหมาย" in dl_type else "⏳"
                    
                    if dl_str and dl_str != "":
                        try:
                            dl_date = datetime.strptime(dl_str, "%Y-%m-%d").date()
                            days_left_task = (dl_date - today_date).days
                            if days_left_task > 0: 
                                deadline_badge = f" {dl_icon} (เหลือ {days_left_task} วัน)"
                            elif days_left_task == 0: 
                                deadline_badge = f" 🚨 **(ต้องเสร็จวันนี้!)**"
                            else: 
                                deadline_badge = f" 💀 **(เลยกำหนดมาแล้ว {-days_left_task} วัน)**"
                                is_overdue = True 
                        except: 
                            pass

                    is_frozen = m.get("skip_today_date") == today_str
                    # ตรวจจับว่าเกราะน้ำแข็งละลายหรือยัง (เลยเที่ยงคืนแล้ว)
                    was_frozen_yesterday = m.get("skip_today_date") != "" and not is_frozen
                    if was_frozen_yesterday:
                        m["skip_today_date"] = "" # เคลียร์ขยะเก่า
                        save_db(db)
                        
                    if is_frozen:
                        if is_overdue: 
                            frozen_badge = " ❄️🚨 [เกราะแตก! แช่แข็งไร้ผลเพราะเลยกำหนดแล้ว]"
                        else: 
                            frozen_badge = " ❄️ [เปิดเกราะแช่แข็งหนีภัยฉุกเฉิน]"
                    else: 
                        frozen_badge = ""

                    c1.write(f"**{m.get('ประเภท','')}** | {task_mode_badge}{is_boss}{is_bounty} {m['ภารกิจ']}{order_badge}{deadline_badge}{frozen_badge}")
                    
                    all_done = True
                    has_today_progress = False
                    
                    if m.get("subtasks"):
                        total_subs = len(m["subtasks"])
                        done_subs = len([s for s in m["subtasks"] if s.get("done")])
                        progress_pct = done_subs / total_subs if total_subs > 0 else 0
                        st.progress(progress_pct, text=f"📊 ความคืบหน้าการสับซุง: {done_subs} / {total_subs} ({int(progress_pct*100)}%)")
                        
                        st.caption("🔒 *งานย่อยที่เสร็จแล้วจะถูกผนึก! มึงต้องขยับสับข้อใหม่ของวันนี้ถึงจะรอด!*")
                        for i, stask in enumerate(m["subtasks"]):
                            is_done = stask.get("done", False)
                            done_date = stask.get("done_date", "")
                            
                            is_locked = is_done and done_date != today_str
                            
                            label = f"{stask['name']}"
                            if is_locked and done_date:
                                try:
                                    d_dt = datetime.strptime(done_date, "%Y-%m-%d").date()
                                    diff_days = (today_date - d_dt).days
                                    if diff_days == 1: 
                                        label += " 🔒 (ผนึกเมื่อวานนี้)"
                                    elif diff_days > 1: 
                                        label += f" 🔒 (ผนึกเมื่อ {diff_days} วันที่แล้ว)"
                                    else: 
                                        label += f" 🔒 (ผนึกแล้ว)"
                                except: 
                                    label += f" 🔒 (ผนึกเมื่อ: {done_date})"
                                
                            can_interact = not is_locked and (not is_frozen or is_overdue)
                            checked = st.checkbox(label, value=is_done, disabled=not can_interact, key=f"st_{m['id']}_{i}")
                            
                            if can_interact:
                                if checked != is_done:
                                    m["subtasks"][i]["done"] = checked
                                    m["subtasks"][i]["done_date"] = today_str if checked else ""
                                    save_db(db)
                                    st.toast("🔥 สับซุงสำเร็จ 1 ท่อน!", icon="🪓")
                                    st.rerun()
                            
                            if m["subtasks"][i].get("done_date", "") == today_str:
                                has_today_progress = True
                                
                        all_done = all(stask.get("done", False) for stask in m["subtasks"])

                        if is_frozen:
                            if is_overdue: 
                                st.markdown("🔴 *⚠️ [เกราะแตก! แช่แข็งไร้ผลเพราะงานเลยกำหนดเวลา มึงโดนพิพากษาแน่!]*")
                            else: 
                                st.markdown("❄️ *[เปิดเกราะแช่แข็ง รอดพ้นศาลเตี้ยคืนนี้]*")
                        elif has_today_progress: 
                            st.markdown("🟢 *[รอดตาย! วันนี้มึงสับงานย่อยแล้ว]*")
                        else: 
                            st.markdown("🔴 *⚠️ [วิกฤต! วันนี้ยังไม่ขยับเลย ระวังแท่นพิพากษา!]*")
                    else:
                        if is_frozen:
                            if is_overdue: 
                                st.markdown("🔴 *⚠️ [เกราะแตก! แช่แข็งไร้ผลเพราะเลยกำหนดเวลา]*")
                            else: 
                                st.markdown("❄️ *[เปิดเกราะแช่แข็ง รอดพ้นศาลเตี้ยคืนนี้]*")
                        else: 
                            st.caption("⚡ *งานนี้ไม่มีงานย่อย ต้องกดปุ่ม [✅ สำเร็จ] ม้วนเดียวให้จบภายในวันนี้!*")
                        all_done = True 

                    if is_frozen:
                        if c4.button("🔥 ปลดล็อก", key=f"unfrz_{m['id']}", use_container_width=True):
                            m["skip_today_date"] = ""
                            save_db(db)
                            st.rerun()
                    else:
                        if c4.button("❄️ เลื่อนฉุกเฉิน", key=f"frz_{m['id']}", use_container_width=True, help="แช่แข็งงานนี้ชั่วคราวเนื่องจากติดภารกิจโครงงานฉุกเฉิน!"):
                            m["skip_today_date"] = today_str
                            save_db(db)
                            st.rerun()

                    if all_done and (not is_frozen or is_overdue):
                        if c2.button("✅ สำเร็จ", key=f"m_{m['id']}"):
                            m["เสร็จแล้ว"] = True
                            exp_gain, fail_reduce = calculate_task_rewards(m, current_streak)
                            
                            if m.get("battle_role") == "Vanguard":
                                exp_gain += 20
                                st.toast("⚡ FIRST STRIKE! เด็ดหัวทัพหน้าศัตรูสำเร็จ รับโบนัสความไวแสง +20 EXP!", icon="⚡")
                                
                            user["exp"] += exp_gain
                            user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce)
                            save_db(db)
                            st.balloons()
                            st.rerun()
                            
                        if c3.button("📤 ส่ง/รอตรวจ", key=f"pend_{m['id']}"):
                            m["รอตรวจ"] = True
                            save_db(db)
                            st.rerun()
                    else:
                        if is_frozen and not is_overdue: 
                            c2.caption("❄️ แช่แข็งชั่วคราว")
                        else: 
                            c2.caption("🔒 งานย่อยยังคาอยู่")
                        
                    if c5.button("🗑️", key=f"del_m_{m['id']}"):
                        db["missions"][safe_email].remove(m)
                        save_db(db)
                        st.rerun()
        else: 
            st.success("✅ วันนี้เคลียร์ภารกิจหลักหมดแล้ว เยี่ยมมากไอ้เสือ!")

        if pending_missions:
            st.divider()
            st.markdown("### ⏳ งานที่รอการตรวจสอบ / พร้อมส่ง")
            for m in pending_missions:
                c1, c2, c3 = st.columns([5, 2, 2])
                is_boss = "💀 " if m.get("is_boss") else ""
                c1.caption(f"⏳ {is_boss}{m['ภารกิจ']}")
                if c2.button("✅ ตรวจผ่าน (รับ EXP)", key=f"appr_{m['id']}"):
                    m["เสร็จแล้ว"] = True
                    m["รอตรวจ"] = False
                    
                    exp_gain, fail_reduce = calculate_task_rewards(m, current_streak)
                    user["exp"] += exp_gain
                    user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce)
                    
                    save_db(db)
                    st.balloons()
                    st.rerun()
                if c3.button("⏪ ดึงกลับมาทำ", key=f"revert_{m['id']}"):
                    m["รอตรวจ"] = False
                    save_db(db)
                    st.rerun()

    # ----------------------------------------------------
    # 📖 TAB 2: ภารกิจการเรียนและการทบทวน (Study Missions Module)
    # ----------------------------------------------------
    with tab_study:
        st.markdown("### 📚 The Academic Siege (กระดานคุมการเรียนและการทบทวน)")
        
        raw_active_study = [s for s in db["study_missions"][safe_email] if not s.get("เสร็จแล้ว")]
        active_single_study = [s for s in raw_active_study if not s.get("รอตรวจ", False) and not s.get("subtasks")]
        
        if len(active_single_study) >= 3:
            st.error("🚨 **กฎเหล็กวิชาการ:** โควตาวิชาทบทวนเดี่ยวเต็ม 3 Slot แล้ว! รีบเคลียร์วิชาเก่า หรือเพิ่มเนื้อหาเป็นแบบสับข้อย่อยท่อนซุงเท่านั้น!")
            
        with st.expander("➕ เพิ่มวิชา/เนื้อหาที่ต้องทบทวน"):
            with st.form("study_form", clear_on_submit=True):
                s_name = st.text_input("วิชา / หัวข้อที่ต้องติวทบทวน:")
                s_is_boss = st.checkbox("💀 ตั้งเป็นบทโหดไฟลุก (BOSS FIGHT ของการเรียน)")
                s_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด (สอบพรุ่งนี้/มะรืน)", "🔥 ติวเข้ม Special Event", "🟡 ปานกลาง (ทบทวนเรื่อยๆ)", "🟢 ชิลๆ (อ่านฆ่าเวลา)"])
                s_bounty = st.checkbox("⚔️ เดิมพันวิชาการ! (ถ้าพลาดโดนทำโทษหนักหนี้เลือดบวก 100 ที)")
                s_subtasks_text = st.text_area("🔪 สับหัวข้อย่อย / บทเรียนที่ต้องเก็บให้ครบ (ใส่ทีละบรรทัด):")
                
                s_dl_type = st.radio("⏰ ระบบเวลา (Dual Clock):", ["ไม่กำหนด (ชิลๆ)", "🗓️ Deadline ทางการ", "🎯 วันเป้าหมาย (กำหนดเอง)"], horizontal=True)
                s_deadline = st.date_input("เลือกวันที่:")
                
                if st.form_submit_button("บรรจุเข้าหลักสูตร"):
                    if s_name:
                        subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in s_subtasks_text.split('\n') if s.strip()]
                        
                        if not subtasks and len(active_single_study) >= 3:
                            st.error("🤡 ตะบัดสัตย์! โควตาวิชาเดี่ยวเต็ม 3 แล้ว ระบบบล็อก! จงแอดเป็นบทย่อยท่อนซุงซะ!")
                        else:
                            final_dl = str(s_deadline) if s_dl_type != "ไม่กำหนด (ชิลๆ)" else ""
                            
                            db["study_missions"][safe_email].append({
                                "id": str(uuid.uuid4()), 
                                "วันที่": today_str, 
                                "ภารกิจ": s_name, 
                                "ประเภท": s_type, 
                                "bounty": s_bounty, 
                                "is_boss": s_is_boss,
                                "custom_order": 99, 
                                "battle_role": "Main",
                                "is_queued": False, 
                                "skip_today_date": "",
                                "subtasks": subtasks, 
                                "เสร็จแล้ว": False, 
                                "รอตรวจ": False,
                                "deadline": final_dl,
                                "deadline_type": s_dl_type,
                                "is_study": True
                            })
                            save_db(db)
                            st.rerun()
                            
        todo_study = [s for s in raw_active_study if not s.get("รอตรวจ", False)]
        pending_study = [s for s in raw_active_study if s.get("รอตรวจ", False)]
        
        # 🧠 V.37 อัปเกรด: AI จัดเรียงรบอัจฉริยะ สำหรับฝั่งการเรียนด้วย
        todo_study.sort(key=lambda x: (
            get_role_score(x.get("battle_role", "Main")), 
            0 if x.get("is_boss") else 1, 
            get_deadline_score(x.get("deadline", "")),
            get_priority_score(x.get("ประเภท", ""))
        ))
        
        study_needs_queueing = [s for s in todo_study if not s.get("is_queued", False)]
        if study_needs_queueing:
            with st.expander("⚔️📖 บัญชาการค่ายกลกระบวนทัพการเรียน (Academic Strategic Formation)", expanded=True):
                with st.form("lock_study_order_form"):
                    st.write("เลือกตำแหน่งกระบวนทัพศึกษาให้หัวข้อวิชาใหม่ (ทัพหน้าศึกษาได้โบนัส +20 EXP ยามสำเร็จ)")
                    updated_s_orders = {}
                    updated_s_roles = {}
                    for s in study_needs_queueing:
                        is_boss_str = "💀 [BOSS] " if s.get("is_boss") else ""
                        role_choice = st.selectbox(f"วางตำแหน่งวิชา: {is_boss_str}{s['ภารกิจ']}", 
                                                   ["⚡ ทัพหน้า (Vanguard - ชิงเปิดอ่านรับโบนัส +20 EXP)", 
                                                    "⚔️ ทัพหลวง (Main Force - แกนกลางการสอบ)", 
                                                    "🏹 ทัพหนุน (Support - อ่านเสริมทบทวน)"], 
                                                   key=f"setup_s_role_{s['id']}")
                        
                        if "ทัพหน้า" in role_choice:
                            updated_s_orders[s["id"]] = 1
                            updated_s_roles[s["id"]] = "Vanguard"
                        elif "ทัพหลวง" in role_choice:
                            updated_s_orders[s["id"]] = 2
                            updated_s_roles[s["id"]] = "Main"
                        else:
                            updated_s_orders[s["id"]] = 3
                            updated_s_roles[s["id"]] = "Support"
                            
                    if st.form_submit_button("🔒 ล็อกค่ายกลการศึกษา!"):
                        for s in db["study_missions"][safe_email]:
                            if s["id"] in updated_s_orders:
                                s["custom_order"] = updated_s_orders[s["id"]]
                                s["battle_role"] = updated_s_roles[s["id"]]
                                s["is_queued"] = True
                        save_db(db)
                        st.success("📚 ตรึงค่ายกลการเรียนเรียบร้อย!")
                        st.rerun()

        if todo_study:
            for s in todo_study:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6])
                    
                    task_mode_badge = "📖 **[ติวโครงการใหญ่]**" if s.get("subtasks") else "⚡ **[ทบทวนรอบเดียวจบ]**"
                    is_bounty = " ⚔️[เดิมพันศึกษา]" if s.get("bounty") else ""
                    is_boss = " 💀 **[BOSS]**" if s.get("is_boss") else ""
                    
                    # ซ่อมบัคเรียกตัวแปร
                    order_badge = f" | {ROLE_MAP.get(s.get('battle_role', 'Main'), '⚔️ [ทัพหลวง]')}"
                    
                    is_overdue = False
                    deadline_badge = ""
                    dl_str = s.get("deadline", "")
                    dl_type = s.get("deadline_type", "🗓️ Deadline ทางการ")
                    dl_icon = "🎯" if "เป้าหมาย" in dl_type else "⏳"
                    
                    if dl_str and dl_str != "":
                        try:
                            dl_date = datetime.strptime(dl_str, "%Y-%m-%d").date()
                            days_left_task = (dl_date - today_date).days
                            if days_left_task > 0: 
                                deadline_badge = f" {dl_icon} (เหลือเวลาอีก {days_left_task} วัน)"
                            elif days_left_task == 0: 
                                deadline_badge = f" 🚨 **(ถึงกำหนดวันนี้!)**"
                            else: 
                                deadline_badge = f" 💀 **(เลยกำหนดมาแล้ว {-days_left_task} วัน)**"
                                is_overdue = True
                        except: 
                            pass

                    is_frozen = s.get("skip_today_date") == today_str
                    was_frozen_yesterday = s.get("skip_today_date") != "" and not is_frozen
                    if was_frozen_yesterday:
                        s["skip_today_date"] = ""
                        save_db(db)
                        
                    if is_frozen:
                        if is_overdue: 
                            frozen_badge = " ❄️🚨 [ค่ายกลแตก! เลยกำหนดเวลา]"
                        else: 
                            frozen_badge = " ❄️ [แช่แข็งวิชานี้ชั่วคราว]"
                    else: 
                        frozen_badge = ""

                    c1.write(f"**{s.get('ประเภท','')}** | {task_mode_badge}{is_boss}{is_bounty} {s['ภารกิจ']}{order_badge}{deadline_badge}{frozen_badge}")
                    
                    all_done = True
                    has_today_progress = False
                    
                    if s.get("subtasks"):
                        total_subs = len(s["subtasks"])
                        done_subs = len([stk for stk in s["subtasks"] if stk.get("done")])
                        progress_pct = done_subs / total_subs if total_subs > 0 else 0
                        st.progress(progress_pct, text=f"📈 ความคืบหน้าการอ่าน: {done_subs} / {total_subs} บท ({int(progress_pct*100)}%)")

                        st.caption("🔒 *บทเรียนย่อยที่อ่านแล้วจะถูกผนึก! ข้ามวันใหม่มึงต้องเปิดสับหน้าถัดไปห้ามอ่านซ้ำรอยเดิม!*")
                        for i, stask in enumerate(s["subtasks"]):
                            is_done = stask.get("done", False)
                            done_date = stask.get("done_date", "")
                            
                            is_locked = is_done and done_date != today_str
                            
                            label = f"{stask['name']}"
                            if is_locked and done_date:
                                try:
                                    d_dt = datetime.strptime(done_date, "%Y-%m-%d").date()
                                    diff_days = (today_date - d_dt).days
                                    if diff_days == 1: 
                                        label += " 🔒 (ติวแล้วเมื่อวานนี้)"
                                    elif diff_days > 1: 
                                        label += f" 🔒 (ติวเสร็จเมื่อ {diff_days} วันก่อน)"
                                    else: 
                                        label += f" 🔒 (ติวแล้ว)"
                                except: 
                                    label += f" 🔒 (ติวแล้วเมื่อ: {done_date})"
                                
                            can_interact = not is_locked and (not is_frozen or is_overdue)
                            checked = st.checkbox(label, value=is_done, disabled=not can_interact, key=f"st_stud_{s['id']}_{i}")
                            
                            if can_interact:
                                if checked != is_done:
                                    s["subtasks"][i]["done"] = checked
                                    s["subtasks"][i]["done_date"] = today_str if checked else ""
                                    save_db(db)
                                    st.toast("🔥 เก็บเนื้อหาได้อีก 1 บท!", icon="📖")
                                    st.rerun()
                                    
                            if s["subtasks"][i].get("done_date", "") == today_str: 
                                has_today_progress = True
                                
                        all_done = all(stask.get("done", False) for stask in s["subtasks"])

                        if is_frozen:
                            if is_overdue: 
                                st.markdown("🔴 *⚠️ [ค่ายกลแตก! แช่แข็งไร้ผลเพราะวิชาเลยกำหนดเวลา มึงโดนพิพากษาแน่!]*")
                            else: 
                                st.markdown("❄️ *[วิชานี้โดนแช่แข็งคุมทัพชั่วคราว รอดพ้นศาลเตี้ยคืนนี้]*")
                        elif has_today_progress: 
                            st.markdown("🟢 *[รอดตาย! วันนี้มึงสับเนื้อหาติววิชานี้แล้ว]*")
                        else: 
                            st.markdown("🔴 *⚠️ [วิกฤตความรู้! วันนี้ยังไม่ทบทวนวิชานี้เลย ระวังศาลเตี้ยลงทัณฑ์!]*")
                    else:
                        if is_frozen:
                            if is_overdue: 
                                st.markdown("🔴 *⚠️ [ค่ายกลแตก! เลยกำหนดเวลา]*")
                            else: 
                                st.markdown("❄️ *[แช่แข็งวิชานี้ไว้ชั่วคราว]*")
                        else: 
                            st.caption("⚡ *วิชานี้ไม่มีข้อย่อย อ่านครบจบเล่มแล้วกดปุ่ม [✅ ติวสำเร็จ] ม้วนเดียวจบซะ!*")
                        all_done = True

                    if is_frozen:
                        if c4.button("🔥 ปลดแช่แข็ง", key=f"unfrz_stud_{s['id']}", use_container_width=True):
                            s["skip_today_date"] = ""
                            save_db(db)
                            st.rerun()
                    else:
                        if c4.button("❄️ เลื่อนวิชานี้", key=f"frz_stud_{s['id']}", use_container_width=True, help="แช่แข็งเนื้อหานี้ชั่วคราวเนื่องจากติดเหตุฉุกเฉิน!"):
                            s["skip_today_date"] = today_str
                            save_db(db)
                            st.rerun()

                    if all_done and (not is_frozen or is_overdue):
                        if c2.button("✅ ติวสำเร็จ", key=f"stud_win_{s['id']}", use_container_width=True):
                            s["เสร็จแล้ว"] = True
                            exp_gain, fail_reduce = calculate_task_rewards(s, current_streak)
                            
                            if s.get("battle_role") == "Vanguard":
                                exp_gain += 20
                                st.toast("⚡ FIRST STRIKE! ชิงลงมืออ่านทัพหน้าสำเร็จ รับโบนัสความไวแสง +20 EXP!", icon="⚡")
                                
                            user["exp"] += exp_gain
                            user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce)
                            save_db(db)
                            st.balloons()
                            st.rerun()
                        if c3.button("📤 ส่งรออนุมัติ", key=f"pend_stud_{s['id']}", use_container_width=True):
                            s["รอตรวจ"] = True
                            save_db(db)
                            st.rerun()
                    else:
                        if is_frozen and not is_overdue: 
                            c2.caption("❄️ แช่แข็งชั่วคราว")
                        else: 
                            c2.caption("🔒 เหลือบทเรียนคาอยู่")
                            
                    if c5.button("🗑️", key=f"del_stud_{s['id']}"):
                        db["study_missions"][safe_email].remove(s)
                        save_db(db)
                        st.rerun()
        else: 
            st.success("📚 ติวทบทวนเนื้อหาครบหมดแล้ว ร่างสมองมึงแกร่งกล้าพร้อมรบทุกห้องสอบ!")

        if pending_study:
            st.divider()
            st.markdown("### ⏳ วิชาที่รออนุมัติความรู้ผ่านเกณฑ์")
            for s in pending_study:
                c1, c2, c3 = st.columns([5, 2, 2])
                c1.caption(f"⏳ [ภารกิจเรียน] {s['ภารกิจ']}")
                if c2.button("✅ ผ่าน (รับ EXP)", key=f"appr_stud_{s['id']}"):
                    s["เสร็จแล้ว"] = True
                    s["รอตรวจ"] = False
                    exp_gain, fail_reduce = calculate_task_rewards(s, current_streak)
                    user["exp"] += exp_gain
                    user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce)
                    save_db(db)
                    st.balloons()
                    st.rerun()
                if c3.button("⏪ ดึงกลับมาอ่านใหม่", key=f"revert_stud_{s['id']}"):
                    s["รอตรวจ"] = False
                    save_db(db)
                    st.rerun()

    # ----------------------------------------------------
    # TAB 3: วินัยเหล็ก (THE IRON HABITS) 
    # ----------------------------------------------------
    with tab_habits:
        st.markdown("### ⛓️ THE IRON HABITS (วินัยเหล็กรายวัน)")
        st.info("สิ่งที่มึงต้องทำทุกวัน ห้ามมีข้ออ้าง พลาด 1 ครั้ง Streak ขาดทันที!")
        with st.form("habit_form", clear_on_submit=True):
            h_name = st.text_input("สร้างวินัยเหล็กใหม่ (เช่น ตื่นตี 5, อ่านหนังสือ 10 หน้า):")
            if st.form_submit_button("เพิ่มวินัยเหล็ก"):
                if h_name:
                    db["iron_habits"][safe_email].append({"id": str(uuid.uuid4()), "name": h_name, "last_done_date": ""})
                    save_db(db)
                    st.rerun()
                    
        if db["iron_habits"][safe_email]:
            for h in db["iron_habits"][safe_email]:
                c1, c2, c3 = st.columns([5, 3, 1])
                c1.write(f"⛓️ **{h['name']}**")
                if h.get("last_done_date") == today_str:
                    c2.success("✅ ทำแล้ววันนี้")
                else:
                    if c2.button("🔥 กูทำสำเร็จ!", key=f"h_done_{h['id']}"):
                        h["last_done_date"] = today_str
                        
                        bonus = 5
                        fail_sub = 2 
                        
                        if current_streak >= 30: 
                            bonus = 10
                            fail_sub = 5 
                        elif current_streak >= 7: 
                            bonus = 7
                            fail_sub = 3 
                            
                        user["exp"] += bonus
                        user["failure_prob"] = max(0, user["failure_prob"] - fail_sub) 
                        
                        save_db(db)
                        st.toast(f"🛡️ วินัยเหล็กสำแดงผล! โอกาสล้มเหลวถดถอยลดลง -{fail_sub}%!", icon="🛡️")
                        st.balloons()
                        st.rerun()
                if c3.button("🗑️", key=f"del_h_{h['id']}"):
                    db["iron_habits"][safe_email].remove(h)
                    save_db(db)
                    st.rerun()
        else:
            st.success("ยังไม่มีวินัยเหล็ก! สร้างมันขึ้นมาซะ!")

    # ----------------------------------------------------
    # TAB 4: สมุดจดงาน (Backlog)
    # ----------------------------------------------------
    with tab_backlog:
        st.markdown("### 📝 สมุดจดงาน (Task Backlog)")
        with st.form("backlog_form", clear_on_submit=True):
            b_name = st.text_input("หัวข้องาน/เนื้อหา/ไอเดียยูทูป:")
            b_detail = st.text_area("รายละเอียด/Note (ถ้ามี):")
            b_subtasks_text = st.text_area("🔪 ซอยงานย่อย (Enter ขึ้นบรรทัดใหม่, ไม่บังคับ):")
            b_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด (คอขาดบาดตาย)", "🔥 งานฉุกเฉิน / Special Event", "🟡 ปานกลาง (ต้องเสร็จ)", "🟢 ชิลๆ (ทำตอนว่าง)"])
            
            b_dl_type = st.radio("⏰ ระบบเวลา (Dual Clock):", ["ไม่กำหนด (ชิลๆ)", "🗓️ Deadline ทางการ", "🎯 วันเป้าหมาย (กำหนดเอง)"], horizontal=True)
            b_deadline = st.date_input("วันกำหนดส่ง (เลือกวันที่):")
            
            if st.form_submit_button("💾 บันทึกลงสมุด"):
                if b_name:
                    b_subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in b_subtasks_text.split('\n') if s.strip()]
                    
                    final_b_dl = str(b_deadline) if b_dl_type != "ไม่กำหนด (ชิลๆ)" else ""
                    
                    db["backlog"][safe_email].append({
                        "id": str(uuid.uuid4()), 
                        "ภารกิจ": b_name, 
                        "รายละเอียด": b_detail,
                        "subtasks": b_subtasks, 
                        "ประเภท": b_type, 
                        "deadline": final_b_dl,
                        "deadline_type": b_dl_type
                    })
                    save_db(db)
                    st.rerun()
                    
        if db["backlog"][safe_email]:
            active_m_slots = len([m for m in db["missions"][safe_email] if not m.get("เสร็จแล้ว") and not m.get("subtasks")])
            active_s_slots = len([s for s in db["study_missions"][safe_email] if not s.get("เสร็จแล้ว") and not s.get("subtasks")])
            
            sorted_backlog = sorted(db["backlog"][safe_email], key=lambda x: x.get("deadline") if x.get("deadline") and x.get("deadline") != "" else "9999-12-31")
            
            for b_task in sorted_backlog:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([4, 2, 2, 0.8])
                    
                    days_badge = ""
                    b_dl_str = b_task.get("deadline", "")
                    b_dl_type_str = b_task.get("deadline_type", "🗓️ Deadline ทางการ")
                    b_icon = "🎯" if "เป้าหมาย" in b_dl_type_str else "📅"
                    
                    if b_dl_str and b_dl_str != "":
                        try:
                            dl_date = datetime.strptime(b_dl_str, "%Y-%m-%d").date()
                            days_left_b = (dl_date - today_date).days
                            if days_left_b > 0: 
                                days_badge = f"⏳ เหลือ {days_left_b} วัน"
                            elif days_left_b == 0: 
                                days_badge = f"🚨 **ถึงกำหนดวันนี้!**"
                            else: 
                                days_badge = f"💀 **เลยกำหนดมา {-days_left_b} วัน**"
                        except: 
                            pass
                            
                    display_dl = f" {b_icon} กำหนดเวลา: {b_dl_str} ({days_badge})" if b_dl_str else " ไม่ระบุเวลา"

                    c1.write(f"**{b_task['ประเภท']}** | 📝 {b_task['ภารกิจ']}")
                    c1.caption(f"{display_dl} | รายละเอียด: {b_task.get('รายละเอียด', '-')}")
                    
                    has_subtasks = bool(b_task.get("subtasks"))
                    
                    if not has_subtasks and active_m_slots >= 3:
                        c2.button("⚡ ดึงเข้าช่องงาน", key=f"pull_m_{b_task['id']}", disabled=True, help="โควตางานเดี่ยวเต็ม 3 ชิ้นแล้ว! งานนี้ไม่มีข้อย่อย ดึงเข้าไม่ได้!")
                    else:
                        if c2.button("⚡ ดึงเข้าช่องงาน", key=f"pull_m_{b_task['id']}", type="primary"):
                            db["missions"][safe_email].append({
                                "id": b_task["id"], 
                                "วันที่": today_str, 
                                "ภารกิจ": b_task["ภารกิจ"],
                                "ประเภท": b_task["ประเภท"], 
                                "bounty": False, 
                                "is_boss": False,
                                "custom_order": 1 if "🔴" in b_task["ประเภท"] else 99, 
                                "battle_role": "Main",
                                "is_queued": False, 
                                "skip_today_date": "",
                                "deadline": b_task.get("deadline", ""),
                                "deadline_type": b_task.get("deadline_type", "🗓️ Deadline ทางการ"),
                                "subtasks": b_task.get("subtasks", []), 
                                "เสร็จแล้ว": False, 
                                "รอตรวจ": False
                            })
                            db["backlog"][safe_email].remove(b_task)
                            save_db(db)
                            st.rerun()
                            
                    if not has_subtasks and active_s_slots >= 3:
                        c3.button("📖 ดึงเข้าช่องเรียน", key=f"pull_s_{b_task['id']}", disabled=True, help="โควตาวิชาเรียนเดี่ยวเต็ม 3Slot แล้ว! ดึงเข้าไม่ได้!")
                    else:
                        if c3.button("📖 ดึงเข้าช่องเรียน", key=f"pull_s_{b_task['id']}", type="secondary"):
                            db["study_missions"][safe_email].append({
                                "id": b_task["id"], 
                                "วันที่": today_str, 
                                "ภารกิจ": b_task["ภารกิจ"],
                                "ประเภท": b_task["ประเภท"], 
                                "bounty": False, 
                                "is_boss": False,
                                "custom_order": 1 if "🔴" in b_task["ประเภท"] else 99,
                                "battle_role": "Main",
                                "is_queued": False, 
                                "skip_today_date": "",
                                "deadline": b_task.get("deadline", ""),
                                "deadline_type": b_task.get("deadline_type", "🗓️ Deadline ทางการ"),
                                "subtasks": b_task.get("subtasks", []), 
                                "เสร็จแล้ว": False, 
                                "รอตรวจ": False,
                                "is_study": True
                            })
                            db["backlog"][safe_email].remove(b_task)
                            save_db(db)
                            st.rerun()
                    
                    if c4.button("🗑️", key=f"del_b_{b_task['id']}"):
                        db["backlog"][safe_email].remove(b_task)
                        save_db(db)
                        st.rerun()
        else: 
            st.success("สมุดจดว่างเปล่า!")

    # ----------------------------------------------------
    # TAB 5: โหลคุกกี้ (Cookie Jar) 🍪
    # ----------------------------------------------------
    with tab_cookie:
        st.markdown("### 🍪 THE COOKIE JAR (โหลเก็บความภูมิใจ)")
        st.info("เวลาที่มึงท้อ หมดไฟ ให้กลับมาเปิดโหลนี้ดูว่ามึงเคยชนะอะไรมาบ้าง!")
        with st.form("cookie_form", clear_on_submit=True):
            win_text = st.text_input("วันนี้มึงชนะใจตัวเองเรื่องอะไรได้บ้าง? (เรื่องเล็กๆ ก็ได้):")
            if st.form_submit_button("เก็บชัยชนะลงโหล!"):
                if win_text:
                    db["cookie_jar"][safe_email].append({"วันที่": today_str, "ชัยชนะ": win_text})
                    user["exp"] += int(5 * (1.5 if current_streak>=30 else 1.2 if current_streak>=7 else 1.0))
                    save_db(db)
                    st.success("✅ เก็บชัยชนะลงโหลเรียบร้อย! มึงแม่งสุดยอด!")
                    st.rerun()
        
        if db["cookie_jar"][safe_email]:
            st.markdown("**ความสำเร็จล่าสุดของมึง:**")
            for c in reversed(db["cookie_jar"][safe_email][-5:]):
                st.success(f"🏆 **[{c['วันที่']}]** {c['ชัยชนะ']}")

    # ----------------------------------------------------
    # TAB 6: ลานประลองปัญญา (EXAM & BEAT YESTERDAY) 📚
    # ----------------------------------------------------
    with tab_academic:
        st.markdown("### 📚 ลานประลองปัญญา (THE ACADEMIC BATTLEFIELD)")
        st.info("ที่นี่ไม่ได้วัดแค่กล้ามเนื้อ แต่วัดความคมของสมองมึงด้วย!")

        st.markdown("#### 📝 ประวัติคะแนนสอบ (มึงก้าวหน้าหรือถอยหลัง?)")
        with st.form("exam_form", clear_on_submit=True):
            e_subj = st.text_input("ชื่อวิชา / เรื่องที่ทดสอบ:")
            e_score = st.number_input("คะแนนที่ได้ล่าสุด:", min_value=0.0, step=0.1)
            if st.form_submit_button("บันทึกคะแนนสอบ"):
                if e_subj:
                    if e_subj not in db["exams"][safe_email]:
                        db["exams"][safe_email][e_subj] = []
                    
                    history = db["exams"][safe_email][e_subj]
                    
                    if len(history) > 0:
                        last_score = history[-1]
                        if e_score > last_score:
                            user["exp"] += int(30 * (1.5 if current_streak>=30 else 1.0))
                            st.success(f"🔥 โคตรเถื่อน! มึงเก่งขึ้นกว่าครั้งที่แล้ว ({last_score} -> {e_score}) รับ EXP ท่วมๆ!")
                        elif e_score < last_score:
                            user["blood_debt"] += 50
                            user["failure_prob"] = min(100, user["failure_prob"] + 10)
                            st.error(f"🤡 กระจอกจัด! คะแนนมึงร่วง ({last_score} -> {e_score}) แท่นพิพากษาสั่งยัดหนี้เลือด 50 ที!")
                        else:
                            st.warning("คะแนนเท่าเดิม... อย่าหยุดพัฒนาสิวะไอ้เวร!")
                    
                    db["exams"][safe_email][e_subj].append(e_score)
                    save_db(db)
                    st.rerun()

        if db["exams"][safe_email]:
            cols = st.columns(3)
            idx = 0
            for subj, scores in db["exams"][safe_email].items():
                if len(scores) > 0:
                    latest = scores[-1]
                    delta = round(latest - scores[-2], 2) if len(scores) > 1 else None
                    cols[idx % 3].metric(label=f"📖 {subj}", value=latest, delta=delta)
                    idx += 1

        st.divider()

        st.markdown("#### 🥊 ชกกับเงา (BEAT YESTERDAY'S SELF)")
        st.write("เลือกมา 1 อย่างที่มึงจะใช้วัดผลความทุ่มเท (เช่น จำนวนหน้า, จำนวนข้อ, นาทีที่โฟกัส)")
        
        yesterday_str = str(today_date - timedelta(days=1))
        
        with st.form("beat_yesterday_form"):
            by_metric = st.text_input("สิ่งที่มึงใช้วัด (เช่น ข้อสอบที่ทำ, หน้าหนังสือ):", value=db["beat_yesterday"][safe_email].get("metric_name", ""))
            by_val = st.number_input("จำนวนที่ทำได้วันนี้:", min_value=0)
            if st.form_submit_button("ทุบสถิติตัวเอง"):
                if by_metric:
                    db["beat_yesterday"][safe_email]["metric_name"] = by_metric
                    if "history" not in db["beat_yesterday"][safe_email]:
                        db["beat_yesterday"][safe_email]["history"] = {}
                    
                    y_val = db["beat_yesterday"][safe_email]["history"].get(yesterday_str, 0)
                    
                    if by_val > y_val:
                        user["exp"] += int(20 * (1.2 if current_streak>=7 else 1.0))
                        st.success(f"🔥 มึงชนะไอ้ขี้แพ้เมื่อวานได้แล้ว! ({y_val} -> {by_val})")
                    elif by_val == y_val:
                        st.warning("มึงแค่เสมอตัวกับเมื่อวาน! พรุ่งนี้ต้องดีกว่านี้!")
                    else:
                        user["blood_debt"] += 30
                        st.error(f"🚨 วันนี้มึงกากกว่าเมื่อวาน! ({y_val} -> {by_val}) รับหนี้เลือดไป 30 ที!")
                        
                    db["beat_yesterday"][safe_email]["history"][today_str] = by_val
                    save_db(db)
                    st.rerun()

        if "history" in db["beat_yesterday"].get(safe_email, {}) and db["beat_yesterday"][safe_email].get("metric_name"):
            st.caption(f"สถิติ: **{db['beat_yesterday'][safe_email]['metric_name']}**")
            y_val = db["beat_yesterday"][safe_email]["history"].get(yesterday_str, 0)
            t_val = db["beat_yesterday"][safe_email]["history"].get(today_str, 0)
            st.metric(label="เปรียบเทียบวันนี้ vs เมื่อวาน", value=t_val, delta=t_val - y_val)

        st.divider()

        st.markdown("#### 🩸 กฎ 40% (THE 40% RULE)")
        st.info("ตอนที่มึงคิดว่าร่างกายหรือสมองมึงรับไม่ไหวแล้ว... ความจริงมึงเพิ่งใช้ขีดจำกัดไปแค่ 40% เท่านั้น! กดปุ่มนี้เมื่อมึงฝืนทำต่อจากจุดที่อยากยอมแพ้ที่สุด!")
        if st.button("🔥 กูเกือบยอมแพ้แล้ว แต่กูฝืนทะลุขีดจำกัดได้!", use_container_width=True):
            if today_str not in db["limit_breaks"][safe_email]:
                db["limit_breaks"][safe_email].append(today_str)
                user["exp"] += int(50 * (1.5 if current_streak>=30 else 1.0))
                user["failure_prob"] = max(0, user["failure_prob"] - 15)
                save_db(db)
                st.balloons()
                st.success("🦍 พลังใจมึงมันระดับสัตว์ประหลาด! เอา EXP ทวีคูณไป และลดโอกาสล้มเหลวลง 15%!")
            else:
                st.warning("วันนี้มึงทะลุขีดจำกัดไปแล้ว! เก็บแรงไว้ลุยพรุ่งนี้บ้างไอ้บ้าพลัง!")

    st.divider()
    st.markdown("### 💰 คลังสมบัตินักรบ (ทุนสร้างฝัน)")
    c_fin1, c_fin2 = st.columns([2, 1])
    with c_fin1:
        st.write(f"**เป้าหมาย:** {finance.get('goal_name', 'ยังไม่ตั้ง')}")
        cur = finance.get('current', 0)
        tgt = finance.get('goal_amount', 1)
        prog = max(0.0, min(cur / tgt, 1.0)) if tgt > 0 else 0.0
        st.progress(prog, text=f"มีแล้ว: {cur} / {tgt} บาท ({int(prog*100)}%)")
    with c_fin2:
        with st.popover("⚙️ จัดการเงิน"):
            new_g_name = st.text_input("ชื่อเป้าหมาย:", value=finance.get('goal_name', ''))
            new_g_amt = st.number_input("จำนวนเงินเป้าหมาย:", value=finance.get('goal_amount', 0))
            if st.button("ตั้งเป้าหมาย"):
                finance['goal_name'] = new_g_name
                finance['goal_amount'] = new_g_amt
                save_db(db)
                st.rerun()
            st.divider()
            add_amt = st.number_input("บวก/ลด เงิน:", value=0)
            if st.button("บันทึกเงิน"):
                finance['current'] += add_amt
                save_db(db)
                st.rerun()

# ==========================================
# 6. หนี้เลือด & THE JUDGMENT FEED (แท่นพิพากษาไร้ปรานีประจำวัน)
# ==========================================
st.divider()
c_bot1, c_bot2 = st.columns(2)
with c_bot1:
    my_exp = ((user["level"] - 1) * 100) + user["exp"]
    st.metric("พลังร่างทอง (มันไม่เคยหยุดเดิน)", f"{user['ghost_exp']} EXP")
    st.metric("พลังของมึงปัจจุบัน", f"{my_exp} EXP", delta=f"{my_exp - user['ghost_exp']} เทียบร่างทอง")
with c_bot2:
    st.markdown("### 🩸 หนี้เลือด (Blood Debt)")
    st.metric("หนี้วิดพื้นที่ต้องจ่าย", f"{user.get('blood_debt', 0)} ที")
    if user.get("blood_debt", 0) > 0:
        if st.button("กูวิดพื้นใช้หนี้หมดแล้ว! (ปลดกรง)"):
            user["blood_debt"] = 0
            user["in_cage"] = False
            save_db(db)
            st.rerun()

st.divider()
st.markdown("<h2>⚖️ THE JUDGMENT FEED (พิพากษาก่อนนอน)</h2>", unsafe_allow_html=True)
if user.get("ambush_task", "") != "":
    st.error(f"🚨 **โดนซุ่มโจมตี!** คำสั่ง: **{user['ambush_task']}**")
    if st.button("🔥 กูทำเสร็จแล้ว!"):
        user["ambush_task"] = ""
        user["exp"] += 20
        save_db(db)
        st.rerun()
elif user.get("cleared_yesterday"): 
    st.success("🔥 พิพากษาเสร็จสิ้น! มึงรอดไปได้อีกหนึ่งวัน!")
else:
    active_for_judgment = []
    
    combined_missions = db["missions"][safe_email] + db["study_missions"][safe_email]
    
    for m in combined_missions:
        if not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False):
            if m.get("skip_today_date") == today_str:
                is_task_overdue = False
                if m.get("deadline") and m["deadline"] != "":
                    try:
                        dl_dt = datetime.strptime(m["deadline"], "%Y-%m-%d").date()
                        if dl_dt < today_date: 
                            is_task_overdue = True 
                    except: 
                        pass
                
                if not is_task_overdue:
                    continue 
                
            if m.get("subtasks"):
                has_today_progress = any(stask.get("done", False) and stask.get("done_date", "") == today_str for stask in m["subtasks"])
                if not has_today_progress: 
                    active_for_judgment.append(m)
            else:
                active_for_judgment.append(m)

    incomplete_habits = [h for h in db["iron_habits"][safe_email] if h.get("last_done_date") != today_str]
    incomplete_bosses = [m for m in active_for_judgment if m.get("is_boss")]

    if incomplete_bosses:
        st.error("💀 ไอ้สวะ! มึงดองงาน BOSS FIGHT (ไม่ว่าจะงานหรือเรียน)! แท่นพิพากษาสั่งลงโทษหนัก!")
        if st.button("🩸 ยอมรับความกาก (รับหนี้เลือด 300 ที!)"):
            user["blood_debt"] += 300
            user["failure_prob"] = min(100, user["failure_prob"] + 30)
            user["in_cage"] = True
            user["cleared_yesterday"] = True
            user["streak"] = 0 
            save_db(db)
            st.rerun()
            
    elif active_for_judgment or incomplete_habits: 
        st.error("❌ มึงกำลังหักหลังตัวเอง! ศาลเตี้ยพบงาน/วิชาเรียน/วินัยที่มึงละทิ้งในวันนี้:")
        
        total_blood_penalty = 0
        for m in active_for_judgment:
            is_overdue_check = False
            if m.get("deadline") and m["deadline"] != "":
                try:
                    if datetime.strptime(m["deadline"], "%Y-%m-%d").date() < today_date: 
                        is_overdue_check = True
                except: 
                    pass
            
            domain_label = "[📚 วิชาเรียน]" if m.get("is_study") else "[🔪 ภารกิจงาน]"
            time_label = "เลยเป้าหมายที่ตั้งไว้" if "เป้าหมาย" in m.get("deadline_type", "") else "เลยกำหนดเดดไลน์"
            
            task_score = get_priority_score(m.get("ประเภท", ""))
            task_penalty = 100 if task_score == 1 else 70 if task_score == 2 else 50
            total_blood_penalty += task_penalty
            
            if is_overdue_check: 
                mode = f"{domain_label} 🚨 เกราะแตก! {time_label} (หนี้เลือด +{task_penalty})"
            else: 
                mode = f"{domain_label} 🔪 โครงการใหญ่ ไม่ยอมทำ (หนี้เลือด +{task_penalty})" if m.get("subtasks") else f"{domain_label} ⚡ ม้วนเดียวจบ ดองข้ามวัน (หนี้เลือด +{task_penalty})"
            st.write(f"👉 **{m['ภารกิจ']}** [{mode}]")
            
        for h in incomplete_habits:
            total_blood_penalty += 30
            st.write(f"👉 **{h['name']}** [⛓️ วินัยเหล็ก ละทิ้ง (หนี้เลือด +30)]")
            
        st.warning("กลับไปจัดการให้จบซะ หรือถ้ามึงสู้ไม่ไหว ก็จงกดปุ่มยอมรับความพ่ายแพ้!")
        
        if st.button(f"🩸 ยอมรับความกาก (ทิ้งงานวันนี้ รับหนี้เลือดรวม {total_blood_penalty} ที)"):
            penalty_count = len(active_for_judgment) + len(incomplete_habits)
            user["blood_debt"] += total_blood_penalty
            user["failure_prob"] = min(100, user["failure_prob"] + (10 * penalty_count))
            user["in_cage"] = True
            user["cleared_yesterday"] = True 
            user["streak"] = 0 
            save_db(db)
            st.rerun()
            
    elif user.get("in_cage") or user.get("blood_debt", 0) > 0: 
        st.error("❌ มึงติดหนี้เลือดอยู่ ชดใช้กรรมซะก่อนถึงจะปิดวันได้!")
    else:
        st.warning("วันนี้มึงใส่เต็ม 100% หรือมึงใช้พลังแค่ 40%?")
        j_col1, j_col2 = st.columns(2)
        with j_col1:
            if st.button("📉 สู้ไม่เต็มที่ (แค่ 40%)"):
                user["exp"] -= 30
                user["cleared_yesterday"] = True
                user["failure_prob"] = min(100, user["failure_prob"] + 10)
                user["streak"] = 0 
                save_db(db)
                st.rerun()
        with j_col2:
            if st.button("🔥 กูใช้พลังทั้งหมด 100%!"):
                if random.random() < 0.2: 
                    user["ambush_task"] = random.choice(AMBUSH_TASKS)
                else: 
                    user["cleared_yesterday"] = True
                    user["streak"] += 1
                    user["exp"] += int(25 * (1.5 if current_streak>=30 else 1.2 if current_streak>=7 else 1.0))
                save_db(db)
                st.rerun()

# ==========================================
# 8. 📜 พงศาวดารความทรงจำ (HISTORY LOG)
# ==========================================
st.divider()
if not monk_mode:
    st.markdown("## 📜 พงศาวดารความทรงจำ (HISTORY LOG)")
    tab1, tab2, tab3, tab4 = st.tabs(["🍪 คลังแสง (ความสำเร็จ)", "🤡 บัญชีหนังหมา (ข้ออ้าง)", "🪵 บันทึกการแบกซุง (ตาราง)", "📊 BATTLE ANALYTICS"])

    with tab1:
        if db["cookie_jar"].get(safe_email):
            for item in reversed(db["cookie_jar"][safe_email]): 
                st.success(f"🏆 **[{item.get('วันที่', 'ไม่ระบุ')}]** : {item.get('ชัยชนะ', '')}")
        else: 
            st.write("ยังไม่มีความสำเร็จอะไรเลย ไปทำซะ!")

    with tab2:
        if db["excuses"].get(safe_email):
            for item in reversed(db["excuses"][safe_email]): 
                st.error(f"🤡 **[{item.get('วันที่', 'ไม่ระบุ')}]** : {item.get('ข้ออ้าง', '')}")
        else: 
            st.write("ดีมาก! ยังไม่มีข้ออ้างขยะๆ ให้รกหูรกตา!")

    with tab3:
        total_missions_list = db["missions"].get(safe_email, []) + db["study_missions"].get(safe_email, [])
        if total_missions_list:
            mission_history = []
            for item in reversed(total_missions_list):
                if item.get("เสร็จแล้ว"): 
                    status = "✅ เสร็จแล้ว"
                elif item.get("รอตรวจ", False): 
                    status = "⏳ รอตรวจ"
                else: 
                    status = "❌ ยังดองอยู่"
                
                domain_type = "📚 เรียน" if item.get("is_study") else "🔪 งาน"
                
                mission_history.append({
                    "วันที่เริ่ม": item.get('วันที่', '-'),
                    "สมรภูมิ": domain_type,
                    "ภารกิจ/วิชา": item.get('ภารกิจ', ''),
                    "ความสำคัญ": item.get('ประเภท','-'),
                    "BOSS?": "💀" if item.get("is_boss") else "-",
                    "เดิมพัน?": "⚔️" if item.get("bounty") else "-",
                    "สถานะ": status
                })
            df_missions = pd.DataFrame(mission_history)
            st.dataframe(df_missions, use_container_width=True, hide_index=True)
        else: 
            st.write("ยังไม่มีประวัติการแบกซุงเลยไอ้ลูกหมา ไปหางานทำซะ!")

    with tab4:
        all_m = db["missions"].get(safe_email, []) + db["study_missions"].get(safe_email, [])
        total_m = len(all_m)
        done_m = len([m for m in all_m if m.get("เสร็จแล้ว")])
        boss_killed = len([m for m in all_m if m.get("เสร็จแล้ว") and m.get("is_boss")])
        win_rate = (done_m / total_m * 100) if total_m > 0 else 0
        
        win_count = len(db["cookie_jar"].get(safe_email, []))
        fail_count = len(db["excuses"].get(safe_email, []))
        
        st.markdown("#### 📊 สรุปผลประกอบการสมอง (BATTLE ANALYTICS)")
        c_stat1, c_stat2, c_stat3, c_stat4 = st.columns(4)
        c_stat1.metric("อัตราการชนะ (Win Rate)", f"{win_rate:.1f}%")
        c_stat2.metric("บอสที่ฆ่าได้ (Boss Kills)", f"{boss_killed} ตัว")
        c_stat3.metric("ภารกิจที่สำเร็จ (Missions)", f"{done_m} / {total_m}")
        c_stat4.metric("รอยแผลความขี้เกียจ", f"{fail_count} รอย")
        
        if win_count + fail_count > 0:
            st.markdown("**กราฟเปรียบเทียบ: ร่างทอง (ชนะใจตัวเอง) VS ร่างขยะ (พ่ายแพ้ปล่อยข้ออ้าง)**")
            chart_data = pd.DataFrame({"จำนวนครั้ง": [win_count, fail_count]}, index=["Savage (ชนะ)", "Bitch (ข้ออ้าง)"])
            st.bar_chart(chart_data)
