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
# 1. ตั้งค่าระบบ (THE IMMORTAL SOUL V.42 - THE FLAWLESS COMMAND)
# ==========================================
st.set_page_config(page_title="THE BRAIN WAR", layout="wide", page_icon="🧠")

# 🎨 Custom CSS แต่ง UI ให้พรีเมียม โหด ดุดัน (แถบเมนูบนไม่หาย ล็อกอินได้ปกติ)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ปรับแต่งกรอบ Container ให้โค้งมนและดูเป็น Card */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #1a1a24;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #3a3a4f;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* แต่ง Tab ให้โดดเด่น */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
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
    
    /* เอฟเฟกต์ปุ่ม */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.03);
    }
</style>
""", unsafe_allow_html=True)

# ⚠️ ลิงก์ Firebase ของมึง
FIREBASE_URL = "https://mytaskpro-f7328-default-rtdb.asia-southeast1.firebasedatabase.app" 
FIREBASE_SECRET = "Wv2Ha7WZrDLwnpJyKMt29z9I0MGb0kxitoOaaoGe"

def get_current_thai_time():
    tz_thai = timezone(timedelta(hours=7))
    return datetime.now(tz_thai)

now_thai = get_current_thai_time()
today_date = now_thai.date()
today_str = str(today_date)

ROLE_MAP = {
    "Vanguard": "⚡ [ทัพหน้า]", 
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
    if not dl_str or dl_str == "": return 999999
    try:
        dl_date = datetime.strptime(dl_str, "%Y-%m-%d").date()
        return (dl_date - today_date).days
    except:
        return 999999

def calculate_task_rewards(task, current_streak):
    score = get_priority_score(task.get("ประเภท", ""))
    base_exp = 40 if score == 1 else 20 if score == 2 else 10
    
    bonus_exp = 0
    if task.get("is_boss"): bonus_exp += 100
    if task.get("bounty"): bonus_exp += 50
    if task.get("subtasks"): bonus_exp += len(task["subtasks"]) * 10  
        
    raw_total_exp = base_exp + bonus_exp
    multiplier = 1.5 if current_streak >= 30 else 1.2 if current_streak >= 7 else 1.1 if current_streak >= 3 else 1.0
    final_exp = int(raw_total_exp * multiplier)
    
    fail_reduce = 10 if score == 1 else 5 if score == 2 else 2
    if task.get("is_boss"): fail_reduce += 15
    if task.get("bounty"): fail_reduce += 5
    
    return final_exp, fail_reduce

def load_db():
    if FIREBASE_URL == "" or FIREBASE_URL is None:
        st.error("🚨 ไอ้เวร! ลิงก์ Firebase หายไปไหน กลับไปแก้เดี๋ยวนี้!")
        st.stop()
    try:
        res = requests.get(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}")
        if res.status_code == 200 and res.json() is not None:
            data = res.json()
            defaults = {
                "users": {}, "missions": {}, "study_missions": {}, 
                "backlog": {}, "dark_room": {}, "anti_simp": {}, 
                "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, 
                "deadlines": {}, "haters": {}, "finance": {}, 
                "iron_habits": {}, "exams": {}, "beat_yesterday": {}, 
                "limit_breaks": {}
            }
            for k, v in defaults.items():
                if k not in data: 
                    data[k] = v
            return data
    except: 
        pass
    return {
        "users": {}, "missions": {}, "study_missions": {}, "backlog": {}, 
        "dark_room": {}, "anti_simp": {}, "dopamine_fails": {}, 
        "excuses": {}, "cookie_jar": {}, "deadlines": {}, "haters": {}, 
        "finance": {}, "iron_habits": {}, "exams": {}, "beat_yesterday": {}, 
        "limit_breaks": {}
    }

def save_db(data):
    try: 
        requests.put(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}", json=data)
    except: 
        st.error("🚨 เซฟข้อมูลลงฐานข้อมูลอมตะไม่สำเร็จ!")

# ==========================================
# 🗺️ THE WAR MAP ENGINE (แกนวาดแผนผังใหม่ V.42 ซ่อมบัค 100%)
# ==========================================
def render_war_map(missions_data, study_data):
    pending_missions = [m for m in missions_data if not m.get('เสร็จแล้ว', False)]
    pending_study = [s for s in study_data if not s.get('เสร็จแล้ว', False)]
    
    if not pending_missions and not pending_study:
        st.info("🗺️ กระดานยุทธศาสตร์ว่างเปล่า ไม่มีภารกิจค้างรอทำ!")
        return

    # ใช้ทิศทางกราฟจากซ้ายไปขวา (LR) ให้ใหญ่เต็มตาอ่านง่ายขึ้นเยอะ
    mermaid_code = "graph LR\n"
    
    # 🎨 กำหนดสไตล์ความปลอดภัย ลบคำสั่งป่วนเกลี้ยงหลอด
    mermaid_code += "classDef active fill:#b37700,color:#fff,stroke:#ffaa00,stroke-width:3px;\n"
    mermaid_code += "classDef blocked fill:#2a2a35,color:#888,stroke:#4d4d4d,stroke-width:2px,stroke-dasharray: 5 5;\n"
    mermaid_code += "classDef boss fill:#8a0303,color:#fff,stroke:#ff3333,stroke-width:3px;\n"

    def build_chain(task_list, chain_id):
        code = ""
        # จัดคิวเรียงลำดับอิงตามค่ายกลยุทธ์ (ทัพหน้า -> ทัพหลวง -> ทัพหนุน)
        task_list.sort(key=lambda x: (
            get_role_score(x.get("battle_role", "Main")), 
            0 if x.get("is_boss") else 1, 
            get_deadline_score(x.get("deadline", "")),
            get_priority_score(x.get("ประเภท", ""))
        ))
        
        prev_id = None
        active_found = False
        
        for t in task_list:
            safe_id = f"{chain_id}_{t['id'].replace('-', '')}"
            # เคลียร์ล้างอักขระพิเศษ ป้องกันกราฟพังขาวโพลนถาวร
            safe_name = re.sub(r'["\'\[\]{}()<>]', '', t['ภารกิจ'])
            if len(safe_name) > 30: safe_name = safe_name[:30] + "..."
            
            is_frozen = t.get("skip_today_date") == today_str
            is_overdue = False
            if t.get("deadline"):
                try: is_overdue = (datetime.strptime(t["deadline"], "%Y-%m-%d").date() < today_date)
                except: pass
            
            eff_frozen = is_frozen and not is_overdue
            
            # ตรรกะล็อกสิทธิ์อัตโนมัติตามสายพานคิวงาน
            is_blocked = False
            if eff_frozen:
                is_blocked = True
            else:
                if not active_found:
                    active_found = True
                    is_blocked = False
                else:
                    is_blocked = True
            
            status_class = "boss" if t.get("is_boss") and not is_blocked else ("blocked" if is_blocked else "active")
            prefix = "💀 " if t.get("is_boss") else ""
            role_icon = "⚡" if t.get("battle_role") == "Vanguard" else "⚔️" if t.get("battle_role") == "Main" else "🏹"
            
            # ใช้สัญลักษณ์เครื่องหมายปีกกาคู่ (...) เพื่อให้กล่องมนสวยงามตามมาตรฐานระบบ
            label = f"{role_icon} {prefix}{safe_name}"
            code += f'    {safe_id}("{label}")\n'
            code += f'    class {safe_id} {status_class};\n'
            
            if prev_id:
                code += f'    {prev_id} ==> {safe_id}\n'
            prev_id = safe_id
            
        return code

    # 🔥 ซ่อมแซมระบบครอบชื่อ Subgraph ป้องกันอักขระพิเศษพ่นบัคพังทลาย
    if pending_missions:
        mermaid_code += 'subgraph missions_group ["⚔️ สายการรบ (Missions)"]\n'
        mermaid_code += build_chain(pending_missions, "M")
        mermaid_code += "end\n"
        
    if pending_study:
        mermaid_code += 'subgraph study_group ["📚 สายวิชาการ (Study)"]\n'
        mermaid_code += build_chain(pending_study, "S")
        mermaid_code += "end\n"

    html_code = f"""
    <style>
        .mermaid svg {{ max-width: 100%; height: auto; font-family: 'Kanit', sans-serif; }}
        .node text {{ font-size: 16px !important; font-weight: bold; }}
        .cluster rect {{ fill: #1e1e2d !important; stroke: #3a3a4f !important; stroke-width: 2px !important; rx: 15px !important; }}
        .cluster text {{ fill: #ffffff !important; font-size: 20px !important; font-weight: bold !important; }}
    </style>
    <div class="mermaid" style="background-color: #12121c; padding: 30px; border-radius: 12px; display: flex; justify-content: center; min-height: 400px; overflow-x: auto;">
        {mermaid_code}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'dark', flowchart: {{ curve: 'basis', htmlLabels: true, nodeSpacing: 60, rankSpacing: 80 }} }});
    </script>
    """
    components.html(html_code, height=550, scrolling=True)

def get_pending_task_options(task_list):
    options = {"🟢 ไม่มี (ทำได้เลย)": None}
    for t in task_list:
        if not t.get("เสร็จแล้ว", False):
            prefix = "📚 " if t.get("is_study") else "🔪 "
            options[f"{prefix}{t['ภารกิจ']}"] = t['id']
    return options

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
    st.caption(f"🗓️ เวลาสมรภูมิ: {today_str}") 
    
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
                            "username": name_input, "level": 1, "exp": 0, "streak": 0, 
                            "blood_debt": 0, "in_cage": False, "ghost_exp": 0, "ambush_task": "", 
                            "failure_prob": 10, "last_login": today_str, "cleared_yesterday": True,
                            "order_locked": False, "target_name": "ทำ 10 ล้านวิว YouTube Shorts", 
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
        if current_streak >= 30: st.success("👑 BUFF: โบนัส EXP x 1.5 (ร่างทองคำ)")
        elif current_streak >= 7: st.success("🔥 BUFF: โบนัส EXP x 1.2 (นักรบคุ้มคลั่ง)")
        elif current_streak >= 3: st.success("⚡ BUFF: โบนัส EXP x 1.1 (เริ่มเข้าฝัก)")
        else: st.caption("💀 BUFF: ไม่มีโบนัส (กระจอก)")
        
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
            
        prog_val = max(0.0, min(1.0, u_data["exp"] / 100))
        st.progress(prog_val, text=f"Lv.{u_data['level']} | EXP: {u_data['exp']}/100")
        
        st.divider()
        monk_mode = st.toggle("🧘‍♂️ โหมดจำศีล (Monk Mode)")
        if st.button("🚪 ถอยทัพ (ออกจากระบบ)"):
            st.session_state.current_user = None
            st.rerun()

if st.session_state.current_user is None:
    st.title("🧠 THE BRAIN WAR V.42")
    st.info("👈 เลือกชื่อตัวเองแล้วกดปุ่ม 'เปิดสมอง!' เพื่อเข้าใช้งาน!")
    st.stop()

safe_email = st.session_state.current_user
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
    except: pass

if overdue_count > 0:
    user["failure_prob"] = min(100, user["failure_prob"] + (10 * overdue_count))
    user["blood_debt"] += (50 * overdue_count)
    user["in_cage"] = True
    save_db(db)
    st.error(f"🚨 ไอ้หน้าโง่! มึงมีงานดองเกินกำหนด {overdue_count} งาน! แท่นพิพากษายัดหนี้เลือดมึงแล้ว รีบไปเคลียร์ซะ!")

# ==========================================
# 4. ส่วนหัว: FUTURE COUNTDOWN
# ==========================================
try: t_date = datetime.strptime(user["target_date"], "%Y-%m-%d").date()
except: t_date = today_date + timedelta(days=90)
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

if user.get("in_cage"): st.error("🚨 **มึงอยู่ในกรง!** วิดพื้นจ่ายหนี้เลือดซะ!")

st.divider()

# ==========================================
# 5. DUAL REALITY DASHBOARD
# ==========================================
if monk_mode:
    st.markdown("## 🧘‍♂️ MONK MODE ACTIVE: สมาธิขั้นสุด!")
    colLeft, colRight = st.columns([0.01, 1]) 
else: 
    colLeft, colRight = st.columns([1, 2.3])

with colLeft:
    if not monk_mode:
        with st.container(border=True):
            st.markdown("### 🗑️ THE BITCH ZONE")
            st.warning(random.choice(LAZY_VOICES))
            
            fail_prob = user.get('failure_prob', 10)
            st.markdown(f"**📉 โอกาสพ่ายแพ้ต่อสิ่งเร้า: {fail_prob}%**")
            st.progress(fail_prob / 100)
            st.caption("🚨 ถ้าระเบิดถึง 100% มึงเตรียมตัวรับกรรมอย่างสาสมได้เลย!")
                
            with st.form("excuse_form", clear_on_submit=True):
                exc_text = st.text_input("ข้ออ้างขยะๆ วันนี้คืออะไร?:")
                if st.form_submit_button("บันทึกข้ออ้าง"):
                    if exc_text:
                        db["excuses"][safe_email].append({"font": today_str, "ข้ออ้าง": exc_text})
                        user["failure_prob"] = min(100, user["failure_prob"] + 10)
                        save_db(db); st.rerun()
                        
            if st.button("💀 แท่นประหาร: กูแพ้ให้สิ่งเร้าขยะ", use_container_width=True):
                db["dopamine_fails"][safe_email].append(today_str)
                user["exp"] = 0; user["blood_debt"] += 50; user["in_cage"] = True
                user["failure_prob"] = min(100, user["failure_prob"] + 20)
                save_db(db); st.rerun()

            st.markdown("#### 🩸 บัญชีแค้น (THE HATER'S WALL)")
            with st.form("hater_form", clear_on_submit=True):
                h_text = st.text_input("คำดูถูกที่มึงเจอ:")
                if st.form_submit_button("ฝังความแค้น"):
                    if h_text: 
                        db["haters"][safe_email].append(h_text)
                        save_db(db); st.rerun()
            if db["haters"][safe_email]: st.error(f"🤬 คำดูถูก: \"{random.choice(db['haters'][safe_email])}\"")

with colRight:
    st.markdown("## ⚔️ THE SAVAGE ZONE (นักรบฝั่งขวา)")
    st.success(random.choice(SAVAGE_VOICES))
    
    # 📌 เปิดแผนผังรบยุทธศาสตร์เวอร์ชันแก้ไขบัคถาวร ตัวใหญ่ คมชัด 
    with st.expander("🗺️ เปิดแผนผังยุทธศาสตร์ (The War Map)", expanded=True):
        render_war_map(db["missions"][safe_email], db["study_missions"][safe_email])
        st.caption("<span style='color:#1a4d1a;'>🟢 สีเขียว = กำลังรบจุดปัจจุบัน</span> | <span style='color:#262626;'>⚪ สีเทาเส้นประ = ติดล็อกคิวงานถัดไป</span> | <span style='color:#ff0000;'>🔴 กรอบแดง = BOSS FIGHT</span>", unsafe_allow_html=True)
    
    all_active_tasks = db["missions"][safe_email] + db["study_missions"][safe_email]
    task_done_map = {t['id']: t.get('เสร็จแล้ว', False) for t in all_active_tasks}
    
    tab_missions, tab_study, tab_habits, tab_backlog, tab_cookie, tab_academic = st.tabs([
        "🔥 ภารกิจวันนี้", "📖 ภารกิจการเรียน", "⛓️ วินัยเหล็ก", "📝 สมุดจดงาน", "🍪 โหลคุกกี้", "📚 ลานประลองปัญญา"
    ])
    
    # ----------------------------------------------------
    # TAB 1: ภารกิจวันนี้ (Daily Missions)
    # ----------------------------------------------------
    with tab_missions:
        st.markdown("### 🪵 The Daily Siege (ตารางรบวันนี้)")
        
        raw_active_missions = [m for m in db["missions"][safe_email] if not m.get("เสร็จแล้ว")]
        active_single_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False) and not m.get("subtasks")]
        
        if len(active_single_missions) >= 3:
            st.error("🚨 **กฎเหล็กจอมทัพ:** โควตางานเดี่ยววันนี้เต็ม 3 Slot แล้ว! รีบเคลียร์ของเก่า!")
        
        with st.expander("➕ เพิ่มงานด่วนวันนี้ (ไม่ผ่านสมุด)"):
            with st.form("mission_form", clear_on_submit=True):
                m_name = st.text_input("ชื่อภารกิจ:")
                m_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด (คอขาดบาดตาย)", "🔥 งานฉุกเฉิน / Special Event", "🟡 ปานกลาง (ต้องเสร็จ)", "🟢 ชิลๆ (ทำตอนว่าง)"])
                
                c_b1, c_b2 = st.columns(2)
                m_is_boss = c_b1.checkbox("💀 ตั้งเป็น THE BOSS FIGHT")
                m_bounty = c_b2.checkbox("⚔️ ตั้งค่าหัว! (เดิมพันศักดิ์ศรี)")
                
                m_subtasks_text = st.text_area("🔪 สับท่อนซุง (ใส่ชื่อย่อยทีละบรรทัด, ไม่บังคับ):")
                m_dl_type = st.radio("⏰ ระบบเวลา:", ["ไม่กำหนด (ชิลๆ)", "🗓️ Deadline ทางการ", "🎯 วันเป้าหมาย (กำหนดเอง)"], horizontal=True)
                m_deadline = st.date_input("เลือกวันที่:")
                
                if st.form_submit_button("เพิ่มภารกิจ"):
                    if m_name:
                        subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in m_subtasks_text.split('\n') if s.strip()]
                        if not subtasks and len(active_single_missions) >= 3:
                            st.error("🤡 ระบบบล็อกไม่ให้เพิ่ม! โควตางานเดี่ยวเต็ม บังคับให้สับข้อย่อยท่อนซุงซะ!")
                        else:
                            final_dl = str(m_deadline) if m_dl_type != "ไม่กำหนด (ชิลๆ)" else ""
                            db["missions"][safe_email].append({
                                "id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": m_name, 
                                "ประเภท": m_type, "bounty": m_bounty, "is_boss": m_is_boss,
                                "custom_order": 99, "battle_role": "Main", "is_queued": False, 
                                "skip_today_date": "", "subtasks": subtasks, "เสร็จแล้ว": False, 
                                "รอตรวจ": False, "deadline": final_dl, "deadline_type": m_dl_type, "prereq_id": None
                            })
                            save_db(db); st.rerun()
                    
        todo_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False)]
        pending_missions = [m for m in raw_active_missions if m.get("รอตรวจ", False)]
        
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
                    st.write("จอมทัพ! เลือกตำแหน่งกระบวนทัพ (ทัพหน้าจะได้โบนัส First Strike +20 EXP!)")
                    updated_orders, updated_roles = {}, {}
                    for m in needs_queueing:
                        is_boss_str = "💀 [BOSS] " if m.get("is_boss") else ""
                        role_choice = st.selectbox(f"วางตำแหน่งทัพ: {is_boss_str}{m['ภารกิจ']}", 
                                                   ["⚡ ทัพหน้า (Vanguard - โบนัส First Strike +20 EXP)", "⚔️ ทัพหลวง (Main Force)", "🏹 ทัพหนุน (Support)"], 
                                                   key=f"setup_role_{m['id']}")
                        if "ทัพหน้า" in role_choice: updated_orders[m["id"]] = 1; updated_roles[m["id"]] = "Vanguard"
                        elif "ทัพหลวง" in role_choice: updated_orders[m["id"]] = 2; updated_roles[m["id"]] = "Main"
                        else: updated_orders[m["id"]] = 3; updated_roles[m["id"]] = "Support"
                    if st.form_submit_button("🔒 ล็อกค่ายกลกระบวนทัพ!"):
                        for m in db["missions"][safe_email]:
                            if m["id"] in updated_orders:
                                m["custom_order"] = updated_orders[m["id"]]; m["battle_role"] = updated_roles[m["id"]]; m["is_queued"] = True
                        save_db(db); st.rerun()

        # ระบบคำนวณลูกโซ่ล็อกงานอัตโนมัติ (Sequential Latching)
        active_m_found = False
        for m in todo_missions:
            is_frozen = m.get("skip_today_date") == today_str
            is_overdue = False
            if m.get("deadline"):
                try: is_overdue = (datetime.strptime(m["deadline"], "%Y-%m-%d").date() < today_date)
                except: pass
            if is_frozen and not is_overdue:
                m['_is_blocked'] = True
            else:
                if not active_m_found:
                    m['_is_blocked'] = False
                    active_m_found = True
                else:
                    m['_is_blocked'] = True

        if todo_missions:
            for m in todo_missions:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6]) 
                    is_blocked = m.get('_is_blocked', False)
                    
                    task_mode_badge = "🔪 **[งานใหญ่]**" if m.get("subtasks") else "⚡ **[ม้วนเดียวจบ]**"
                    is_bounty = " ⚔️[เดิมพัน]" if m.get("bounty") else ""
                    is_boss = " 💀 **[BOSS]**" if m.get("is_boss") else ""
                    order_badge = f" | {ROLE_MAP.get(m.get('battle_role', 'Main'), '⚔️ [ทัพหลวง]')}"
                    
                    is_overdue, deadline_badge = False, ""
                    if m.get("deadline"):
                        try:
                            dl_date = datetime.strptime(m["deadline"], "%Y-%m-%d").date()
                            days_left_task = (dl_date - today_date).days
                            if days_left_task > 0: deadline_badge = f" ⏳ (เหลือ {days_left_task} วัน)"
                            elif days_left_task == 0: deadline_badge = f" 🚨 **(ต้องเสร็จวันนี้!)**"
                            else: deadline_badge = f" 💀 **(เลยกำหนดมา {-days_left_task} วัน)**"; is_overdue = True 
                        except: pass

                    is_frozen = m.get("skip_today_date") == today_str
                    was_frozen_yesterday = m.get("skip_today_date") != "" and not is_frozen
                    if was_frozen_yesterday:
                        m["skip_today_date"] = ""; save_db(db)
                        
                    frozen_badge = " ❄️🚨 [เกราะแตก!]" if (is_frozen and is_overdue) else " ❄️ [แช่แข็ง]" if is_frozen else ""

                    if is_blocked:
                        c1.markdown(f"🔒 **<span style='color:#777;'>[ติดล็อกลำดับคิวแผนรบ] {m['ภารกิจ']}{is_boss}</span>**", unsafe_allow_html=True)
                        c1.caption(f"⚠️ *จอมทัพต้องปิดงานแรกในแผนผังยุทธศาสตร์ก่อน ถึงจะปลดล็อกเป้าหมายนี้ได้!*")
                    else:
                        c1.write(f"**{m.get('ประเภท','')}** | {task_mode_badge}{is_boss}{is_bounty} {m['ภารกิจ']}{order_badge}{deadline_badge}{frozen_badge}")
                    
                    all_done = True
                    if m.get("subtasks"):
                        total_subs = len(m["subtasks"])
                        done_subs = len([s for s in m["subtasks"] if s.get("done")])
                        st.progress(done_subs / total_subs if total_subs > 0 else 0, text=f"📊 ความคืบหน้าการสับซุง: {done_subs} / {total_subs}")
                        
                        for i, stask in enumerate(m["subtasks"]):
                            is_done = stask.get("done", False)
                            is_locked = is_done and stask.get("done_date", "") != today_str
                            label = f"{stask['name']} 🔒 (ผนึกแล้ว)" if is_locked else stask['name']
                                
                            can_interact = not is_locked and (not is_frozen or is_overdue) and not is_blocked
                            checked = st.checkbox(label, value=is_done, disabled=not can_interact, key=f"st_{m['id']}_{i}")
                            if can_interact and checked != is_done:
                                m["subtasks"][i]["done"] = checked; m["subtasks"][i]["done_date"] = today_str if checked else ""; save_db(db); st.rerun()
                        all_done = all(stask.get("done", False) for stask in m["subtasks"])
                    else: all_done = True 

                    if not is_blocked:
                        if is_frozen:
                            if c4.button("🔥 ปลดล็อก", key=f"unfrz_{m['id']}", use_container_width=True): m["skip_today_date"] = ""; save_db(db); st.rerun()
                        else:
                            if c4.button("❄️ เลื่อนฉุกเฉิน", key=f"frz_{m['id']}", use_container_width=True): m["skip_today_date"] = today_str; save_db(db); st.rerun()

                    if is_blocked: c2.error("🔒 รอปลดล็อก")
                    elif all_done and (not is_frozen or is_overdue):
                        if c2.button("✅ สำเร็จ", key=f"m_{m['id']}"):
                            m["เสร็จแล้ว"] = True
                            exp_gain, fail_reduce = calculate_task_rewards(m, current_streak)
                            if m.get("battle_role") == "Vanguard": exp_gain += 20; st.toast("⚡ FIRST STRIKE! +20 EXP!", icon="⚡")
                            user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce); save_db(db); st.balloons(); st.rerun()
                        if c3.button("📤 ส่ง/รอตรวจ", key=f"pend_{m['id']}"): m["รอตรวจ"] = True; save_db(db); st.rerun()
                    else: c2.caption("🔒 งานย่อยคาอยู่") if not is_frozen else c2.caption("❄️ แช่แข็งชั่วคราว")
                    if c5.button("🗑️", key=f"del_m_{m['id']}"): db["missions"][safe_email].remove(m); save_db(db); st.rerun()
        else: st.success("✅ วันนี้เคลียร์ภารกิจหลักหมดแล้ว เยี่ยมมากไอ้เสือ!")

    # ----------------------------------------------------
    # 📖 TAB 2: ภารกิจการเรียนและการทบทวน
    # ----------------------------------------------------
    with tab_study:
        st.markdown("### 📚 The Academic Siege (กระดานคุมการเรียน)")
        raw_active_study = [s for s in db["study_missions"][safe_email] if not s.get("เสร็จแล้ว")]
        active_single_study = [s for s in raw_active_study if not s.get("รอตรวจ", False) and not s.get("subtasks")]
        
        if len(active_single_study) >= 3: st.error("🚨 **กฎเหล็กวิชาการ:** โควตาวิชาทบทวนเดี่ยวเต็ม 3 Slot แล้ว!")
            
        with st.expander("➕ เพิ่มวิชา/เนื้อหาที่ต้องทบทวน"):
            with st.form("study_form", clear_on_submit=True):
                s_name = st.text_input("วิชา / หัวข้อ:")
                s_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด (สอบพรุ่งนี้/มะรืน)", "🔥 ติวเข้ม Special Event", "🟡 ปานกลาง (ทบทวนเรื่อยๆ)", "🟢 ชิลๆ (อ่านฆ่าเวลา)"])
                
                c_sb1, c_sb2 = st.columns(2)
                s_is_boss = c_sb1.checkbox("💀 ตั้งเป็นบทโหดไฟลุก")
                s_bounty = c_sb2.checkbox("⚔️ เดิมพันวิชาการ!")
                
                s_subtasks_text = st.text_area("🔪 สับหัวข้อย่อย / บทเรียนที่ต้องเก็บให้ครบ:")
                s_dl_type = st.radio("⏰ ระบบเวลา:", ["ไม่กำหนด (ชิลๆ)", "🗓️ Deadline ทางการ", "🎯 วันเป้าหมาย (กำหนดเอง)"], horizontal=True)
                s_deadline = st.date_input("เลือกวันที่:")
                
                if st.form_submit_button("บรรจุเข้าหลักสูตร"):
                    if s_name:
                        subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in s_subtasks_text.split('\n') if s.strip()]
                        if not subtasks and len(active_single_study) >= 3: st.error("🤡 ระบบบล็อกโควตาเต็ม!")
                        else:
                            db["study_missions"][safe_email].append({
                                "id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": s_name, "ประเภท": s_type, 
                                "bounty": s_bounty, "is_boss": s_is_boss, "custom_order": 99, "battle_role": "Main", 
                                "is_queued": False, "skip_today_date": "", "subtasks": subtasks, "เสร็จแล้ว": False, 
                                "รอตรวจ": False, "deadline": str(s_deadline) if s_dl_type != "ไม่กำหนด" else "", "deadline_type": s_dl_type, "is_study": True
                            })
                            save_db(db); st.rerun()
                            
        todo_study = [s for s in raw_active_study if not s.get("รอตรวจ", False)]
        pending_study = [s for s in raw_active_study if s.get("รอตรวจ", False)]
        
        todo_study.sort(key=lambda x: (get_role_score(x.get("battle_role", "Main")), 0 if x.get("is_boss") else 1, get_deadline_score(x.get("deadline", "")), get_priority_score(x.get("ประเภท", ""))))
        
        study_needs_queueing = [s for s in todo_study if not s.get("is_queued", False)]
        if study_needs_queueing:
            with st.expander("⚔️📖 บัญชาการค่ายกลกระบวนทัพการเรียน", expanded=True):
                with st.form("lock_study_order_form"):
                    updated_s_orders, updated_s_roles = {}, {}
                    for s in study_needs_queueing:
                        role_choice = st.selectbox(f"วางตำแหน่งวิชา: {s['ภารกิจ']}", ["⚡ ทัพหน้า", "⚔️ ทัพหลวง", "🏹 ทัพหนุน"], key=f"setup_s_role_{s['id']}")
                        if "ทัพหน้า" in role_choice: updated_s_orders[s["id"]] = 1; updated_s_roles[s["id"]] = "Vanguard"
                        elif "ทัพหลวง" in role_choice: updated_s_orders[s["id"]] = 2; updated_s_roles[s["id"]] = "Main"
                        else: updated_s_orders[s["id"]] = 3; updated_s_roles[s["id"]] = "Support"
                    if st.form_submit_button("🔒 ล็อกค่ายกลการศึกษา!"):
                        for s in db["study_missions"][safe_email]:
                            if s["id"] in updated_s_orders: s["custom_order"] = updated_s_orders[s["id"]]; s["battle_role"] = updated_s_roles[s["id"]]; s["is_queued"] = True
                        save_db(db); st.rerun()

        # ล็อกลำดับฝั่งการเรียนแบบอัตโนมัติ
        active_s_found = False
        for s in todo_study:
            is_frozen = s.get("skip_today_date") == today_str
            is_overdue = False
            if s.get("deadline"):
                try: is_overdue = (datetime.strptime(s["deadline"], "%Y-%m-%d").date() < today_date)
                except: pass
            if is_frozen and not is_overdue: s['_is_blocked'] = True
            else:
                if not active_s_found: s['_is_blocked'] = False; active_s_found = True
                else: s['_is_blocked'] = True

        if todo_study:
            for s in todo_study:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6])
                    is_blocked = s.get('_is_blocked', False)
                    
                    task_mode_badge = "📖 **[โครงการใหญ่]**" if s.get("subtasks") else "⚡ **[ทบทวนรอบเดียว]**"
                    is_bounty = " ⚔️" if s.get("bounty") else ""
                    is_boss = " 💀 **[BOSS]**" if s.get("is_boss") else ""
                    order_badge = f" | {ROLE_MAP.get(s.get('battle_role', 'Main'), '⚔️ [ทัพหลวง]')}"
                    
                    is_overdue, deadline_badge = False, ""
                    dl_str = s.get("deadline", "")
                    if dl_str and dl_str != "":
                        try:
                            days_left_task = (datetime.strptime(dl_str, "%Y-%m-%d").date() - today_date).days
                            if days_left_task > 0: deadline_badge = f" ⏳ (เหลือ {days_left_task} วัน)"
                            elif days_left_task == 0: deadline_badge = f" 🚨 **(ถึงกำหนดวันนี้!)**"
                            else: deadline_badge = f" 💀 **(เลยมาแล้ว {-days_left_task} วัน)**"; is_overdue = True
                        except: pass

                    is_frozen = s.get("skip_today_date") == today_str
                    was_frozen_yesterday = s.get("skip_today_date") != "" and not is_frozen
                    if was_frozen_yesterday: s["skip_today_date"] = ""; save_db(db)
                    frozen_badge = " ❄️🚨 [ค่ายกลแตก!]" if (is_frozen and is_overdue) else " ❄️ [แช่แข็ง]" if is_frozen else ""

                    if is_blocked: c1.markdown(f"🔒 **<span style='color:#777;'>[ติดล็อกรอคิววิชาหลัก] {s['ภารกิจ']}{is_boss}</span>**", unsafe_allow_html=True)
                    else: c1.write(f"**{s.get('ประเภท','')}** | {task_mode_badge}{is_boss}{is_bounty} {s['ภารกิจ']}{order_badge}{deadline_badge}{frozen_badge}")
                    
                    all_done = True
                    if s.get("subtasks"):
                        total_subs = len(s["subtasks"])
                        done_subs = len([stk for stk in s["subtasks"] if stk.get("done")])
                        st.progress(done_subs / total_subs if total_subs > 0 else 0, text=f"📈 ความคืบหน้า: {done_subs} / {total_subs}")

                        for i, stask in enumerate(s["subtasks"]):
                            is_done = stask.get("done", False)
                            is_locked = is_done and stask.get("done_date", "") != today_str
                            label = f"{stask['name']} 🔒" if is_locked else stask['name']
                                
                            can_interact = not is_locked and (not is_frozen or is_overdue) and not is_blocked
                            checked = st.checkbox(label, value=is_done, disabled=not can_interact, key=f"st_stud_{s['id']}_{i}")
                            if can_interact and checked != is_done:
                                s["subtasks"][i]["done"] = checked; s["subtasks"][i]["done_date"] = today_str if checked else ""; save_db(db); st.rerun()
                        all_done = all(stask.get("done", False) for stask in s["subtasks"])
                    else: all_done = True

                    if not is_blocked:
                        if is_frozen:
                            if c4.button("🔥 ปลดแช่", key=f"unfrz_stud_{s['id']}", use_container_width=True): s["skip_today_date"] = ""; save_db(db); st.rerun()
                        else:
                            if c4.button("❄️ เลื่อนวิชา", key=f"frz_stud_{s['id']}", use_container_width=True): s["skip_today_date"] = today_str; save_db(db); st.rerun()

                    if is_blocked: c2.error("🔒 รอวิชาหลัก")
                    elif all_done and (not is_frozen or is_overdue):
                        if c2.button("✅ ติวสำเร็จ", key=f"stud_win_{s['id']}", use_container_width=True):
                            s["เสร็จแล้ว"] = True; exp_gain, fail_reduce = calculate_task_rewards(s, current_streak)
                            if s.get("battle_role") == "Vanguard": exp_gain += 20
                            user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce); save_db(db); st.balloons(); st.rerun()
                        if c3.button("📤 ส่งรออนุมัติ", key=f"pend_stud_{s['id']}", use_container_width=True): s["รอตรวจ"] = True; save_db(db); st.rerun()
                    else: c2.caption("🔒 ค้างอยู่")
                    if c5.button("🗑️", key=f"del_stud_{s['id']}"): db["study_missions"][safe_email].remove(s); save_db(db); st.rerun()
        else: st.success("📚 ติวทบทวนเนื้อหาครบหมดแล้ว ร่างสมองมึงแกร่งกล้าพร้อมรบทุกห้องสอบ!")

    # ----------------------------------------------------
    # TAB 3: วินัยเหล็ก (THE IRON HABITS)
    # ----------------------------------------------------
    with tab_habits:
        st.markdown("### ⛓️ THE IRON HABITS (วินัยเหล็กรายวัน)")
        with st.form("habit_form", clear_on_submit=True):
            h_name = st.text_input("สร้างวินัยเหล็กใหม่:")
            if st.form_submit_button("เพิ่มวินัยเหล็ก"):
                if h_name: db["iron_habits"][safe_email].append({"id": str(uuid.uuid4()), "name": h_name, "last_done_date": ""}); save_db(db); st.rerun()
                    
        if db["iron_habits"][safe_email]:
            for h in db["iron_habits"][safe_email]:
                c1, c2, c3 = st.columns([5, 3, 1])
                c1.write(f"⛓️ **{h['name']}**")
                if h.get("last_done_date") == today_str: c2.success("✅ ทำแล้ววันนี้")
                else:
                    if c2.button("🔥 กูทำสำเร็จ!", key=f"h_done_{h['id']}"):
                        h["last_done_date"] = today_str
                        bonus = 10 if current_streak >= 30 else 7 if current_streak >= 7 else 5
                        fail_sub = 5 if current_streak >= 30 else 3 if current_streak >= 7 else 2
                        user["exp"] += bonus; user["failure_prob"] = max(0, user["failure_prob"] - fail_sub); save_db(db); st.balloons(); st.rerun()
                if c3.button("🗑️", key=f"del_h_{h['id']}"): db["iron_habits"][safe_email].remove(h); save_db(db); st.rerun()

    # ----------------------------------------------------
    # TAB 4: สมุดจดงาน (Backlog)
    # ----------------------------------------------------
    with tab_backlog:
        st.markdown("### 📝 สมุดจดงาน (Task Backlog)")
        with st.form("backlog_form", clear_on_submit=True):
            b_name = st.text_input("หัวข้องาน/เนื้อหา/ไอเดียยูทูป:")
            b_detail = st.text_area("รายละเอียด/Note (ถ้ามี):")
            b_subtasks_text = st.text_area("🔪 ซอยงานย่อย (Enter ขึ้นบรรทัดใหม่):")
            b_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"])
            b_dl_type = st.radio("⏰ ระบบเวลา:", ["ไม่กำหนด (ชิลๆ)", "🗓️ Deadline ทางการ", "🎯 วันเป้าหมาย (กำหนดเอง)"], horizontal=True)
            b_deadline = st.date_input("วันกำหนดส่ง:")
            
            if st.form_submit_button("💾 บันทึกลงสมุด"):
                if b_name:
                    b_subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in b_subtasks_text.split('\n') if s.strip()]
                    db["backlog"][safe_email].append({
                        "id": str(uuid.uuid4()), "ภารกิจ": b_name, "รายละเอียด": b_detail, "subtasks": b_subtasks, "ประเภท": b_type, "deadline": str(b_deadline) if b_dl_type != "ไม่กำหนด" else "", "deadline_type": b_dl_type
                    })
                    save_db(db); st.rerun()
                    
        if db["backlog"][safe_email]:
            sorted_backlog = sorted(db["backlog"][safe_email], key=lambda x: x.get("deadline") if x.get("deadline") and x.get("deadline") != "" else "9999-12-31")
            for b_task in sorted_backlog:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([4, 2, 2, 0.8])
                    dl_str = b_task.get("deadline", "")
                    c1.write(f"**{b_task['ประเภท']}** | 📝 {b_task['ภารกิจ']}")
                    c1.caption(f"เวลาเป้าหมาย: {dl_str if dl_str else 'ไม่กำหนด'} | รายละเอียด: {b_task.get('รายละเอียด', '-')}")
                    
                    if c2.button("⚡ เข้าช่องงาน", key=f"pull_m_{b_task['id']}", type="primary"):
                        db["missions"][safe_email].append({
                            "id": b_task["id"], "วันที่": today_str, "ภารกิจ": b_task["ภารกิจ"], "ประเภท": b_task["ประเภท"], "bounty": False, "is_boss": False, "custom_order": 99, "battle_role": "Main", "is_queued": False, "skip_today_date": "", "deadline": dl_str, "deadline_type": b_task.get("deadline_type", "🗓️"), "subtasks": b_task.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False
                        })
                        db["backlog"][safe_email].remove(b_task); save_db(db); st.rerun()
                    if c3.button("📖 เข้าช่องเรียน", key=f"pull_s_{b_task['id']}", type="secondary"):
                        db["study_missions"][safe_email].append({
                            "id": b_task["id"], "วันที่": today_str, "ภารกิจ": b_task["ภารกิจ"], "ประเภท": b_task["ประเภท"], "bounty": False, "is_boss": False, "custom_order": 99, "battle_role": "Main", "is_queued": False, "skip_today_date": "", "deadline": dl_str, "deadline_type": b_task.get("deadline_type", "🗓️"), "subtasks": b_task.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False, "is_study": True
                        })
                        db["backlog"][safe_email].remove(b_task); save_db(db); st.rerun()
                    if c4.button("🗑️", key=f"del_b_{b_task['id']}"): db["backlog"][safe_email].remove(b_task); save_db(db); st.rerun()

    # ----------------------------------------------------
    # TAB 5: โหลคุกกี้ (Cookie Jar)
    # ----------------------------------------------------
    with tab_cookie:
        st.markdown("### 🍪 THE COOKIE JAR (โหลเก็บความภูมิใจ)")
        with st.form("cookie_form", clear_on_submit=True):
            win_text = st.text_input("วันนี้มึงชนะใจตัวเองเรื่องอะไรได้บ้าง?:")
            if st.form_submit_button("เก็บชัยชนะลงโหล!"):
                if win_text:
                    db["cookie_jar"][safe_email].append({"วันที่": today_str, "ชัยชนะ": win_text})
                    user["exp"] += int(5 * (1.5 if current_streak>=30 else 1.2 if current_streak>=7 else 1.0)); save_db(db); st.rerun()
        if db["cookie_jar"][safe_email]:
            for c in reversed(db["cookie_jar"][safe_email][-5:]): st.success(f"🏆 **[{c['วันที่']}]** {c['ชัยชนะ']}")

    # ----------------------------------------------------
    # TAB 6: ลานประลองปัญญา
    # ----------------------------------------------------
    with tab_academic:
        st.markdown("### 📚 ลานประลองปัญญา")
        with st.form("exam_form", clear_on_submit=True):
            e_subj = st.text_input("ชื่อวิชาสอบ:")
            e_score = st.number_input("คะแนนล่าสุด:", min_value=0.0, step=0.1)
            if st.form_submit_button("บันทึกคะแนน"):
                if e_subj:
                    if e_subj not in db["exams"][safe_email]: db["exams"][safe_email][e_subj] = []
                    if len(db["exams"][safe_email][e_subj]) > 0:
                        if e_score > db["exams"][safe_email][e_subj][-1]: user["exp"] += 30; st.success("🔥 คะแนนขึ้น!")
                        elif e_score < db["exams"][safe_email][e_subj][-1]: user["blood_debt"] += 50; st.error("🤡 คะแนนร่วง!")
                    db["exams"][safe_email][e_subj].append(e_score); save_db(db); st.rerun()

        if db["exams"][safe_email]:
            cols = st.columns(3)
            for idx, (subj, scores) in enumerate(db["exams"][safe_email].items()):
                if scores: cols[idx%3].metric(subj, scores[-1], round(scores[-1]-scores[-2],2) if len(scores)>1 else None)

        st.divider()
        with st.form("beat_y_form"):
            by_metric = st.text_input("สิ่งที่ใช้วัด:", value=db["beat_yesterday"][safe_email].get("metric_name", ""))
            by_val = st.number_input("จำนวนวันนี้:", min_value=0)
            if st.form_submit_button("ทุบสถิติ"):
                if by_metric:
                    db["beat_yesterday"][safe_email]["metric_name"] = by_metric
                    if "history" not in db["beat_yesterday"][safe_email]: db["beat_yesterday"][safe_email]["history"] = {}
                    y_val = db["beat_yesterday"][safe_email]["history"].get(str(today_date - timedelta(days=1)), 0)
                    if by_val > y_val: user["exp"] += 20; st.success("🔥 ชนะสถิติตัวเองเมื่อวาน!")
                    elif by_val < y_val: user["blood_debt"] += 30; st.error("🚨 แพ้เมื่อวาน!")
                    db["beat_yesterday"][safe_email]["history"][today_str] = by_val; save_db(db); st.rerun()

        st.divider()
        if st.button("🔥 กฎ 40%: กูฝืนทะลุขีดจำกัดได้!", use_container_width=True):
            if today_str not in db["limit_breaks"][safe_email]:
                db["limit_breaks"][safe_email].append(today_str)
                user["exp"] += 50; user["failure_prob"] = max(0, user["failure_prob"] - 15); save_db(db); st.rerun()

    # ทุนสร้างฝัน (Finance)
    st.divider()
    st.markdown("### 💰 คลังสมบัตินักรบ (ทุนสร้างฝัน)")
    c_fin1, c_fin2 = st.columns([2, 1])
    with c_fin1:
        st.write(f"**เป้าหมาย:** {finance.get('goal_name', 'ยังไม่ตั้ง')}")
        prog = max(0.0, min(finance.get('current', 0) / finance.get('goal_amount', 1), 1.0)) if finance.get('goal_amount', 0) > 0 else 0.0
        st.progress(prog, text=f"มีแล้ว: {finance.get('current', 0)} / {finance.get('goal_amount', 0)} บาท")
    with c_fin2:
        with st.popover("⚙️ จัดการเงิน"):
            finance['goal_name'] = st.text_input("ชื่อ:", value=finance.get('goal_name', ''))
            finance['goal_amount'] = st.number_input("จำนวน:", value=finance.get('goal_amount', 0))
            if st.button("ตั้งเป้า"): save_db(db); st.rerun()
            add_amt = st.number_input("บวก/ลด:", value=0)
            if st.button("บันทึกเงิน"): finance['current'] += add_amt; save_db(db); st.rerun()

# ==========================================
# 6. หนี้เลือด & THE JUDGMENT FEED 
# ==========================================
st.divider()
c_bot1, c_bot2 = st.columns(2)
with c_bot1:
    my_exp = ((user["level"] - 1) * 100) + user["exp"]
    st.metric("พลังร่างทอง", f"{user['ghost_exp']} EXP")
    st.metric("พลังของมึงปัจจุบัน", f"{my_exp} EXP", delta=f"{my_exp - user['ghost_exp']} เทียบร่างทอง")
with c_bot2:
    st.markdown("### 🩸 หนี้เลือด")
    st.metric("หนี้วิดพื้นค้างจ่าย", f"{user.get('blood_debt', 0)} ที")
    if user.get("blood_debt", 0) > 0:
        if st.button("กูวิดพื้นใช้หนี้หมดแล้ว!"): user["blood_debt"] = 0; user["in_cage"] = False; save_db(db); st.rerun()

st.divider()
st.markdown("<h2>⚖️ THE JUDGMENT FEED (พิพากษาก่อนนอน)</h2>", unsafe_allow_html=True)
if user.get("ambush_task", "") != "":
    st.error(f"🚨 **โดนซุ่มโจมตี!** : {user['ambush_task']}")
    if st.button("🔥 ทำเสร็จแล้ว!"): user["ambush_task"] = ""; user["exp"] += 20; save_db(db); st.rerun()
elif user.get("cleared_yesterday"): st.success("🔥 พิพากษาเสร็จสิ้น! มึงรอดไปได้อีกหนึ่งวัน!")
else:
    active_for_judgment = []
    for m in db["missions"][safe_email] + db["study_missions"][safe_email]:
        if not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False):
            if m.get("skip_today_date") == today_str:
                is_task_overdue = False
                if m.get("deadline") and m["deadline"] != "":
                    try: is_task_overdue = (datetime.strptime(m["deadline"], "%Y-%m-%d").date() < today_date)
                    except: pass
                if not is_task_overdue: continue 
            if m.get("subtasks"):
                if not any(stask.get("done", False) and stask.get("done_date", "") == today_str for stask in m["subtasks"]): active_for_judgment.append(m)
            else: active_for_judgment.append(m)

    incomplete_habits = [h for h in db["iron_habits"][safe_email] if h.get("last_done_date") != today_str]
    incomplete_bosses = [m for m in active_for_judgment if m.get("is_boss")]

    if incomplete_bosses:
        st.error("💀 ไอ้สวะ! มึงดองงาน BOSS FIGHT!")
        if st.button("🩸 ยอมรับความกาก (รับหนี้ 300 ที!)"):
            user["blood_debt"] += 300; user["failure_prob"] = min(100, user["failure_prob"] + 30); user["in_cage"] = True; user["cleared_yesterday"] = True; user["streak"] = 0; save_db(db); st.rerun()
    elif active_for_judgment or incomplete_habits:
        st.error("❌ ศาลเตี้ยพบงานค้างที่มึงทิ้งขว้าง:")
        total_blood_penalty = sum(100 if get_priority_score(m.get("ประเภท", "")) == 1 else 70 if get_priority_score(m.get("ประเภท", "")) == 2 else 50 for m in active_for_judgment) + (len(incomplete_habits) * 30)
        for m in active_for_judgment: st.write(f"👉 **{m['ภารกิจ']}**")
        for h in incomplete_habits: st.write(f"👉 **{h['name']}** [วินัยรายวัน]")
        if st.button(f"🩸 ยอมรับ (รับหนี้เลือด {total_blood_penalty} ที)"):
            user["blood_debt"] += total_blood_penalty; user["failure_prob"] = min(100, user["failure_prob"] + (10 * (len(active_for_judgment) + len(incomplete_habits)))); user["in_cage"] = True; user["cleared_yesterday"] = True; user["streak"] = 0; save_db(db); st.rerun()
    elif user.get("in_cage") or user.get("blood_debt", 0) > 0: st.error("❌ จ่ายหนี้เลือดก่อนปิดวัน!")
    else:
        c1, c2 = st.columns(2)
        if c1.button("📉 สู้แค่ 40%"): user["exp"] -= 30; user["cleared_yesterday"] = True; user["failure_prob"] = min(100, user["failure_prob"] + 10); user["streak"] = 0; save_db(db); st.rerun()
        if c2.button("🔥 กูใช้พลัง 100%!"):
            if random.random() < 0.2: user["ambush_task"] = random.choice(AMBUSH_TASKS)
            else: user["cleared_yesterday"] = True; user["streak"] += 1; user["exp"] += int(25 * (1.5 if current_streak>=30 else 1.2 if current_streak>=7 else 1.0))
            save_db(db); st.rerun()

# ==========================================
# 8. 📜 พงศาวดารความทรงจำ (HISTORY LOG)
# ==========================================
st.divider()
if not monk_mode:
    st.markdown("## 📜 พงศาวดารความทรงจำ (HISTORY LOG)")
    t1, t2, t3, t4 = st.tabs(["🍪 คลังแสง (ความสำเร็จ)", "🤡 บัญชีหนังหมา (ข้ออ้าง)", "🪵 บันทึกการแบกซุง (ตาราง)", "📊 BATTLE ANALYTICS"])
    with t1:
        for item in reversed(db["cookie_jar"].get(safe_email, [])): st.success(f"🏆 **[{item.get('วันที่', '-')}]** : {item.get('ชัยชนะ', '')}")
    with t2:
        for item in reversed(db["excuses"].get(safe_email, [])): st.error(f"🤡 **[{item.get('วันที่', '-')}]** : {item.get('ข้ออ้าง', '')}")
    with t3:
        total_missions_list = db["missions"].get(safe_email, []) + db["study_missions"].get(safe_email, [])
        if total_missions_list:
            hist_data = [{"วันที่": i.get('วันที่', '-'), "ภารกิจ": i.get('ภารกิจ', ''), "สถานะ": "✅ เสร็จ" if i.get("เสร็จแล้ว") else "❌ ค้าง"} for i in reversed(total_missions_list)]
            st.dataframe(pd.DataFrame(hist_data), use_container_width=True, hide_index=True)
    with t4:
        all_m = db["missions"].get(safe_email, []) + db["study_missions"].get(safe_email, [])
        done_m = len([m for m in all_m if m.get("เสร็จแล้ว")])
        st.metric("ภารกิจที่สำเร็จรวมทั้งหมด", f"{done_m} / {len(all_m)}")
        if len(db["cookie_jar"].get(safe_email, [])) + len(db["excuses"].get(safe_email, [])) > 0:
            st.bar_chart(pd.DataFrame({"จำนวนครั้ง": [len(db["cookie_jar"].get(safe_email, [])), len(db["excuses"].get(safe_email, []))]}, index=["Savage (ชนะ)", "Bitch (ข้ออ้าง)"]))
