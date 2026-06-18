import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import requests
import uuid
import hashlib
import random

# ==========================================
# 1. ตั้งค่าระบบ (THE IMMORTAL SOUL V.22 - THE ORDER OF DOOM)
# ==========================================
st.set_page_config(page_title="THE BRAIN WAR", layout="wide", page_icon="🧠")

# ⚠️ ลิงก์ Firebase ของมึง
FIREBASE_URL = "https://mytaskpro-f7328-default-rtdb.asia-southeast1.firebasedatabase.app/" 

today_date = date.today()
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
                        user_data["order_locked"] = False # ขึ้นวันใหม่ ปลดล็อกแผนรบให้ตั้งใหม่
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
        st.progress(u_data["exp"] / 100, text=f"Lv.{u_data['level']} | EXP: {u_data['exp']}/100")
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
valid_backlog = []
for task in db["backlog"][safe_email]:
    try:
        dl_date = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
        if dl_date < today_date: overdue_count += 1
        else: valid_backlog.append(task)
    except: valid_backlog.append(task)

if overdue_count > 0:
    db["backlog"][safe_email] = valid_backlog
    user["failure_prob"] = min(100, user["failure_prob"] + (10 * overdue_count))
    user["blood_debt"] += (50 * overdue_count); user["in_cage"] = True
    save_db(db)
    st.error(f"🚨 ไอ้หน้าโง่! ดองงานจนเลยเวลาไป {overdue_count} งาน! ระบบยัดหนี้เลือดมึงแล้ว!")

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
                m_name = st.text_input("ท่อนซุงที่ต้องแบกวันนี้:")
                m_is_boss = st.checkbox("💀 ตั้งเป็น THE BOSS FIGHT (งานกลืนกบประจำวัน! หนี=หนี้เลือด x3)")
                m_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด (คอขาดบาดตาย)", "🔥 งานฉุกเฉิน / Special Event", "🟡 ปานกลาง (ต้องเสร็จ)", "🟢 ชิลๆ (ทำตอนว่าง)"])
                m_bounty = st.checkbox("⚔️ ตั้งค่าหัว! (เดิมพันศักดิ์ศรี: พลาดโดนหนี้ 100 ที)")
                m_subtasks_text = st.text_area("🔪 สับท่อนซุง (ใส่ชื่อย่อยทีละบรรทัด, ไม่บังคับ):")
                
                if st.form_submit_button("เพิ่มภารกิจ"):
                    if m_name:
                        subtasks = [{"name": s.strip(), "done": False} for s in m_subtasks_text.split('\n') if s.strip()]
                        db["missions"][safe_email].append({
                            "id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": m_name, 
                            "ประเภท": m_type, "bounty": m_bounty, "is_boss": m_is_boss,
                            "custom_order": 99, # ค่าเริ่มต้นคิวท้ายสุด
                            "subtasks": subtasks, "เสร็จแล้ว": False, "รอตรวจ": False
                        })
                        save_db(db); st.rerun()
                    
        raw_active = [m for m in db["missions"][safe_email] if not m.get("เสร็จแล้ว")]
        todo_missions = [m for m in raw_active if not m.get("รอตรวจ", False)]
        pending_missions = [m for m in raw_active if m.get("รอตรวจ", False)]
        
        # เรียงลำดับตาม: Boss ก่อน -> ลำดับตัวเลขแผนรบ (custom_order) -> ระดับความสำคัญเดิม
        todo_missions.sort(key=lambda x: (0 if x.get("is_boss") else 1, x.get("custom_order", 99), get_priority_score(x.get("ประเภท", ""))))
        
        # 🔥 ฟีเจอร์ "จัดลำดับคิวแผนรบและสั่งล็อกตาย"
        if todo_missions:
            if not user.get("order_locked", False):
                with st.expander("🔢 ⚡ วางแผนทัพ: จัดลำดับการรบวันนี้ (ล็อกแล้วห้ามแก้ไข!)"):
                    with st.form("lock_order_form"):
                        st.write("ถ้างานมันเยอะจนไม่รู้จะเริ่มทำอะไรก่อน พิมพ์เลขคิวรันให้ตัวเองซะ (เลขน้อยขึ้นก่อน เช่น 1, 2, 3...) เสร็จแล้วกดล็อกชะตากรรม!")
                        updated_orders = {}
                        for m in todo_missions:
                            is_boss_str = "💀 [BOSS] " if m.get("is_boss") else ""
                            updated_orders[m["id"]] = st.number_input(f"กำหนดคิวของภารกิจ: {is_boss_str}{m['ภารกิจ']}", min_value=1, value=int(m.get("custom_order", 99)), key=f"setup_ord_{m['id']}")
                        
                        if st.form_submit_button("🔒 ล็อกแผนการรบวันนี้! (ห้ามตระบัดสัตย์)"):
                            for m in db["missions"][safe_email]:
                                if m["id"] in updated_orders:
                                    m["custom_order"] = updated_orders[m["id"]]
                            user["order_locked"] = True
                            save_db(db); st.success("⚔️ ล็อกคิวแผนรบเรียบร้อย! ไม่มีสิทธิ์แก้ไขอีก ไปแบกซุงตามหน้าที่ซะไอ้เสือ!"); st.rerun()
            else:
                st.info("🔒 **ลำดับแผนการรบวันนี้ถูกล็อกตายด้วยวินัยเหล็กแล้ว!** ห้ามมึงโกง ห้ามมึงสลับคิว ลุยตามนี้!")

        # แสดงรายการภารกิจหลัก
        if todo_missions:
            for m in todo_missions:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([5, 2, 2, 0.6]) 
                    is_bounty = "⚔️[เดิมพัน] " if m.get("bounty") else ""
                    is_boss = "💀 **[BOSS FIGHT]** " if m.get("is_boss") else ""
                    
                    # แสดงป้ายลำดับคิวแบบล็อกตาย (ถ้าตั้งค่าแล้ว)
                    order_num = m.get("custom_order", 99)
                    order_badge = f" 🔢 [คิวที่ {order_num}]" if order_num != 99 else " 🔢 [ยังไม่ระบุคิว]"
                    
                    c1.write(f"**{m.get('ประเภท','')}** | {is_boss}{is_bounty}{m['ภารกิจ']}{order_badge}")
                    
                    all_done = True
                    if m.get("subtasks"):
                        st.caption("🔪 งานย่อย (ทำอย่างน้อย 1 อย่างรอดพิพากษาคืนนี้ | ล็อคปุ่มสำเร็จจนกว่าจะครบทั้งหมด):")
                        for i, stask in enumerate(m["subtasks"]):
                            checked = st.checkbox(stask["name"], value=stask["done"], key=f"st_{m['id']}_{i}")
                            if checked != stask["done"]:
                                m["subtasks"][i]["done"] = checked
                                save_db(db); st.rerun()
                        all_done = all(stask["done"] for stask in m["subtasks"])

                    if all_done:
                        if c2.button("✅ สำเร็จ", key=f"m_{m['id']}"):
                            m["เสร็จแล้ว"] = True
                            exp_gain = 40 if (get_priority_score(m.get("ประเภท", "")) == 1 or m.get("bounty")) else 20
                            if m.get("is_boss"): exp_gain = 100
                            elif m.get("bounty") and get_priority_score(m.get("ประเภท", "")) == 1: exp_gain = 80 
                            user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - 5)
                            if user["exp"] >= 100: user["level"] += 1; user["exp"] -= 100
                            save_db(db); st.balloons(); st.rerun()
                        
                        if c3.button("📤 ส่ง/รอตรวจ", key=f"pend_{m['id']}"):
                            m["รอตรวจ"] = True
                            save_db(db); st.rerun()
                    else:
                        c2.caption("🔒 งานใหญ่ยังล็อคอยู่")
                        
                    if c4.button("🗑️", key=f"del_m_{m['id']}"):
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
                    if user["exp"] >= 100: user["level"] += 1; user["exp"] -= 100
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
                    b_subtasks = [{"name": s.strip(), "done": False} for s in b_subtasks_text.split('\n') if s.strip()]
                    db["backlog"][safe_email].append({
                        "id": str(uuid.uuid4()), "ภารกิจ": b_name, "รายละเอียด": b_detail,
                        "subtasks": b_subtasks, "ประเภท": b_type, "deadline": str(b_deadline)
                    })
                    save_db(db); st.rerun()
                    
        if db["backlog"][safe_email]:
            for b_task in sorted(db["backlog"][safe_email], key=lambda x: x["deadline"]):
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"**{b_task['ประเภท']}** | 📝 {b_task['ภารกิจ']}")
                    c1.caption(f"📅 Deadline: {b_task['deadline']} | รายละเอียด: {b_task.get('รายละเอียด', '-')}")
                    
                    if c2.button("⚡ ดึงทำวันนี้", key=f"pull_{b_task['id']}", type="primary"):
                        db["missions"][safe_email].append({
                            "id": b_task["id"], "วันที่": today_str, "ภารกิจ": b_task["ภารกิจ"],
                            "ประเภท": b_task["ประเภท"], "bounty": False, "is_boss": False,
                            "custom_order": 99,
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
        prog = min(cur / tgt, 1.0) if tgt > 0 else 0
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
# 6. หนี้เลือด & THE JUDGMENT FEED (ระบบพิพากษาอัปเกรด)
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
            # 💡 ระบบเช็คงานย่อย: ติ๊กเสร็จอย่างน้อย 1 ข้อ = รอดตาย! ไม่โดนพิพากษาปรับแพ้
            if m.get("subtasks"):
                has_progress = any(stask.get("done", False) for stask in m["subtasks"])
                if has_progress:
                    continue 
            active_for_judgment.append(m)

    incomplete_bosses = [m for m in active_for_judgment if m.get("is_boss")]
    incomplete_habits = [h for h in db["iron_habits"][safe_email] if h.get("last_done_date") != today_str]

    if incomplete_bosses:
        st.error("💀 ไอ้สวะ! มึงดองงาน BOSS FIGHT! แท่นพิพากษาสั่งลงโทษหนัก!")
        if st.button("🩸 ยอมรับความกาก (รับหนี้เลือด 300 ที!)"):
            user["blood_debt"] += 300
            user["failure_prob"] = min(100, user["failure_prob"] + 30)
            user["in_cage"] = True
            user["cleared_yesterday"] = True
            save_db(db); st.rerun()
    elif active_for_judgment: 
        st.error("❌ มึงกำลังหักหลังตัวเอง! ภารกิจวันนี้มึงยังทำไม่เสร็จ! (หรืองานย่อยมึงยังไม่ได้ขยับทำเลยสักข้อ!)")
    elif incomplete_habits:
        st.error(f"⛓️ วินัยเหล็กมึงขาด! มึงยังไม่ได้ทำ: " + ", ".join([h['name'] for h in incomplete_habits]))
        st.warning("กลับไปแท็บ '⛓️ วินัยเหล็ก' แล้วไปทำให้เสร็จซะ ถึงจะปิดวันได้!")
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
                save_db(db); rerun()

# ==========================================
# 8. 📜 พงศาวดารความทรงจำ (HISTORY LOG)
# ==========================================
st.divider()
if not monk_mode:
    st.markdown("## 📜 พงศาวดารความทรงจำ (HISTORY LOG)")
    tab1, tab2, tab3, tab4 = st.tabs(["🍪 คลังแสง (ความสำเร็จ)", "🤡 บัญชีหนังหมา (ข้ออ้าง)", "🪵 ภารกิจทั้งหมด", "📊 ดัชนีวินัย (สถิติ)"])

    with tab1:
        if db["cookie_jar"].get(safe_email):
            for item in reversed(db["cookie_jar"][safe_email]): st.success(f"🏆 **[{item.get('วันที่', 'ไม่ระบุ')}]** : {item.get('ชัยชนะ', '')}")
        else: st.write("ยังไม่มีความสำเร็จอะไรเลย ไปทำซะ!")

    with tab2:
        if db["excuses"].get(safe_email):
            for item in reversed(db["excuses"][safe_email]): st.error(f"🤡 **[{item.get('วันที่', 'ไม่ระบุ')}]** : {item.get('ข้ออ้าง', '')}")
        else: st.write("ดีมาก! ยังไม่มีข้ออ้างขยะๆ ให้รกหูรกตา!")

    with tab3:
        if db["missions"].get(safe_email):
            for item in reversed(db["missions"][safe_email]):
                if item.get("เสร็จแล้ว"): status = "✅ เสร็จแล้ว"
                elif item.get("รอตรวจ", False): status = "⏳ รอตรวจ/พร้อมส่ง"
                else: status = "❌ ยังดองอยู่"
                st.write(f"🔹 **[{item.get('วันที่', 'ไม่ระบุ')}]** {item.get('ภารกิจ', '')} ({item.get('ประเภท','ทั่วไป')}) 👉 {status}")
        else: st.write("ยังไม่มีประวัติการแบกซุง!")

    with tab4:
        win_count = len(db["cookie_jar"].get(safe_email, []))
        fail_count = len(db["excuses"].get(safe_email, []))
        st.write(f"📈 จำนวนครั้งที่ชนะใจตัวเอง: **{win_count}** ครั้ง")
        st.write(f"📉 จำนวนครั้งที่พ่ายแพ้ปล่อยข้ออ้าง: **{fail_count}** ครั้ง")
        if win_count + fail_count > 0:
            chart_data = pd.DataFrame({"จำนวนครั้ง": [win_count, fail_count]}, index=["Savage (ชนะ)", "Bitch (ข้ออ้าง)"])
            st.bar_chart(chart_data)
