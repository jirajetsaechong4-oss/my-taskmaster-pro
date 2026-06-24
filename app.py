import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import requests
import uuid
import hashlib
import random

# ==========================================
# 1. ตั้งค่าระบบ (THE IMMORTAL SOUL V.30 - THE TIME-BOUND STRATEGIST)
# ==========================================
st.set_page_config(page_title="THE BRAIN WAR", layout="wide", page_icon="🧠")

# ⚠️ ลิงก์ Firebase ของมึง
FIREBASE_URL = "https://mytaskpro-f7328-default-rtdb.asia-southeast1.firebasedatabase.app/" 

# ⏱️ ล็อกเวลาให้เป็นโซนประเทศไทย (GMT+7) เสมอ แบบ Real-time!
tz_thai = timezone(timedelta(hours=7))
now_thai = datetime.now(tz_thai)
today_date = now_thai.date()
today_str = str(today_date)

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

def get_safe_email(email): return email.replace(".", "-").replace("@", "-")

def get_title(level):
    if level < 3: return "🤡 ไอ้ลูกหมาขี้ขลาด"
    elif level < 7: return "⚔️ นักรบฝึกหัดแบกซุง"
    elif level < 12: return "🦍 แม่ทัพคุมโดพามีน"
    else: return "👑 มหาจักรพรรดิผู้คุมชะตา"

def get_priority_score(task_type):
    if "🔴 ด่วนสุด" in task_type or "🔥 งานฉุกเฉิน" in task_type: return 1
    if "🟡 ปานกลาง" in task_type: return 2
    if "🟢 ชิลๆ" in task_type: return 3
    return 4

def load_db():
    if FIREBASE_URL == "" or FIREBASE_URL is None:
        st.error("🚨 ไอ้เวร! ลิงก์ Firebase หายไปไหน กลับไปแก้เดี๋ยวนี้!")
        st.stop()
    try:
        res = requests.get(f"{FIREBASE_URL}/db.json")
        if res.status_code == 200 and res.json() is not None:
            data = res.json()
            defaults = {
                "users": {}, "missions": {}, "backlog": {}, "dark_room": {}, 
                "anti_simp": {}, "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, 
                "deadlines": {}, "haters": {}, "finance": {}, "iron_habits": {},
                "exams": {}, "beat_yesterday": {}, "limit_breaks": {}
            }
            for k, v in defaults.items():
                if k not in data: data[k] = v
            return data
    except: pass
    return {
        "users": {}, "missions": {}, "backlog": {}, "dark_room": {}, 
        "anti_simp": {}, "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, 
        "deadlines": {}, "haters": {}, "finance": {}, "iron_habits": {},
        "exams": {}, "beat_yesterday": {}, "limit_breaks": {}
    }

def save_db(data):
    try: requests.put(f"{FIREBASE_URL}/db.json", json=data)
    except: st.error("🚨 เซฟข้อมูลลงฐานข้อมูลอมตะไม่สำเร็จ!")

db = load_db()

# ==========================================
# 2. OVERLAY นรก (PUNISHMENT ACTIVE)
# ==========================================
if "punishment_active" in st.session_state:
    st.error("🚨 วงล้อแห่งกรรมทำงาน! มึงต้องชดใช้ความกระจอกเดี๋ยวนี้! 🚨")
    st.title(f"🔥 คำสั่งทรมานร่างขยะ: {st.session_state.punishment_task}")
    if st.button("🩸 กูทำเสร็จแล้ว! (ชดใช้กรรมเรียบร้อย)"):
        del st.session_state.punishment_active; st.rerun()
    st.stop() 

# ==========================================
# 3. ระบบล็อกอิน
# ==========================================
if "current_user" not in st.session_state: st.session_state.current_user = None

