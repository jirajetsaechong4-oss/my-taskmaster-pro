import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import requests
import uuid
import hashlib
import random
import re
import streamlit.components.v1 as components

# ==========================================
# 1. ตั้งค่าระบบ (V.40 - THE SUPREME WARLORD)
# ==========================================
st.set_page_config(page_title="THE BRAIN WAR", layout="wide", page_icon="🧠")

# 🎨 Custom CSS แต่ง UI ให้พรีเมียม โหด ดุดัน (แก้บัค Header หายแล้ว)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #1a1a24;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #3a3a4f;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #2b2b3d;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: white !important;
        font-weight: bold;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover { transform: scale(1.03); }
</style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://mytaskpro-f7328-default-rtdb.asia-southeast1.firebasedatabase.app" 
FIREBASE_SECRET = "Wv2Ha7WZrDLwnpJyKMt29z9I0MGb0kxitoOaaoGe"

def get_current_thai_time():
    tz_thai = timezone(timedelta(hours=7))
    return datetime.now(tz_thai)

now_thai = get_current_thai_time()
today_date = now_thai.date()
today_str = str(today_date)

ROLE_MAP = {"Vanguard": "⚡ [ทัพหน้า]", "Main": "⚔️ [ทัพหลวง]", "Support": "🏹 [ทัพหนุน]"}

PUNISHMENTS = [
    "ไปดันพื้น 50 ทีเดี๋ยวนี้!", "แพลงก์ 2 นาที! เอาความเจ็บปวดล้างสมอง!", 
    "ลุกไปอาบน้ำเย็นจัด 5 นาทีเดี๋ยวนี้!", "กระโดดตบ 100 ครั้ง!", 
    "ห้ามจับมือถือ 1 ชั่วโมงนับจากนี้!", "สควอช (ลุกนั่ง) 60 ที!"
]
LAZY_VOICES = ["🤡 'พักเถอะมึง วันนี้เหนื่อยแล้ว...'", "🤡 'พรุ่งนี้ค่อยทำก็ได้น่า...'", "🤡 'เล่นเกมแป๊บเดียวเอง...'"]
SAVAGE_VOICES = ["🦍 'หุบปากไอ้สวะ! ลุยต่อ!'", "🦍 'มึงจะฟังสวะนั่น หรือจะลุกมาสร้างตำนานวะ!'", "🦍 'ความสบายคือยาพิษ ลุย!'"]
AMBUSH_TASKS = ["กฎก้าวสุดท้าย! ไปแพลงก์ 1 นาที!", "คิดว่ารอดแล้วหรอ? วิดพื้น 20 ที!"]

def get_safe_email(email): return email.replace(".", "-").replace("@", "-")

def get_title(level):
    if level < 3: return "🤡 ไอ้ลูกหมาขี้ขลาด"
    elif level < 7: return "⚔️ นักรบฝึกหัดแบกซุง"
    elif level < 12: return "🦍 แม่ทัพคุมโดพามีน"
    else: return "👑 มหาจักรพรรดิผู้คุมชะตา"

def get_priority_score(task_type):
    if "🔴" in task_type: return 1
    if "🟡" in task_type: return 2
    if "🟢" in task_type: return 3
    return 4

def get_role_score(role):
    if role == "Vanguard": return 1
    if role == "Main": return 2
    return 3

def get_deadline_score(dl_str):
    if not dl_str: return 999999
    try: return (datetime.strptime(dl_str, "%Y-%m-%d").date() - today_date).days
    except: return 999999

def calculate_task_rewards(task, current_streak):
    score = get_priority_score(task.get("ประเภท", ""))
    base_exp = 40 if score == 1 else 20 if score == 2 else 10
    bonus_exp = (100 if task.get("is_boss") else 0) + (50 if task.get("bounty") else 0) + (len(task.get("subtasks", [])) * 10)
    
    multiplier = 1.5 if current_streak >= 30 else 1.2 if current_streak >= 7 else 1.1 if current_streak >= 3 else 1.0
    final_exp = int((base_exp + bonus_exp) * multiplier)
    
    fail_reduce = 10 if score == 1 else 5 if score == 2 else 2
    if task.get("is_boss"): fail_reduce += 15
    if task.get("bounty"): fail_reduce += 5
    return final_exp, fail_reduce

