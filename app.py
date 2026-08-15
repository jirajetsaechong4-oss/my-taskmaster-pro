import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import requests
import uuid
import hashlib
import random

# ==========================================
# 1. ตั้งค่าระบบ (DISCIPLINE ARC - FLAWLESS EDITION)
# ==========================================
st.set_page_config(page_title="DISCIPLINE ARC", layout="wide", page_icon="⚙️", initial_sidebar_state="expanded")

FIREBASE_URL = "https://mytaskpro-f7328-default-rtdb.asia-southeast1.firebasedatabase.app" 
FIREBASE_SECRET = "Wv2Ha7WZrDLwnpJyKMt29z9I0MGb0kxitoOaaoGe"

def get_current_thai_time():
    tz_thai = timezone(timedelta(hours=7))
    return datetime.now(tz_thai)

now_thai = get_current_thai_time()
today_date = now_thai.date()
today_str = str(today_date)
yesterday_date = today_date - timedelta(days=1)
yesterday_str = str(yesterday_date)

# 🔄 ระบบแปลงวันที่เป็นภาษาไทยเต็มยศ (วัน+วันที่+เดือน+ปี) ตามคำสั่ง!
THAI_DAYS = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
THAI_MONTHS = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

def thai_date_format(date_str):
    if not date_str or date_str == "": return "ไม่มีกำหนด"
    try:
        if isinstance(date_str, date) or isinstance(date_str, datetime):
            d = date_str
        else:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = THAI_DAYS[d.weekday()]
        return f"{day_name}ที่ {d.day} {THAI_MONTHS[d.month]} {d.year}"
    except:
        return date_str

def safe_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

def get_stable_index(id_str, list_len):
    return int(hashlib.md5(id_str.encode('utf-8')).hexdigest(), 16) % list_len

# ==========================================
# 🧠 THE MENTOR SYSTEM
# ==========================================
MENTORS = {
    "None": {
        "name": "ไม่มี (วิถีคนเถื่อน)", "icon": "⚔️", 
        "desc": "พึ่งพาแค่สันดานดิบของตัวเอง ไม่มีสกิลบัฟอะไรทั้งนั้น! (ชีวิตมันโหดร้ายแบบนี้แหละ)",
        "quotes": [
            "มึงจะยอมแพ้แค่นี้หรอวะ? กลับไปกระจอกเหมือนเดิมก็เอาดิ ถ้ารับตัวเองได้!", "ความเหนื่อยวันนี้ คือกล้ามเนื้อของความสำเร็จพรุ่งนี้ ลุยดิวะ!", "ปีศาจขี้เกียจมันกำลังหัวเราะมึงอยู่... มึงจะยอมให้มันชนะหรอ? ฟาดหน้ามัน!", "ไม่มีข้ออ้างสำหรับคนจริง! ทางเดียวคือเดินหน้าและบดขยี้เป้าหมายให้แหลก!"
        ]
    },
    "Jesus": {
        "name": "พระเยซู (Jesus)", "icon": "✝️", 
        "desc": "สกิล [พระคุณ]: ยอมรับความพ่ายแพ้จะลดทอนค่าปรับลง 50% เสมอ เริ่มต้นใหม่ได้เสมอ",
        "quotes": [
            "บรรดาผู้เหน็ดเหนื่อยและแบกภาระหนัก จงมาหาเราเถิด และเราจะให้ท่านทั้งหลายได้พักสงบ", "จงเข้มแข็งและกล้าหาญเถิด อย่าหวาดหวั่นพรั่นพรึง เพราะพระเจ้าอยู่กับเจ้าทุกแห่งหน"
        ]
    },
    "Zenitsu": {
        "name": "เซนอิทสึ (ร่างเอาจริง)", "icon": "⚡",
        "desc": "สกิล [Godspeed]: ในโหมด Locked In ทำงานด่วนลด Failure Prob x2 แต่ดองงานโดนหนี้เลือด x2!",
        "quotes": [
            "เวลาของความลังเลมันหมดลงไปตั้งนานแล้ว", "จะเหนื่อย จะเจ็บแค่ไหน ร่างกายนี้ก็ต้องขยับตามคำสั่ง"
        ]
    },
    "Yuji": {
        "name": "ยูจิ (ฟันเฟืองทรหด)", "icon": "⚙️", 
        "desc": "สกิล [ก้าวเล็กๆ]: ติ๊ก 'งานย่อย' สำเร็จ 1 ข้อ จะลดอัตราความกากได้ 2 เท่า",
        "quotes": [
            "ถึงจะอ่อนแอแค่ไหน หน้าที่ของกูก็คือทำสิ่งที่อยู่ตรงหน้าให้พังไปข้างนึง!", "ถ้ากูไม่ทำตอนนี้ แล้วใครจะมาทำชีวิตกูให้ดีขึ้นวะ? ลุยดิวะ!"
        ]
    },
    "Gojo": {
        "name": "โกโจ (ไร้ขีดจำกัด)", "icon": "🤞", 
        "desc": "สกิล [กรองเสียงรบกวน]: บทลงโทษหนี้เลือดจากงานค้าง ถูกจำกัดไว้สูงสุดไม่เกิน 100 ที/วัน",
        "quotes": [
            "เรื่องแค่นี้เอง ไม่เป็นไรหรอก เพราะฉันน่ะเก่งที่สุดแล้ว!", "ปล่อยให้พวกอ่อนแอมันกังวลไป ส่วนเรามาเคลียร์งานนี้ให้จบสวยๆ กันดีกว่า!"
        ]
    },
    "Toji": {
        "name": "โทจิ (นักล่าสัญญาสวรรค์)", "icon": "🐛", 
        "desc": "สกิล [High Risk, High Return]: สำเร็จงาน Boss รับโบนัส +30% EXP แต่ดองงาน Boss โดนหนี้เลือด x2!",
        "quotes": [
            "ข้ออ้างหรือพรสวรรค์กูไม่สน กูสนแค่ผลลัพธ์และเป้าหมายที่อยู่ตรงหน้า!", "อย่ามาสำออยให้กูเห็น ลุกขึ้นไปทำหน้าที่ของมึงให้คุ้มกับลมหายใจซะ!"
        ]
    },
    "Subaru": {
        "name": "ซุบารุ (Return by Death)", "icon": "⏪", 
        "desc": "สกิล [ราคาของการแก้ตัว]: เลื่อน Deadline งานมาเป็นวันนี้ได้ แต่ต้องจ่าย 10 EXP เป็นข้อแลกเปลี่ยน",
        "quotes": [
            "ถึงวันนี้จะพังพินาศ แต่พรุ่งนี้กูจะหาวิธีเอาชนะมันให้ดู!", "ความกลัวมันเกาะกินใจกูตลอดแหละ แต่กูทิ้งมันไว้ข้างหลังไม่ได้ กูต้องลุย!"
        ]
    },
    "Ippo": {
        "name": "อิปโป (Dempsey Roll)", "icon": "🥊", 
        "desc": "สกิล [พื้นฐานรักษาชีวิต]: หากพลาดงานใหญ่ แต่มึงเคลียร์ 'วินัยเหล็ก' ครบ 100% ในวันนั้น Streak จะไม่ขาด!",
        "quotes": [
            "ความสำเร็จไม่มีทางลัด มันเกิดจากการสะสมการกระทำเล็กๆ ทุกวันต่างหาก!", "ฝึกซ้อมจนอ้วกแตก ดีกว่าไปพ่ายแพ้อย่างน่าสมเพชบนสังเวียนชีวิต!"
        ]
    },
    "Future You": {
        "name": "นักรบจากอนาคต (Future You)", "icon": "⏳", 
        "desc": "สกิล [รากฐานแห่งอนาคต]: เคลียร์งานด่วน รับโบนัสพิเศษ +20 EXP แต่ดองงานค้าง Failure Prob เด้ง x2!",
        "quotes": [
            "กูคือตัวมึงในอีก 20 ปีข้างหน้า มึงอยากเป็นไอ้ขี้แพ้หรือคนรวย มึงเลือกเลยวันนี้!", "อย่าให้กูต้องนั่งด่ามึงในใจทุกวันเลย... เปลี่ยนแปลงตัวเองเดี๋ยวนี้!"
        ]
    }
}