with st.sidebar:
    st.title("🧠 สมรภูมิในสมอง")
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
                    if safe_email in db.get("users", {}): st.error("อีเมล/ID นี้มีในระบบแล้ว!")
                    else:
                        db["users"][safe_email] = {
                            "username": name_input, "level": 1, "exp": 0, "streak": 0, "blood_debt": 0, "in_cage": False,
                            "ghost_exp": 0, "ambush_task": "", "failure_prob": 10,
                            "last_login": today_str, "cleared_yesterday": True,
                            "order_locked": False,
                            "target_name": "ทำ 10 ล้านวิว YouTube Shorts", 
                            "target_date": str(today_date + timedelta(days=90))
                        }
                        save_db(db); st.success("🔥 ลงทะเบียนสำเร็จ! ไปที่ 'ล็อกอินด่วน' ได้เลย!")
                else: st.warning("กรอกชื่อกับอีเมลให้ครบ!")
                
        elif auth_mode == "⚡ ล็อกอินด่วน":
            if not db.get("users"): st.warning("ยังไม่มีนักรบในระบบ ไปสร้างนักรบใหม่ก่อน!")
            else:
                user_options = {f"{data['username']}": email for email, data in db["users"].items()}
                selected_display = st.selectbox("เลือกบัญชีของคุณ:", list(user_options.keys()))
                
                if st.button("🔥 เปิดสมอง! (เข้าสู่ระบบ)"):
                    safe_email = user_options[selected_display]
                    user_data = db["users"][safe_email]
                    
                    if "target_name" not in user_data: 
                        user_data["target_name"] = "ทำ 10 ล้านวิว YouTube Shorts"
                        user_data["target_date"] = str(today_date + timedelta(days=90))

                    if user_data["last_login"] != today_str:
                        user_data["ghost_exp"] += 25 
                        user_data["order_locked"] = False
                        unpaid_bounties = [m for m in db.get("missions", {}).get(safe_email, []) if m.get("bounty") and not m.get("เสร็จแล้ว")]
                        if unpaid_bounties or not user_data.get("cleared_yesterday", False):
                            penalty = 100 + (len(unpaid_bounties) * 100)
                            user_data["exp"] = 0; user_data["level"] = max(1, user_data["level"] - 1)
                            user_data["streak"] = 0; user_data["blood_debt"] += penalty
                            user_data["failure_prob"] = min(100, user_data["failure_prob"] + 20)
                        user_data["last_login"] = today_str; user_data["cleared_yesterday"] = False
                        save_db(db)
                    
                    st.session_state.current_user = safe_email; st.rerun()
    else:
        safe_email = st.session_state.current_user
        u_data = db["users"][safe_email]
        st.error(f"⚔️ นักรบ: {u_data['username']}")
        st.info(f"🛡️ ฉายา: {get_title(u_data['level'])}")
        
        scars = len(db.get("dopamine_fails", {}).get(safe_email, []))
        st.markdown(f"🩻 **รอยแผลเป็นความพ่ายแพ้: {scars} รอย**")
        st.warning(f"🔥 สถิติไม่แพ้: {u_data['streak']} วัน")
        
        needs_save = False
        while u_data["exp"] >= 100:
            u_data["level"] += 1
            u_data["exp"] -= 100
            needs_save = True
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
            st.session_state.current_user = None; st.rerun()

if st.session_state.current_user is None:
    st.title("🧠 THE BRAIN WAR")
    st.info("👈 เลือกชื่อตัวเองแล้วกดปุ่ม 'เปิดสมอง!' เพื่อเข้าใช้งาน!")
    st.stop()

safe_email = st.session_state.current_user

for k in ["missions", "backlog", "dark_room", "anti_simp", "dopamine_fails", "excuses", "cookie_jar", "deadlines", "haters", "finance", "iron_habits", "exams", "beat_yesterday", "limit_breaks"]:
    if safe_email not in db[k] or db[k][safe_email] is None: 
        if k == "finance": db[k][safe_email] = {"goal_name": "ยังไม่ได้ตั้ง", "goal_amount": 0, "current": 0}
        elif k in ["exams", "beat_yesterday"]: db[k][safe_email] = {}
        else: db[k][safe_email] = []

user = db["users"][safe_email]
finance = db["finance"][safe_email]

# ===== 🚨 CHECK OVERDUE BACKLOG =====
overdue_count = 0
for task in db["backlog"][safe_email]:
    try:
        dl_date = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
        if dl_date < today_date and task.get("last_penalized") != today_str:
            overdue_count += 1
            task["last_penalized"] = today_str
    except: pass

if overdue_count > 0:
    user["failure_prob"] = min(100, user["failure_prob"] + (10 * overdue_count))
    user["blood_debt"] += (50 * overdue_count); user["in_cage"] = True
    save_db(db)
    st.error(f"🚨 ไอ้หน้าโง่! มึงมีงานดองเกินกำหนด {overdue_count} งาน! แท่นพิพากษายัดหนี้เลือดมึงแล้ว รีบไปเคลียร์ซะ!")

# ==========================================
# 🎯 ส่วนหัว: ปลุกพลัง & ระบบนับถอยหลังอนาคต (FUTURE COUNTDOWN)
# ==========================================
try: t_date = datetime.strptime(user["target_date"], "%Y-%m-%d").date()
except: t_date = today_date + timedelta(days=90)
days_left = (t_date - today_date).days

colTop1, colTop2, colTop3 = st.columns([1, 1, 3])
with colTop1:
    if st.button("🎰 วงล้อชดใช้กรรม\n(กูเริ่มขี้เกียจ)", type="primary", use_container_width=True):
        st.session_state.punishment_active = True
        st.session_state.punishment_task = random.choice(PUNISHMENTS); st.rerun()
with colTop2:
    if st.button("⚡ คาถาระเบิดพลัง\n(เรียกสติเดี่ยวนี้)", use_container_width=True):
        st.toast(f"🔊 ตื่นดิวะ! {random.choice(PUNISHMENTS)}", icon="🦍")
with colTop3:
    st.error(f"⏳ **นับถอยหลังชี้ชะตา:** {user.get('target_name', 'เป้าหมายสูงสุด')} ในอีก **{days_left}** วัน!")
    with st.popover("⚙️ ตั้งค่านับถอยหลัง"):
        new_t_name = st.text_input("เป้าหมายสูงสุด (เช่น 10ล้านวิว):", user.get("target_name", ""))
        new_t_date = st.date_input("วันกำหนดชี้ชะตา (Deadline ใหญ่):", t_date)
        if st.button("บันทึกเป้าหมายชี้ชะตา"):
            user["target_name"] = new_t_name; user["target_date"] = str(new_t_date)
            save_db(db); st.rerun()