def load_db():
    if not FIREBASE_URL: st.stop()
    try:
        res = requests.get(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}")
        if res.status_code == 200 and res.json():
            data = res.json()
            defaults = {
                "users": {}, "missions": {}, "study_missions": {}, "backlog": {}, 
                "dark_room": {}, "anti_simp": {}, "dopamine_fails": {}, "excuses": {}, 
                "cookie_jar": {}, "deadlines": {}, "haters": {}, "finance": {}, 
                "iron_habits": {}, "exams": {}, "beat_yesterday": {}, "limit_breaks": {}
            }
            for k, v in defaults.items():
                if k not in data: data[k] = v
            return data
    except: pass
    return {"users": {}, "missions": {}, "study_missions": {}, "backlog": {}, "dark_room": {}, "anti_simp": {}, "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, "deadlines": {}, "haters": {}, "finance": {}, "iron_habits": {}, "exams": {}, "beat_yesterday": {}, "limit_breaks": {}}

def save_db(data):
    try: requests.put(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}", json=data)
    except: st.error("🚨 เซฟข้อมูลลงฐานข้อมูลอมตะไม่สำเร็จ!")

# ==========================================
# 🗺️ THE WAR MAP ENGINE (แกนวาดแผนผัง อัปเกรด V.40)
# ==========================================
def render_war_map(missions_data, study_data):
    all_tasks = missions_data + study_data
    if not all_tasks:
        st.info("🗺️ ยังไม่มีภารกิจในกระดาน แผนที่จึงว่างเปล่า!")
        return

    mermaid_code = "graph TD\n"
    mermaid_code += "classDef done fill:#1a4d1a,color:#fff,stroke:#2b7d2b,stroke-width:2px;\n"
    mermaid_code += "classDef pending fill:#b37700,color:#fff,stroke:#ffaa00,stroke-width:2px;\n"
    mermaid_code += "classDef blocked fill:#262626,color:#888,stroke:#4d4d4d,stroke-width:2px,stroke-dasharray: 5 5;\n"
    mermaid_code += "classDef boss fill:#660000,color:#fff,stroke:#ff0000,stroke-width:3px;\n"

    task_status_map = {t['id']: t.get('เสร็จแล้ว', False) for t in all_tasks}

    for t in all_tasks:
        safe_id = t['id'].replace("-", "")
        # ล้างอักขระพิเศษที่ทำให้กราฟพัง
        safe_name = re.sub(r'["\'\[\]{}()<>]', '', t['ภารกิจ'])
        if len(safe_name) > 25: safe_name = safe_name[:25] + "..."
        
        prereq_id = t.get('prereq_id', None)
        is_done = t.get('เสร็จแล้ว', False)
        is_boss = t.get('is_boss', False)
        
        is_blocked = False
        if prereq_id and not is_done and not task_status_map.get(prereq_id, True):
            is_blocked = True

        status_class = "done" if is_done else ("blocked" if is_blocked else ("boss" if is_boss else "pending"))
        prefix = "💀 " if is_boss else ("📚 " if t.get("is_study") else "🔪 ")
        
        mermaid_code += f'    {safe_id}["{prefix}{safe_name}"]\n'
        mermaid_code += f'    class {safe_id} {status_class};\n'
        
        if prereq_id and prereq_id in [x['id'] for x in all_tasks]:
            safe_prereq_id = prereq_id.replace("-", "")
            mermaid_code += f'    {safe_prereq_id} --> {safe_id}\n'

    # ล็อกเวอร์ชัน Mermaid v9 ป้องกันบัคหน้าจอดำจาก CDN
    html_code = f"""
    <div class="mermaid" style="background-color: #1a1a24; padding: 20px; border-radius: 12px; display: flex; justify-content: center; min-height: 300px;">
        {mermaid_code}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'dark', securityLevel: 'loose' }});
    </script>
    """
    components.html(html_code, height=450, scrolling=True)

def get_pending_task_options(task_list):
    options = {"🟢 ไม่มี (ทำได้เลย)": None}
    for t in task_list:
        if not t.get("เสร็จแล้ว", False):
            prefix = "📚 " if t.get("is_study") else "🔪 "
            options[f"{prefix}{t['ภารกิจ']}"] = t['id']
    return options

db = load_db()

# ==========================================
# 2. OVERLAY นรก
# ==========================================
if "punishment_active" in st.session_state:
    st.error("🚨 วงล้อแห่งกรรมทำงาน! มึงต้องชดใช้ความกระจอกเดี๋ยวนี้! 🚨")
    st.title(f"🔥 คำสั่งทรมาน: {st.session_state.punishment_task}")
    if st.button("🩸 กูทำเสร็จแล้ว! (ชดใช้กรรมเรียบร้อย)"):
        del st.session_state.punishment_active
        st.rerun()
    st.stop() 

# ==========================================
# 3. ระบบล็อกอิน
# ==========================================
if "current_user" not in st.session_state: st.session_state.current_user = None

with st.sidebar:
    st.title("🧠 สมรภูมิในสมอง")
    st.caption(f"🗓️ เวลาสมรภูมิ: {today_str}") 
    
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือกโหมด:", ["⚡ ล็อกอินด่วน", "➕ สร้างนักรบใหม่"])
        st.divider()
        
        if auth_mode == "➕ สร้างนักรบใหม่":
            name_input = st.text_input("ชื่อนักรบ:")
            email_input = st.text_input("อีเมล (ใช้เป็น ID):")
            if st.button("ทิ้งความเป็นคนซะ!"):
                if email_input and name_input:
                    safe_email = get_safe_email(email_input)
                    if safe_email in db.get("users", {}): st.error("อีเมล/ID นี้มีในระบบแล้ว!")
                    else:
                        db["users"][safe_email] = {
                            "username": name_input, "level": 1, "exp": 0, "streak": 0, 
                            "blood_debt": 0, "in_cage": False, "ghost_exp": 0, "ambush_task": "", 
                            "failure_prob": 10, "last_login": today_str, "cleared_yesterday": True,
                            "order_locked": False, "target_name": "ทำ 10 ล้านวิว YouTube Shorts", 
                            "target_date": str(today_date + timedelta(days=90))
                        }
                        save_db(db)
                        st.success("🔥 ลงทะเบียนสำเร็จ! ไปที่ 'ล็อกอินด่วน' ได้เลย!")
        elif auth_mode == "⚡ ล็อกอินด่วน":
            if not db.get("users"): st.warning("ยังไม่มีนักรบในระบบ!")
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
        st.markdown(f"🩻 **รอยแผลความพ่ายแพ้: {scars} รอย**")
        st.warning(f"🔥 สถิติไม่แพ้ (Streak): {u_data['streak']} วัน")
        
        cs = u_data.get("streak", 0)
        if cs >= 30: st.success("👑 BUFF: โบนัส EXP x 1.5")
        elif cs >= 7: st.success("🔥 BUFF: โบนัส EXP x 1.2")
        elif cs >= 3: st.success("⚡ BUFF: โบนัส EXP x 1.1")
        
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
            else: u_data["exp"] = 0
            needs_save = True
            
        if needs_save: save_db(db)
            
        st.progress(max(0.0, min(1.0, u_data["exp"] / 100)), text=f"Lv.{u_data['level']} | EXP: {u_data['exp']}/100")
        st.divider()
        monk_mode = st.toggle("🧘‍♂️ โหมดจำศีล (Monk Mode)")
        if st.button("🚪 ถอยทัพ (ออกจากระบบ)"):
            st.session_state.current_user = None
            st.rerun()

if st.session_state.current_user is None:
    st.title("🧠 THE BRAIN WAR V.40")
    st.info("👈 เลือกชื่อตัวเองแล้วกดปุ่ม 'เปิดสมอง!' เพื่อเข้าใช้งาน!")
    st.stop()

safe_email = st.session_state.current_user
user = db["users"][safe_email]
finance = db["finance"][safe_email]
current_streak = user.get("streak", 0)

# ===== 🚨 CHECK OVERDUE BACKLOG =====
overdue_count = 0
for task in db["backlog"][safe_email]:
    if task.get("deadline") and task["deadline"] != "":
        try:
            if datetime.strptime(task["deadline"], "%Y-%m-%d").date() < today_date and task.get("last_penalized") != today_str:
                overdue_count += 1
                task["last_penalized"] = today_str
        except: pass
if overdue_count > 0:
    user["failure_prob"] = min(100, user["failure_prob"] + (10 * overdue_count))
    user["blood_debt"] += (50 * overdue_count)
    user["in_cage"] = True
    save_db(db)
    st.error(f"🚨 ไอ้หน้าโง่! มึงมีงานดองเกินกำหนด {overdue_count} งาน! รับหนี้เลือดไปซะ!")

# ==========================================
# 🎯 ส่วนหัว: FUTURE COUNTDOWN
# ==========================================
try: t_date = datetime.strptime(user["target_date"], "%Y-%m-%d").date()
except: t_date = today_date + timedelta(days=90)
days_left = (t_date - today_date).days

colTop1, colTop2, colTop3 = st.columns([1, 1, 3])
with colTop1:
    if st.button("🎰 วงล้อชดใช้กรรม\n(เริ่มขี้เกียจ)", type="primary", use_container_width=True):
        st.session_state.punishment_active = True
        st.session_state.punishment_task = random.choice(PUNISHMENTS)
        st.rerun()
with colTop2:
    if st.button("⚡ คาถาระเบิดพลัง\n(เรียกสติ)", use_container_width=True):
        st.toast(f"🔊 ตื่นดิวะ! {random.choice(PUNISHMENTS)}", icon="🦍")
with colTop3:
    st.error(f"⏳ **ชี้ชะตา:** {user.get('target_name', 'เป้าหมาย')} ในอีก **{days_left}** วัน!")
    with st.popover("⚙️ ตั้งค่านับถอยหลัง"):
        new_t_name = st.text_input("เป้าหมายสูงสุด:", user.get("target_name", ""))
        new_t_date = st.date_input("วันกำหนด:", t_date)
        if st.button("บันทึกเป้าหมาย"):
            user["target_name"] = new_t_name
            user["target_date"] = str(new_t_date)
            save_db(db)
            st.rerun()

if user.get("in_cage"): st.error("🚨 **มึงอยู่ในกรง!** วิดพื้นจ่ายหนี้เลือดซะ!")

st.divider()

# ==========================================
# 5. DUAL REALITY DASHBOARD
# ==========================================
if monk_mode:
    st.markdown("## 🧘‍♂️ MONK MODE ACTIVE")
    colLeft, colRight = st.columns([0.01, 1]) 
else: 
    colLeft, colRight = st.columns([1, 2.2])

with colLeft:
    if not monk_mode:
        with st.container(border=True):
            st.markdown("### 🗑️ THE BITCH ZONE")
            st.warning(random.choice(LAZY_VOICES))
            fail_prob = user.get('failure_prob', 10)
            st.markdown(f"**📉 โอกาสพ่ายแพ้: {fail_prob}%**")
            st.progress(fail_prob / 100)
            
            with st.form("excuse_form", clear_on_submit=True):
                exc_text = st.text_input("ข้ออ้างขยะๆ วันนี้:")
                if st.form_submit_button("บันทึกข้ออ้าง"):
                    if exc_text:
                        db["excuses"][safe_email].append({"วันที่": today_str, "ข้ออ้าง": exc_text})
                        user["failure_prob"] = min(100, user["failure_prob"] + 10)
                        save_db(db)
                        st.rerun()
            if st.button("💀 แท่นประหาร: กูแพ้ให้สิ่งเร้าขยะ", use_container_width=True):
                db["dopamine_fails"][safe_email].append(today_str)
                user["exp"] = 0
                user["blood_debt"] += 50
                user["in_cage"] = True
                user["failure_prob"] = min(100, user["failure_prob"] + 20)
                save_db(db)
                st.rerun()

            st.markdown("#### 🩸 บัญชีแค้น")
            with st.form("hater_form", clear_on_submit=True):
                h_text = st.text_input("คำดูถูกที่มึงเจอ:")
                if st.form_submit_button("ฝังความแค้น"):
                    if h_text: 
                        db["haters"][safe_email].append(h_text)
                        save_db(db)
                        st.rerun()
            if db["haters"][safe_email]: st.error(f"🤬 \"{random.choice(db['haters'][safe_email])}\"")

with colRight:
    st.markdown("## ⚔️ THE SAVAGE ZONE")
    
    # 📌 ดึง War Map มาไว้ข้างบนสุด ให้เห็นชัดๆ หาง่ายๆ ไม่ต้องสลับแท็บ!
    with st.expander("🗺️ เปิดดูแผนผังยุทธศาสตร์ (The War Map)", expanded=False):
        render_war_map(db["missions"][safe_email], db["study_missions"][safe_email])
        st.caption("<span style='color:#2b7d2b;'>🟢 สีเขียว = เสร็จ</span> | <span style='color:#b37700;'>🟡 สีส้ม = รอทำ</span> | <span style='color:#4d4d4d;'>⚪ เทาเส้นประ = ติดล็อก</span> | <span style='color:#ff0000;'>🔴 แดง = BOSS</span>", unsafe_allow_html=True)
    
    all_active_tasks = db["missions"][safe_email] + db["study_missions"][safe_email]
    prereq_options = get_pending_task_options(all_active_tasks)
    task_done_map = {t['id']: t.get('เสร็จแล้ว', False) for t in all_active_tasks}
    
    # ตัดแท็บ Map ออกเพราะเอามาโชว์ด้านบนแล้ว
    tab_missions, tab_study, tab_habits, tab_backlog, tab_cookie, tab_academic = st.tabs([
        "🔥 ภารกิจวันนี้", "📖 ภารกิจเรียน", "⛓️ วินัยเหล็ก", "📝 สมุดจดงาน", "🍪 โหลคุกกี้", "📚 ประลองปัญญา"
    ])
    
    # ----------------------------------------------------
    # TAB 1: ภารกิจวันนี้
    # ----------------------------------------------------
    with tab_missions:
        raw_active_missions = [m for m in db["missions"][safe_email] if not m.get("เสร็จแล้ว")]
        active_single_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False) and not m.get("subtasks")]
        
        if len(active_single_missions) >= 3: st.error("🚨 โควตางานเดี่ยววันนี้เต็ม 3 Slot แล้ว!")
        
        with st.expander("➕ เพิ่มงานด่วนวันนี้"):
            with st.form("mission_form", clear_on_submit=True):
                c_f1, c_f2 = st.columns(2)
                m_name = c_f1.text_input("ชื่อภารกิจ:")
                m_type = c_f2.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"])
                m_prereq_name = st.selectbox("🔗 ต้องรองานไหนเสร็จก่อนไหม? (โยงเส้น)", list(prereq_options.keys()))
                
                c_b1, c_b2 = st.columns(2)
                m_is_boss = c_b1.checkbox("💀 THE BOSS FIGHT (พลาด=หนี้ x3)")
                m_bounty = c_b2.checkbox("⚔️ มีค่าหัว! (เดิมพันศักดิ์ศรี)")
                
                m_subtasks_text = st.text_area("🔪 สับท่อนซุง (ใส่ชื่อย่อยทีละบรรทัด):")
                m_dl_type = st.radio("⏰ ระบบเวลา:", ["ไม่กำหนด", "🗓️ Deadline", "🎯 วันเป้าหมาย"], horizontal=True)
                m_deadline = st.date_input("เลือกวันที่:")
                
                if st.form_submit_button("เพิ่มภารกิจ"):
                    if m_name:
                        subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in m_subtasks_text.split('\n') if s.strip()]
                        if not subtasks and len(active_single_missions) >= 3:
                            st.error("🤡 ระบบบล็อก! บังคับให้สับข้อย่อยซะ!")
                        else:
                            db["missions"][safe_email].append({
                                "id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": m_name, 
                                "ประเภท": m_type, "bounty": m_bounty, "is_boss": m_is_boss,
                                "custom_order": 99, "battle_role": "Main", "is_queued": False, 
                                "skip_today_date": "", "subtasks": subtasks, "เสร็จแล้ว": False, 
                                "รอตรวจ": False, "deadline": str(m_deadline) if m_dl_type != "ไม่กำหนด" else "", 
                                "deadline_type": m_dl_type, "prereq_id": prereq_options[m_prereq_name]
                            })
                            save_db(db)
                            st.rerun()
                    
        todo_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False)]
        pending_missions = [m for m in raw_active_missions if m.get("รอตรวจ", False)]
        todo_missions.sort(key=lambda x: (get_role_score(x.get("battle_role", "Main")), 0 if x.get("is_boss") else 1, get_deadline_score(x.get("deadline", "")), get_priority_score(x.get("ประเภท", ""))))
        needs_queueing = [m for m in todo_missions if not m.get("is_queued", False)]
        
        if needs_queueing:
            with st.expander("⚔️🛡️ จัดค่ายกลกระบวนทัพรบ", expanded=True):
                with st.form("lock_order_form"):
                    updated_orders, updated_roles = {}, {}
                    for m in needs_queueing:
                        role_choice = st.selectbox(f"ทัพ: {m['ภารกิจ']}", ["⚡ ทัพหน้า", "⚔️ ทัพหลวง", "🏹 ทัพหนุน"], key=f"s_{m['id']}")
                        updated_orders[m["id"]] = 1 if "หน้า" in role_choice else 2 if "หลวง" in role_choice else 3
                        updated_roles[m["id"]] = "Vanguard" if "หน้า" in role_choice else "Main" if "หลวง" in role_choice else "Support"
                    if st.form_submit_button("🔒 ล็อกค่ายกล!"):
                        for m in db["missions"][safe_email]:
                            if m["id"] in updated_orders:
                                m["custom_order"] = updated_orders[m["id"]]; m["battle_role"] = updated_roles[m["id"]]; m["is_queued"] = True
                        save_db(db)
                        st.rerun()

        if todo_missions:
            for m in todo_missions:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6]) 
                    
                    prereq_id = m.get("prereq_id", None)
                    is_blocked = prereq_id and not task_done_map.get(prereq_id, True)

                    t_badge = "🔪 **[งานใหญ่]**" if m.get("subtasks") else "⚡ **[จบในตัว]**"
                    is_boss = " 💀 **[BOSS]**" if m.get("is_boss") else ""
                    o_badge = f" | {ROLE_MAP.get(m.get('battle_role', 'Main'), '⚔️')}"
                    
                    is_overdue, d_badge = False, ""
                    if m.get("deadline"):
                        try:
                            days_l = (datetime.strptime(m["deadline"], "%Y-%m-%d").date() - today_date).days
                            if days_l > 0: d_badge = f" ⏳ (เหลือ {days_l} วัน)"
                            elif days_l == 0: d_badge = f" 🚨 **(ต้องเสร็จวันนี้!)**"
                            else: d_badge = f" 💀 **(เลยมา {-days_l} วัน)**"; is_overdue = True 
                        except: pass

                    if m.get("skip_today_date") != "" and m.get("skip_today_date") != today_str:
                        m["skip_today_date"] = ""; save_db(db)
                    is_frozen = m.get("skip_today_date") == today_str
                    f_badge = " ❄️🚨 [เกราะแตก!]" if is_frozen and is_overdue else " ❄️ [แช่แข็ง]" if is_frozen else ""

                    if is_blocked:
                        c1.markdown(f"🔒 **<span style='color:#888;'>[ติดล็อกรอคิว] {m['ภารกิจ']}{is_boss}</span>**", unsafe_allow_html=True)
                    else:
                        c1.write(f"**{m.get('ประเภท','')}** | {t_badge}{is_boss} {m['ภารกิจ']}{o_badge}{d_badge}{f_badge}")
                    
                    all_done = True
                    if m.get("subtasks"):
                        done_subs = len([s for s in m["subtasks"] if s.get("done")])
                        st.progress(done_subs / len(m["subtasks"]), text=f"📊 ความคืบหน้า: {done_subs}/{len(m['subtasks'])}")
                        
                        for i, stask in enumerate(m["subtasks"]):
                            is_done = stask.get("done", False)
                            is_locked = is_done and stask.get("done_date", "") != today_str
                            label = f"{stask['name']} 🔒" if is_locked else stask['name']
                            can_interact = not is_locked and (not is_frozen or is_overdue) and not is_blocked
                            
                            if st.checkbox(label, value=is_done, disabled=not can_interact, key=f"st_{m['id']}_{i}") != is_done:
                                m["subtasks"][i]["done"] = not is_done
                                m["subtasks"][i]["done_date"] = today_str if not is_done else ""
                                save_db(db)
                                st.rerun()
                        all_done = all(s.get("done", False) for s in m["subtasks"])
                    else: all_done = True 

                    if not is_blocked:
                        if is_frozen:
                            if c4.button("🔥 ปลดล็อก", key=f"uf_{m['id']}", use_container_width=True):
                                m["skip_today_date"] = ""; save_db(db); st.rerun()
                        else:
                            if c4.button("❄️ เลื่อน", key=f"fr_{m['id']}", use_container_width=True):
                                m["skip_today_date"] = today_str; save_db(db); st.rerun()

                    if is_blocked: c2.error("🔒 ติดล็อก")
                    elif all_done and (not is_frozen or is_overdue):
                        if c2.button("✅ สำเร็จ", key=f"m_{m['id']}", use_container_width=True):
                            m["เสร็จแล้ว"] = True
                            exp_gain, fail_reduce = calculate_task_rewards(m, current_streak)
                            if m.get("battle_role") == "Vanguard": exp_gain += 20
                            user["exp"] += exp_gain
                            user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce)
                            save_db(db); st.balloons(); st.rerun()
                        if c3.button("📤 ส่งตรวจ", key=f"pd_{m['id']}", use_container_width=True):
                            m["รอตรวจ"] = True; save_db(db); st.rerun()
                    else: c2.caption("🔒 ติดงานย่อย") if not is_frozen else c2.caption("❄️ แช่แข็ง")
                    if c5.button("🗑️", key=f"d_{m['id']}"): db["missions"][safe_email].remove(m); save_db(db); st.rerun()
        else: st.success("✅ เคลียร์ภารกิจหลักหมดแล้ว เยี่ยมมากไอ้เสือ!")

        if pending_missions:
            st.divider()
            st.markdown("### ⏳ งานที่รอตรวจ")
            for m in pending_missions:
                c1, c2, c3 = st.columns([5, 2, 2])
                c1.caption(f"⏳ {m['ภารกิจ']}")
                if c2.button("✅ ผ่าน", key=f"ap_{m['id']}"):
                    m["เสร็จแล้ว"] = True; m["รอตรวจ"] = False
                    exp_gain, fail_reduce = calculate_task_rewards(m, current_streak)
                    user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce)
                    save_db(db); st.balloons(); st.rerun()
                if c3.button("⏪ ดึงกลับ", key=f"rv_{m['id']}"): m["รอตรวจ"] = False; save_db(db); st.rerun()

    # ----------------------------------------------------
    # 📖 TAB 2: ภารกิจเรียน
    # ----------------------------------------------------
    with tab_study:
        raw_active_study = [s for s in db["study_missions"][safe_email] if not s.get("เสร็จแล้ว")]
        active_single_study = [s for s in raw_active_study if not s.get("รอตรวจ", False) and not s.get("subtasks")]
        
        with st.expander("➕ เพิ่มวิชาทบทวน"):
            with st.form("study_form", clear_on_submit=True):
                c_s1, c_s2 = st.columns(2)
                s_name = c_s1.text_input("วิชา/เรื่อง:")
                s_type = c_s2.selectbox("ระดับ:", ["🔴 ด่วนสุด", "🔥 ติวเข้ม", "🟡 ปานกลาง", "🟢 ชิลๆ"])
                s_prereq_name = st.selectbox("🔗 ต้องรองานไหนก่อนไหม?", list(prereq_options.keys()))
                s_is_boss = st.checkbox("💀 บทโหดไฟลุก")
                s_subtasks_text = st.text_area("🔪 สับบทเรียนย่อย (ทีละบรรทัด):")
                s_dl_type = st.radio("⏰ เวลา:", ["ไม่กำหนด", "🗓️ Deadline", "🎯 เป้าหมาย"], horizontal=True)
                s_deadline = st.date_input("เลือกวันที่:")
                
                if st.form_submit_button("บรรจุวิชา"):
                    if s_name:
                        db["study_missions"][safe_email].append({
                            "id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": s_name, 
                            "ประเภท": s_type, "bounty": False, "is_boss": s_is_boss,
                            "custom_order": 99, "battle_role": "Main", "is_queued": False, 
                            "skip_today_date": "", "subtasks": [{"name": s.strip(), "done": False, "done_date": ""} for s in s_subtasks_text.split('\n') if s.strip()], 
                            "เสร็จแล้ว": False, "รอตรวจ": False, "deadline": str(s_deadline) if s_dl_type != "ไม่กำหนด" else "", 
                            "deadline_type": s_dl_type, "is_study": True, "prereq_id": prereq_options[s_prereq_name]
                        })
                        save_db(db); st.rerun()
                        
        todo_study = [s for s in raw_active_study if not s.get("รอตรวจ", False)]
        todo_study.sort(key=lambda x: (get_role_score(x.get("battle_role", "Main")), 0 if x.get("is_boss") else 1, get_deadline_score(x.get("deadline", ""))))

        for s in todo_study:
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6])
                prereq_id = s.get("prereq_id", None)
                is_blocked = prereq_id and not task_done_map.get(prereq_id, True)
                
                if is_blocked: c1.markdown(f"🔒 **<span style='color:#888;'>[ติดล็อกรอคิว] {s['ภารกิจ']}</span>**", unsafe_allow_html=True)
                else: c1.write(f"**{s.get('ประเภท','')}** | 📖 {s['ภารกิจ']}")
                
                all_done = True
                if s.get("subtasks"):
                    done_subs = len([stk for stk in s["subtasks"] if stk.get("done")])
                    st.progress(done_subs / len(s["subtasks"]), text=f"📈 ความคืบหน้า: {done_subs}/{len(s['subtasks'])}")
                    for i, stask in enumerate(s["subtasks"]):
                        is_done = stask.get("done", False)
                        if st.checkbox(stask['name'], value=is_done, disabled=is_blocked or (is_done and stask.get("done_date") != today_str), key=f"st_s_{s['id']}_{i}") != is_done:
                            s["subtasks"][i]["done"] = not is_done
                            s["subtasks"][i]["done_date"] = today_str if not is_done else ""
                            save_db(db); st.rerun()
                    all_done = all(stk.get("done", False) for stk in s["subtasks"])
                else: all_done = True

                if not is_blocked:
                    if c4.button("❄️ เลื่อน", key=f"frs_{s['id']}", use_container_width=True):
                        s["skip_today_date"] = today_str if s.get("skip_today_date") == "" else ""
                        save_db(db); st.rerun()

                if is_blocked: c2.error("🔒")
                elif all_done:
                    if c2.button("✅ ติวสำเร็จ", key=f"sw_{s['id']}", use_container_width=True):
                        s["เสร็จแล้ว"] = True
                        eg, fr = calculate_task_rewards(s, current_streak)
                        user["exp"] += eg; user["failure_prob"] = max(0, user["failure_prob"] - fr)
                        save_db(db); st.balloons(); st.rerun()
                if c5.button("🗑️", key=f"ds_{s['id']}"): db["study_missions"][safe_email].remove(s); save_db(db); st.rerun()

    # ----------------------------------------------------
    # TAB 3: วินัยเหล็ก 
    # ----------------------------------------------------
    with tab_habits:
        with st.form("habit_form", clear_on_submit=True):
            h_name = st.text_input("สร้างวินัยเหล็กใหม่:")
            if st.form_submit_button("เพิ่ม"):
                if h_name:
                    db["iron_habits"][safe_email].append({"id": str(uuid.uuid4()), "name": h_name, "last_done_date": ""})
                    save_db(db); st.rerun()
        for h in db["iron_habits"][safe_email]:
            c1, c2, c3 = st.columns([5, 3, 1])
            c1.write(f"⛓️ **{h['name']}**")
            if h.get("last_done_date") == today_str: c2.success("✅ ทำแล้ว")
            else:
                if c2.button("🔥 สำเร็จ!", key=f"hd_{h['id']}"):
                    h["last_done_date"] = today_str
                    user["exp"] += 10 if current_streak >= 30 else 5
                    user["failure_prob"] = max(0, user["failure_prob"] - 2) 
                    save_db(db); st.rerun()
            if c3.button("🗑️", key=f"dh_{h['id']}"): db["iron_habits"][safe_email].remove(h); save_db(db); st.rerun()

    # ----------------------------------------------------
    # TAB 4: สมุดจดงาน (Backlog)
    # ----------------------------------------------------
    with tab_backlog:
        with st.form("backlog_form", clear_on_submit=True):
            b_name = st.text_input("หัวข้องาน/ไอเดีย:")
            b_detail = st.text_area("รายละเอียด:")
            b_subtasks_text = st.text_area("🔪 ซอยงานย่อย (Enter):")
            b_type = st.selectbox("ระดับ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"])
            b_dl_type = st.radio("⏰ เวลา:", ["ไม่กำหนด", "🗓️ Deadline", "🎯 เป้าหมาย"], horizontal=True)
            b_deadline = st.date_input("วันกำหนด:")
            
            if st.form_submit_button("💾 บันทึกลงสมุด"):
                if b_name:
                    db["backlog"][safe_email].append({
                        "id": str(uuid.uuid4()), "ภารกิจ": b_name, "รายละเอียด": b_detail,
                        "subtasks": [{"name": s.strip(), "done": False, "done_date": ""} for s in b_subtasks_text.split('\n') if s.strip()], 
                        "ประเภท": b_type, "deadline": str(b_deadline) if b_dl_type != "ไม่กำหนด" else "", "deadline_type": b_dl_type
                    })
                    save_db(db); st.rerun()
                    
        for b_task in sorted(db["backlog"][safe_email], key=lambda x: x.get("deadline") if x.get("deadline") else "9999"):
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([4, 2, 2, 0.8])
                dl_str = b_task.get('deadline', '')
                c1.write(f"**{b_task['ประเภท']}** | 📝 {b_task['ภารกิจ']}")
                c1.caption(f"เวลา: {dl_str if dl_str else 'ไม่ระบุ'} | รายละเอียด: {b_task.get('รายละเอียด', '-')}")
                
                if c2.button("⚡ เข้างาน", key=f"pm_{b_task['id']}"):
                    db["missions"][safe_email].append({
                        "id": b_task["id"], "วันที่": today_str, "ภารกิจ": b_task["ภารกิจ"], "ประเภท": b_task["ประเภท"], 
                        "bounty": False, "is_boss": False, "custom_order": 99, "battle_role": "Main", "is_queued": False, 
                        "skip_today_date": "", "deadline": dl_str, "deadline_type": b_task.get("deadline_type", "🗓️"),
                        "subtasks": b_task.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False, "prereq_id": None
                    })
                    db["backlog"][safe_email].remove(b_task); save_db(db); st.rerun()
                if c3.button("📖 เข้าเรียน", key=f"ps_{b_task['id']}"):
                    db["study_missions"][safe_email].append({
                        "id": b_task["id"], "วันที่": today_str, "ภารกิจ": b_task["ภารกิจ"], "ประเภท": b_task["ประเภท"], 
                        "bounty": False, "is_boss": False, "custom_order": 99, "battle_role": "Main", "is_queued": False, 
                        "skip_today_date": "", "deadline": dl_str, "deadline_type": b_task.get("deadline_type", "🗓️"),
                        "subtasks": b_task.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False, "is_study": True, "prereq_id": None
                    })
                    db["backlog"][safe_email].remove(b_task); save_db(db); st.rerun()
                if c4.button("🗑️", key=f"db_{b_task['id']}"): db["backlog"][safe_email].remove(b_task); save_db(db); st.rerun()

    # ----------------------------------------------------
    # TAB 5: โหลคุกกี้ 
    # ----------------------------------------------------
    with tab_cookie:
        with st.form("cookie_form", clear_on_submit=True):
            win_text = st.text_input("วันนี้มึงชนะใจตัวเองเรื่องอะไรได้บ้าง?:")
            if st.form_submit_button("เก็บชัยชนะ!"):
                if win_text:
                    db["cookie_jar"][safe_email].append({"วันที่": today_str, "ชัยชนะ": win_text})
                    user["exp"] += 5; save_db(db); st.rerun()
        if db["cookie_jar"][safe_email]:
            for c in reversed(db["cookie_jar"][safe_email][-5:]): st.success(f"🏆 **[{c['วันที่']}]** {c['ชัยชนะ']}")

    # ----------------------------------------------------
    # TAB 6: ประลองปัญญา
    # ----------------------------------------------------
    with tab_academic:
        with st.form("exam_form", clear_on_submit=True):
            e_subj = st.text_input("ชื่อวิชาสอบ:")
            e_score = st.number_input("คะแนนล่าสุด:", min_value=0.0)
            if st.form_submit_button("บันทึกคะแนนสอบ"):
                if e_subj:
                    if e_subj not in db["exams"][safe_email]: db["exams"][safe_email][e_subj] = []
                    if len(db["exams"][safe_email][e_subj]) > 0:
                        last_s = db["exams"][safe_email][e_subj][-1]
                        if e_score > last_s: user["exp"] += 30; st.success("🔥 โคตรเถื่อน คะแนนขึ้น!")
                        elif e_score < last_s: user["blood_debt"] += 50; st.error("🤡 คะแนนร่วง รับหนี้เลือด 50!")
                    db["exams"][safe_email][e_subj].append(e_score); save_db(db); st.rerun()

        if db["exams"][safe_email]:
            cols = st.columns(3)
            for idx, (subj, scores) in enumerate(db["exams"][safe_email].items()):
                if scores: cols[idx%3].metric(subj, scores[-1], round(scores[-1]-scores[-2],2) if len(scores)>1 else None)

        st.divider()
        yesterday_str = str(today_date - timedelta(days=1))
        with st.form("beat_y_form"):
            b_met = st.text_input("สิ่งที่ใช้วัด (เช่น ข้อสอบ, นาที):", value=db["beat_yesterday"][safe_email].get("metric_name", ""))
            b_val = st.number_input("จำนวนวันนี้:", min_value=0)
            if st.form_submit_button("ทุบสถิติ"):
                if b_met:
                    db["beat_yesterday"][safe_email]["metric_name"] = b_met
                    if "history" not in db["beat_yesterday"][safe_email]: db["beat_yesterday"][safe_email]["history"] = {}
                    y_val = db["beat_yesterday"][safe_email]["history"].get(yesterday_str, 0)
                    if b_val > y_val: user["exp"] += 20; st.success("🔥 ชนะไอ้ขี้แพ้เมื่อวาน!")
                    elif b_val < y_val: user["blood_debt"] += 30; st.error("🚨 กากกว่าเมื่อวาน รับหนี้เลือด!")
                    db["beat_yesterday"][safe_email]["history"][today_str] = b_val
                    save_db(db); st.rerun()
                    
        st.divider()
        if st.button("🔥 กฎ 40%: กูฝืนทะลุขีดจำกัดได้!", use_container_width=True):
            if today_str not in db["limit_breaks"][safe_email]:
                db["limit_breaks"][safe_email].append(today_str)
                user["exp"] += 50; user["failure_prob"] = max(0, user["failure_prob"] - 15)
                save_db(db); st.success("🦍 พลังใจระดับสัตว์ประหลาด!")
            else: st.warning("วันนี้มึงทะลุขีดจำกัดไปแล้ว!")

    # ----------------------------------------------------
    # ส่วนล่าง: ทุนสร้างฝัน (Finance)
    # ----------------------------------------------------
    st.divider()
    c_fin1, c_fin2 = st.columns([2, 1])
    with c_fin1:
        st.write(f"**เป้าหมายเงิน:** {finance.get('goal_name', 'ยังไม่ตั้ง')}")
        cur, tgt = finance.get('current', 0), finance.get('goal_amount', 1)
        st.progress(max(0.0, min(cur / tgt, 1.0)) if tgt > 0 else 0.0, text=f"มีแล้ว: {cur}/{tgt} บาท")
    with c_fin2:
        with st.popover("⚙️ จัดการเงิน"):
            finance['goal_name'] = st.text_input("ชื่อ:", value=finance.get('goal_name', ''))
            finance['goal_amount'] = st.number_input("เป้าหมาย:", value=finance.get('goal_amount', 0))
            if st.button("ตั้งเป้า"): save_db(db); st.rerun()
            st.divider()
            add_amt = st.number_input("บวก/ลด:", value=0)
            if st.button("บันทึกเงิน"): finance['current'] += add_amt; save_db(db); st.rerun()