PUNISHMENTS = ["ไปดันพื้น 50 ทีเดี๋ยวนี้!", "แพลงก์ 2 นาที!", "ลุกไปอาบน้ำเย็นจัด 5 นาทีเดี๋ยวนี้!", "กระโดดตบ 100 ครั้ง!", "สควอช (ลุกนั่ง) 60 ที!"]
WARRIOR_OATHS = ["ข้ออ้างมีไว้สำหรับไอ้กระจอก! วันนี้มึงจะสร้างผลงาน หรือจะสร้างข้ออ้าง เลือกเอา!", "ความสบายในวันนี้ คือความชิบหายในวันหน้า! ลุกขึ้นมาบดขยี้ความขี้เกียจของมึงซะ!"]
WARRIOR_CONSEQUENCES = ["กูจะต้องทนเห็นคนที่พยายามน้อยกว่ากู ได้ดีกว่ากู!", "อนาคตที่กูวาดฝันไว้ จะพังทลายลงด้วยมือของกูเอง!"]
ABYSS_VOICES = ["มึงทำ '{task}' ไม่ได้หรอก... ยอมแพ้แล้วกลับไปนอนโง่ๆ ซะเถอะ...", "ดอง '{task}' ไว้ก่อนสิ ไม่มีใครรู้หรอก พักก่อน..."]
COMMANDER_VOICES = ["อย่าไปฟังเสียงสวะนั่น! ลุกขึ้นมา! ร่างกายนี้มึงคุม ไปฟาด '{task}' ให้แหลกคามือ!", "เป้าหมายอยู่ตรงหน้า! เหยียบหัวความขี้เกียจแล้วลุย '{task}' เดี๋ยวนี้!"]
ETERNAL_ECHOES = ["โลกไม่สนหรอกว่ามึงจะเหนื่อย โลกสนแค่ว่ามึงทำสำเร็จหรือเปล่า!", "ทุกวินาทีที่มึงขี้เกียจ คือวินาทีที่มึงปล่อยให้ตัวเองกลับไปเป็นไอ้ขี้แพ้!"]
AMBUSH_TASKS = ["กฎก้าวสุดท้าย! ไปแพลงก์ 1 นาทีก่อนนอน!", "คิดว่ารอดแล้วหรอ? วิดพื้น 20 ที!"]

def get_safe_email(email): return email.replace(".", "-").replace("@", "-")

def get_title(level):
    if level < 3: return "🤡 ไอ้ขี้แพ้ที่รอการพิสูจน์"
    elif level < 7: return "⚙️ ผู้ทุบทำลายขีดจำกัด"
    elif level < 12: return "🦍 นักรบผู้คุมปีศาจในใจ"
    else: return "👑 ปรมาจารย์แห่งวินัยเหล็ก"

def get_priority_score(task_type):
    if not task_type: return 4
    if "🔴 ด่วนสุด" in task_type or "🔥 งานฉุกเฉิน" in task_type: return 1
    if "🟡 ปานกลาง" in task_type: return 2
    if "🟢 ชิลๆ" in task_type: return 3
    return 4

def get_deadline_score(dl_str):
    if not dl_str or dl_str == "": return 999999
    try: return (datetime.strptime(dl_str, "%Y-%m-%d").date() - today_date).days
    except: return 999999

def format_days_left(dl_str):
    days = get_deadline_score(dl_str)
    if days == 999999: return ""
    if days > 0: return f"⏳ (เหลือ {days} วัน)"
    if days == 0: return f"🚨 **(ต้องเสร็จวันนี้!)**"
    return f"💀 **(เลยกำหนด {-days} วัน)**"

def is_overdue_check(dl_str):
    return get_deadline_score(dl_str) < 0

def calculate_task_rewards(task, current_streak, mentor_name):
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
    
    if mentor_name == "Toji" and task.get("is_boss"):
        final_exp = int(final_exp * 1.3)
        st.toast("🐛 [สัญญาสวรรค์] โทจิรีดศักยภาพดิบ ได้โบนัส EXP +30% จากงาน BOSS!", icon="🩸")
    if mentor_name == "Zenitsu" and st.session_state.get("locked_in_active", False) and score == 1:
        fail_reduce *= 2; st.toast("⚡ [Godspeed] เซนอิทสึทะลวงงานด่วน! ลดความอ่อนแอ 2 เท่า!", icon="🔥")
    if mentor_name == "Future You" and score == 1:
        final_exp += 20; st.toast("⏳ [รากฐานแห่งอนาคต] รับโบนัสพิเศษ!", icon="🔥")
    return final_exp, fail_reduce

def load_db():
    if FIREBASE_URL == "" or FIREBASE_URL is None: st.error("🚨 ใส่ลิงก์ Firebase ก่อน!"); st.stop()
    try:
        res = requests.get(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}", timeout=5)
        if res.status_code == 200 and res.json() is not None:
            data = res.json()
            if not isinstance(data, dict): data = {}
            defaults = {
                "users": {}, "missions": {}, "study_missions": {}, 
                "command_log": {}, "accountability_mirror": {}, "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, 
                "haters": {}, "finance": {}, "iron_habits": {}, "daily_wins": {}, "exams": {}, "beat_yesterday": {}, 
                "limit_breaks": {}, "weakness_fuel": {}, "sanctuary": {}, "skill_forge": {}
            }
            for k, v in defaults.items():
                if k not in data or data[k] is None: data[k] = v
            return data
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")
    return {
        "users": {}, "missions": {}, "study_missions": {}, "command_log": {}, "accountability_mirror": {},
        "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, "haters": {}, "finance": {}, "iron_habits": {}, "daily_wins": {},
        "exams": {}, "beat_yesterday": {}, "limit_breaks": {}, "weakness_fuel": {}, "sanctuary": {}, "skill_forge": {}
    }

def save_db(data):
    try: 
        requests.put(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}", json=data, timeout=5)
    except Exception as e: 
        st.error(f"🚨 เซฟข้อมูลลงฐานข้อมูลไม่สำเร็จ! Error: {e}")

db = load_db()

# ==========================================
# 2. OVERLAY นรก & SLAP AWAKE
# ==========================================
if "punishment_active" in st.session_state:
    st.error("🚨 วงล้อแห่งกรรมทำงาน! มึงหลุดจากวินัย ต้องชดใช้! 🚨")
    st.title(f"🔥 คำสั่งชดใช้กรรม: {st.session_state.punishment_task}")
    if st.button("🩸 กูทำเสร็จแล้ว! (กลับสู่ Discipline Arc)"):
        del st.session_state.punishment_active; safe_rerun()
    st.stop() 