if user.get("in_cage"): st.error("🚨 **มึงอยู่ในกรง!** วิดพื้นจ่ายหนี้เลือดซะ!")

# ==========================================
# 5. DUAL REALITY DASHBOARD
# ==========================================
st.divider()
if monk_mode:
    st.markdown("## 🧘‍♂️ MONK MODE ACTIVE: สมาธิขั้นสุด!")
    colLeft, colRight = st.columns([0.01, 1]) 
else: colLeft, colRight = st.columns(2)

with colLeft:
    if not monk_mode:
        st.markdown("## 🗑️ THE BITCH ZONE (ฝั่งขยะ)")
        st.warning(random.choice(LAZY_VOICES))
        st.metric("📉 โอกาสล้มเหลวในอนาคต", f"{user['failure_prob']}%")
            
        with st.form("excuse_form", clear_on_submit=True):
            exc_text = st.text_input("ข้ออ้างขยะๆ วันนี้คืออะไร?:")
            if st.form_submit_button("บันทึกข้ออ้าง"):
                if exc_text:
                    db["excuses"][safe_email].append({"วันที่": today_str, "ข้ออ้าง": exc_text})
                    user["failure_prob"] = min(100, user["failure_prob"] + 10); save_db(db); st.rerun()
                    
        if st.button("💀 แท่นประหาร: กูแพ้ให้สิ่งเร้าขยะ"):
            db["dopamine_fails"][safe_email].append(today_str)
            user["exp"] = 0; user["blood_debt"] += 50; user["in_cage"] = True
            user["failure_prob"] = min(100, user["failure_prob"] + 20); save_db(db); st.rerun()

        st.markdown("### 🩸 บัญชีแค้น (THE HATER'S WALL)")
        with st.form("hater_form", clear_on_submit=True):
            h_text = st.text_input("คำดูถูกที่มึงเจอ:")
            if st.form_submit_button("ฝังความแค้น"):
                if h_text: db["haters"][safe_email].append(h_text); save_db(db); st.rerun()
        if db["haters"][safe_email]: st.error(f"🤬 คำดูถูก: \"{random.choice(db['haters'][safe_email])}\"")