# ==========================================
# 6. แท่นพิพากษา (THE JUDGMENT)
# ==========================================
st.divider()
c_bot1, c_bot2 = st.columns(2)
with c_bot1:
    my_exp = ((user["level"] - 1) * 100) + user["exp"]
    st.metric("พลังร่างทอง", f"{user['ghost_exp']} EXP")
    st.metric("พลังของมึง", f"{my_exp} EXP", delta=f"{my_exp - user['ghost_exp']} เทียบร่างทอง")
with c_bot2:
    st.markdown("### 🩸 หนี้เลือด")
    st.metric("ต้องวิดพื้น", f"{user.get('blood_debt', 0)} ที")
    if user.get("blood_debt", 0) > 0:
        if st.button("กูวิดพื้นใช้หนี้หมดแล้ว! (ปลดกรง)"): user["blood_debt"] = 0; user["in_cage"] = False; save_db(db); st.rerun()

st.divider()
st.markdown("<h2>⚖️ THE JUDGMENT FEED (พิพากษาก่อนนอน)</h2>", unsafe_allow_html=True)
if user.get("ambush_task", "") != "":
    st.error(f"🚨 **โดนซุ่มโจมตี!** คำสั่ง: **{user['ambush_task']}**")
    if st.button("🔥 ทำเสร็จแล้ว!"): user["ambush_task"] = ""; user["exp"] += 20; save_db(db); st.rerun()
