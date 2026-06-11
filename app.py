import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import requests
import uuid
import hashlib
import random
import extra_streamlit_components as stx

# ==========================================
# 1. ตั้งค่าระบบ (THE IMMORTAL SOUL V.15.8)
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
def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

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
    if FIREBASE_URL == "ใส่ลิงก์FIREBASEของมึงตรงนี้" or FIREBASE_URL == "":
        st.error("🚨 ไอ้เวร! มึงยังไม่ได้เอาลิงก์ Firebase มาใส่ในโค้ด! กลับไปแก้เดี๋ยวนี้!")
        st.stop()
    try:
        res = requests.get(f"{FIREBASE_URL}/db.json")
        if res.status_code == 200 and res.json() is not None:
            data = res.json()
            defaults = {"users": {}, "missions": {}, "dark_room": {}, "anti_simp": {}, "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, "deadlines": {}, "haters": {}, "finance": {}}
            for k, v in defaults.items():
                if k not in data: data[k] = v
            return data
    except: pass
    return {"users": {}, "missions": {}, "dark_room": {}, "anti_simp": {}, "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}}

def save_db(data):
    try: requests.put(f"{FIREBASE_URL}/db.json", json=data)
    except: st.error("🚨 เซฟข้อมูลลงฐานข้อมูลอมตะไม่สำเร็จ!")

db = load_db()

# 🍪 ระบบจัดการความจำ (COOKIE MANAGER)
@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

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
# 3. ระบบกำเนิด (Login / Register / Auto-Login)
# ==========================================
if "current_user" not in st.session_state: 
    st.session_state.current_user = None

# ตรวจสอบคุกกี้เพื่อล็อกอินอัตโนมัติ
saved_email = cookie_manager.get(cookie="warrior_email")
if saved_email and st.session_state.current_user is None:
    if saved_email in db["users"]:
        st.session_state.current_user = saved_email
        user_data = db["users"][saved_email]
        if user_data["last_login"] != today_str:
            user_data["ghost_exp"] += 25 
            unpaid_bounties = [m for m in db.get("missions", {}).get(saved_email, []) if m.get("bounty") and not m.get("เสร็จแล้ว")]
            if unpaid_bounties or not user_data.get("cleared_yesterday", False):
                penalty = 100 + (len(unpaid_bounties) * 100)
                user_data["exp"] = 0; user_data["level"] = max(1, user_data["level"] - 1)
                user_data["streak"] = 0; user_data["blood_debt"] += penalty
                user_data["failure_prob"] = min(100, user_data["failure_prob"] + 20)
            user_data["last_login"] = today_str; user_data["cleared_yesterday"] = False
            save_db(db)
        st.rerun()

with st.sidebar:
    st.title("🧠 สมรภูมิในสมอง")
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือก:", ["ลุย (Login)", "เกิดใหม่ (Register)"])
        email_input = st.text_input("อีเมล:")
        pass_input = st.text_input("รหัสผ่าน:", type="password")
        
        if auth_mode == "เกิดใหม่ (Register)":
            name_input = st.text_input("ชื่อนักรบ:")
            if st.button("ทิ้งความเป็นคนซะ!"):
                if email_input and pass_input and name_input:
                    safe_email = get_safe_email(email_input)
                    if safe_email in db["users"]: st.error("อีเมลนี้ถูกใช้ไปแล้ว!")
                    else:
                        db["users"][safe_email] = {
                            "password": hash_password(pass_input), "username": name_input,
                            "level": 1, "exp": 0, "streak": 0, "blood_debt": 0, "in_cage": False,
                            "ghost_exp": 0, "ambush_task": "", "failure_prob": 10,
                            "last_login": today_str, "cleared_yesterday": True
                        }
                        save_db(db); st.success("🔥 ลงทะเบียนสำเร็จ! ไปล็อกอินซะ!")
                else: st.warning("กรอกให้ครบ!")
                
        elif auth_mode == "ลุย (Login)":
            if st.button("เปิดสมอง!"):
                safe_email = get_safe_email(email_input)
                if safe_email not in db["users"]: st.error("❌ ไม่พบบัญชีนี้!")
                elif db["users"][safe_email]["password"] != hash_password(pass_input): st.error("❌ รหัสผ่านผิด!")
                else:
                    # 🍪 ฝังคุกกี้ให้จำบัญชีนี้ไปอีก 30 วัน!
                    cookie_manager.set("warrior_email", safe_email, expires_at=datetime.now() + timedelta(days=30))
                    
                    user_data = db["users"][safe_email]
                    if user_data["last_login"] != today_str:
                        user_data["ghost_exp"] += 25 
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
        monk_mode = st.toggle("🧘‍♂️ โหมดจำศีล (Monk Mode)\nซ่อนกิเลสทั้งหมด โฟกัสแค่งาน!")
        
        if st.button("🚪 ถอยทัพ (ปิดเว็บ / ออกจากระบบ)"):
            cookie_manager.delete("warrior_email") # ลบคุกกี้ทิ้ง
            st.session_state.current_user = None; st.rerun()

if st.session_state.current_user is None:
    st.title("🧠 THE BRAIN WAR (สงครามสองอนาคต)")
    st.info("👈 ล็อกอินเข้ามาดิวะ บัลลังก์นักรบฝั่งขวารอมึงอยู่!")
    st.stop()

safe_email = st.session_state.current_user

# ===== 🛡️ FIREBASE SHIELD =====
for k in ["missions", "dark_room", "anti_simp", "dopamine_fails", "excuses", "cookie_jar", "deadlines", "haters", "finance"]:
    if safe_email not in db[k] or db[k][safe_email] is None: 
        if k == "finance": db[k][safe_email] = {"goal_name": "ยังไม่ได้ตั้ง", "goal_amount": 0, "current": 0}
        else: db[k][safe_email] = []
# ===============================

user = db["users"][safe_email]
finance = db["finance"][safe_email]

# ==========================================
# 🎯 เป้าหมาย & ปุ่มสับระเบิดพลัง
# ==========================================
colTop1, colTop2, colTop3 = st.columns([1, 1, 3])
with colTop1:
    if st.button("🎰 วงล้อชดใช้กรรม\n(กูเริ่มขี้เกียจ)", type="primary", use_container_width=True):
        st.session_state.punishment_active = True
        st.session_state.punishment_task = random.choice(PUNISHMENTS)
        st.rerun()
with colTop2:
    if st.button("⚡ คาถาระเบิดพลัง\n(เรียกสติเดี่ยวนี้)", use_container_width=True):
        st.toast(f"🔊 ตื่นดิวะ! ไปทำอันนี้เดี๋ยวนี้: {random.choice(PUNISHMENTS)}", icon="🦍")
with colTop3:
    st.error("🔥 **คำสาบาน:** กูจะปั้นช่อง YouTube ให้ทะลุ 10 ล้านวิว! กูจะสร้างชีวิตที่กูคุมเกมเอง จะไม่ยอมเป็นทาสความขี้เกียจ ถ้ากูยอมแพ้ กูยอมตายซะดีกว่า!")

# ==========================================
# ⏳ แท่นชี้ชะตาเดดไลน์
# ==========================================
st.divider()
st.markdown("### ⏳ แท่นชี้ชะตาเดดไลน์")
with st.expander("➕ เพิ่มกำหนดวันชี้ชะตาใหม่"):
    with st.form("deadline_form", clear_on_submit=True):
        dl_name = st.text_input("ชื่อเหตุการณ์:")
        dl_date = st.date_input("วันที่กำหนดชะตา:")
        if st.form_submit_button("จารึกลงแท่นชี้ชะตา"):
            if dl_name:
                db["deadlines"][safe_email].append({"id": str(uuid.uuid4()), "ชื่อ": dl_name, "วันที่": str(dl_date)})
                save_db(db); st.rerun()

if db["deadlines"][safe_email]:
    dl_cols = st.columns(min(len(db["deadlines"][safe_email]), 4))
    for idx, item in enumerate(db["deadlines"][safe_email]):
        with dl_cols[idx % 4]:
            try:
                t_date = datetime.strptime(item["วันที่"], "%Y-%m-%d").date()
                days_left = (t_date - today_date).days
                if days_left <= 3: st.error(f"🚨 **{item['ชื่อ']}**\n\nวิกฤต! เหลืออีกแค่ **{days_left} วัน**!")
                else: st.info(f"📅 **{item['ชื่อ']}**\n\nเหลือเวลาอีก **{days_left} วัน**")
                if st.button("🗑️", key=f"del_dl_{item['id']}"):
                    db["deadlines"][safe_email].remove(item); save_db(db); st.rerun()
            except: pass

if user.get("in_cage"): st.error("🚨 **มึงอยู่ในกรง!** วิดพื้นจ่ายหนี้เลือดซะ!")

# ==========================================
# 5. DUAL REALITY DASHBOARD
# ==========================================
st.divider()
if monk_mode:
    st.markdown("## 🧘‍♂️ MONK MODE ACTIVE: สมาธิขั้นสุด!")
    st.info("โซนขยะถูกล็อก! ก้มหน้าก้มตาแบกซุงของมึงซะ!")
    colLeft, colRight = st.columns([0.01, 1]) 
else:
    colLeft, colRight = st.columns(2)

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
            h_text = st.text_input("คำดูถูก/คำสบประมาทที่มึงเคยเจอ:")
            if st.form_submit_button("ฝังความแค้น"):
                if h_text: db["haters"][safe_email].append(h_text); save_db(db); st.rerun()
        if db["haters"][safe_email]:
            st.error(f"🤬 คำดูถูกเตือนใจ: \"{random.choice(db['haters'][safe_email])}\"")

with colRight:
    st.markdown("## ⚔️ THE SAVAGE ZONE (นักรบฝั่งขวา)")
    st.success(random.choice(SAVAGE_VOICES))
    
    st.markdown("### 🪵 The Daily Siege (ตารางรบ)")
    with st.form("mission_form", clear_on_submit=True):
        m_name = st.text_input("ท่อนซุงที่ต้องแบกวันนี้:")
        m_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด (คอขาดบาดตาย)", "🔥 งานฉุกเฉิน / Special Event", "🟡 ปานกลาง (ต้องเสร็จ)", "🟢 ชิลๆ (ทำตอนว่าง)"])
        m_bounty = st.checkbox("⚔️ ตั้งค่าหัว! (เดิมพันศักดิ์ศรี: ได้ EXPx2 แต่ถ้าอู้โดนหนี้เลือด 100 ที!)")
        
        if st.form_submit_button("เพิ่มภารกิจ"):
            if m_name:
                db["missions"][safe_email].append({"id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": m_name, "ประเภท": m_type, "bounty": m_bounty, "เสร็จแล้ว": False})
                save_db(db); st.rerun()
                
    active_missions = [m for m in db["missions"][safe_email] if not m.get("เสร็จแล้ว")]
    active_missions.sort(key=lambda x: get_priority_score(x.get("ประเภท", "")))
    
    if active_missions:
        for m in active_missions:
            c1, c2 = st.columns([3, 1])
            is_bounty = "⚔️[เดิมพัน] " if m.get("bounty") else ""
            c1.write(f"**{m.get('ประเภท','')}** | {is_bounty}{m['ภารกิจ']}")
            if c2.button("✅ Tick!", key=f"m_{m['id']}"):
                m["เสร็จแล้ว"] = True
                exp_gain = 40 if (get_priority_score(m.get("ประเภท", "")) == 1 or m.get("bounty")) else 20
                if m.get("bounty") and get_priority_score(m.get("ประเภท", "")) == 1: exp_gain = 80 
                user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - 5)
                if user["exp"] >= 100: user["level"] += 1; user["exp"] -= 100
                save_db(db); st.balloons(); st.rerun()
    else: st.success("✅ วันนี้มึงแบกซุงหมดแล้ว มหาบุรุษฝั่งขวาภูมิใจในตัวมึง!")

    st.markdown("### 💰 คลังสมบัตินักรบ (สร้างทุนทำยูทูป/ฝัน)")
    c_fin1, c_fin2 = st.columns([2, 1])
    with c_fin1:
        st.write(f"**เป้าหมาย:** {finance.get('goal_name', 'ยังไม่ตั้ง')}")
        cur = finance.get('current', 0)
        tgt = finance.get('goal_amount', 1)
        prog = min(cur / tgt, 1.0) if tgt > 0 else 0
        st.progress(prog, text=f"มีแล้ว: {cur} / {tgt} บาท ({int(prog*100)}%)")
    with c_fin2:
        with st.popover("⚙️ จัดการเงิน"):
            new_g_name = st.text_input("ชื่อเป้าหมาย:", value=finance.get('goal_name', ''))
            new_g_amt = st.number_input("จำนวนเงินเป้าหมาย:", value=finance.get('goal_amount', 0))
            if st.button("ตั้งเป้าหมาย"):
                finance['goal_name'] = new_g_name; finance['goal_amount'] = new_g_amt; save_db(db); st.rerun()
            st.divider()
            add_amt = st.number_input("บวก/ลด เงิน (ใส่ติดลบเพื่อจ่าย):", value=0)
            if st.button("บันทึกเงิน"):
                finance['current'] += add_amt; save_db(db); st.rerun()

# ==========================================
# 6. หนี้เลือด & THE JUDGMENT FEED
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
    if active_missions: st.error("❌ มึงกำลังหักหลังตัวเอง! งานยังไม่เสร็จ!")
    elif user.get("in_cage") or user.get("blood_debt", 0) > 0: st.error("❌ มึงติดหนี้เลือดอยู่!")
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
                status = "✅ เสร็จแล้ว" if item.get("เสร็จแล้ว") else "❌ ยังดองอยู่"
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