with colRight:
    st.markdown("## ⚔️ THE SAVAGE ZONE (นักรบฝั่งขวา)")
    st.success(random.choice(SAVAGE_VOICES))
    
    tab_missions, tab_habits, tab_backlog, tab_cookie, tab_academic = st.tabs(["🔥 ภารกิจวันนี้", "⛓️ วินัยเหล็ก", "📝 สมุดจดงาน", "🍪 โหลคุกกี้", "📚 ลานประลองปัญญา"])
    
    # ----------------------------------------------------
    # TAB 1: ภารกิจวันนี้ (Daily Missions)
    # ----------------------------------------------------
    with tab_missions:
        st.markdown("### 🪵 The Daily Siege (ตารางรบวันนี้)")
        with st.expander("➕ เพิ่มงานด่วนวันนี้ (ไม่ผ่านสมุด)"):
            with st.form("mission_form", clear_on_submit=True):
                m_name = st.text_input("ชื่อภารกิจ:")
                m_is_boss = st.checkbox("💀 ตั้งเป็น THE BOSS FIGHT (งานกลืนกบประจำวัน! หนี=หนี้เลือด x3)")
                m_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด (คอขาดบาดตาย)", "🔥 งานฉุกเฉิน / Special Event", "🟡 ปานกลาง (ต้องเสร็จ)", "🟢 ชิลๆ (ทำตอนว่าง)"])
                m_bounty = st.checkbox("⚔️ ตั้งค่าหัว! (เดิมพันศักดิ์ศรี: พลาดโดนหนี้ 100 ที)")
                st.caption("💡 ทริค: \n- **ถ้าพิมพ์งานย่อย:** จะเป็น **[งานใหญ่]** (มึงสับซุงแค่วันละข้อก็รอดพิพากษา)\n- **ถ้าปล่อยว่าง:** จะเป็น **[ม้วนเดียวจบ]** (มึงต้องทำเสร็จภายในวันนี้ ไม่งั้นตาย!)")
                m_subtasks_text = st.text_area("🔪 สับท่อนซุง (ใส่ชื่อย่อยทีละบรรทัด, ไม่บังคับ):")
                m_deadline = st.date_input("วันกำหนดส่ง (Deadline ถ้ามี):")
                
                if st.form_submit_button("เพิ่มภารกิจ"):
                    if m_name:
                        subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in m_subtasks_text.split('\n') if s.strip()]
                        db["missions"][safe_email].append({
                            "id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": m_name, 
                            "ประเภท": m_type, "bounty": m_bounty, "is_boss": m_is_boss,
                            "custom_order": 99, "is_queued": False, "skip_today_date": "",
                            "subtasks": subtasks, "เสร็จแล้ว": False, "รอตรวจ": False,
                            "deadline": str(m_deadline)
                        })
                        save_db(db); st.rerun()
                    
        raw_active = [m for m in db["missions"][safe_email] if not m.get("เสร็จแล้ว")]
        todo_missions = [m for m in raw_active if not m.get("รอตรวจ", False)]
        pending_missions = [m for m in raw_active if m.get("รอตรวจ", False)]
        
        todo_missions.sort(key=lambda x: (0 if x.get("is_boss") else 1, x.get("custom_order", 99), get_priority_score(x.get("ประเภท", ""))))
        
        needs_queueing = [m for m in todo_missions if not m.get("is_queued", False)]
        
        if needs_queueing:
            with st.expander("🔢 ⚡ ทัพหนุนมาใหม่: จัดลำดับงานที่ยังไม่เข้าคิว (ล็อกแล้วห้ามเปลี่ยน!)", expanded=True):
                with st.form("lock_order_form"):
                    st.write("มึงมีงานใหม่ที่เพิ่งแอดเข้ามา พิมพ์เลขคิวแทรกเข้าไปซะ (เลขน้อยขึ้นก่อน) เสร็จแล้วกดล็อกชะตากรรม!")
                    updated_orders = {}
                    for m in needs_queueing:
                        is_boss_str = "💀 [BOSS] " if m.get("is_boss") else ""
                        updated_orders[m["id"]] = st.number_input(f"กำหนดคิวแทรก: {is_boss_str}{m['ภารกิจ']}", min_value=1, value=int(m.get("custom_order", 99)), key=f"setup_ord_{m['id']}")
                    
                    if st.form_submit_button("🔒 ยืนยันคิวงานใหม่! (ห้ามตระบัดสัตย์)"):
                        for m in db["missions"][safe_email]:
                            if m["id"] in updated_orders:
                                m["custom_order"] = updated_orders[m["id"]]
                                m["is_queued"] = True
                        save_db(db); st.success("⚔️ ล็อกคิวงานใหม่เรียบร้อย!"); st.rerun()

        if todo_missions:
            for m in todo_missions:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6]) 
                    
                    task_mode_badge = "🔪 **[งานใหญ่]**" if m.get("subtasks") else "⚡ **[ม้วนเดียวจบ]**"
                    is_bounty = " ⚔️[เดิมพัน]" if m.get("bounty") else ""
                    is_boss = " 💀 **[BOSS]**" if m.get("is_boss") else ""
                    
                    order_num = m.get("custom_order", 99)
                    order_badge = f" 🔢 [คิวที่ {order_num}]" if m.get("is_queued", False) else " 🔢 [ยังไม่ระบุคิว]"
                    
                    # ⏰ คำนวณความศักดิ์สิทธิ์ของ Deadline (นับถอยหลังเสมอโลกไม่เคยหยุดรอ)
                    is_overdue = False
                    deadline_badge = ""
                    if m.get("deadline"):
                        try:
                            dl_date = datetime.strptime(m["deadline"], "%Y-%m-%d").date()
                            days_left_task = (dl_date - today_date).days
                            if days_left_task > 0: deadline_badge = f" ⏳ (เหลือ {days_left_task} วัน)"
                            elif days_left_task == 0: deadline_badge = f" 🚨 **(วันสุดท้าย!)**"
                            else: 
                                deadline_badge = f" 💀 **(เลยกำหนด {-days_left_task} วัน)**"
                                is_overdue = True # บันทึกสถานะเลยเวลาส่ง
                        except: pass

                    # 🔥 ป้ายกำกับแช่แข็งคุมทัพฉุกเฉิน
                    is_frozen = m.get("skip_today_date") == today_str
                    
                    if is_frozen:
                        if is_overdue: frozen_badge = " ❄️🚨 [เกราะแตก! เลยกำหนดส่งแล้ว]"
                        else: frozen_badge = " ❄️ [แช่แข็งหนีภัยฉุกเฉิน]"
                    else: frozen_badge = ""

                    c1.write(f"**{m.get('ประเภท','')}** | {task_mode_badge}{is_boss}{is_bounty} {m['ภารกิจ']}{order_badge}{deadline_badge}{frozen_badge}")
                    
                    all_done = True
                    has_today_progress = False
                    
                    if m.get("subtasks"):
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
                                    if diff_days == 1: label += " 🔒 (ผนึกเมื่อวานนี้)"
                                    elif diff_days > 1: label += f" 🔒 (ผนึกเมื่อ {diff_days} วันที่แล้ว)"
                                    else: label += f" 🔒 (ผนึกแล้ว)"
                                except: label += f" 🔒 (ผนึกเมื่อ: {done_date})"
                                
                            # 🛡️ เงื่อนไข: ถ้าแช่แข็งชั่วคราวและยังไม่เลยเดดไลน์ จะบล็อกปุ่มติ๊กไว้ แต่ถ้าเลยเดดไลน์แล้วเกราะแตก! ต้องปลดเพื่อให้ทำงานแก้ตัวได้!
                            can_interact = not is_locked and (not is_frozen or is_overdue)
                            checked = st.checkbox(label, value=is_done, disabled=not can_interact, key=f"st_{m['id']}_{i}")
                            
                            if can_interact:
                                if checked != is_done:
                                    m["subtasks"][i]["done"] = checked
                                    m["subtasks"][i]["done_date"] = today_str if checked else ""
                                    save_db(db); st.rerun()
                            
                            if m["subtasks"][i].get("done_date", "") == today_str:
                                has_today_progress = True
                                
                        all_done = all(stask.get("done", False) for stask in m["subtasks"])

                        if is_frozen:
                            if is_overdue: st.markdown("🔴 *⚠️ [เกราะแตก! แช่แข็งไร้ผลเพราะงานเลยเดดไลน์แล้ว มึงโดนพิพากษาแน่!]*")
                            else: st.markdown("❄️ *[วิชานี้เปิดเกราะแช่แข็งฉุกเฉิน รอดพ้นศาลเตี้ยคืนนี้]*")
                        elif has_today_progress: st.markdown("🟢 *[รอดตาย! วันนี้มึงสับงานย่อยแล้ว]*")
                        else: st.markdown("🔴 *⚠️ [วิกฤต! วันนี้ยังไม่ขยับเลย ระวังแท่นพิพากษา!]*")
                    else:
                        if is_frozen:
                            if is_overdue: st.markdown("🔴 *⚠️ [เกราะแตก! แช่แข็งไร้ผลเพราะงานเลยเดดไลน์แล้ว]*")
                            else: st.markdown("❄️ *[งานนี้เปิดเกราะแช่แข็งฉุกเฉิน รอดพ้นศาลเตี้ยคืนนี้]*")
                        else: st.caption("⚡ *งานนี้ไม่มีงานย่อย ต้องกดปุ่ม [✅ สำเร็จ] ม้วนเดียวให้จบภายในวันนี้!*")
                        all_done = True 

                    # ❄️ แผงควบคุมระบบแช่แข็งหนีภัยสงคราม
                    if is_frozen:
                        if c4.button("🔥 ปลดล็อก", key=f"unfrz_{m['id']}", use_container_width=True):
                            m["skip_today_date"] = ""
                            save_db(db); st.rerun()
                    else:
                        if c4.button("❄️ เลื่อนฉุกเฉิน", key=f"frz_{m['id']}", use_container_width=True, help="แช่แข็งงานนี้วันนี้ชั่วคราวเนื่องจากติดภารกิจโครงงานฉุกเฉิน! รอดโทษประจำวัน (ยกเว้นงานที่เลยเดดไลน์แล้ว)"):
                            m["skip_today_date"] = today_str
                            save_db(db); st.rerun()

                    # ปุ่มปิดภารกิจ (จะทำงานได้ก็ต่อเมื่อไม่ได้โดนแช่แข็งแบบปกติ)
                    if all_done and (not is_frozen or is_overdue):
                        if c2.button("✅ สำเร็จ", key=f"m_{m['id']}"):
                            m["เสร็จแล้ว"] = True
                            save_db(db); st.balloons(); st.rerun()
                        if c3.button("📤 ส่ง/รอตรวจ", key=f"pend_{m['id']}"):
                            m["รอตรวจ"] = True
                            save_db(db); st.rerun()
                    else:
                        if is_frozen and not is_overdue: c2.caption("❄️ แช่แข็งชั่วคราว")
                        else: c2.caption("🔒 งานย่อยยังคาอยู่")
                        
                    if c5.button("🗑️", key=f"del_m_{m['id']}"):
                        db["missions"][safe_email].remove(m)
                        save_db(db); st.rerun()
        else: st.success("✅ วันนี้เคลียร์ภารกิจหลักหมดแล้ว เยี่ยมมากไอ้เสือ!")

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
                    exp_gain = 40 if (get_priority_score(m.get("ประเภท", "")) == 1 or m.get("bounty")) else 20
                    if m.get("is_boss"): exp_gain = 100
                    elif m.get("bounty") and get_priority_score(m.get("ประเภท", "")) == 1: exp_gain = 80 
                    user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - 5)
                    save_db(db); st.balloons(); st.rerun()
                if c3.button("⏪ ดึงกลับมาทำ", key=f"revert_{m['id']}"):
                    m["รอตรวจ"] = False
                    save_db(db); st.rerun()

    # ----------------------------------------------------
    # TAB 2: วินัยเหล็ก (THE IRON HABITS)
    # ----------------------------------------------------
    with tab_habits:
        st.markdown("### ⛓️ THE IRON HABITS (วินัยเหล็กรายวัน)")
        st.info("สิ่งที่มึงต้องทำทุกวัน ห้ามมีข้ออ้าง พลาด 1 ครั้ง Streak ขาดทันที!")
        with st.form("habit_form", clear_on_submit=True):
            h_name = st.text_input("สร้างวินัยเหล็กใหม่ (เช่น ตื่นตี 5, อ่านหนังสือ 10 หน้า):")
            if st.form_submit_button("เพิ่มวินัยเหล็ก"):
                if h_name:
                    db["iron_habits"][safe_email].append({"id": str(uuid.uuid4()), "name": h_name, "last_done_date": ""})
                    save_db(db); st.rerun()
                    
        if db["iron_habits"][safe_email]:
            for h in db["iron_habits"][safe_email]:
                c1, c2, c3 = st.columns([5, 3, 1])
                c1.write(f"⛓️ **{h['name']}**")
                if h.get("last_done_date") == today_str:
                    c2.success("✅ ทำแล้ววันนี้")
                else:
                    if c2.button("🔥 กูทำสำเร็จ!", key=f"h_done_{h['id']}"):
                        h["last_done_date"] = today_str
                        user["exp"] += 5
                        save_db(db); st.balloons(); st.rerun()
                if c3.button("🗑️", key=f"del_h_{h['id']}"):
                    db["iron_habits"][safe_email].remove(h)
                    save_db(db); st.rerun()
        else:
            st.success("ยังไม่มีวินัยเหล็ก! สร้างมันขึ้นมาซะ!")

    # ----------------------------------------------------
    # TAB 3: สมุดจดงาน (Backlog)
    # ----------------------------------------------------
    with tab_backlog:
        st.markdown("### 📝 สมุดจดงาน (Task Backlog)")
        with st.form("backlog_form", clear_on_submit=True):
            b_name = st.text_input("หัวข้องาน/ไอเดียยูทูป:")
            b_detail = st.text_area("รายละเอียด/Note (ถ้ามี):")
            b_subtasks_text = st.text_area("🔪 ซอยงานย่อย (Enter ขึ้นบรรทัดใหม่, ไม่บังคับ):")
            b_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด (คอขาดบาดตาย)", "🔥 งานฉุกเฉิน / Special Event", "🟡 ปานกลาง (ต้องเสร็จ)", "🟢 ชิลๆ (ทำตอนว่าง)"])
            b_deadline = st.date_input("วันกำหนดส่ง (Deadline):")
            
            if st.form_submit_button("💾 บันทึกลงสมุด"):
                if b_name:
                    b_subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in b_subtasks_text.split('\n') if s.strip()]
                    db["backlog"][safe_email].append({
                        "id": str(uuid.uuid4()), "ภารกิจ": b_name, "รายละเอียด": b_detail,
                        "subtasks": b_subtasks, "ประเภท": b_type, "deadline": str(b_deadline)
                    })
                    save_db(db); st.rerun()
                    
        if db["backlog"][safe_email]:
            for b_task in sorted(db["backlog"][safe_email], key=lambda x: x.get("deadline", "9999-12-31")):
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    
                    days_badge = ""
                    if b_task.get("deadline"):
                        try:
                            dl_date = datetime.strptime(b_task["deadline"], "%Y-%m-%d").date()
                            days_left_b = (dl_date - today_date).days
                            if days_left_b > 0: days_badge = f"⏳ เหลือ {days_left_b} วัน"
                            elif days_left_b == 0: days_badge = f"🚨 **วันสุดท้าย!**"
                            else: days_badge = f"💀 **เลยกำหนด {-days_left_b} วัน**"
                        except: pass

                    c1.write(f"**{b_task['ประเภท']}** | 📝 {b_task['ภารกิจ']}")
                    c1.caption(f"📅 Deadline: {b_task.get('deadline', '-')} ({days_badge}) | รายละเอียด: {b_task.get('รายละเอียด', '-')}")
                    
                    if c2.button("⚡ ดึงทำวันนี้", key=f"pull_{b_task['id']}", type="primary"):
                        db["missions"][safe_email].append({
                            "id": b_task["id"], "วันที่": today_str, "ภารกิจ": b_task["ภารกิจ"],
                            "ประเภท": b_task["ประเภท"], "bounty": False, "is_boss": False,
                            "custom_order": 99, "is_queued": False, "skip_today_date": "",
                            "deadline": b_task.get("deadline", ""),
                            "subtasks": b_task.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False
                        })
                        db["backlog"][safe_email].remove(b_task)
                        save_db(db); st.rerun()
                    
                    if c2.button("🗑️ ลบ", key=f"del_b_{b_task['id']}"):
                        db["backlog"][safe_email].remove(b_task); save_db(db); st.rerun()
        else: st.success("สมุดจดว่างเปล่า!")

    # ----------------------------------------------------
    # TAB 4: โหลคุกกี้ (Cookie Jar) 🍪
    # ----------------------------------------------------
    with tab_cookie:
        st.markdown("### 🍪 THE COOKIE JAR (โหลเก็บความภูมิใจ)")
        st.info("เวลาที่มึงท้อ หมดไฟ ให้กลับมาเปิดโหลนี้ดูว่ามึงเคยชนะอะไรมาบ้าง!")
        with st.form("cookie_form", clear_on_submit=True):
            win_text = st.text_input("วันนี้มึงชนะใจตัวเองเรื่องอะไรได้บ้าง? (เรื่องเล็กๆ ก็ได้):")
            if st.form_submit_button("เก็บชัยชนะลงโหล!"):
                if win_text:
                    db["cookie_jar"][safe_email].append({"วันที่": today_str, "ชัยชนะ": win_text})
                    user["exp"] += 5
                    save_db(db); st.success("✅ เก็บชัยชนะลงโหลเรียบร้อย! มึงแม่งสุดยอด!"); st.rerun()
        
        if db["cookie_jar"][safe_email]:
            st.markdown("**ความสำเร็จล่าสุดของมึง:**")
            for c in reversed(db["cookie_jar"][safe_email][-5:]):
                st.success(f"🏆 **[{c['วันที่']}]** {c['ชัยชนะ']}")

    # ----------------------------------------------------
    # TAB 5: ลานประลองปัญญา (EXAM & BEAT YESTERDAY) 📚
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
                            user["exp"] += 30
                            st.success(f"🔥 โคตรเถื่อน! มึงเก่งขึ้นกว่าครั้งที่แล้ว ({last_score} -> {e_score}) รับ 30 EXP!")
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
                        user["exp"] += 20
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
                user["exp"] += 50
                user["failure_prob"] = max(0, user["failure_prob"] - 15)
                save_db(db)
                st.balloons()
                st.success("🦍 พลังใจมึงมันระดับสัตว์ประหลาด! เอา EXP ไป 50 และลดโอกาสล้มเหลวลง 15%!")
            else:
                st.warning("วันนี้มึงทะลุขีดจำกัดไปแล้ว! เก็บแรงไว้ลุยพรุ่งนี้บ้างไอ้บ้าพลัง!")

    st.divider()
    st.markdown("### 💰 คลังสมบัตินักรบ (ทุนสร้างฝัน)")
    c_fin1, c_fin2 = st.columns([2, 1])
    with c_fin1:
        st.write(f"**เป้าหมาย:** {finance.get('goal_name', 'ยังไม่ตั้ง')}")
        cur = finance.get('current', 0); tgt = finance.get('goal_amount', 1)
        prog = max(0.0, min(cur / tgt, 1.0)) if tgt > 0 else 0.0
        st.progress(prog, text=f"มีแล้ว: {cur} / {tgt} บาท ({int(prog*100)}%)")
    with c_fin2:
        with st.popover("⚙️ จัดการเงิน"):
            new_g_name = st.text_input("ชื่อเป้าหมาย:", value=finance.get('goal_name', ''))
            new_g_amt = st.number_input("จำนวนเงินเป้าหมาย:", value=finance.get('goal_amount', 0))
            if st.button("ตั้งเป้าหมาย"):
                finance['goal_name'] = new_g_name; finance['goal_amount'] = new_g_amt; save_db(db); st.rerun()
            st.divider()
            add_amt = st.number_input("บวก/ลด เงิน:", value=0)
            if st.button("บันทึกเงิน"):
                finance['current'] += add_amt; save_db(db); st.rerun()

