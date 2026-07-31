import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import requests
import uuid
import hashlib
import random

# ==========================================
# 1. ตั้งค่าระบบ (DISCIPLINE ARC V.50 - MAXIMUM OVERDRIVE)
# ==========================================
st.set_page_config(page_title="DISCIPLINE ARC", layout="wide", page_icon="⚙️")

FIREBASE_URL = "https://mytaskpro-f7328-default-rtdb.asia-southeast1.firebasedatabase.app" 
FIREBASE_SECRET = "Wv2Ha7WZrDLwnpJyKMt29z9I0MGb0kxitoOaaoGe"

def get_current_thai_time():
    tz_thai = timezone(timedelta(hours=7))
    return datetime.now(tz_thai)

now_thai = get_current_thai_time()
today_date = now_thai.date()
today_str = str(today_date)

def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# ----------------- ระบบสุ่มที่เสถียร (Stable Random) -----------------
def get_stable_index(id_str, list_len):
    """ใช้ Hash ID ของงาน เพื่อให้สุ่มได้ประโยคเดิมเสมอ ไม่กระพริบเปลี่ยนไปมาเวลาคลิกปุ่ม"""
    return int(hashlib.md5(id_str.encode('utf-8')).hexdigest(), 16) % list_len

ROLE_MAP = {
    "Vanguard": "⚡ [ทัพหน้า - First Strike]", 
    "Main": "⚔️ [ทัพหลวง]", 
    "Support": "🏹 [ทัพหนุน]"
}

PUNISHMENTS = [
    "ไปดันพื้น 50 ทีเดี๋ยวนี้! ลงโทษความอ่อนแอ!",
    "แพลงก์ 2 นาที! เอาความเจ็บปวดล้างสมองซะ!",
    "ลุกไปอาบน้ำเย็นจัด 5 นาทีเดี๋ยวนี้ ไป!",
    "กระโดดตบ 100 ครั้ง สลัดความขี้เกียจทิ้งไป!",
    "ห้ามจับมือถือ 1 ชั่วโมงนับจากนี้! นั่งสมาธิทบทวนความกากของตัวเอง!",
    "สควอช (ลุกนั่ง) 60 ที เอาให้ขาเบิร์น!",
    "เดินไปตะโกนใส่กำแพงว่า 'กูจะไม่ยอมกลับไปกระจอกอีก!' 10 รอบ!"
]

WARRIOR_OATHS = [
    "โลกนี้ไม่มีที่ยืนให้คนอ่อนแอ! ถ้ามึงเลือกที่จะขี้เกียจ ก็เตรียมตัวดูคนที่พยายามน้อยกว่ามึงแซงหน้าไปได้เลย!",
    "ข้ออ้างมีไว้สำหรับไอ้กระจอก! วันนี้มึงจะสร้างผลงาน หรือจะสร้างข้ออ้าง เลือกเอา!",
    "ความสบายในวันนี้ คือความชิบหายในวันหน้า! ลุกขึ้นมาบดขยี้ความขี้เกียจของมึงซะ!",
    "เวลาไม่เคยรอใคร ทุกวินาทีที่มึงไถมือถือโง่ๆ คือเวลาที่มึงกำลังฆ่าอนาคตตัวเอง!",
    "มึงบอกว่าอยากสำเร็จ แต่การกระทำมึงเหมือนคนรอวันตาย! ตื่น! แล้วไปทำในสิ่งที่ต้องทำเดี๋ยวนี้!",
    "ความเจ็บปวดจากการมีวินัย มันเทียบไม่ได้เลยกับความเจ็บปวดจากความเสียดายในตอนที่มึงแก่ตัวลง!",
    "ไม่มีใครมาช่วยมึงได้นอกจากตัวมึงเอง! อนาคตของมึงอยู่ในมือมึง เลิกหวังพึ่งโชคชะตาแล้วลงมือทำ!"
]

# 🩸 20 ประโยค: ผลของการกระจอก (Consequences)
WARRIOR_CONSEQUENCES = [
    "กูจะต้องทนเห็นคนที่พยายามน้อยกว่ากู ได้ดีกว่ากู!",
    "พรุ่งนี้กูก็จะตื่นมาเป็นไอ้ขี้แพ้คนเดิม ที่เก่งแต่ปาก!",
    "ความฝันที่กูโม้ไว้ ก็จะเป็นแค่อากาศธาตุ!",
    "กูจะกลายเป็นภาระของครอบครัวและคนที่รักกู!",
    "ชีวิตกูก็จะย่ำอยู่กับที่ ไม่มีวันเงยหน้าอ้าปากได้!",
    "กูจะต้องก้มหัวให้คนที่กูเกลียดไปตลอดชีวิต!",
    "อนาคตที่กูวาดฝันไว้ จะพังทลายลงด้วยมือของกูเอง!",
    "กูจะต้องเสียใจและเกลียดตัวเองในอีก 5 ปีข้างหน้า!",
    "กูมันก็แค่สวะที่ปล่อยให้เวลาชีวิตหมดไปวันๆ!",
    "คนที่ดูถูกกูไว้ เขาจะหัวเราะเยาะกูได้อย่างเต็มปาก!",
    "กูจะไม่มีวันก้าวข้ามขีดจำกัดของตัวเองได้เลย!",
    "ความเหนื่อยยากทั้งหมดที่ผ่านมา จะกลายเป็นศูนย์!",
    "กูจะต้องใช้ชีวิตแบบ 'รู้งี้' ไปจนวันตาย!",
    "กูจะสูญเสียอำนาจในการควบคุมชีวิตตัวเอง ให้กับความขี้เกียจ!",
    "กูจะตอกย้ำให้โลกเห็นว่ากูมันเหยียบขี้ไก่ไม่ฝ่อ!",
    "กูจะถูกระบบทุนนิยมกลืนกินและเป็นได้แค่ไอ้กระจอกตลอดไป!",
    "พ่อแม่กูจะต้องเหนื่อยต่อไป เพราะความไม่เอาไหนของกู!",
    "กูจะสูญเสียความเคารพในตัวเองจนหมดสิ้น!",
    "ทุกคำดูถูกที่เคยได้รับ มันจะกลายเป็นความจริง!",
    "กูยอมรับสภาพว่าตัวเองเป็นได้แค่นี้... แค่ไอ้ขี้แพ้ที่ไร้ค่า!"
]

# 🔥 20 ประโยค: ปลุกใจขั้นสุดยอด (Motivations)
WARRIOR_MOTIVATIONS = [
    "มึงจะยอมแพ้แค่นี้หรอวะ? กลับไปกระจอกเหมือนเดิมก็เอาดิ ถ้ารับตัวเองได้!",
    "ความเหนื่อยวันนี้ คือกล้ามเนื้อของความสำเร็จพรุ่งนี้ ลุยดิวะ!",
    "ปีศาจขี้เกียจมันกำลังหัวเราะมึงอยู่... มึงจะยอมให้มันชนะหรอ? ฟาดหน้ามัน!",
    "ไม่มีข้ออ้างสำหรับคนจริง! ทางเดียวคือเดินหน้าและบดขยี้เป้าหมายให้แหลก!",
    "ก้มหน้าทำไป! เหงื่อและน้ำตามันคือร่องรอยของนักรบ ไม่ใช่น้ำตาของไอ้ขี้แพ้!",
    "โลกไม่จำคนเกือบสำเร็จ... เอาให้สุด อย่าหยุดแค่คำว่า 'พอแล้ว'!",
    "ถ้ามันง่าย ทุกคนก็รวยและสำเร็จไปหมดแล้ว! ความยากนี่แหละคือด่านคัดคนจริง!",
    "พักได้ แต่อย่ายอมแพ้! เลียแผลเสร็จแล้วลุกขึ้นมาจับอาวุธซะ!",
    "ความเจ็บปวดจากการฝืนตัวเอง มีค่ามากกว่าความสบายที่พาไปสู่ความล้มเหลว!",
    "อย่ายอมให้คำดูถูกของพวกสวะกลายเป็นความจริง มึงคือของจริง พิสูจน์ดิวะ!",
    "มึงเดินมาไกลเกินกว่าจะหันหลังกลับไปซุกผ้าห่มแล้ว ลุกขึ้น!",
    "คนกระจอกจะหาเหตุผลที่จะหยุด แต่คนจริงจะหาเหตุผลที่จะลุยต่อ!",
    "อย่าทรยศความฝันตัวเองด้วยความขี้เกียจชั่วคราว!",
    "มึงเกิดมาเพื่อเป็นราชสีห์ อย่าลดตัวไปทำตัวเป็นหมาขี้แพ้ที่คอยหลบมุม!",
    "ศัตรูที่น่ากลัวที่สุดคือตัวมึงเองในกระจก เอาชนะมันให้ได้!",
    "ทุกก้าวที่มึงฝืนเดินต่อ คือการตบหน้าโชคชะตาที่บอกว่ามึงทำไม่ได้!",
    "มึงจะปล่อยให้เวลาชีวิตไหลทิ้งไปเปล่าๆ หรือจะใช้มันสร้างอาณาจักรของมึงเอง!",
    "เหนื่อยหรอ? แต่อย่าลืมนะว่าความจนและความล้มเหลวมันเหนื่อยกว่านี้ร้อยเท่า!",
    "เวลาไม่เคยรอใคร ทุกวินาทีที่มึงทิ้งไป คืออนาคตที่ค่อยๆ พังทลาย!",
    "ความสำเร็จไม่ได้ตกลงมาจากฟ้า แต่มันถูกสร้างจากการกัดฟันสู้ในวันที่มึงไม่อยากทำ!"
]

ABYSS_VOICES = [
    "มึงทำ '{task}' ไม่ได้หรอก... ยอมแพ้แล้วกลับไปนอนโง่ๆ ซะเถอะ...",
    "ดอง '{task}' ไว้ก่อนสิ ไม่มีใครรู้หรอก พักก่อน... มึงมันก็แค่ไอ้ขี้แพ้คนเดิมนั่นแหละ!",
    "ถ้า '{task}' มันยากนัก ก็เทมันทิ้งไปสิ มึงจะได้กลับไปใช้ชีวิตกากๆ แบบที่มึงคู่ควรไง..."
]