if st.session_state.get("slap_awake_active", False):
    st.markdown("<h1 style='text-align: center; color: #ff4b4b; font-size: 4em;'>💥 ตื่นได้แล้วไอ้เวร!</h1>", unsafe_allow_html=True)
    st.error("🚨 **คำสั่งกระชากสติ:** ลุกไปล้างหน้าด้วยน้ำเย็นจัด แล้ววิดพื้น 20 ทีเดี๋ยวนี้! ถ้าทำไม่ได้ก็เป็นไอ้ขี้แพ้ต่อไป!")
    st.warning("พิมพ์คำปฏิญาณนี้เพื่อปลดล็อกหน้าจอ: **'กูจะไม่ยอมกลับไปเป็นขยะ'**")
    confirm_text = st.text_input("พิมพ์ที่นี่:")
    if st.button("🔥 กูพร้อมกลับไปลุยแล้ว!"):
        if confirm_text.strip() == "กูจะไม่ยอมกลับไปเป็นขยะ":
            del st.session_state["slap_awake_active"]; st.toast("🔥 ดีมาก! กลับไปลุยงานของมึงซะ!", icon="⚔️"); safe_rerun()
        else: st.error("พิมพ์ให้ถูกทุกตัวอักษร! มึงยังไม่ตั้งใจพอ!")
    st.stop()

# ==========================================
# 3. ระบบล็อกอิน & แถบด้านข้าง
# ==========================================
if "current_user" not in st.session_state: st.session_state.current_user = None

with st.sidebar:
    st.title("⚙️ DISCIPLINE ARC")
    st.caption(f"🗓️ ประจำ{thai_date_format(today_str)}") 
    
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือกโหมด:", ["⚡ ล็อกอิน", "➕ สร้างไอดีใหม่"], key="auth_mode_radio")
        st.divider()
        if auth_mode == "➕ สร้างไอดีใหม่":
            name_input = st.text_input("ชื่อนักรบ:")
            email_input = st.text_input("อีเมล (ID):")
            if st.button("เข้าสู่ Discipline Arc!"):
                if email_input and name_input:
                    safe_email = get_safe_email(email_input)
                    if safe_email in db.get("users", {}): st.error("อีเมล/ID นี้มีในระบบแล้ว!")
                    else:
                        db["users"][safe_email] = {
                            "username": name_input, "level": 1, "exp": 0, "streak": 0, "blood_debt": 0, "in_cage": False, "ghost_exp": 0, 
                            "ambush_task": "", "failure_prob": 10, "last_login": today_str, "cleared_yesterday": True,
                            "target_name": "เป้าหมายสูงสุดของชีวิต", "target_date": str(today_date + timedelta(days=90)),
                            "daily_oath_date": "", "anime_mentor": "None", "mentor_date": ""
                        }
                        # โครงสร้าง Daily Wins ใหม่ (Dictionary ชัวร์ๆ)
                        db["daily_wins"][safe_email] = {
                            "items": [
                                {"id": str(uuid.uuid4()), "name": "🚫 No Fap / No Gooning (คุมสติตัวเองให้ได้)"},
                                {"id": str(uuid.uuid4()), "name": "🌅 ตื่นนอนตรงเวลา ไม่กด Snooze เด็ดขาด!"},
                                {"id": str(uuid.uuid4()), "name": "🗣️ ลุย Anki (อังกฤษ/จีน) ไม่ขาดสาย"}
                            ],
                            "logs": {}
                        }
                        save_db(db); st.success("🔥 ลงทะเบียนสำเร็จ! ล็อกอินเลย!")
                else: st.warning("กรอกข้อมูลให้ครบ!")
                
        elif auth_mode == "⚡ ล็อกอิน":
            if not db.get("users"): st.warning("ยังไม่มีนักรบในระบบ ไปสร้างไอดีก่อน!")
            else:
                user_options = {f"{data.get('username', 'Unknown Warrior')}": email for email, data in db["users"].items() if isinstance(data, dict)}
                selected_display = st.selectbox("เลือกบัญชีของคุณ:", list(user_options.keys()))
                
                if st.button("🔥 เริ่มต้นวันใหม่ (Login)"):
                    safe_email = user_options[selected_display]
                    user_data = db["users"][safe_email]
                    
                    if "target_name" not in user_data: user_data["target_name"] = "เป้าหมายสูงสุด"; user_data["target_date"] = str(today_date + timedelta(days=90))
                    if "anime_mentor" not in user_data: user_data["anime_mentor"] = "None"
                    
                    # 🛠️ AUTO-FIX: ซ่อมโครงสร้าง Database ของ Daily Wins ถ้าพัง (กันบั๊ก List)
                    if safe_email not in db.get("daily_wins", {}) or not isinstance(db["daily_wins"][safe_email], dict):
                        st.toast("🛠️ ระบบกำลังซ่อมโครงสร้างเป้าหมายรายวัน...", icon="⚙️")
                        db["daily_wins"][safe_email] = {"items": [], "logs": {}}
                    if "items" not in db["daily_wins"][safe_email] or not isinstance(db["daily_wins"][safe_email]["items"], list):
                        db["daily_wins"][safe_email]["items"] = []
                    if "logs" not in db["daily_wins"][safe_email] or not isinstance(db["daily_wins"][safe_email]["logs"], dict):
                        db["daily_wins"][safe_email]["logs"] = {}

                    if user_data.get("last_login") != today_str:
                        user_data["ghost_exp"] = user_data.get("ghost_exp", 0) + 25 
                        unpaid_bounties = [m for m in db.get("missions", {}).get(safe_email, []) if isinstance(m, dict) and m.get("bounty") and not m.get("เสร็จแล้ว")]
                        if unpaid_bounties or not user_data.get("cleared_yesterday", False):
                            penalty = 100 + (len(unpaid_bounties) * 100)
                            if user_data.get("anime_mentor") == "Jesus":
                                penalty = int(penalty * 0.5); user_data["exp"] = max(0, user_data.get("exp", 0) - 10)
                                st.toast("✝️ [พระคุณ] พระเยซูแบ่งเบาภาระหนี้เลือด 50%", icon="🕊️")
                            else:
                                user_data["exp"] = 0; user_data["level"] = max(1, user_data.get("level", 1) - 1); user_data["streak"] = 0
                            user_data["blood_debt"] = user_data.get("blood_debt", 0) + penalty
                            user_data["failure_prob"] = min(100, user_data.get("failure_prob", 10) + 20)
                            
                        user_data["last_login"] = today_str; user_data["cleared_yesterday"] = False
                        save_db(db)
                    st.session_state.current_user = safe_email
                    safe_rerun()
    else:
        safe_email = st.session_state.current_user
        u_data = db["users"][safe_email]
        
        st.markdown(f"<div style='background-color:#2a0000; padding:15px; border-left: 5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>เป้าหมายสูงสุด:</h3><b style='font-size:1.1em;'>{u_data.get('target_name', '')}</b><p style='color:#ffaaaa; font-style:italic; margin-top:10px;'>\"{random.choice(ETERNAL_ECHOES)}\"</p></div>", unsafe_allow_html=True)
        st.divider()
        st.error(f"👤 ตัวตน: {u_data['username']}")
        st.info(f"🛡️ ฉายา: {get_title(u_data['level'])}")
        
        st.markdown("### 🧬 SOUL RESONANCE")
        if u_data.get("mentor_date") != today_str:
            u_data["anime_mentor"] = random.choice(list(MENTORS.keys())); u_data["mentor_date"] = today_str; save_db(db)
            st.toast(f"🎲 โชคชะตาส่ง {MENTORS[u_data['anime_mentor']]['name']} มาคุมมึง!", icon="🔮")
            
        current_mentor = u_data.get("anime_mentor", "None")
        m_info = MENTORS[current_mentor]
        st.success(f"{m_info['icon']} **{m_info['name']}**\n\n*{m_info['desc']}*")

        st.divider()
        if st.button("🔥 ขอกำลังใจด่ากูหน่อย! (SLAP ME!)", type="primary", use_container_width=True):
            st.session_state.active_slap_message = random.choice(m_info["quotes"]); safe_rerun()
            
        if st.session_state.get("active_slap_message"):
            st.warning(f"**{m_info['icon']} {m_info['name']}:**\n\n\"{st.session_state.active_slap_message}\"")
            if st.button("✅ รับทราบ! ลุย!", use_container_width=True): st.session_state.active_slap_message = ""; safe_rerun()
        st.divider()

        locked_in = st.toggle("🔒 LOCKED IN (โฟกัสขั้นสุด)")
        st.session_state.locked_in_active = locked_in
        
        if not locked_in:
            st.warning(f"🔥 ความต่อเนื่อง: {u_data['streak']} วัน")
            current_streak = u_data.get("streak", 0)
            if current_streak >= 30: st.success("👑 BUFF: วินัยระดับพระเจ้า (EXP x 1.5)")
            elif current_streak >= 7: st.success("🔥 BUFF: วินัยเหล็ก (EXP x 1.2)")
            elif current_streak >= 3: st.success("⚡ BUFF: เริ่มก่อร่างสร้างวินัย (EXP x 1.1)")
            else: st.caption("💀 BUFF: ไร้วินัย (ไม่มีโบนัส)")
            
            needs_save = False
            while u_data["exp"] >= 100:
                u_data["level"] += 1; u_data["exp"] -= 100; needs_save = True
                st.toast(f"🔥 LEVEL UP! Lv.{u_data['level']}", icon="⚙️")
            while u_data["exp"] < 0:
                if u_data["level"] > 1: u_data["level"] -= 1; u_data["exp"] += 100
                else: u_data["exp"] = 0
                needs_save = True
            if needs_save: save_db(db)
            st.progress(max(0.0, min(1.0, u_data["exp"] / 100)), text=f"Lv.{u_data['level']} | EXP: {u_data['exp']}/100")
            st.divider()
        
        if st.button("🚪 ออกจากระบบ"): st.session_state.current_user = None; safe_rerun()