elif user.get("cleared_yesterday"): 
    st.success("🔥 พิพากษาเสร็จสิ้น! มึงรอดไปได้อีกวัน!")
else:
    active_for_judgment = [m for m in db["missions"][safe_email] + db["study_missions"][safe_email] if not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False) and m.get("skip_today_date") != today_str]
    incomplete_habits = [h for h in db["iron_habits"][safe_email] if h.get("last_done_date") != today_str]
    incomplete_bosses = [m for m in active_for_judgment if m.get("is_boss")]

    if incomplete_bosses:
        st.error("💀 ไอ้สวะ! มึงดองงาน BOSS FIGHT! รับหนี้เลือด!")
        if st.button("🩸 ยอมรับ (รับหนี้เลือด 300 ที!)"):
            user["blood_debt"] += 300; user["failure_prob"] = min(100, user["failure_prob"] + 30)
            user["in_cage"] = True; user["cleared_yesterday"] = True; user["streak"] = 0; save_db(db); st.rerun()
    elif active_for_judgment or incomplete_habits: 
        st.error("❌ ศาลเตี้ยพบงาน/วินัยที่มึงละทิ้ง:")
        total_pen = sum(100 if get_priority_score(m.get("ประเภท", "")) == 1 else 70 if get_priority_score(m.get("ประเภท", "")) == 2 else 50 for m in active_for_judgment) + (len(incomplete_habits) * 30)
        
        for m in active_for_judgment: st.write(f"👉 **{m['ภารกิจ']}** [ดองข้ามวัน]")
        for h in incomplete_habits: st.write(f"👉 **{h['name']}** [ละทิ้งวินัย]")
            
        if st.button(f"🩸 ยอมรับ (รับหนี้เลือดรวม {total_pen} ที)"):
            user["blood_debt"] += total_pen; user["failure_prob"] = min(100, user["failure_prob"] + (10 * (len(active_for_judgment) + len(incomplete_habits))))
            user["in_cage"] = True; user["cleared_yesterday"] = True; user["streak"] = 0; save_db(db); st.rerun()
    elif user.get("in_cage") or user.get("blood_debt", 0) > 0: st.error("❌ ชดใช้หนี้เลือดซะก่อนถึงจะปิดวันได้!")
    else:
        c_j1, c_j2 = st.columns(2)
        if c_j1.button("📉 สู้ไม่เต็มที่ (แค่ 40%)"):
            user["exp"] -= 30; user["cleared_yesterday"] = True; user["failure_prob"] = min(100, user["failure_prob"] + 10)
            user["streak"] = 0; save_db(db); st.rerun()
        if c_j2.button("🔥 กูใช้พลัง 100%!"):
            if random.random() < 0.2: user["ambush_task"] = random.choice(AMBUSH_TASKS)
            else: 
                user["cleared_yesterday"] = True; user["streak"] += 1; user["exp"] += 25
            save_db(db); st.rerun()