COMMANDER_VOICES = [
    "อย่าไปฟังเสียงสวะนั่น! ลุกขึ้นมา! ร่างกายนี้มึงคุม ไปฟาด '{task}' ให้แหลกคามือ!",
    "ความสำเร็จไม่เคยปรานีคนอ่อนแอ! ปิดหูแล้วเดินหน้าชน '{task}' ตอนนี้เลย!",
    "ความเจ็บปวดจากการมีวินัย ดีกว่าความเจ็บปวดจากความเสียใจ! จับอาวุธไปลุย '{task}' ซะ!"
]

AMBUSH_TASKS = [
    "กฎก้าวสุดท้าย! ไปแพลงก์ 1 นาทีก่อนนอน!",
    "คิดว่ารอดแล้วหรอ? วิดพื้น 20 ที!",
    "เขียนเป้าหมายพรุ่งนี้ 3 ข้อใส่กระดาษเดี๋ยวนี้!"
]

def get_safe_email(email): 
    return email.replace(".", "-").replace("@", "-")

def get_title(level):
    if level < 3: return "🤡 ไอ้ขี้แพ้ที่รอการพิสูจน์"
    elif level < 7: return "⚙️ ผู้ทุบทำลายขีดจำกัด (Limit Breaker)"
    elif level < 12: return "🦍 นักรบผู้คุมปีศาจในใจ (Mind Master)"
    else: return "👑 ปรมาจารย์แห่งวินัยเหล็ก (Discipline God)"

def get_priority_score(task_type):
    if not task_type: return 4
    if "🔴 ด่วนสุด" in task_type or "🔥 งานฉุกเฉิน" in task_type: return 1
    if "🟡 ปานกลาง" in task_type: return 2
    if "🟢 ชิลๆ" in task_type: return 3
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
    if score == 1: base_exp = 40
    elif score == 2: base_exp = 20
    else: base_exp = 10
    
    bonus_exp = 0
    if task.get("is_boss"): bonus_exp += 100
    if task.get("bounty"): bonus_exp += 50
    if task.get("subtasks"): bonus_exp += len(task["subtasks"]) * 10  
        
    raw_total_exp = base_exp + bonus_exp
    multiplier = 1.0
    if current_streak >= 30: multiplier = 1.5
    elif current_streak >= 7: multiplier = 1.2
    elif current_streak >= 3: multiplier = 1.1
        
    final_exp = int(raw_total_exp * multiplier)
    if score == 1: fail_reduce = 10
    elif score == 2: fail_reduce = 5
    else: fail_reduce = 2
    
    if task.get("is_boss"): fail_reduce += 15
    if task.get("bounty"): fail_reduce += 5
    
    return final_exp, fail_reduce

def load_db():
    if FIREBASE_URL == "" or FIREBASE_URL is None:
        st.error("🚨 ใส่ลิงก์ Firebase ก่อน!")
        st.stop()
    try:
        res = requests.get(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}")
        if res.status_code == 200 and res.json() is not None:
            data = res.json()
            if not isinstance(data, dict): data = {}
            defaults = {
                "users": {}, "missions": {}, "study_missions": {}, 
                "backlog": {}, "dark_room": {}, "anti_simp": {}, 
                "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, 
                "deadlines": {}, "haters": {}, "finance": {}, 
                "iron_habits": {}, "exams": {}, "beat_yesterday": {}, 
                "limit_breaks": {}, "weakness_fuel": {}, "notes": {}
            }
            for k, v in defaults.items():
                if k not in data or data[k] is None: 
                    data[k] = v
            return data
    except: 
        pass
    
    return {
        "users": {}, "missions": {}, "study_missions": {}, "backlog": {}, 
        "dark_room": {}, "anti_simp": {}, "dopamine_fails": {}, 
        "excuses": {}, "cookie_jar": {}, "deadlines": {}, "haters": {}, 
        "finance": {}, "iron_habits": {}, "exams": {}, "beat_yesterday": {}, 
        "limit_breaks": {}, "weakness_fuel": {}, "notes": {}
    }

def save_db(data):
    try: 
        requests.put(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}", json=data)
    except Exception as e: 
        st.error(f"🚨 เซฟข้อมูลลงฐานข้อมูลไม่สำเร็จ! Error: {e}")

db = load_db()

# ==========================================
# 2. OVERLAY นรก (PUNISHMENT ACTIVE)
# ==========================================
if "punishment_active" in st.session_state:
    st.error("🚨 วงล้อแห่งกรรมทำงาน! มึงหลุดจากวินัย ต้องชดใช้! 🚨")
    st.title(f"🔥 คำสั่งชดใช้กรรม: {st.session_state.punishment_task}")
    if st.button("🩸 กูทำเสร็จแล้ว! (กลับสู่ Discipline Arc)"):
        del st.session_state.punishment_active
        safe_rerun()
    st.stop() 

# ==========================================
# 3. ระบบล็อกอิน
# ==========================================
if "current_user" not in st.session_state: 
    st.session_state.current_user = None

with st.sidebar:
    st.title("⚙️ DISCIPLINE ARC")
    st.caption(f"🗓️ วันที่: {today_str}") 
    
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือกโหมด:", ["⚡ ล็อกอิน", "➕ สร้างไอดีใหม่"], key="auth_mode_radio")
        st.divider()
        
        if auth_mode == "➕ สร้างไอดีใหม่":
            name_input = st.text_input("ชื่อนักรบ:", key="reg_name")
            email_input = st.text_input("อีเมล (ID):", key="reg_email")
            if st.button("เข้าสู่ Discipline Arc!"):
                if email_input and name_input:
                    safe_email = get_safe_email(email_input)
                    if safe_email in db.get("users", {}): 
                        st.error("อีเมล/ID นี้มีในระบบแล้ว!")
                    else:
                        db["users"][safe_email] = {
                            "username": name_input, "level": 1, "exp": 0, "streak": 0, 
                            "blood_debt": 0, "in_cage": False, "ghost_exp": 0, 
                            "ambush_task": "", "failure_prob": 10, "last_login": today_str, 
                            "cleared_yesterday": True, "order_locked": False,
                            "target_name": "เป้าหมายสูงสุดของชีวิต", 
                            "target_date": str(today_date + timedelta(days=90)),
                            "daily_oath_date": ""
                        }
                        save_db(db)
                        st.success("🔥 ลงทะเบียนสำเร็จ! ล็อกอินเลย!")
                else: 
                    st.warning("กรอกข้อมูลให้ครบ!")
                
        elif auth_mode == "⚡ ล็อกอิน":
            if not db.get("users"): 
                st.warning("ยังไม่มีนักรบในระบบ ไปสร้างไอดีก่อน!")
            else:
                user_options = {f"{data.get('username', 'Unknown Warrior')}": email for email, data in db["users"].items() if isinstance(data, dict)}
                selected_display = st.selectbox("เลือกบัญชีของคุณ:", list(user_options.keys()), key="login_select")
                
                if st.button("🔥 เริ่มต้นวันใหม่ (Login)"):
                    safe_email = user_options[selected_display]
                    user_data = db["users"][safe_email]
                    
                    if "target_name" not in user_data: 
                        user_data["target_name"] = "เป้าหมายสูงสุดของชีวิต"
                        user_data["target_date"] = str(today_date + timedelta(days=90))

                    if user_data["last_login"] != today_str:
                        user_data["ghost_exp"] += 25 
                        user_data["order_locked"] = False
                        unpaid_bounties = [m for m in db.get("missions", {}).get(safe_email, []) if isinstance(m, dict) and m.get("bounty") and not m.get("เสร็จแล้ว")]
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
                    safe_rerun()
    else:
        safe_email = st.session_state.current_user
        u_data = db["users"][safe_email]
        st.error(f"👤 ตัวตน: {u_data['username']}")
        st.info(f"🛡️ ฉายา: {get_title(u_data['level'])}")
        
        scars = len(db.get("dopamine_fails", {}).get(safe_email, []))
        st.markdown(f"🩻 **รอยแผลความพ่ายแพ้: {scars} รอย**")
        st.warning(f"🔥 ความต่อเนื่อง (Consistency): {u_data['streak']} วัน")
        
        current_streak = u_data.get("streak", 0)
        if current_streak >= 30: st.success("👑 BUFF: วินัยระดับพระเจ้า (EXP x 1.5)")
        elif current_streak >= 7: st.success("🔥 BUFF: วินัยเหล็ก (EXP x 1.2)")
        elif current_streak >= 3: st.success("⚡ BUFF: เริ่มก่อร่างสร้างวินัย (EXP x 1.1)")
        else: st.caption("💀 BUFF: ไร้วินัย (ไม่มีโบนัส)")
        
        needs_save = False
        while u_data["exp"] >= 100:
            u_data["level"] += 1; u_data["exp"] -= 100; needs_save = True
            st.toast(f"🔥 LEVEL UP! วินัยของมึงยกระดับเป็น Lv.{u_data['level']}", icon="⚙️")
        while u_data["exp"] < 0:
            if u_data["level"] > 1: u_data["level"] -= 1; u_data["exp"] += 100
            else: u_data["exp"] = 0
            needs_save = True
            
        if needs_save: save_db(db)
            
        prog_val = max(0.0, min(1.0, u_data["exp"] / 100))
        st.progress(prog_val, text=f"Lv.{u_data['level']} | EXP: {u_data['exp']}/100")
        
        st.divider()
        monk_mode = st.toggle("🧘‍♂️ MONK MODE (ตัดขาดโลกภายนอก)", key="toggle_monk")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.current_user = None
            safe_rerun()

if st.session_state.current_user is None:
    st.title("⚙️ DISCIPLINE ARC: V.50 MAXIMUM OVERDRIVE")
    st.info("👈 ล็อกอินด้านซ้ายเพื่อเผชิญหน้ากับปีศาจในใจและสร้างวินัยเหล็ก!")
    st.stop()

safe_email = st.session_state.current_user
user = db["users"][safe_email]