if st.session_state.current_user is None:
    st.title("⚙️ DISCIPLINE ARC")
    st.info("👈 ล็อกอินด้านซ้ายเพื่อเผชิญหน้ากับปีศาจในใจและสร้างวินัยเหล็ก!")
    st.stop()

safe_email = st.session_state.current_user
user = db["users"][safe_email]
active_mentor = user.get("anime_mentor", "None")
active_quotes = MENTORS[active_mentor]["quotes"]
is_locked_in = st.session_state.get("locked_in_active", False)

# ==========================================
# 🚨 THE DAILY OATH
# ==========================================
if user.get("daily_oath_date") != today_str:
    st.markdown("<h1 style='text-align: center; color: #ff4b4b; font-size: 3em;'>🩸 ดึงสติรับวันใหม่!</h1>", unsafe_allow_html=True)
    st.error(f"### ⚔️ เสียงจากแม่ทัพเหล็ก:\n\n> **\"{random.choice(WARRIOR_OATHS)}\"**")
    st.warning("มึงจะยอมแพ้ตั้งแต่ยังไม่เริ่ม แล้วกลับไปซุกผ้าห่ม หรือจะลุกขึ้นมาสู้เพื่อชีวิตตัวเอง?")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔥 กูขอสาบานว่าจะไม่ยอมเป็นไอ้ขี้แพ้!", use_container_width=True, type="primary"):
            user["daily_oath_date"] = today_str; save_db(db); safe_rerun()
    st.stop() 