# ==========================================
# 8. พงศาวดารความทรงจำ
# ==========================================
st.divider()
if not monk_mode:
    st.markdown("## 📜 พงศาวดารความทรงจำ")
    th_1, th_2, th_3 = st.tabs(["ประวัติงาน", "ข้ออ้าง", "สถิติภาพรวม"])

    with th_1:
        hist = [{"วิชา/งาน": m.get('ภารกิจ', ''), "สถานะ": "✅ เสร็จแล้ว" if m.get("เสร็จแล้ว") else "⏳ รอตรวจ" if m.get("รอตรวจ") else "❌ ยังดองอยู่"} for m in db["missions"].get(safe_email, []) + db["study_missions"].get(safe_email, [])]
        if hist: st.dataframe(pd.DataFrame(hist[::-1]), use_container_width=True, hide_index=True)
        else: st.write("ยังไม่มีประวัติ!")

    with th_2:
        if db["excuses"].get(safe_email):
            for i in reversed(db["excuses"][safe_email]): st.error(f"🤡 **[{i.get('วันที่', '-')}]** : {i.get('ข้ออ้าง', '')}")

    with th_3:
        all_m = db["missions"].get(safe_email, []) + db["study_missions"].get(safe_email, [])
        done_m = len([m for m in all_m if m.get("เสร็จแล้ว")])
        st.metric("ภารกิจที่สำเร็จ", f"{done_m} / {len(all_m)}")
        if len(db["cookie_jar"].get(safe_email, [])) + len(db["excuses"].get(safe_email, [])) > 0:
            st.bar_chart(pd.DataFrame({"จำนวนครั้ง": [len(db["cookie_jar"].get(safe_email, [])), len(db["excuses"].get(safe_email, []))]}, index=["Savage (ชนะ)", "Bitch (ข้ออ้าง)"]))