# ==========================================
# 🚨 THE DAILY OATH (กำแพงดัดสันดานความขี้เกียจ)
# ==========================================
if user.get("daily_oath_date") != today_str:
    st.markdown("<h1 style='text-align: center; color: #ff4b4b; font-size: 3em;'>🩸 ดึงสติรับวันใหม่!</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>ก่อนที่มึงจะเริ่มวัน กูมีเรื่องจะบอก...</h3><br>", unsafe_allow_html=True)
    
    oath_msg = random.choice(WARRIOR_OATHS)
    
    st.error(f"### ⚔️ เสียงจากแม่ทัพเหล็ก:\n\n> **\"{oath_msg}\"**")
    st.warning("ความขี้เกียจกำลังรอแดกหัวมึงอยู่ มึงจะยอมแพ้ตั้งแต่ยังไม่เริ่ม แล้วกลับไปซุกผ้าห่ม หรือจะลุกขึ้นมาสู้เพื่อชีวิตตัวเอง?")
    
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔥 กูขอสาบานว่าจะไม่ยอมเป็นไอ้ขี้แพ้! (เข้าสู่สมรภูมิ)", use_container_width=True, type="primary"):
            user["daily_oath_date"] = today_str
            save_db(db)
            safe_rerun()
            
    st.stop() 

# ==========================================
# 🔥 คอนฟิกโครงสร้าง Database
# ==========================================
list_keys = ["missions", "study_missions", "backlog", "dark_room", "anti_simp", "dopamine_fails", "excuses", "cookie_jar", "deadlines", "haters", "iron_habits", "limit_breaks", "weakness_fuel", "notes"]
dict_keys = ["finance", "exams", "beat_yesterday"]

for k in list_keys:
    if safe_email not in db[k] or db[k][safe_email] is None: db[k][safe_email] = []
    else:
        if isinstance(db[k][safe_email], dict): db[k][safe_email] = list(db[k][safe_email].values())
        if isinstance(db[k][safe_email], list): db[k][safe_email] = [item for item in db[k][safe_email] if item is not None]

for k in dict_keys:
    if safe_email not in db[k] or db[k][safe_email] is None: 
        if k == "finance": db[k][safe_email] = {"goal_name": "ยังไม่ได้ตั้ง", "goal_amount": 0, "current": 0}
        else: db[k][safe_email] = {}

finance = db["finance"][safe_email]
current_streak = user.get("streak", 0)

# ===== 🚨 CHECK OVERDUE BACKLOG =====
overdue_count = 0
for task in db["backlog"][safe_email]:
    if not isinstance(task, dict): continue 
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
    st.error(f"🚨 ไร้วินัย! มีงานเป้าหมายเลยกำหนด {overdue_count} งาน! มึงโดนลงโทษหนี้เลือด รีบเคลียร์ซะ!")

# ==========================================
# 🎯 ส่วนหัว: ปลุกพลัง & ระบบนับถอยหลังอนาคต
# ==========================================
try: t_date = datetime.strptime(user.get("target_date", str(today_date)), "%Y-%m-%d").date()
except: t_date = today_date + timedelta(days=90)
days_left = (t_date - today_date).days

colTop1, colTop2, colTop3 = st.columns([1, 1, 3])
with colTop1:
    if st.button("🎰 วงล้อชดใช้กรรม\n(ดึงสติกลับมา)", type="primary", use_container_width=True, key="btn_punish"):
        st.session_state.punishment_active = True
        st.session_state.punishment_task = random.choice(PUNISHMENTS)
        safe_rerun()
with colTop2:
    if st.button("⚡ ปลุกวินัย\n(Focus Now!)", use_container_width=True, key="btn_boost"):
        st.toast("🔥 อย่าถอย! ลุยดิวะ!", icon="⚙️")
with colTop3:
    st.error(f"⏳ **ชะตาชีวิต:** {user.get('target_name', 'เป้าหมายสูงสุด')} ในอีก **{days_left}** วัน!")
    with st.popover("⚙️ ตั้งค่านับถอยหลัง"):
        new_t_name = st.text_input("เป้าหมายสูงสุด:", user.get("target_name", ""), key="input_tname")
        new_t_date = st.date_input("วันกำหนด (Deadline):", t_date, key="input_tdate")
        if st.button("บันทึกเป้าหมาย", key="btn_save_target"):
            user["target_name"] = new_t_name
            user["target_date"] = str(new_t_date)
            save_db(db)
            safe_rerun()

if user.get("in_cage"): st.error("🚨 **มึงอยู่ในกรง!** วิดพื้นจ่ายหนี้เลือดเพื่อออกมาทำตามแผนซะ!")

st.divider()

# ==========================================
# 🗺️ THE ROADMAP (แผนผังชีวิตบังคับกฎ)
# ==========================================
st.markdown("## 🗺️ THE ULTIMATE ROADMAP (แผนผังชีวิตประจำวัน)")
st.caption("กฎเหล็กของ Roadmap: งาน (Missions) ➔ เรียน (Study) ➔ วินัยเหล็ก (Habits) ห้ามทำข้ามสเต็ปเด็ดขาด!")