# ==========================================
# 🔊 ETERNAL ECHO (TOP BANNER)
# ==========================================
st.markdown(f"""
<div style="background: linear-gradient(90deg, #4b0000 0%, #1a0000 100%); padding: 10px 20px; border-left: 8px solid #ff4b4b; margin-bottom: 20px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center;">
    <div><h4 style="color:#ff4b4b; margin:0;">🔥 มึงบอกว่าไม่อยากกากอีกแล้วใช่มั้ย?</h4><span style="color:#fff; font-size:14px;">เป้าหมายมึงคือ: <b>{user.get('target_name', 'เป้าหมายสูงสุด')}</b></span></div>
    <div style="color:#ffaaaa; font-style:italic; max-width: 50%; text-align:right;">"{random.choice(ETERNAL_ECHOES)}"</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 🔥 คอนฟิกโครงสร้าง Database เพิ่มเติม
# ==========================================
list_keys = ["missions", "study_missions", "command_log", "accountability_mirror", "dopamine_fails", "excuses", "cookie_jar", "haters", "iron_habits", "limit_breaks", "weakness_fuel", "sanctuary", "skill_forge"]
for k in list_keys:
    if safe_email not in db[k] or db[k][safe_email] is None: db[k][safe_email] = []
    elif isinstance(db[k][safe_email], dict): db[k][safe_email] = list(db[k][safe_email].values())

for k in ["finance", "exams", "beat_yesterday"]:
    if safe_email not in db[k] or db[k][safe_email] is None: 
        if k == "finance": db[k][safe_email] = {"goal_name": "ยังไม่ได้ตั้ง", "goal_amount": 0, "current": 0}
        else: db[k][safe_email] = {}

finance = db["finance"][safe_email]
current_streak = user.get("streak", 0)

# ===== 🚨 CHECK OVERDUE COMMAND LOG (สมุดบัญชาการดองงาน) =====
overdue_count = 0
overdue_debt_accum = 0
overdue_tasks_names = []

for item in db["command_log"][safe_email]:
    if not isinstance(item, dict): continue 
    if item.get("type") in ["task", "study"] and item.get("deadline") and item["deadline"] != "":
        if is_overdue_check(item["deadline"]) and item.get("last_penalized") != today_str:
            overdue_count += 1
            item["last_penalized"] = today_str
            overdue_debt_accum += 50
            overdue_tasks_names.append(item.get("title", ""))

if overdue_count > 0:
    fail_prob_penalty = 10 * overdue_count
    if active_mentor == "Future You":
        fail_prob_penalty *= 2
        st.toast("⏳ [รากฐานแห่งอนาคต] มึงทำอนาคตกูพัง! โดนค่าความกาก x2 จากงานค้าง!", icon="💀")
    user["failure_prob"] = min(100, user.get("failure_prob", 10) + fail_prob_penalty)
    user["blood_debt"] = user.get("blood_debt", 0) + overdue_debt_accum
    user["in_cage"] = True; save_db(db)
    if not is_locked_in: st.error(f"🚨 **มึงโดนลงโทษ {overdue_debt_accum} ที!** ข้อหา: ดองงานในสมุดบัญชาการจนเลยเวลา! ({', '.join(overdue_tasks_names)})")

# ==========================================
# 🗺️ PREPARE ACTIVE TASKS
# ==========================================
raw_m = [m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False) and m.get("skip_today_date") != today_str]
raw_s = [s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว") and not s.get("รอตรวจ", False) and s.get("skip_today_date") != today_str]
raw_h = [h for h in db["iron_habits"][safe_email] if isinstance(h, dict) and h.get("last_done_date") != today_str]
for h in raw_h: h["ภารกิจ"] = h["name"]; h["is_habit"] = True

all_active_tasks = raw_m + raw_s + raw_h
all_active_tasks.sort(key=lambda x: (3 if x.get("is_habit") else 2 if x.get("is_study") else 1, x.get("user_order", 99)))

# ==========================================
# 🔒 LOCKED IN MODE
# ==========================================
if is_locked_in:
    st.markdown("<h1 style='text-align: center; color: #ff4b4b; font-size: 3em;'>🔒 LOCKED IN MODE</h1>", unsafe_allow_html=True)
    st.divider()
    if not all_active_tasks: st.success("🎉 ไม่มีงานค้างแล้ว! ปิดโหมด Locked In ได้เลย")
    else:
        top_task = all_active_tasks[0]
        icon = "⛓️" if top_task.get("is_habit") else "📖" if top_task.get("is_study") else "🔪"
        st.markdown(f"## {icon} เป้าหมายปัจจุบัน: **{top_task.get('ภารกิจ')}**")
        st.caption("มึงไม่เห็นงานอื่น และระบบอื่นๆ จนกว่ามึงจะทำไอ้งานนี้เสร็จ!")
        display_hype = active_quotes[get_stable_index(str(top_task.get("id", "")) + "hype", len(active_quotes))]
        hype_color = "#4ba3ff" if active_mentor == "Jesus" else "#e2d141" if active_mentor == "Zenitsu" else "#ffa500"
        st.markdown(f"<div style='font-size: 1.2em; background: rgba(255, 255, 255, 0.05); padding: 15px; border-left: 5px solid {hype_color}; margin-bottom: 20px;'>{MENTORS[active_mentor]['icon']} <b>{MENTORS[active_mentor]['name']}:</b> {display_hype}</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if top_task.get("is_habit"):
                if st.button("🔥 ก้าวข้ามมันไป! (ทำสำเร็จ)", use_container_width=True, type="primary"):
                    for h in db["iron_habits"][safe_email]:
                        if h.get("id") == top_task.get("id"):
                            if h.get("last_done_date") == yesterday_str: h["streak"] = h.get("streak", 0) + 1
                            else: h["streak"] = 1
                            h["last_done_date"] = today_str; h["total_done"] = h.get("total_done", 0) + 1
                    user["exp"] += 10; save_db(db); safe_rerun()
            elif top_task.get("subtasks"):
                st.warning("ซอยขั้นตอนไว้ ลุยทีละข้อ!")
                target_list = db["study_missions"][safe_email] if top_task.get("is_study") else db["missions"][safe_email]
                for task in target_list:
                    if task.get("id") == top_task.get("id"):
                        all_done = True
                        for i, stask in enumerate(task["subtasks"]):
                            is_locked = stask.get("done", False) and stask.get("done_date", "") != today_str
                            checked = st.checkbox(stask['name'], value=stask.get("done", False), disabled=is_locked, key=f"locked_sub_{i}")
                            if not is_locked and checked != stask.get("done", False):
                                task["subtasks"][i]["done"] = checked; task["subtasks"][i]["done_date"] = today_str if checked else ""; save_db(db); safe_rerun()
                            if not checked: all_done = False
                        if all_done:
                            if st.button("✅ พิชิตงานใหญ่!", use_container_width=True, type="primary"):
                                task["เสร็จแล้ว"] = True
                                exp_gain, fail_reduce = calculate_task_rewards(task, current_streak, active_mentor)
                                user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
            else:
                if st.button("✅ จัดการเรียบร้อย!", use_container_width=True, type="primary"):
                    target_list = db["study_missions"][safe_email] if top_task.get("is_study") else db["missions"][safe_email]
                    for task in target_list:
                        if task.get("id") == top_task.get("id"):
                            task["เสร็จแล้ว"] = True
                            exp_gain, fail_reduce = calculate_task_rewards(task, current_streak, active_mentor)
                            user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
    st.stop()

# ==========================================
# 🎯 ส่วนหัว: ปุ่มควบคุมฉุกเฉิน
# ==========================================
try: t_date = datetime.strptime(user.get("target_date", str(today_date)), "%Y-%m-%d").date()
except: t_date = today_date + timedelta(days=90)
days_left = (t_date - today_date).days

if st.button("💥 กูเริ่มเหนื่อยและอยากสบาย (Slap Me Awake!)", use_container_width=True, type="secondary"):
    st.session_state.slap_awake_active = True; safe_rerun()

colTop1, colTop2, colTop3 = st.columns([1, 1, 3])
with colTop1:
    if st.button("🎰 วงล้อชดใช้กรรม", type="primary", use_container_width=True):
        st.session_state.punishment_active = True; st.session_state.punishment_task = random.choice(PUNISHMENTS); safe_rerun()
with colTop2:
    if st.button("⚡ ปลุกวินัย", use_container_width=True): st.toast("🔥 อย่าถอย! ลุยดิวะ!", icon="⚙️")
with colTop3:
    with st.popover("⚙️ ตั้งเป้าหมายสูงสุด"):
        new_t_name = st.text_input("เป้าหมายสูงสุด:", user.get("target_name", ""))
        new_t_date = st.date_input("วันกำหนด (Deadline):", t_date)
        if st.button("บันทึกเป้าหมาย"): user["target_name"] = new_t_name; user["target_date"] = str(new_t_date); save_db(db); safe_rerun()
    st.caption(f"เหลือเวลาอีก **{days_left}** วัน ที่มึงต้องพิสูจน์ตัวเอง!")

if user.get("in_cage"): st.error("🚨 **มึงอยู่ในกรง!** วิดพื้นจ่ายหนี้เลือดเพื่อออกมาทำตามแผนซะ!")
st.divider()

# ==========================================
# 5. DUAL REALITY DASHBOARD
# ==========================================
colLeft, colRight = st.columns([1.2, 2.8])

with colLeft:
    st.markdown("### 🗑️ ขยะในจิตใจ (Distractions)")
    fail_prob = user.get('failure_prob', 10)
    st.markdown(f"**📉 โอกาสหลุดวงโคจรวินัย: {fail_prob}%**")
    st.progress(fail_prob / 100)
    if st.button("💀 กดยอมแพ้ให้สิ่งเร้า", use_container_width=True):
        db["dopamine_fails"][safe_email].append(today_str); user["exp"] = 0; user["blood_debt"] = user.get("blood_debt", 0) + 50; user["in_cage"] = True; user["failure_prob"] = min(100, user["failure_prob"] + 20); save_db(db); safe_rerun()

    st.markdown("#### 🩸 เชื้อเพลิงความแค้น")
    with st.form("weakness_fuel_form", clear_on_submit=True):
        w_text = st.text_input("ความอ่อนแอที่มึงเคยทำพลาด:")
        if st.form_submit_button("🔥 เผาความกากเป็นพลัง!"):
            if w_text: db["weakness_fuel"][safe_email].append({"id": str(uuid.uuid4()), "text": w_text}); save_db(db); safe_rerun()
                
    if db.get("weakness_fuel", {}).get(safe_email):
        random_weakness = random.choice(db["weakness_fuel"][safe_email])
        w_disp = random_weakness.get("text", "") if isinstance(random_weakness, dict) else random_weakness
        st.error(f"🩸 **มึงเคยกากแบบนี้:**\n\n\"{w_disp}\"\n\n*(ห้ามกลับไปเป็นไอ้ขี้แพ้แบบเดิม!)*")

    st.markdown("#### 🗣️ THE HATER'S WALL")
    with st.form("hater_form", clear_on_submit=True):
        h_text = st.text_input("คำดูถูกที่ฝังใจ:")
        if st.form_submit_button("ฝังความแค้น"):
            if h_text: db["haters"][safe_email].append(h_text); save_db(db); safe_rerun()
    if db.get("haters", {}).get(safe_email): st.warning(f"🤬 \"{random.choice(db['haters'][safe_email])}\"")

with colRight:
    st.markdown("## ⚙️ DISCIPLINE ZONE")
    
    tab_missions, tab_study, tab_forge, tab_planner, tab_mirror, tab_habits, tab_daily_wins, tab_sanctuary, tab_cookie, tab_academic = st.tabs([
        "🔪 งาน", "📖 เรียน", "⚒️ ตีเหล็ก", "📝 สมุดบัญชาการ", "🪞 กระจกรับผิดชอบ", "⛓️ วินัย", "🏅 ชัยชนะรายวัน", "🔥 พักใจ", "🍪 โหลคุกกี้", "📚 ลานประลอง"
    ])
    
    # ----------------------------------------------------
    # TAB 1: 🔪 งาน
    # ----------------------------------------------------
    with tab_missions:
        st.markdown("### 🔪 งานที่ต้องบดขยี้วันนี้")
        raw_active_missions = [m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว")]
        todo_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False)]
        todo_missions.sort(key=lambda x: (x.get("user_order", 99), 0 if x.get("is_boss") else 1, get_deadline_score(x.get("deadline", "")), get_priority_score(x.get("ประเภท", ""))))
        
        if todo_missions:
            for m in todo_missions:
                bg_style = "border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; margin-bottom: 10px;" if m == todo_missions[0] else "border: 1px solid #444; padding: 10px; border-radius: 5px; margin-bottom: 10px;"
                st.markdown(f"<div style='{bg_style}'>", unsafe_allow_html=True)
                c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6]) 
                
                is_overdue = is_overdue_check(m.get("deadline", ""))
                dl_formatted = thai_date_format(m.get("deadline", ""))
                deadline_badge = f"{format_days_left(m.get('deadline', ''))} (เดดไลน์: {dl_formatted})" if m.get("deadline") else ""
                
                is_frozen = (m.get("skip_today_date") == today_str)
                if m.get("skip_today_date") != "" and not is_frozen: m["skip_today_date"] = ""; save_db(db)
                frozen_badge = " ❄️🚨 [เกราะแตก!]" if is_frozen and is_overdue else " ❄️ [แช่แข็ง]" if is_frozen else ""

                c1.write(f"**{m.get('ประเภท','')}** | {'🎯 **[Q' + str(m.get('user_order', 99)) + ']** ' if m.get('user_order', 99) != 99 else ''}{'🔪 **[ซอยงาน]**' if m.get('subtasks') else '⚡ **[ชิ้นเดียวจบ]**'}{' 💀 **[BOSS]**' if m.get('is_boss') else ''} {m['ภารกิจ']} {deadline_badge}{frozen_badge}")
                
                with st.expander("📝 ดูรายละเอียดและเนื้องาน"):
                    if m.get("รายละเอียด"): st.write(m["รายละเอียด"])
                    all_done = True
                    if m.get("subtasks"):
                        for i, stask in enumerate(m["subtasks"]):
                            is_locked = stask.get("done", False) and stask.get("done_date", "") != today_str
                            can_interact = not is_locked and (not is_frozen or is_overdue)
                            checked = st.checkbox(f"{stask['name']} {'🔒 ('+thai_date_format(stask.get('done_date', ''))+')' if is_locked else ''}", value=stask.get("done", False), disabled=not can_interact, key=f"st_{m['id']}_{i}")
                            if can_interact and checked != stask.get("done", False):
                                m["subtasks"][i]["done"] = checked; m["subtasks"][i]["done_date"] = today_str if checked else ""; save_db(db); safe_rerun()
                            if not checked: all_done = False

                if all_done and (not is_frozen or is_overdue):
                    if c2.button("✅ สำเร็จ", key=f"m_{m['id']}"):
                        m["เสร็จแล้ว"] = True
                        exp_gain, fail_reduce = calculate_task_rewards(m, current_streak, active_mentor)
                        user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                if c5.button("🗑️", key=f"del_m_{m['id']}"): db["missions"][safe_email].remove(m); save_db(db); safe_rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 4: 📝 สมุดบัญชาการ (COMMAND LOG)
    # ----------------------------------------------------
    with tab_planner:
        st.markdown("### 📝 สมุดบัญชาการ (Command Log)")
        pl_type = st.radio("ประเภทการบันทึก:", ["📝 โน้ตทั่วไป", "🔪 เตรียมงาน", "📖 เตรียมเรียน", "⚠️ ตารางสอบ"], horizontal=True)
        pl_title = st.text_input("หัวข้อเรื่อง:")
        pl_detail = st.text_area("รายละเอียด / ขอบเขตเนื้อหา:")
        
        pl_priority = "🟡 ปานกลาง"
        pl_subtasks_str = ""
        pl_date = None
        
        if "งาน" in pl_type or "เรียน" in pl_type:
            pl_priority = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"])
            pl_subtasks_str = st.text_area("🔪 ซอยข้อย่อย (Enter ขึ้นบรรทัดใหม่):")
            pl_date = st.date_input("กำหนดส่ง / วันที่ต้องเสร็จ:")
        elif "สอบ" in pl_type:
            pl_date = st.date_input("วันที่สอบ:")

        if st.button("💾 บันทึกลงสมุดบัญชาการ", type="primary"):
            if pl_title:
                item_type = "note"
                if "งาน" in pl_type: item_type = "task"
                elif "เรียน" in pl_type: item_type = "study"
                elif "สอบ" in pl_type: item_type = "exam"
                
                final_dl = str(pl_date) if item_type != "note" else ""
                subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in pl_subtasks_str.split('\n') if s.strip()] if item_type in ["task", "study"] else []
                
                db["command_log"][safe_email].append({
                    "id": str(uuid.uuid4()), "type": item_type, "title": pl_title, "detail": pl_detail, "priority": pl_priority, 
                    "subtasks": subtasks, "deadline": final_dl, "date_added": today_str
                })
                save_db(db); st.success("บันทึกสำเร็จ!"); safe_rerun()
                    
        planner_items = db["command_log"].get(safe_email, [])
        if planner_items:
            exams = [i for i in planner_items if i.get("type") == "exam"]
            tasks_study = [i for i in planner_items if i.get("type") in ["task", "study"]]
            notes = [i for i in planner_items if i.get("type") == "note"]
            
            if exams:
                st.divider()
                st.markdown("#### ⚠️ ตารางสอบ (Exams)")
                for exam in sorted(exams, key=lambda x: x.get("deadline", "9999-12-31")):
                    with st.container(border=True):
                        c1, c2 = st.columns([5, 1])
                        c1.markdown(f"**{exam['title']}** | 📅 วันสอบ: {thai_date_format(exam.get('deadline', '-'))} {format_days_left(exam.get('deadline', ''))}")
                        if c2.button("🗑️", key=f"del_exm_{exam['id']}"): planner_items.remove(exam); save_db(db); safe_rerun()
            
            if tasks_study:
                st.divider()
                st.markdown("#### ⏳ งานและการเรียนที่เตรียมไว้")
                for item in sorted(tasks_study, key=lambda x: x.get("deadline", "9999-12-31")):
                    is_overdue = is_overdue_check(item.get("deadline", ""))
                    bg_style = "border: 2px solid #ff4b4b; background-color: rgba(255,0,0,0.05);" if is_overdue else "border: 1px solid #444;"
                    st.markdown(f"<div style='{bg_style} padding: 10px; border-radius: 5px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([5, 2, 1])
                    
                    icon = "🔪 [งาน]" if item.get("type") == "task" else "📖 [เรียน]"
                    c1.markdown(f"**{item.get('priority', '🟡 ปานกลาง')}** | **{icon} {item['title']}** | 📅 เดดไลน์: {thai_date_format(item.get('deadline', '-'))} {format_days_left(item.get('deadline', ''))}")
                    
                    if item.get("type") == "task":
                        if c2.button("⚡ ดึงเข้าหน้างาน", key=f"pl_{item['id']}", type="primary"):
                            db["missions"][safe_email].append({
                                "id": item["id"], "วันที่": today_str, "ภารกิจ": item["title"], "รายละเอียด": item.get("detail", ""), 
                                "ประเภท": item.get("priority", "🟡 ปานกลาง"), "deadline": item.get("deadline", ""), 
                                "subtasks": item.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False
                            })
                            planner_items.remove(item); save_db(db); safe_rerun()
                    if c3.button("🗑️", key=f"del_pl_{item['id']}"): planner_items.remove(item); save_db(db); safe_rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            if notes:
                st.divider()
                st.markdown("#### 📝 โน้ตทั่วไป")
                for note in reversed(notes):
                    with st.expander(f"📝 {note['title']} (บันทึกเมื่อ: {thai_date_format(note.get('date_added', '-'))})"):
                        st.write(note.get('detail', ''))
                        if st.button("🗑️ ลบทิ้ง", key=f"del_note_{note['id']}"): planner_items.remove(note); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 7: 🏅 ชัยชนะรายวัน (Daily Wins) [ฟีเจอร์ใหม่ ซ่อมสมบูรณ์!]
    # ----------------------------------------------------
    with tab_daily_wins:
        st.markdown("### 🏅 ชัยชนะรายวัน (Daily Wins)")
        st.write(f"**ประจำ{thai_date_format(today_str)}**")
        st.write("เช็คลิสต์ความสำเร็จเล็กๆ ที่มึงต้องเคลียร์ทุกวัน! ชนะก็กดชนะ แพ้ก็ยอมรับว่าแพ้ (กดแพ้โดนหนี้เลือด 10 ที!) เมื่อขึ้นวันใหม่กระดานนี้จะรีเซ็ตให้ทำใหม่")
        
        daily_wins_data = db["daily_wins"][safe_email]
        win_items = daily_wins_data.get("items", [])
        today_logs = daily_wins_data.setdefault("logs", {}).setdefault(today_str, {})
        
        with st.expander("➕ เพิ่มเป้าหมายแห่งชัยชนะ"):
            with st.form("add_daily_win_form", clear_on_submit=True):
                new_win = st.text_input("เรื่องที่ต้องชนะตัวเองทุกวัน (เช่น ไม่ลืมกินข้าวเช้า, ยิ้มให้ตัวเอง):")
                if st.form_submit_button("บันทึกเป้าหมาย"):
                    if new_win:
                        win_items.append({"id": str(uuid.uuid4()), "name": new_win})
                        save_db(db); safe_rerun()
                        
        if win_items:
            for item in win_items:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([5, 1.5, 1.5, 0.5])
                    
                    # Log object looks like: {"status": "win", "name": "เป้าหมาย"}
                    item_log = today_logs.get(item["id"], {})
                    status = item_log.get("status") if isinstance(item_log, dict) else item_log
                    
                    if status == "win":
                        col1.markdown(f"✅ **<span style='color:#4bff4b;'>{item['name']}</span>**", unsafe_allow_html=True)
                        col2.write("🏆 ชนะแล้ว!")
                    elif status == "lose":
                        col1.markdown(f"❌ **<span style='color:#ff4b4b; text-decoration: line-through;'>{item['name']}</span>**", unsafe_allow_html=True)
                        col2.write("💀 แพ้ราบคาบ")
                    else:
                        col1.markdown(f"**{item['name']}**")
                        if col2.button("✅ ชนะ", key=f"win_{item['id']}", use_container_width=True):
                            today_logs[item["id"]] = {"status": "win", "name": item["name"]}
                            user["exp"] += 5; st.balloons(); save_db(db); safe_rerun()
                        if col3.button("❌ แพ้", key=f"lose_{item['id']}", use_container_width=True):
                            today_logs[item["id"]] = {"status": "lose", "name": item["name"]}
                            user["blood_debt"] = user.get("blood_debt", 0) + 10; save_db(db); safe_rerun()
                            
                    if col4.button("🗑️", key=f"del_dwin_{item['id']}"):
                        win_items.remove(item); save_db(db); safe_rerun()
                        
            # ประวัติการเอาชนะตัวเอง (ประวัติไม่หายแม้วันเปลี่ยน หรือลบเป้าหมายทิ้ง)
            with st.expander("📜 ประวัติการเอาชนะตัวเอง (ย้อนหลัง)"):
                past_dates = sorted([d for d in daily_wins_data.get("logs", {}).keys() if d != today_str], reverse=True)
                if not past_dates: st.info("ยังไม่มีประวัติของวันก่อนๆ")
                
                for log_date in past_dates:
                    st.markdown(f"**📅 {thai_date_format(log_date)}**")
                    day_log = daily_wins_data["logs"][log_date]
                    
                    for w_id, w_data in day_log.items():
                        if isinstance(w_data, dict):
                            w_status = w_data.get("status")
                            w_name = w_data.get("name", "ภารกิจเก่าที่ถูกลบไปแล้ว")
                        else: # เผื่อโครงสร้างเก่าหลุดรอด
                            w_status = w_data
                            w_name = next((i["name"] for i in win_items if i["id"] == w_id), "ภารกิจเก่าที่ถูกลบไปแล้ว")
                            
                        icon = "✅" if w_status == "win" else "❌" if w_status == "lose" else "➖"
                        color = "#4bff4b" if w_status == "win" else "#ff4b4b" if w_status == "lose" else "#ffffff"
                        st.markdown(f"- {icon} <span style='color:{color}'>{w_name}</span>", unsafe_allow_html=True)
                    st.divider()
        else: st.info("ยังไม่มีเป้าหมายรายวัน เพิ่มเข้าไปดิวะ!")

    # ----------------------------------------------------
    # TAB 8: 🔥 พักใจ (Sanctuary)
    # ----------------------------------------------------
    with tab_sanctuary:
        st.markdown("## 🔥 แคมป์ไฟพักใจ (The Sanctuary)")
        st.write("ที่นี่ไม่มีตารางงาน ไม่มีบทลงโทษ มีแค่กองไฟและความเงียบ... ถ้าวันนี้มันหนักหนา หรือรู้สึกโดดเดี่ยวเกินไป พิมพ์ทิ้งไว้ที่นี่ได้เลย")
        with st.form("sanctuary_form", clear_on_submit=True):
            sanc_text = st.text_area("โยนความรู้สึกหนักๆ ของมึงลงในกองไฟ...", placeholder="วันนี้แม่งโคตรเหนื่อยเลยว่ะ กูรู้สึกเหมือนสู้อยู่คนเดียว...", height=150)
            if st.form_submit_button("🔥 ปล่อยวางมันลง"):
                if sanc_text: db["sanctuary"][safe_email].append({"id": str(uuid.uuid4()), "วันที่": today_str, "ข้อความ": sanc_text}); save_db(db); st.success("รับฟังแล้ว... พักซะ"); safe_rerun()
        st.divider()
        if db.get("sanctuary", {}).get(safe_email):
            for note in reversed(db["sanctuary"][safe_email][-10:]):
                if isinstance(note, dict):
                    with st.container(border=True):
                        st.caption(f"📅 เขียนเมื่อ: {thai_date_format(note.get('วันที่', ''))}"); st.write(f"💭 {note.get('ข้อความ', '')}")

    # ----------------------------------------------------
    # TAB 9: โหลคุกกี้ (Cookie Jar) 🍪
    # ----------------------------------------------------
    with tab_cookie:
        st.markdown("### 🍪 โหลเก็บความภูมิใจ (Cookie Jar)")
        st.write("ที่เก็บความสำเร็จชิ้นใหญ่ เรื่องราวที่ทำให้มึงภูมิใจในตัวเองแบบสุดๆ")
        with st.form("cookie_form", clear_on_submit=True):
            win_text = st.text_input("ความสำเร็จที่อยากเก็บไว้เป็นความทรงจำ:")
            if st.form_submit_button("เก็บเข้าโหล!"):
                if win_text: db["cookie_jar"][safe_email].append({"id": str(uuid.uuid4()), "วันที่": today_str, "ชัยชนะ": win_text}); user["exp"] += 5; save_db(db); st.success("✅ เก็บความสำเร็จ!"); safe_rerun()
        if db["cookie_jar"][safe_email]:
            for c in reversed(db["cookie_jar"][safe_email][-5:]):
                if isinstance(c, dict): st.success(f"🏆 **[{thai_date_format(c.get('วันที่', '-'))}]** {c.get('ชัยชนะ', '')}")

# ==========================================
# 6. หนี้เลือด & THE JUDGMENT FEED 
# ==========================================
st.divider()
c_bot1, c_bot2 = st.columns(2)
with c_bot1:
    my_exp = ((user.get("level",1) - 1) * 100) + user.get("exp",0)
    st.metric("พลังร่างวินัยสูงสุด", f"{user.get('ghost_exp',0)} EXP")
    st.metric("พลังในปัจจุบัน", f"{my_exp} EXP", delta=f"{my_exp - user.get('ghost_exp',0)} (เปรียบเทียบ)")
with c_bot2:
    st.markdown("### 🩸 หนี้เลือด (ชดใช้ความไร้วินัย)")
    st.metric("ต้องวิดพื้นชดใช้", f"{user.get('blood_debt', 0)} ที")
    if user.get("blood_debt", 0) > 0:
        if st.button("วิดพื้นใช้หนี้หมดแล้ว! (ปลดล็อก)", key="btn_pay_debt"): user["blood_debt"] = 0; user["in_cage"] = False; save_db(db); safe_rerun()

st.divider()
st.markdown("<h2>⚖️ THE JUDGMENT FEED (พิพากษาก่อนนอน)</h2>", unsafe_allow_html=True)
if user.get("ambush_task", "") != "":
    st.error(f"🚨 **โดนซุ่มโจมตีวินัย!** คำสั่ง: **{user['ambush_task']}**")
    if st.button("🔥 ทำเสร็จแล้ว!", key="btn_clear_ambush"): user["ambush_task"] = ""; user["exp"] += 20; save_db(db); safe_rerun()
elif user.get("cleared_yesterday"): 
    st.success("🔥 พิพากษาเรียบร้อย! มึงรักษาวินัยได้อีกวัน!")
else:
    st.warning("วันนี้ทำตามแผนสุดกำลัง หรือแค่ทำผ่านๆ ไป?")
    if st.button("🔥 ใส่เต็ม 100% ตามเส้นทางวินัย!"):
        user["cleared_yesterday"] = True; user["streak"] = user.get("streak",0) + 1; user["exp"] += 25; save_db(db); safe_rerun()

# ==========================================
# 8. 📜 ประวัติศาสตร์เส้นทางวินัย
# ==========================================
st.divider()
st.markdown("## 📜 ประวัติศาสตร์เส้นทางวินัย (HISTORY LOG)")
tab1, tab2, tab3 = st.tabs(["🗺️ บันทึกเดินทาง", "🏆 โหลความภูมิใจ", "🤡 ความกาก & ข้ออ้าง"])

with tab1:
    st.markdown("### 🗺️ ประวัติภารกิจที่พิชิตแล้ว")
    completed_m = sorted([m for m in db["missions"].get(safe_email, []) if isinstance(m, dict) and m.get("เสร็จแล้ว")], key=lambda x: x.get("วันที่", ""), reverse=True)
    all_completed = completed_m
    
    if not all_completed: st.info("ยังไม่มีภารกิจที่ทำสำเร็จ ไปลุยซะ!")
    for idx, item in enumerate(all_completed):
        c1, c2 = st.columns([10, 1])
        c1.info(f"✅ **[{thai_date_format(item.get('วันที่', '-'))}]** | 🔪 งาน | {item.get('ภารกิจ', '')}")
        if c2.button("🗑️", key=f"del_hm_{idx}_{item.get('id', idx)}"):
            db["missions"][safe_email].remove(item); save_db(db); safe_rerun()

with tab2:
    st.markdown("### 🏆 โหลความภูมิใจ (Cookie Jar)")
    if not db["cookie_jar"].get(safe_email): st.info("ยังไม่มีความภูมิใจสะสมไว้")
    for idx, c in enumerate(reversed(db["cookie_jar"].get(safe_email, []))):
        c1, c2 = st.columns([10, 1])
        if isinstance(c, dict):
            c1.success(f"🏆 **[{thai_date_format(c.get('วันที่', '-'))}]** {c.get('ชัยชนะ', '')}")
            if c2.button("🗑️", key=f"del_cj_{idx}_{c.get('id', idx)}"): db["cookie_jar"][safe_email].remove(c); save_db(db); safe_rerun()

with tab3:
    st.markdown("### 🩸 เชื้อเพลิงความแค้น (ความกากในอดีต)")
    if not db["weakness_fuel"].get(safe_email): st.info("ยังไม่มีประวัติความกาก")
    for idx, w in enumerate(reversed(db["weakness_fuel"].get(safe_email, []))):
        c1, c2 = st.columns([10, 1])
        c1.error(f"🩸 **[เชื้อเพลิงความแค้น]** : {w.get('text', '') if isinstance(w, dict) else w}")
        if c2.button("🗑️", key=f"del_wf_{idx}"): db["weakness_fuel"][safe_email].remove(w); save_db(db); safe_rerun()