# ==========================================
# 6. หนี้เลือด & THE JUDGMENT FEED (แท่นพิพากษาไร้ปรานี)
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
            user["blood_debt"] = 0; user["in_cage"] = False; save_db(db); st.rerun()

st.divider()
st.markdown("<h2>⚖️ THE JUDGMENT FEED (พิพากษาก่อนนอน)</h2>", unsafe_allow_html=True)
if user.get("ambush_task", "") != "":
    st.error(f"🚨 **โดนซุ่มโจมตี!** คำสั่ง: **{user['ambush_task']}**")
    if st.button("🔥 กูทำเสร็จแล้ว!"):
        user["ambush_task"] = ""; user["exp"] += 20; save_db(db); st.rerun()
elif user.get("cleared_yesterday"): st.success("🔥 พิพากษาเสร็จสิ้น! มึงรอดไปได้อีกหนึ่งวัน!")
else:
    active_for_judgment = []
    for m in db["missions"][safe_email]:
        if not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False):
            # 🔥 ตรรกะใหม่: ถ้าโดนแช่แข็งวันนี้ ให้รอดสิทธิ์พิพากษาประจำวัน... "ยกเว้น" ว่ามันจะเลยกำหนดส่ง (Overdue) แล้ว!
            if m.get("skip_today_date") == today_str:
                is_task_overdue = False
                if m.get("deadline"):
                    try:
                        dl_dt = datetime.strptime(m["deadline"], "%Y-%m-%d").date()
                        if dl_dt < today_date: is_task_overdue = True # เลยกำหนดส่งจริง
                    except: pass
                
                if not is_task_overdue:
                    continue # ยังไม่เลยเดดไลน์ ให้รอดตัวไปโฟกัสงานโครงงานฉุกเฉินได้!
                
            if m.get("subtasks"):
                has_today_progress = any(stask.get("done", False) and stask.get("done_date", "") == today_str for stask in m["subtasks"])
                if not has_today_progress: active_for_judgment.append(m)
            else:
                active_for_judgment.append(m)

    incomplete_habits = [h for h in db["iron_habits"][safe_email] if h.get("last_done_date") != today_str]
    incomplete_bosses = [m for m in active_for_judgment if m.get("is_boss")]

    if incomplete_bosses:
        st.error("💀 ไอ้สวะ! มึงดองงาน BOSS FIGHT! แท่นพิพากษาสั่งลงโทษหนัก!")
        if st.button("🩸 ยอมรับความกาก (รับหนี้เลือด 300 ที!)"):
            user["blood_debt"] += 300
            user["failure_prob"] = min(100, user["failure_prob"] + 30)
            user["in_cage"] = True
            user["cleared_yesterday"] = True
            save_db(db); st.rerun()
            
    elif active_for_judgment or incomplete_habits: 
        st.error("❌ มึงกำลังหักหลังตัวเอง! ศาลเตี้ยพบงาน/วินัยที่มึงละทิ้งในวันนี้:")
        for m in active_for_judgment:
            # เพิ่ม Badge แจ้งให้ชัดเจนว่าโดนทำโทษเพราะเลยเวลาส่ง
            is_overdue_check = False
            if m.get("deadline"):
                try:
                    if datetime.strptime(m["deadline"], "%Y-%m-%d").date() < today_date: is_overdue_check = True
                except: pass
            
            if is_overdue_check: mode = "🚨 เกราะแตก! เลยกำหนดส่งแล้ว ต่อให้แช่แข็งก็ไม่รอด!"
            else: mode = "🔪 งานใหญ่ (มึงลืมสับซุง)" if m.get("subtasks") else "⚡ ม้วนเดียวจบ (มึงดองข้ามวัน)"
            st.write(f"👉 **{m['ภารกิจ']}** [{mode}]")
        for h in incomplete_habits:
            st.write(f"👉 **{h['name']}** [⛓️ วินัยเหล็ก]")
            
        st.warning("กลับไปจัดการให้จบซะ หรือถ้ามึงมีทัพเสริมฉุกเฉินเข้ามาชนจริง ให้กดยอมรับหนี้ หรือกดแช่แข็งงานข้างบนซะ!")
        
        if st.button("🩸 ยอมรับความกาก (ทิ้งงานวันนี้ รับหนี้เลือด 50 ที/งานที่ดอง)"):
            penalty_count = len(active_for_judgment) + len(incomplete_habits)
            user["blood_debt"] += (50 * penalty_count)
            user["failure_prob"] = min(100, user["failure_prob"] + (10 * penalty_count))
            user["in_cage"] = True
            user["cleared_yesterday"] = True 
            save_db(db); st.rerun()
            
    elif user.get("in_cage") or user.get("blood_debt", 0) > 0: 
        st.error("❌ มึงติดหนี้เลือดอยู่ ชดใช้กรรมซะก่อนถึงจะปิดวันได้!")
    else:
        st.warning("วันนี้มึงใส่เต็ม 100% หรือมึงใช้พลังแค่ 40%?")
        j_col1, j_col2 = st.columns(2)
        with j_col1:
            if st.button("📉 สู้ไม่เต็มที่ (แค่ 40%)"):
                user["exp"] -= 30; user["cleared_yesterday"] = True
                user["failure_prob"] = min(100, user["failure_prob"] + 10); save_db(db); st.rerun()
        with j_col2:
            if st.button("🔥 กูใช้พลังทั้งหมด 100%!"):
                if random.random() < 0.2: user["ambush_task"] = random.choice(AMBUSH_TASKS)
                else: user["cleared_yesterday"] = True; user["streak"] += 1; user["exp"] += 25
                save_db(db); st.rerun()