raw_m = [m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False) and m.get("skip_today_date") != today_str]
raw_s = [s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว") and not s.get("รอตรวจ", False) and s.get("skip_today_date") != today_str]
raw_h = []
for h in db["iron_habits"][safe_email]:
    if isinstance(h, dict) and h.get("last_done_date") != today_str:
        raw_h.append({
            "ภารกิจ": h["name"], "user_order": h.get("user_order", 99), "battle_role": "Support", "is_boss": False, "ประเภท": "🟢 ชิลๆ", "is_habit": True
        })

all_active_tasks = raw_m + raw_s + raw_h

def get_hierarchy_score(t):
    if t.get("is_habit"): return 3
    if t.get("is_study"): return 2
    return 1

all_active_tasks.sort(key=lambda x: (get_hierarchy_score(x), x.get("user_order", 99)))

if not all_active_tasks:
    st.success("✅ Roadmap ว่างเปล่า! วันนี้เคลียร์แผนผังชีวิตหมดแล้ว ยอดเยี่ยมมาก!")
else:
    mermaid_str = "graph TD\n"
    mermaid_str += "classDef targetNode fill:#ff4b4b,stroke:#ffffff,stroke-width:4px,color:#ffffff,font-size:18px,font-weight:bold;\n"
    mermaid_str += "classDef pendingNode fill:#262730,stroke:#888888,stroke-width:2px,color:#ffffff,font-size:16px;\n"
    mermaid_str += "classDef habitNode fill:#1E88E5,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-size:16px;\n"
    mermaid_str += "START((🔥 เริ่มวัน)):::pendingNode --> "
    
    for idx, task in enumerate(all_active_tasks):
        task_id = f"T{idx}"
        q_num = task.get("user_order", 99)
        q_label = f"[Q{q_num}] " if q_num != 99 else ""
        
        if task.get("is_habit"):
            icon = "⛓️"
            node_class = "habitNode" if idx != 0 else "targetNode"
        elif task.get("is_study"):
            icon = "📖"
            node_class = "targetNode" if idx == 0 else "pendingNode"
        else:
            icon = "🔪"
            node_class = "targetNode" if idx == 0 else "pendingNode"
            
        task_name = str(task.get('ภารกิจ', '')).replace('"', "'").replace('\n', ' ').replace('(', '[').replace(')', ']')
        node_label = f"{q_label}{icon} {task_name}"
        
        mermaid_str += f'{task_id}["{node_label}"]:::{node_class}\n'
        
        if idx < len(all_active_tasks) - 1:
            mermaid_str += f'{task_id} --> '
            
    mermaid_str += f'{task_id} --> END((🌙 จบวัน/พักผ่อน)):::pendingNode\n'
    st.markdown(f"```mermaid\n{mermaid_str}\n```")

    # ==========================================
    # 🧠 THE INTERNAL CLASH (สงครามในหัวมึง)
    # ==========================================
    next_task_name = all_active_tasks[0]['ภารกิจ']
    st.divider()
    st.markdown("### 🧠 สงครามในจิตใจ (The Clash of Minds)")
    c_abyss, c_cmdr = st.columns(2)
    
    with c_abyss:
        abyss_msg = random.choice(ABYSS_VOICES).format(task=next_task_name)
        st.error(f"💀 **ก้นเหวแห่งความขี้เกียจ (ดึงลง):**\n\n\"{abyss_msg}\"")
        
    with c_cmdr:
        cmdr_msg = random.choice(COMMANDER_VOICES).format(task=next_task_name)
        st.success(f"⚔️ **แม่ทัพเหล็ก (กระชากขึ้น):**\n\n\"{cmdr_msg}\"")

st.divider()

# ==========================================
# 5. DUAL REALITY DASHBOARD
# ==========================================
if monk_mode:
    st.markdown("## 🧘‍♂️ MONK MODE ACTIVE: สมาธิขั้นสุด!")
    colLeft, colRight = st.columns([0.01, 1]) 
else: 
    colLeft, colRight = st.columns([1.2, 2.8])

with colLeft:
    if not monk_mode:
        st.markdown("### 🗑️ ขยะในจิตใจ (Distractions)")
        fail_prob = user.get('failure_prob', 10)
        st.markdown(f"**📉 โอกาสหลุดวงโคจรวินัย: {fail_prob}%**")
        st.progress(fail_prob / 100)
        
        if st.button("💀 กดยอมแพ้ให้สิ่งเร้า", key="btn_fail_dopamine", use_container_width=True):
            db["dopamine_fails"][safe_email].append(today_str)
            user["exp"] = 0; user["blood_debt"] += 50; user["in_cage"] = True
            user["failure_prob"] = min(100, user["failure_prob"] + 20)
            save_db(db); safe_rerun()

        st.markdown("#### 🩸 เชื้อเพลิงความแค้น (Vengeance Fuel)")
        st.caption("จดความกากของตัวเองในอดีต เอาไว้ดูเพื่อความเจ็บใจ จะได้ไม่ทำตัวแบบนั้นอีก!")
        with st.form("weakness_fuel_form", clear_on_submit=True):
            w_text = st.text_input("ความอ่อนแอที่มึงเคยทำพลาด:", key="input_weakness")
            if st.form_submit_button("🔥 เผาความกากเป็นพลัง!"):
                if w_text: 
                    db["weakness_fuel"][safe_email].append({"id": str(uuid.uuid4()), "text": w_text})
                    save_db(db); safe_rerun()
                    
        if safe_email in db.get("weakness_fuel", {}) and len(db["weakness_fuel"][safe_email]) > 0:
            random_weakness = random.choice(db["weakness_fuel"][safe_email])
            w_disp = random_weakness.get("text", "") if isinstance(random_weakness, dict) else random_weakness
            st.error(f"🩸 **มึงเคยกากแบบนี้:**\n\n\"{w_disp}\"\n\n*(จงแค้นตัวเอง และห้ามกลับไปเป็นไอ้ขี้แพ้แบบเดิม!)*")

        st.markdown("#### 🗣️ THE HATER'S WALL")
        with st.form("hater_form", clear_on_submit=True):
            h_text = st.text_input("คำดูถูกที่ฝังใจ:", key="input_hater")
            if st.form_submit_button("ฝังความแค้น"):
                if h_text: 
                    db["haters"][safe_email].append(h_text); save_db(db); safe_rerun()
        if safe_email in db.get("haters", {}) and isinstance(db["haters"][safe_email], list) and len(db["haters"][safe_email]) > 0:
            st.warning(f"🤬 \"{random.choice(db['haters'][safe_email])}\"")

with colRight:
    st.markdown("## ⚙️ DISCIPLINE ZONE (พื้นที่ลงมือทำ)")
    
    tab_missions, tab_study, tab_habits, tab_notes, tab_backlog, tab_cookie, tab_academic = st.tabs([
        "🔪 งาน", "📖 เรียน", "⛓️ วินัยเหล็ก", "📓 โน้ตบัญชาการ", "📝 สมุดจดแผน", "🍪 ชัยชนะ", "📚 ลานประลอง"
    ])
    
    # ----------------------------------------------------
    # TAB 1: ภารกิจวันนี้ (Daily Missions)
    # ----------------------------------------------------
    with tab_missions:
        st.markdown("### 🔪 งานที่ต้องบดขยี้วันนี้")
        
        raw_active_missions = [m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว")]
        active_single_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False) and not m.get("subtasks")]
        
        if len(active_single_missions) >= 3:
            st.error("🚨 **กฎของ Discipline:** ห้ามรับงานย่อยเกิน 3 งาน! ต้องซอยงานใหญ่เท่านั้น!")
        
        with st.expander("➕ เพิ่มงานด่วนลงผังชีวิต"):
            with st.form("mission_form", clear_on_submit=True):
                m_name = st.text_input("ชื่อภารกิจ:", key="m_name")
                m_detail = st.text_area("รายละเอียด / Note เพิ่มเติม (ถ้ามี):", key="m_detail")
                m_conseq = st.text_input("🩸 ผลของการกระจอก (ถ้ากูไม่ทำงานนี้ จะเกิดอะไรขึ้น? / ว่างไว้เพื่อสุ่มคำด่า):", key="m_conseq")
                m_is_boss = st.checkbox("💀 THE BOSS FIGHT (งานยักษ์)", key="m_is_boss")
                m_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"], key="m_type")
                m_bounty = st.checkbox("⚔️ เดิมพันศักดิ์ศรี! (พลาดโดนหนี้ 100 ที)", key="m_bounty")
                m_subtasks_text = st.text_area("🔪 ซอยขั้นตอนให้ชัดเจน (Enter ขึ้นบรรทัดใหม่):", key="m_subtasks")
                m_dl_type = st.radio("⏰ ระบบเวลา:", ["ไม่กำหนด", "🗓️ Deadline", "🎯 วันเป้าหมาย"], horizontal=True, key="m_dl_type")
                m_deadline = st.date_input("เลือกวันที่:", key="m_deadline")
                
                if st.form_submit_button("เพิ่มเข้าแผนผัง"):
                    if m_name:
                        subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in m_subtasks_text.split('\n') if s.strip()]
                        if not subtasks and len(active_single_missions) >= 3:
                            st.error("🤡 โควตางานเดี่ยวเต็มแล้ว ต้องซอยข้อย่อย!")
                        else:
                            final_dl = str(m_deadline) if m_dl_type != "ไม่กำหนด" else ""
                            db["missions"][safe_email].append({
                                "id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": m_name, "รายละเอียด": m_detail, 
                                "consequence": m_conseq.strip(), # เซฟข้อมูล (ถ้าว่างระบบจะดึงจาก Hashing)
                                "ประเภท": m_type, "bounty": m_bounty, "is_boss": m_is_boss,
                                "custom_order": 99, "user_order": 99, "battle_role": "Main", "is_queued": False, "skip_today_date": "", "subtasks": subtasks, "เสร็จแล้ว": False, 
                                "รอตรวจ": False, "deadline": final_dl, "deadline_type": m_dl_type
                            })
                            save_db(db); safe_rerun()
                    
        todo_missions = [m for m in raw_active_missions if not m.get("รอตรวจ", False)]
        pending_missions = [m for m in raw_active_missions if m.get("รอตรวจ", False)]
        
        todo_missions.sort(key=lambda x: (x.get("user_order", 99), get_role_score(x.get("battle_role", "Main")), 0 if x.get("is_boss") else 1, get_deadline_score(x.get("deadline", "")), get_priority_score(x.get("ประเภท", ""))))
        
        if todo_missions:
            with st.expander("🎯 วางแผนลำดับงาน (Q-Order Strategy)", expanded=False):
                with st.form("set_order_form"):
                    st.info("ระบุตัวเลขคิวงาน (1, 2, 3...) แล้วกด 'ล็อคผังชีวิต' ทีเดียว!")
                    new_orders = {}
                    for m in todo_missions:
                        col_q, col_n = st.columns([1, 5])
                        new_orders[m["id"]] = col_q.number_input("คิว", min_value=1, max_value=99, value=m.get("user_order", 99), step=1, key=f"q_{m['id']}", label_visibility="collapsed")
                        is_boss_lbl = "💀 [BOSS] " if m.get("is_boss") else ""
                        col_n.write(f"{is_boss_lbl}{m['ภารกิจ']}")
                    
                    if st.form_submit_button("🔒 ล็อคผังชีวิต! (เซฟแผนทั้งหมด)"):
                        for m in db["missions"][safe_email]:
                            if isinstance(m, dict) and m.get("id") in new_orders:
                                m["user_order"] = new_orders[m["id"]]
                        save_db(db); st.success("✅ อัปเดตผัง Roadmap ชีวิตเรียบร้อย!"); safe_rerun()

        if todo_missions:
            for m in todo_missions:
                is_first_task = (m == todo_missions[0])
                bg_style = "border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; margin-bottom: 10px;" if is_first_task else "border: 1px solid #444; padding: 10px; border-radius: 5px; margin-bottom: 10px;"
                
                st.markdown(f"<div style='{bg_style}'>", unsafe_allow_html=True)
                c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6]) 
                
                task_mode_badge = "🔪 **[โครงงาน]**" if m.get("subtasks") else "⚡ **[ม้วนเดียวจบ]**"
                is_bounty = " ⚔️" if m.get("bounty") else ""; is_boss = " 💀 **[BOSS]**" if m.get("is_boss") else ""
                q_num = m.get("user_order", 99)
                q_badge = f"🎯 **[Q{q_num}]** " if q_num != 99 else ""
                
                is_overdue, deadline_badge = False, ""
                dl_str = m.get("deadline", "")
                if dl_str and dl_str != "":
                    try:
                        dl_date = datetime.strptime(dl_str, "%Y-%m-%d").date()
                        days_left_task = (dl_date - today_date).days
                        if days_left_task > 0: deadline_badge = f" ⏳ (เหลือ {days_left_task} วัน)"
                        elif days_left_task == 0: deadline_badge = f" 🚨 **(ต้องเสร็จวันนี้!)**"
                        else: deadline_badge = f" 💀 **(เลยกำหนด {-days_left_task} วัน)**"; is_overdue = True 
                    except: pass

                is_frozen = m.get("skip_today_date") == today_str
                was_frozen_yesterday = m.get("skip_today_date") != "" and not is_frozen
                if was_frozen_yesterday: m["skip_today_date"] = ""; save_db(db)
                    
                frozen_badge = " ❄️🚨 [เกราะแตก!]" if is_frozen and is_overdue else " ❄️ [แช่แข็ง]" if is_frozen else ""

                c1.write(f"**{m.get('ประเภท','')}** | {q_badge}{task_mode_badge}{is_boss}{is_bounty} {m['ภารกิจ']}{deadline_badge}{frozen_badge}")
                
                # 🔥 STABLE HYPE RENDERING LOGIC (The Ultimate Optimization)
                task_id = str(m.get("id", "unk"))
                display_conseq = m.get("consequence", "")
                if not display_conseq: 
                    display_conseq = WARRIOR_CONSEQUENCES[get_stable_index(task_id + "conseq", len(WARRIOR_CONSEQUENCES))]
                
                display_hype = m.get("motivation", "")
                if not display_hype: 
                    display_hype = WARRIOR_MOTIVATIONS[get_stable_index(task_id + "hype", len(WARRIOR_MOTIVATIONS))]
                
                # เรนเดอร์ความเจ็บปวดและการปลุกใจ
                c1.markdown(f"<div style='font-size: 0.9em; background: rgba(255, 0, 0, 0.1); padding: 5px; border-left: 3px solid #ff4b4b; margin-bottom: 5px; margin-top: 5px;'>🩸 <b>ถ้ากูไม่ทำ:</b> {display_conseq}</div>", unsafe_allow_html=True)
                c1.markdown(f"<div style='font-size: 0.9em; background: rgba(255, 165, 0, 0.1); padding: 5px; border-left: 3px solid #ffa500; margin-bottom: 10px;'>🔥 <b>ปลุกใจ:</b> {display_hype}</div>", unsafe_allow_html=True)
                
                if m.get("รายละเอียด"):
                    with st.expander("📝 ดูรายละเอียดงาน"):
                        st.write(m["รายละเอียด"])
                
                all_done, has_today_progress = True, False
                if m.get("subtasks"):
                    total_subs = len(m["subtasks"])
                    done_subs = len([s for s in m["subtasks"] if s.get("done")])
                    progress_pct = done_subs / total_subs if total_subs > 0 else 0
                    st.progress(progress_pct, text=f"📊 ความคืบหน้า: {done_subs} / {total_subs}")
                    
                    for i, stask in enumerate(m["subtasks"]):
                        is_done = stask.get("done", False)
                        done_date = stask.get("done_date", "")
                        is_locked = is_done and done_date != today_str
                        label = f"{stask['name']}" + (f" 🔒 ({done_date})" if is_locked else "")
                        can_interact = not is_locked and (not is_frozen or is_overdue)
                        checked = st.checkbox(label, value=is_done, disabled=not can_interact, key=f"st_{m['id']}_{i}")
                        
                        if can_interact and checked != is_done:
                            m["subtasks"][i]["done"] = checked; m["subtasks"][i]["done_date"] = today_str if checked else ""; save_db(db); st.toast("🔥 บดขยี้ได้ 1 สเต็ป!", icon="⚙️"); safe_rerun()
                        if m["subtasks"][i].get("done_date", "") == today_str: has_today_progress = True
                            
                    all_done = all(stask.get("done", False) for stask in m["subtasks"])
                else:
                    all_done = True 

                if is_frozen:
                    if c4.button("🔥 ปลดล็อก", key=f"unfrz_{m['id']}", use_container_width=True): m["skip_today_date"] = ""; save_db(db); safe_rerun()
                else:
                    if c4.button("❄️ แช่แข็ง", key=f"frz_{m['id']}", use_container_width=True): m["skip_today_date"] = today_str; save_db(db); safe_rerun()

                if all_done and (not is_frozen or is_overdue):
                    if c2.button("✅ สำเร็จ", key=f"m_{m['id']}"):
                        m["เสร็จแล้ว"] = True
                        exp_gain, fail_reduce = calculate_task_rewards(m, current_streak)
                        user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                    if c3.button("📤 ส่งตรวจ", key=f"pend_{m['id']}"): m["รอตรวจ"] = True; save_db(db); safe_rerun()
                else: c2.caption("❄️ แช่แข็ง" if is_frozen and not is_overdue else "🔒 งานย่อยคาอยู่")
                if c5.button("🗑️", key=f"del_m_{m['id']}"): db["missions"][safe_email].remove(m); save_db(db); safe_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        else: st.success("✅ วันนี้เคลียร์แผนผังงานหมดแล้ว!")

        if pending_missions:
            st.divider(); st.markdown("### ⏳ งานที่รอรีวิวผลงาน")
            for m in pending_missions:
                c1, c2, c3 = st.columns([5, 2, 2])
                c1.caption(f"⏳ {'💀 ' if m.get('is_boss') else ''}{m['ภารกิจ']}")
                if c2.button("✅ ตรวจผ่าน", key=f"appr_{m['id']}"):
                    m["เสร็จแล้ว"] = True; m["รอตรวจ"] = False
                    exp_gain, fail_reduce = calculate_task_rewards(m, current_streak)
                    user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                if c3.button("⏪ ดึงกลับมาทำ", key=f"revert_{m['id']}"): m["รอตรวจ"] = False; save_db(db); safe_rerun()

    # ----------------------------------------------------
    # 📖 TAB 2: ภารกิจการเรียนและการทบทวน
    # ----------------------------------------------------
    with tab_study:
        st.markdown("### 📖 วิชาที่ต้องบรรลุในวันนี้")
        raw_active_study = [s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว")]
        active_single_study = [s for s in raw_active_study if not s.get("รอตรวจ", False) and not s.get("subtasks")]
        
        if len(active_single_study) >= 3: st.error("🚨 **กฎของ Discipline:** ห้ามแอดวิชาเดี่ยวเกิน 3 วิชา!")
            
        with st.expander("➕ เพิ่มวิชาเข้าแผนผัง"):
            with st.form("study_form", clear_on_submit=True):
                s_name = st.text_input("วิชา / หัวข้อที่ต้องติว:", key="s_name")
                s_detail = st.text_area("รายละเอียด / ขอบเขตเนื้อหา (ถ้ามี):", key="s_detail")
                s_conseq = st.text_input("🩸 ผลของการกระจอก (ถ้ากูไม่เรียนบทนี้ จะเกิดอะไรขึ้น? / ว่างไว้เพื่อสุ่มคำด่า):", key="s_conseq")
                s_is_boss = st.checkbox("💀 THE BOSS FIGHT (บทโหด)", key="s_is_boss")
                s_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 ติวเข้ม", "🟡 ปานกลาง", "🟢 ชิลๆ"], key="s_type")
                s_subtasks_text = st.text_area("🔪 ซอยบทย่อยที่ต้องเก็บ (ทีละบรรทัด):", key="s_subtasks")
                s_dl_type = st.radio("⏰ ระบบเวลา:", ["ไม่กำหนด", "🗓️ Deadline", "🎯 วันเป้าหมาย"], horizontal=True, key="s_dl_type")
                s_deadline = st.date_input("เลือกวันที่:", key="s_deadline")
                
                if st.form_submit_button("เพิ่มเข้าหลักสูตร"):
                    if s_name:
                        subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in s_subtasks_text.split('\n') if s.strip()]
                        if not subtasks and len(active_single_study) >= 3: st.error("🤡 โควตาเต็ม จงแอดเป็นบทย่อย!")
                        else:
                            final_dl = str(s_deadline) if "ไม่กำหนด" not in s_dl_type else ""
                            db["study_missions"][safe_email].append({
                                "id": str(uuid.uuid4()), "วันที่": today_str, "ภารกิจ": s_name, "รายละเอียด": s_detail, 
                                "consequence": s_conseq.strip(),
                                "ประเภท": s_type, "bounty": False, "is_boss": s_is_boss,
                                "custom_order": 99, "user_order": 99, "battle_role": "Main", "is_queued": False, "skip_today_date": "", "subtasks": subtasks, "เสร็จแล้ว": False, 
                                "รอตรวจ": False, "deadline": final_dl, "deadline_type": s_dl_type, "is_study": True
                            })
                            save_db(db); safe_rerun()
                            
        todo_study = [s for s in raw_active_study if not s.get("รอตรวจ", False)]
        pending_study = [s for s in raw_active_study if s.get("รอตรวจ", False)]
        
        todo_study.sort(key=lambda x: (x.get("user_order", 99), get_role_score(x.get("battle_role", "Main")), 0 if x.get("is_boss") else 1, get_deadline_score(x.get("deadline", "")), get_priority_score(x.get("ประเภท", ""))))
        
        if todo_study:
            with st.expander("🎯 วางแผนลำดับวิชาเรียน (Q-Order Strategy)", expanded=False):
                with st.form("set_study_order_form"):
                    st.info("ระบุเลขคิวเรียน ระบบจะดึงไปร้อยเรียงในผัง Roadmap ด้านบนสุด!")
                    new_s_orders = {}
                    for s in todo_study:
                        col_q, col_n = st.columns([1, 5])
                        new_s_orders[s["id"]] = col_q.number_input("คิว", min_value=1, max_value=99, value=s.get("user_order", 99), step=1, key=f"q_s_{s['id']}", label_visibility="collapsed")
                        is_boss_lbl = "💀 [BOSS] " if s.get("is_boss") else ""
                        col_n.write(f"{is_boss_lbl}{s['ภารกิจ']}")
                    
                    if st.form_submit_button("🔒 ล็อคผังเรียน! (เซฟแผน)"):
                        for s in db["study_missions"][safe_email]:
                            if isinstance(s, dict) and s.get("id") in new_s_orders:
                                s["user_order"] = new_s_orders[s["id"]]
                        save_db(db); st.success("✅ อัปเดตผัง Roadmap การเรียน!"); safe_rerun()

        if todo_study:
            for s in todo_study:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6])
                    
                    task_mode_badge = "📖 **[ติวโครงใหญ่]**" if s.get("subtasks") else "⚡ **[ทบทวนจบ]**"
                    is_boss = " 💀 **[BOSS]**" if s.get("is_boss") else ""
                    q_num = s.get("user_order", 99)
                    q_badge = f"🎯 **[Q{q_num}]** " if q_num != 99 else ""

                    is_overdue, deadline_badge = False, ""
                    dl_str = s.get("deadline", "")
                    if dl_str and dl_str != "":
                        try:
                            dl_date = datetime.strptime(dl_str, "%Y-%m-%d").date()
                            days_left_task = (dl_date - today_date).days
                            if days_left_task > 0: deadline_badge = f" ⏳ (เหลือ {days_left_task} วัน)"
                            elif days_left_task == 0: deadline_badge = f" 🚨 **(ถึงกำหนดวันนี้!)**"
                            else: deadline_badge = f" 💀 **(เลยกำหนด {-days_left_task} วัน)**"; is_overdue = True
                        except: pass

                    is_frozen = s.get("skip_today_date") == today_str
                    was_frozen_yesterday = s.get("skip_today_date") != "" and not is_frozen
                    if was_frozen_yesterday: s["skip_today_date"] = ""; save_db(db)
                        
                    frozen_badge = " ❄️🚨 [แช่แข็งแตก!]" if is_frozen and is_overdue else " ❄️ [แช่แข็ง]" if is_frozen else ""

                    c1.write(f"**{s.get('ประเภท','')}** | {q_badge}{task_mode_badge}{is_boss} {s['ภารกิจ']}{deadline_badge}{frozen_badge}")
                    
                    # 🔥 STABLE HYPE RENDERING LOGIC สำหรับเรียน
                    s_id = str(s.get("id", "unk"))
                    display_conseq = s.get("consequence", "")
                    if not display_conseq: 
                        display_conseq = WARRIOR_CONSEQUENCES[get_stable_index(s_id + "conseq", len(WARRIOR_CONSEQUENCES))]
                    
                    display_hype = s.get("motivation", "")
                    if not display_hype: 
                        display_hype = WARRIOR_MOTIVATIONS[get_stable_index(s_id + "hype", len(WARRIOR_MOTIVATIONS))]
                    
                    c1.markdown(f"<div style='font-size: 0.9em; background: rgba(255, 0, 0, 0.1); padding: 5px; border-left: 3px solid #ff4b4b; margin-bottom: 5px; margin-top: 5px;'>🩸 <b>ถ้ากูไม่ทำ:</b> {display_conseq}</div>", unsafe_allow_html=True)
                    c1.markdown(f"<div style='font-size: 0.9em; background: rgba(255, 165, 0, 0.1); padding: 5px; border-left: 3px solid #ffa500; margin-bottom: 10px;'>🔥 <b>ปลุกใจ:</b> {display_hype}</div>", unsafe_allow_html=True)
                    
                    if s.get("รายละเอียด"):
                        with st.expander("📝 ดูขอบเขต/รายละเอียด"):
                            st.write(s["รายละเอียด"])
                    
                    all_done, has_today_progress = True, False
                    if s.get("subtasks"):
                        total_subs = len(s["subtasks"])
                        done_subs = len([stk for stk in s["subtasks"] if stk.get("done")])
                        progress_pct = done_subs / total_subs if total_subs > 0 else 0
                        st.progress(progress_pct, text=f"📈 คืบหน้า: {done_subs} / {total_subs} บท")

                        for i, stask in enumerate(s["subtasks"]):
                            is_done = stask.get("done", False)
                            done_date = stask.get("done_date", "")
                            is_locked = is_done and done_date != today_str
                            
                            label = f"{stask['name']}" + (f" 🔒 ({done_date})" if is_locked else "")
                            can_interact = not is_locked and (not is_frozen or is_overdue)
                            checked = st.checkbox(label, value=is_done, disabled=not can_interact, key=f"st_stud_{s['id']}_{i}")
                            
                            if can_interact and checked != is_done:
                                s["subtasks"][i]["done"] = checked; s["subtasks"][i]["done_date"] = today_str if checked else ""; save_db(db); st.toast("🔥 เก็บเนื้อหาไป 1 บท!", icon="📖"); safe_rerun()
                            if s["subtasks"][i].get("done_date", "") == today_str: has_today_progress = True
                                
                        all_done = all(stask.get("done", False) for stask in s["subtasks"])
                    else: all_done = True

                    if is_frozen:
                        if c4.button("🔥 ปลดแช่แข็ง", key=f"unfrz_stud_{s['id']}", use_container_width=True): s["skip_today_date"] = ""; save_db(db); safe_rerun()
                    else:
                        if c4.button("❄️ แช่แข็ง", key=f"frz_stud_{s['id']}", use_container_width=True): s["skip_today_date"] = today_str; save_db(db); safe_rerun()

                    if all_done and (not is_frozen or is_overdue):
                        if c2.button("✅ ติวสำเร็จ", key=f"stud_win_{s['id']}", use_container_width=True):
                            s["เสร็จแล้ว"] = True
                            exp_gain, fail_reduce = calculate_task_rewards(s, current_streak)
                            user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                        if c3.button("📤 ส่งอนุมัติ", key=f"pend_stud_{s['id']}", use_container_width=True): s["รอตรวจ"] = True; save_db(db); safe_rerun()
                    else: c2.caption("❄️ แช่แข็ง" if is_frozen and not is_overdue else "🔒 บทเรียนคาอยู่")
                    if c5.button("🗑️", key=f"del_stud_{s['id']}"): db["study_missions"][safe_email].remove(s); save_db(db); safe_rerun()
        else: st.success("📚 ติวทบทวนเนื้อหาครบหมดแล้วใน Roadmap!")

        if pending_study:
            st.divider(); st.markdown("### ⏳ วิชาที่รออนุมัติ")
            for s in pending_study:
                c1, c2, c3 = st.columns([5, 2, 2])
                c1.caption(f"⏳ {s['ภารกิจ']}")
                if c2.button("✅ ผ่าน", key=f"appr_stud_{s['id']}"):
                    s["เสร็จแล้ว"] = True; s["รอตรวจ"] = False
                    exp_gain, fail_reduce = calculate_task_rewards(s, current_streak)
                    user["exp"] += exp_gain; user["failure_prob"] = max(0, user["failure_prob"] - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                if c3.button("⏪ กลับมาอ่าน", key=f"revert_stud_{s['id']}"): s["รอตรวจ"] = False; save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 3: วินัยเหล็ก (THE IRON HABITS) 
    # ----------------------------------------------------
    with tab_habits:
        st.markdown("### ⛓️ THE IRON HABITS (คุมวินัยให้เข้ากระดูก)")
        
        with st.expander("➕ เพิ่มวินัยเหล็กใหม่"):
            with st.form("habit_form", clear_on_submit=True):
                h_name = st.text_input("ชื่อวินัย (เช่น นั่งสมาธิ 10 นาที, ดื่มน้ำ):", key="h_name")
                h_detail = st.text_input("คติเตือนใจ / ทำไปทำไม?:", key="h_detail")
                if st.form_submit_button("บรรจุวินัยเหล็ก"):
                    if h_name:
                        db["iron_habits"][safe_email].append({
                            "id": str(uuid.uuid4()), "name": h_name, "รายละเอียด": h_detail, "last_done_date": "", "total_done": 0, "user_order": 99
                        })
                        save_db(db); safe_rerun()
        
        todo_habits = [h for h in db["iron_habits"][safe_email] if isinstance(h, dict) and h.get("last_done_date") != today_str]
        
        if todo_habits:
            with st.expander("🎯 วางแผนลำดับวินัย (Q-Order)"):
                with st.form("set_habit_order_form"):
                    st.info("ระบุเลขคิววินัย เพื่อดึงเข้าไปแทรกในแผนผังชีวิต Roadmap ด้านบนสุด!")
                    new_h_orders = {}
                    for h in todo_habits:
                        col_q, col_n = st.columns([1, 5])
                        new_h_orders[h["id"]] = col_q.number_input("คิว", min_value=1, max_value=99, value=h.get("user_order", 99), step=1, key=f"q_h_{h['id']}", label_visibility="collapsed")
                        col_n.write(f"⛓️ {h['name']}")
                    if st.form_submit_button("🔒 ล็อคคิววินัย! (เซฟแผน)"):
                        for h in db["iron_habits"][safe_email]:
                            if isinstance(h, dict) and h.get("id") in new_h_orders:
                                h["user_order"] = new_h_orders[h["id"]]
                        save_db(db); st.success("✅ อัปเดตผังวินัยเรียบร้อย!"); safe_rerun()
                    
        if db["iron_habits"][safe_email]:
            st.divider()
            for h in db["iron_habits"][safe_email]:
                if not isinstance(h, dict): continue 
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 3, 1])
                    
                    q_num = h.get("user_order", 99)
                    q_badge = f"🎯 **[Q{q_num}]** " if q_num != 99 else ""
                    total_d = h.get("total_done", 0)
                    
                    c1.write(f"⛓️ {q_badge}**{h['name']}**  *(ทำไปแล้ว {total_d} ครั้ง)*")
                    if h.get("รายละเอียด"):
                        c1.caption(f"💡 เป้าหมาย: {h['รายละเอียด']}")
                        
                    if h.get("last_done_date") == today_str: 
                        c2.success("✅ รักษาวินัยได้แล้ววันนี้!")
                    else:
                        if c2.button("🔥 กูทำสำเร็จ!", key=f"h_done_{h['id']}", use_container_width=True):
                            h["last_done_date"] = today_str
                            h["total_done"] = h.get("total_done", 0) + 1
                            bonus, fail_sub = (10, 5) if current_streak >= 30 else (7, 3) if current_streak >= 7 else (5, 2)
                            user["exp"] += bonus; user["failure_prob"] = max(0, user["failure_prob"] - fail_sub); save_db(db); st.toast(f"🛡️ โอกาสหลุดวงโคจรลดลง -{fail_sub}%!", icon="🛡️"); safe_rerun()
                    if c3.button("🗑️", key=f"del_h_{h['id']}"): db["iron_habits"][safe_email].remove(h); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 4: โน้ตบัญชาการ (Command Notes System) 📓
    # ----------------------------------------------------
    with tab_notes:
        st.markdown("### 📓 สมุดบัญชาการ (Command Notes)")
        st.caption("จดเหตุการณ์สำคัญ แผนการล่วงหน้า หรือกลยุทธ์ต่างๆ เอาไว้ที่นี่ (แก้ไข / ลบได้ตลอดเวลา)")
        
        with st.form("note_form", clear_on_submit=True):
            n_title = st.text_input("หัวข้อเรื่อง:", key="n_title")
            n_content = st.text_area("รายละเอียดโน้ต / กลยุทธ์:", key="n_content")
            if st.form_submit_button("💾 บันทึกโน้ต"):
                if n_title:
                    db["notes"][safe_email].append({
                        "id": str(uuid.uuid4()), "date": today_str, "title": n_title, "content": n_content
                    })
                    save_db(db); st.success("✅ บันทึกกลยุทธ์เรียบร้อย!"); safe_rerun()

        if db["notes"].get(safe_email):
            st.divider()
            for n in reversed(db["notes"][safe_email]):
                if not isinstance(n, dict): continue
                with st.expander(f"📝 {n['title']} (บันทึกเมื่อ: {n['date']})"):
                    with st.form(f"edit_form_{n['id']}"):
                        new_title = st.text_input("แก้หัวข้อ:", value=n['title'], key=f"edit_t_{n['id']}")
                        new_content = st.text_area("แก้เนื้อหา:", value=n['content'], height=150, key=f"edit_c_{n['id']}")
                        
                        c1, c2 = st.columns([1, 1])
                        if c1.form_submit_button("💾 บันทึกการแก้ไข"):
                            n['title'] = new_title; n['content'] = new_content
                            save_db(db); st.success("อัปเดตเรียบร้อย!"); safe_rerun()
                        if c2.form_submit_button("🗑️ ลบทิ้ง"):
                            db["notes"][safe_email].remove(n)
                            save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 5: สมุดจดแผน (Backlog)
    # ----------------------------------------------------
    with tab_backlog:
        st.markdown("### 📝 แผนการในอนาคต (Backlog)")
        with st.form("backlog_form", clear_on_submit=True):
            b_name = st.text_input("ไอเดีย / งานที่ต้องทำในอนาคต:", key="b_name")
            b_detail = st.text_area("รายละเอียด / Note:", key="b_detail")
            b_subtasks_text = st.text_area("🔪 ซอยข้อย่อย (Enter ขึ้นบรรทัดใหม่):", key="b_subtasks")
            b_type = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"], key="b_type")
            b_dl_type = st.radio("⏰ ระบบเวลา:", ["ไม่กำหนด", "🗓️ Deadline", "🎯 วันเป้าหมาย"], horizontal=True, key="b_dl_type")
            b_deadline = st.date_input("กำหนดส่ง (เลือกวันที่):", key="b_deadline")
            
            if st.form_submit_button("💾 บันทึกแผน"):
                if b_name:
                    b_subtasks = [{"name": s.strip(), "done": False, "done_date": ""} for s in b_subtasks_text.split('\n') if s.strip()]
                    final_b_dl = str(b_deadline) if "ไม่กำหนด" not in b_dl_type else ""
                    db["backlog"][safe_email].append({"id": str(uuid.uuid4()), "ภารกิจ": b_name, "รายละเอียด": b_detail, "subtasks": b_subtasks, "ประเภท": b_type, "deadline": final_b_dl, "deadline_type": b_dl_type})
                    save_db(db); safe_rerun()
                    
        if db["backlog"][safe_email]:
            active_m_slots = len([m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว") and not m.get("subtasks")])
            active_s_slots = len([s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว") and not s.get("subtasks")])
            sorted_backlog = sorted([b for b in db["backlog"][safe_email] if isinstance(b, dict)], key=lambda x: x.get("deadline") if x.get("deadline") and x.get("deadline") != "" else "9999-12-31")
            
            for b_task in sorted_backlog:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([4, 2, 2, 0.8])
                    b_dl_str = b_task.get("deadline", "")
                    display_dl = f" 📅 กำหนด: {b_dl_str}" if b_dl_str else " ไม่ระบุเวลา"

                    c1.write(f"**{b_task.get('ประเภท', '-')}** | 📝 {b_task.get('ภารกิจ', '-')}")
                    c1.caption(f"{display_dl} | Note: {b_task.get('รายละเอียด', '-')}")
                    
                    has_subtasks = bool(b_task.get("subtasks"))
                    
                    if not has_subtasks and active_m_slots >= 3: c2.button("⚡ ดึงเข้างาน", key=f"pull_m_{b_task['id']}", disabled=True)
                    else:
                        if c2.button("⚡ ดึงเข้างาน", key=f"pull_m_{b_task['id']}", type="primary"):
                            db["missions"][safe_email].append({"id": b_task["id"], "วันที่": today_str, "ภารกิจ": b_task["ภารกิจ"], "รายละเอียด": b_task.get("รายละเอียด", ""), "ประเภท": b_task["ประเภท"], "bounty": False, "is_boss": False, "custom_order": 99, "user_order": 99, "battle_role": "Main", "is_queued": False, "skip_today_date": "", "deadline": b_task.get("deadline", ""), "deadline_type": b_task.get("deadline_type", "🗓️"), "subtasks": b_task.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False})
                            db["backlog"][safe_email].remove(b_task); save_db(db); safe_rerun()
                            
                    if not has_subtasks and active_s_slots >= 3: c3.button("📖 ดึงเข้าเรียน", key=f"pull_s_{b_task['id']}", disabled=True)
                    else:
                        if c3.button("📖 ดึงเข้าเรียน", key=f"pull_s_{b_task['id']}", type="secondary"):
                            db["study_missions"][safe_email].append({"id": b_task["id"], "วันที่": today_str, "ภารกิจ": b_task["ภารกิจ"], "รายละเอียด": b_task.get("รายละเอียด", ""), "ประเภท": b_task["ประเภท"], "bounty": False, "is_boss": False, "custom_order": 99, "user_order": 99, "battle_role": "Main", "is_queued": False, "skip_today_date": "", "deadline": b_task.get("deadline", ""), "deadline_type": b_task.get("deadline_type", "🗓️"), "subtasks": b_task.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False, "is_study": True})
                            db["backlog"][safe_email].remove(b_task); save_db(db); safe_rerun()
                    
                    if c4.button("🗑️", key=f"del_b_{b_task['id']}"): db["backlog"][safe_email].remove(b_task); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 6: โหลคุกกี้ (Cookie Jar) 🍪
    # ----------------------------------------------------
    with tab_cookie:
        st.markdown("### 🍪 คลังเก็บความสำเร็จ (Cookie Jar)")
        with st.form("cookie_form", clear_on_submit=True):
            win_text = st.text_input("วันนี้ทำอะไรสำเร็จบ้างที่ภูมิใจ?:", key="win_input")
            if st.form_submit_button("เก็บเข้าคลัง!"):
                if win_text:
                    db["cookie_jar"][safe_email].append({"id": str(uuid.uuid4()), "วันที่": today_str, "ชัยชนะ": win_text})
                    user["exp"] += int(5 * (1.5 if current_streak>=30 else 1.2 if current_streak>=7 else 1.0)); save_db(db); st.success("✅ เก็บชัยชนะเรียบร้อย!"); safe_rerun()
        if db["cookie_jar"][safe_email]:
            for c in reversed(db["cookie_jar"][safe_email][-5:]):
                if isinstance(c, dict): st.success(f"🏆 **[{c.get('วันที่', '-')}]** {c.get('ชัยชนะ', '')}")

    # ----------------------------------------------------
    # TAB 7: ลานประลองปัญญา (EXAM & BEAT YESTERDAY) 📚
    # ----------------------------------------------------
    with tab_academic:
        st.markdown("### 📚 ลานประลอง (วัดผลความก้าวหน้า)")
        with st.form("exam_form", clear_on_submit=True):
            e_subj = st.text_input("ชื่อวิชา / เรื่องที่ทดสอบ:", key="e_subj")
            e_score = st.number_input("คะแนนที่ได้ล่าสุด:", min_value=0.0, step=0.1, key="e_score")
            if st.form_submit_button("บันทึกคะแนนสอบ"):
                if e_subj:
                    if e_subj not in db["exams"][safe_email]: db["exams"][safe_email][e_subj] = []
                    history = db["exams"][safe_email][e_subj]
                    if len(history) > 0:
                        last_score = history[-1]
                        if e_score > last_score: user["exp"] += int(30 * (1.5 if current_streak>=30 else 1.0))
                        elif e_score < last_score: user["blood_debt"] += 50; user["failure_prob"] = min(100, user["failure_prob"] + 10)
                    db["exams"][safe_email][e_subj].append(e_score); save_db(db); safe_rerun()

        if db["exams"][safe_email]:
            cols = st.columns(3); idx = 0
            for subj, scores in db["exams"][safe_email].items():
                if len(scores) > 0:
                    latest = scores[-1]
                    delta = round(latest - scores[-2], 2) if len(scores) > 1 else None
                    cols[idx % 3].metric(label=f"📖 {subj}", value=latest, delta=delta); idx += 1

        st.divider()
        st.markdown("#### 🥊 ชกกับตัวเองเมื่อวาน (BEAT YESTERDAY)")
        yesterday_str = str(today_date - timedelta(days=1))
        with st.form("beat_yesterday_form"):
            by_metric = st.text_input("สิ่งที่ใช้วัดผล (เช่น จำนวนข้อที่ทำได้):", value=db["beat_yesterday"][safe_email].get("metric_name", ""), key="by_metric")
            by_val = st.number_input("สถิติที่ทำได้วันนี้:", min_value=0, key="by_val")
            if st.form_submit_button("ทุบสถิติตัวเอง"):
                if by_metric:
                    db["beat_yesterday"][safe_email]["metric_name"] = by_metric
                    if "history" not in db["beat_yesterday"][safe_email]: db["beat_yesterday"][safe_email]["history"] = {}
                    y_val = db["beat_yesterday"][safe_email]["history"].get(yesterday_str, 0)
                    if by_val > y_val: user["exp"] += int(20 * (1.2 if current_streak>=7 else 1.0))
                    elif by_val < y_val: user["blood_debt"] += 30
                    db["beat_yesterday"][safe_email]["history"][today_str] = by_val; save_db(db); safe_rerun()

        st.divider()
        if st.button("🔥 ทะลุขีดจำกัด (ก้าวข้ามความเหนื่อยล้าไปได้)!", use_container_width=True, key="btn_limit_break"):
            if today_str not in db["limit_breaks"][safe_email]:
                db["limit_breaks"][safe_email].append(today_str); user["exp"] += int(50 * (1.5 if current_streak>=30 else 1.0)); user["failure_prob"] = max(0, user["failure_prob"] - 15); save_db(db); safe_rerun()

    st.divider()
    st.markdown("### 💰 คลังทุนสร้างฝัน (Financial Goal)")
    c_fin1, c_fin2 = st.columns([2, 1])
    with c_fin1:
        st.write(f"**เป้าหมาย:** {finance.get('goal_name', 'ยังไม่ตั้ง')}")
        cur = finance.get('current', 0); tgt = finance.get('goal_amount', 1); prog = max(0.0, min(cur / tgt, 1.0)) if tgt > 0 else 0.0
        st.progress(prog, text=f"มียอดแล้ว: {cur} / {tgt} บาท")
    with c_fin2:
        with st.popover("⚙️ จัดการกองทุน"):
            new_g_name = st.text_input("ชื่อเป้าหมายเงิน:", value=finance.get('goal_name', ''), key="fin_name")
            new_g_amt = st.number_input("ยอดเป้าหมาย:", value=finance.get('goal_amount', 0), key="fin_amt")
            if st.button("ตั้งเป้าหมาย", key="fin_save_goal"): finance['goal_name'] = new_g_name; finance['goal_amount'] = new_g_amt; save_db(db); safe_rerun()
            st.divider()
            add_amt = st.number_input("บวก/ลด เงิน:", value=0, key="fin_add")
            if st.button("บันทึกยอดเงิน", key="fin_save_add"): finance['current'] += add_amt; save_db(db); safe_rerun()

# ==========================================
# 6. หหนี้เลือด & THE JUDGMENT FEED (พิพากษาวินัยประจำวัน)
# ==========================================
st.divider()
c_bot1, c_bot2 = st.columns(2)
with c_bot1:
    my_exp = ((user["level"] - 1) * 100) + user["exp"]
    st.metric("พลังร่างวินัยสูงสุด", f"{user['ghost_exp']} EXP")
    st.metric("พลังในปัจจุบัน", f"{my_exp} EXP", delta=f"{my_exp - user['ghost_exp']} (เปรียบเทียบ)")
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
    active_for_judgment = []
    combined_missions = [m for m in db["missions"][safe_email] if isinstance(m, dict)] + [s for s in db["study_missions"][safe_email] if isinstance(s, dict)]
    
    for m in combined_missions:
        if not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False):
            if m.get("skip_today_date") == today_str:
                is_task_overdue = False
                if m.get("deadline") and m.get("deadline") != "":
                    try:
                        if datetime.strptime(m["deadline"], "%Y-%m-%d").date() < today_date: is_task_overdue = True 
                    except: pass
                if not is_task_overdue: continue 
                
            if m.get("subtasks"):
                if not any(stask.get("done", False) and stask.get("done_date", "") == today_str for stask in m["subtasks"]): active_for_judgment.append(m)
            else: active_for_judgment.append(m)

    incomplete_habits = [h for h in db["iron_habits"][safe_email] if isinstance(h, dict) and h.get("last_done_date") != today_str]
    incomplete_bosses = [m for m in active_for_judgment if m.get("is_boss")]

    if incomplete_bosses:
        st.error("💀 ไร้วินัยขั้นรุนแรง! ดองงานระดับ BOSS!")
        if st.button("🩸 ยอมรับความล้มเหลว (รับหนี้เลือด 300 ที!)", key="btn_boss_penalty"):
            user["blood_debt"] += 300; user["failure_prob"] = min(100, user["failure_prob"] + 30); user["in_cage"] = True; user["cleared_yesterday"] = True; user["streak"] = 0; save_db(db); safe_rerun()
            
    elif active_for_judgment or incomplete_habits: 
        st.error("❌ ศาลแห่งวินัยพบงานค้าง:")
        total_blood_penalty = sum(100 if get_priority_score(m.get("ประเภท", "")) == 1 else 70 if get_priority_score(m.get("ประเภท", "")) == 2 else 50 for m in active_for_judgment) + (len(incomplete_habits) * 30)
        for m in active_for_judgment: st.write(f"👉 **{m.get('ภารกิจ','')}**")
        for h in incomplete_habits: st.write(f"👉 **{h.get('name','')}** [วินัยเหล็ก]")
        
        if st.button(f"🩸 ยอมรับความอ่อนแอ (รับหนี้เลือด {total_blood_penalty} ที)", key="btn_accept_penalty"):
            user["blood_debt"] += total_blood_penalty; user["failure_prob"] = min(100, user["failure_prob"] + (10 * (len(active_for_judgment) + len(incomplete_habits)))); user["in_cage"] = True; user["cleared_yesterday"] = True; user["streak"] = 0; save_db(db); safe_rerun()
            
    elif user.get("in_cage") or user.get("blood_debt", 0) > 0: 
        st.error("❌ ติดหนี้เลือดอยู่ ชดใช้กรรมให้หมดก่อนพิพากษา!")
    else:
        st.warning("วันนี้ทำตามแผนสุดกำลัง หรือแค่ทำผ่านๆ ไป?")
        j_col1, j_col2 = st.columns(2)
        with j_col1:
            if st.button("📉 ทำลวกๆ ไม่เต็ม 100%", key="btn_40pct"):
                user["exp"] -= 30; user["cleared_yesterday"] = True; user["failure_prob"] = min(100, user["failure_prob"] + 10); user["streak"] = 0; save_db(db); safe_rerun()
        with j_col2:
            if st.button("🔥 ใส่เต็ม 100% ตามเส้นทางวินัย!", key="btn_100pct"):
                if random.random() < 0.2: user["ambush_task"] = random.choice(AMBUSH_TASKS)
                else: user["cleared_yesterday"] = True; user["streak"] += 1; user["exp"] += int(25 * (1.5 if current_streak>=30 else 1.2 if current_streak>=7 else 1.0))
                save_db(db); safe_rerun()

# ==========================================
# 8. 📜 ประวัติศาสตร์เส้นทางวินัย (HISTORY LOG - REBUILT)
# ==========================================
st.divider()
if not monk_mode:
    st.markdown("## 📜 ประวัติศาสตร์เส้นทางวินัย (HISTORY LOG)")
    st.caption("ระบบประวัติแบบใหม่! แสดงเฉพาะงานที่ทำเสร็จแล้ว และลบข้อมูลเก่าๆ ทิ้งได้หากต้องการ!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ บันทึกเดินทาง (ภารกิจ)", "🏆 โหลคุกกี้ (สำเร็จ)", "🤡 ความกาก & ข้ออ้าง", "📊 BATTLE ANALYTICS"])

    with tab1:
        st.markdown("### 🗺️ ประวัติภารกิจที่พิชิตแล้ว")
        completed_m = sorted([m for m in db["missions"].get(safe_email, []) if isinstance(m, dict) and m.get("เสร็จแล้ว")], key=lambda x: x.get("วันที่", ""), reverse=True)
        completed_s = sorted([s for s in db["study_missions"].get(safe_email, []) if isinstance(s, dict) and s.get("เสร็จแล้ว")], key=lambda x: x.get("วันที่", ""), reverse=True)
        all_completed = completed_m + completed_s
        
        if not all_completed: st.info("ยังไม่มีภารกิจที่ทำสำเร็จ ไปลุยซะ!")
        
        for idx, item in enumerate(all_completed):
            c1, c2 = st.columns([10, 1])
            icon = "📖 เรียน" if item.get("is_study") else "🔪 งาน"
            c1.info(f"✅ **[{item.get('วันที่', '-')}]** | {icon} | {item.get('ภารกิจ', '')} *(ความสำคัญ: {item.get('ประเภท','')})*")
            if c2.button("🗑️", key=f"del_hm_{idx}_{item.get('id', idx)}"):
                if item.get("is_study"): db["study_missions"][safe_email].remove(item)
                else: db["missions"][safe_email].remove(item)
                save_db(db); safe_rerun()

    with tab1: pass 
    with tab2:
        st.markdown("### 🏆 โหลคุกกี้ (ความภูมิใจ)")
        if not db["cookie_jar"].get(safe_email): st.info("ยังไม่มีความภูมิใจสะสมไว้")
        for idx, c in enumerate(reversed(db["cookie_jar"].get(safe_email, []))):
            c1, c2 = st.columns([10, 1])
            if isinstance(c, dict):
                c1.success(f"🏆 **[{c.get('วันที่', '-')}]** {c.get('ชัยชนะ', '')}")
                if c2.button("🗑️", key=f"del_cj_{idx}_{c.get('id', idx)}"):
                    db["cookie_jar"][safe_email].remove(c)
                    save_db(db); safe_rerun()
            else: 
                c1.success(f"🏆 {c}")
                if c2.button("🗑️", key=f"del_cj_old_{idx}"):
                    db["cookie_jar"][safe_email].remove(c)
                    save_db(db); safe_rerun()

    with tab3:
        st.markdown("### 🩸 เชื้อเพลิงความแค้น (ความกากในอดีต)")
        if not db["weakness_fuel"].get(safe_email): st.info("ยังไม่มีประวัติความกากที่จดไว้ (ดีมาก!)")
        for idx, w in enumerate(reversed(db["weakness_fuel"].get(safe_email, []))):
            c1, c2 = st.columns([10, 1])
            w_text = w.get("text", "") if isinstance(w, dict) else w
            c1.error(f"🩸 **[เชื้อเพลิงความแค้น]** : {w_text}")
            if c2.button("🗑️", key=f"del_wf_{idx}"):
                db["weakness_fuel"][safe_email].remove(w)
                save_db(db); safe_rerun()
                
        st.divider()
        st.markdown("### 🤡 ข้ออ้างที่เคยใช้")
        if not db["excuses"].get(safe_email): st.info("ยังไม่มีข้ออ้างขยะๆ (รักษาความดีนี้ไว้!)")
        for idx, e in enumerate(reversed(db["excuses"].get(safe_email, []))):
            c1, c2 = st.columns([10, 1])
            if isinstance(e, dict):
                c1.warning(f"🤡 **[{e.get('วันที่', '-')}]** : {e.get('ข้ออ้าง', '')}")
                if c2.button("🗑️", key=f"del_ex_{idx}"):
                    db["excuses"][safe_email].remove(e)
                    save_db(db); safe_rerun()

    with tab4:
        all_m = [m for m in db["missions"].get(safe_email, []) if isinstance(m, dict)] + [s for s in db["study_missions"].get(safe_email, []) if isinstance(s, dict)]
        total_m = len(all_m)
        done_m = len([m for m in all_m if m.get("เสร็จแล้ว")])
        win_rate = (done_m / total_m * 100) if total_m > 0 else 0
        win_count, fail_count = len([c for c in db["cookie_jar"].get(safe_email, []) if isinstance(c, dict)]), len(db["weakness_fuel"].get(safe_email, []))
        
        c_stat1, c_stat2, c_stat3, c_stat4 = st.columns(4)
        c_stat1.metric("อัตราการรักษาวินัย", f"{win_rate:.1f}%"); c_stat2.metric("บอสที่จัดการได้", f"{len([m for m in all_m if m.get('เสร็จแล้ว') and m.get('is_boss')])} ตัว")
        c_stat3.metric("เป้าหมายสำเร็จ", f"{done_m} / {total_m}"); c_stat4.metric("รอยแผลความกาก", f"{fail_count} รอย")
        if win_count + fail_count > 0: st.bar_chart(pd.DataFrame({"จำนวนครั้ง": [win_count, fail_count]}, index=["Discipline (ชนะใจ)", "Weakness (เคยกาก)"]))