# ==========================================
# 8. 📜 พงศาวดารความทรงจำ (HISTORY LOG) อัปเกรด
# ==========================================
st.divider()
if not monk_mode:
    st.markdown("## 📜 พงศาวดารความทรงจำ (HISTORY LOG)")
    tab1, tab2, tab3, tab4 = st.tabs(["🍪 คลังแสง (ความสำเร็จ)", "🤡 บัญชีหนังหมา (ข้ออ้าง)", "🪵 บันทึกการแบกซุง (ตาราง)", "📊 BATTLE ANALYTICS"])

    with tab1:
        if db["cookie_jar"].get(safe_email):
            for item in reversed(db["cookie_jar"][safe_email]): 
                st.success(f"🏆 **[{item.get('วันที่', 'ไม่ระบุ')}]** : {item.get('ชัยชนะ', '')}")
        else: st.write("ยังไม่มีความสำเร็จอะไรเลย ไปทำซะ!")

    with tab2:
        if db["excuses"].get(safe_email):
            for item in reversed(db["excuses"][safe_email]): 
                st.error(f"🤡 **[{item.get('วันที่', 'ไม่ระบุ')}]** : {item.get('ข้ออ้าง', '')}")
        else: st.write("ดีมาก! ยังไม่มีข้ออ้างขยะๆ ให้รกหูรกตา!")

    with tab3:
        if db["missions"].get(safe_email):
            mission_history = []
            for item in reversed(db["missions"][safe_email]):
                if item.get("เสร็จแล้ว"): status = "✅ เสร็จแล้ว"
                elif item.get("รอตรวจ", False): status = "⏳ รอตรวจ"
                else: status = "❌ ยังดองอยู่"
                
                mission_history.append({
                    "วันที่เริ่ม": item.get('วันที่', '-'),
                    "ภารกิจ": item.get('ภารกิจ', ''),
                    "ความสำคัญ": item.get('ประเภท','-'),
                    "BOSS?": "💀" if item.get("is_boss") else "-",
                    "เดิมพัน?": "⚔️" if item.get("bounty") else "-",
                    "สถานะ": status
                })
            df_missions = pd.DataFrame(mission_history)
            st.dataframe(df_missions, use_container_width=True, hide_index=True)
        else: st.write("ยังไม่มีประวัติการแบกซุงเลยไอ้ลูกหมา ไปหางานทำซะ!")

    with tab4:
        all_m = db["missions"].get(safe_email, [])
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
