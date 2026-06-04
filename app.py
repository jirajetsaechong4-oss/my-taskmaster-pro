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
st.set_page_config(page_title="TaskMaster Pro 5.0", layout="wide", page_icon="👑")
DB_FILE = "taskmaster_db_v5.json"
today = date.today()

# ฟังก์ชันเข้ารหัสผ่าน (เพื่อความปลอดภัย)
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def is_past(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date() < today
    except:
        return False

# โหลดฐานข้อมูล (โครงสร้างใหม่เอี่ยม)
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "public": [], "private": {}, "qa_board": []}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()

# ==========================================
# 2. ระบบ Authentication (Login / Register)
# ==========================================
if "current_user" not in st.session_state:
    st.session_state.current_user = None

with st.sidebar:
    st.title("🔐 ระบบเข้าสู่ระบบ")
    
    if st.session_state.current_user is None:
        auth_mode = st.radio("เลือกทำรายการ:", ["เข้าสู่ระบบ (Login)", "สมัครสมาชิก (Register)"])
        
        email_input = st.text_input("📧 อีเมล:")
        pass_input = st.text_input("🔑 รหัสผ่าน:", type="password")
        
        if auth_mode == "สมัครสมาชิก (Register)":
            name_input = st.text_input("👤 ชื่อผู้ใช้ (แสดงให้เพื่อนเห็น):")
            if st.button("สมัครสมาชิก"):
                if email_input and pass_input and name_input:
                    if email_input in db["users"]:
                        st.error("อีเมลนี้มีผู้ใช้งานแล้ว!")
                    else:
                        db["users"][email_input] = {
                            "password": hash_password(pass_input),
                            "username": name_input
                        }
                        db["private"][email_input] = []
                        save_db(db)
                        st.success("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ")
                else:
                    st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")
                    
        elif auth_mode == "เข้าสู่ระบบ (Login)":
            if st.button("เข้าสู่ระบบ"):
                if email_input in db["users"] and db["users"][email_input]["password"] == hash_password(pass_input):
                    st.session_state.current_user = {
                        "email": email_input,
                        "username": db["users"][email_input]["username"]
                    }
                    st.toast("เข้าสู่ระบบสำเร็จ!", icon="✅")
                    st.rerun()
                else:
                    st.error("อีเมล หรือ รหัสผ่านไม่ถูกต้อง!")
    else:
        st.success(f"ยินดีต้อนรับ, {st.session_state.current_user['username']}")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.current_user = None
            st.rerun()

# บังคับ Login
if st.session_state.current_user is None:
    st.title("👋 ยินดีต้อนรับสู่ TaskMaster Pro 5.0")
    st.info("👈 กรุณาเข้าสู่ระบบ หรือ สมัครสมาชิกที่เมนูด้านซ้ายเพื่อเริ่มใช้งาน")
    st.stop()

user_email = st.session_state.current_user["email"]
username = st.session_state.current_user["username"]

# ==========================================
# 3. คัดกรองข้อมูล Active
# ==========================================
pub_active = [t for t in db["public"] if not is_past(t["กำหนดส่ง"])]
priv_active = [t for t in db["private"].get(user_email, []) if not is_past(t["กำหนดส่ง"]) and not t.get("เสร็จแล้ว")]

# ==========================================
# 4. หน้าต่างหลัก (5 แถบ)
# ==========================================
st.title(f"🚀 พื้นที่ทำงานส่วนตัวของ: {username}")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📢 บอร์ดห้องเรียน", "💬 ถาม-ตอบงาน", "🔒 งานส่วนตัว", "📈 สถิติห้องเรียน", "🗄️ ประวัติ"])

# ----------------- แถบที่ 1: บอร์ดห้องเรียน -----------------
with tab1:
    with st.expander("➕ เพิ่มประกาศงานค้าง / วันสอบ"):
        with st.form("pub_form", clear_on_submit=True):
            t_name = st.text_input("หัวข้องาน / การสอบ:")
            t_details = st.text_area("รายละเอียดเพิ่มเติม:")
            c1, c2 = st.columns(2)
            t_type = c1.selectbox("ประเภท:", ["งานค้าง", "การสอบ"])
            t_date = c2.date_input("กำหนดวัน:")
            if st.form_submit_button("📢 ประกาศ"):
                if t_name:
                    db["public"].append({
                        "id": str(uuid.uuid4()), "รายการ": t_name, "รายละเอียด": t_details, 
                        "ประเภท": t_type, "กำหนดส่ง": str(t_date), 
                        "คนประกาศ": username, "email_เจ้าของ": user_email
                    })
                    save_db(db)
                    st.toast("ประกาศให้ห้องรู้แล้ว!", icon="📢")
                    st.rerun()

    st.markdown("### 📋 ประกาศทั้งหมด (เรียงตามกำหนดส่ง)")
    if pub_active:
        # เรียงลำดับให้งานที่ใกล้ถึงกำหนดขึ้นก่อน
        pub_active_sorted = sorted(pub_active, key=lambda x: x["กำหนดส่ง"])
        
        for item in pub_active_sorted:
            with st.container():
                st.info(f"**[{item['ประเภท']}] {item['รายการ']}** | 📅 วันที่: {item['กำหนดส่ง']} | 👤 โดย: {item['คนประกาศ']}")
                st.caption(f"รายละเอียด: {item['รายละเอียด']}")
                
                colA, colB = st.columns([1, 4])
                with colA:
                    if st.button("📥 เก็บเข้าส่วนตัว", key=f"copy_{item['id']}"):
                        new_type = "เตือนความจำ" if item["ประเภท"] == "การสอบ" else item["ประเภท"]
                        db["private"][user_email].append({
                            "id": str(uuid.uuid4()), "รายการ": item["รายการ"], "รายละเอียด": item["รายละเอียด"], 
                            "ประเภท": new_type, "กำหนดส่ง": item["กำหนดส่ง"], "เสร็จแล้ว": False
                        })
                        save_db(db)
                        st.toast("บันทึกเข้างานส่วนตัวแล้ว!", icon="✅")
                
                # ลบได้เฉพาะเจ้าของเท่านั้น!
                with colB:
                    if item.get("email_เจ้าของ") == user_email:
                        if st.button("🗑️ ลบประกาศนี้", key=f"del_{item['id']}"):
                            db["public"] = [t for t in db["public"] if t["id"] != item["id"]]
                            save_db(db)
                            st.rerun()
                st.divider()
    else:
        st.success("ไม่มีงานค้างของห้องเรียน!")

# ----------------- แถบที่ 2: บอร์ด Q&A -----------------
with tab2:
    st.markdown("### 💬 กระดานถาม-ตอบเรื่องงาน (Q&A)")
    
    with st.expander("📝 ตั้งกระทู้ถามเรื่องงาน"):
        with st.form("qa_form", clear_on_submit=True):
            q_topic = st.text_input("เรื่องที่สงสัย:")
            if st.form_submit_button("ตั้งคำถาม"):
                if q_topic:
                    db["qa_board"].append({
                        "id": str(uuid.uuid4()), "คำถาม": q_topic, 
                        "คนถาม": username, "email_คนถาม": user_email, 
                        "เวลา": str(datetime.now().strftime("%Y-%m-%d %H:%M")), "คอมเมนต์": []
                    })
                    save_db(db)
                    st.rerun()
                    
    for q in reversed(db["qa_board"]):
        with st.container():
            st.markdown(f"#### ❓ {q['คำถาม']}")
            st.caption(f"ถามโดย: {q['คนถาม']} | เวลา: {q['เวลา']}")
            
            # โชว์คอมเมนต์
            for c in q["คอมเมนต์"]:
                st.write(f"💬 **{c['คนตอบ']}**: {c['ข้อความ']} *(เวลา: {c['เวลา']})*")
            
            # ฟอร์มตอบคอมเมนต์
            c_input = st.text_input("พิมพ์คำตอบของคุณ...", key=f"ans_input_{q['id']}")
            c1, c2 = st.columns([1, 4])
            with c1:
                if st.button("ส่งคำตอบ", key=f"btn_ans_{q['id']}"):
                    if c_input:
                        q["คอมเมนต์"].append({
                            "ข้อความ": c_input, "คนตอบ": username, "เวลา": str(datetime.now().strftime("%Y-%m-%d %H:%M"))
                        })
                        save_db(db)
                        st.rerun()
            with c2:
                # ปุ่มลบกระทู้ (เฉพาะเจ้าของ)
                if q.get("email_คนถาม") == user_email:
                    if st.button("🗑️ ลบกระทู้", key=f"del_q_{q['id']}"):
                        db["qa_board"] = [item for item in db["qa_board"] if item["id"] != q["id"]]
                        save_db(db)
                        st.rerun()
            st.divider()

# ----------------- แถบที่ 3: งานส่วนตัว -----------------
with tab3:
    with st.expander("➕ เพิ่มงานส่วนตัว / เตือนความจำ"):
        with st.form("priv_form", clear_on_submit=True):
            p_name = st.text_input("หัวข้องาน:")
            p_details = st.text_area("รายละเอียด:")
            c3, c4 = st.columns(2)
            p_type = c3.text_input("ประเภทงาน:", value="งานค้าง")
            p_date = c4.date_input("กำหนดวัน:")
            if st.form_submit_button("💾 บันทึก"):
                if p_name:
                    db["private"][user_email].append({
                        "id": str(uuid.uuid4()), "รายการ": p_name, "รายละเอียด": p_details, 
                        "ประเภท": p_type, "กำหนดส่ง": str(p_date), "เสร็จแล้ว": False
                    })
                    save_db(db)
                    st.rerun()

    if priv_active:
        df_priv = pd.DataFrame(priv_active).set_index("id")
        edited_priv = st.data_editor(
            df_priv[["เสร็จแล้ว", "รายการ", "รายละเอียด", "ประเภท", "กำหนดส่ง"]],
            column_config={"เสร็จแล้ว": st.column_config.CheckboxColumn("✅ เสร็จแล้ว")},
            disabled=["รายการ", "รายละเอียด", "ประเภท", "กำหนดส่ง"],
            use_container_width=True, key="priv_editor"
        )
        
        for task_id, row in edited_priv.iterrows():
            if row["เสร็จแล้ว"]:
                for item in db["private"][user_email]:
                    if item["id"] == task_id:
                        item["เสร็จแล้ว"] = True
                        save_db(db)
                        st.toast("เยี่ยมมาก! เคลียร์งานสำเร็จ", icon="🎉")
                        st.rerun()
                        
        priv_dict = {f"[{t['ประเภท']}] {t['รายการ']}": t["id"] for t in priv_active}
        del_priv_choice = st.selectbox("🗑️ ลบงานส่วนตัวถาวร:", list(priv_dict.keys()))
        if st.button("❌ ลบทิ้ง"):
            target_id = priv_dict[del_priv_choice]
            db["private"][user_email] = [t for t in db["private"][user_email] if t["id"] != target_id]
            save_db(db)
            st.rerun()
    else:
        st.success("ไม่มีงานส่วนตัวค้างเลย!")

# ----------------- แถบที่ 4: สถิติ -----------------
with tab4:
    st.subheader("📊 สถิติความก้าวหน้าของห้องเรียน")
    
    total_pub = len(db["public"])
    active_pub = len(pub_active)
    completed_pub = total_pub - active_pub
    
    c1, c2, c3 = st.columns(3)
    c1.metric("งานห้องเรียนทั้งหมด", total_pub)
    c2.metric("ยังค้างอยู่", active_pub, delta="- ด่วน", delta_color="inverse")
    c3.metric("เคลียร์แล้ว/เลยกำหนด", completed_pub, delta="ผ่านไปแล้ว")
    
    if total_pub > 0:
        progress = int((completed_pub / total_pub) * 100)
        st.progress(progress, text=f"ความคืบหน้าของห้องเรียน: {progress}%")
        
        # จัดอันดับคนขยันประกาศ
        st.markdown("#### 🏆 Leaderboard: คนขยันประกาศงานห้อง")
        announcers = [t["คนประกาศ"] for t in db["public"]]
        if announcers:
            df_stats = pd.Series(announcers).value_counts().reset_index()
            df_stats.columns = ['ชื่อ', 'จำนวนประกาศ (งาน)']
            st.bar_chart(df_stats.set_index('ชื่อ'))

# ----------------- แถบที่ 5: ประวัติ -----------------
with tab5:
    st.subheader("🗄️ ประวัติย้อนหลัง")
    pub_history = [t for t in db["public"] if is_past(t["กำหนดส่ง"])]
    priv_history = [t for t in db["private"][user_email] if is_past(t["กำหนดส่ง"]) or t.get("เสร็จแล้ว")]
    
    if pub_history:
        st.markdown("**ประวัติประกาศส่วนรวม**")
        st.dataframe(pd.DataFrame(pub_history)[["รายการ", "กำหนดส่ง", "คนประกาศ"]], hide_index=True, use_container_width=True)
    if priv_history:
        st.markdown("**ประวัติส่วนตัวของคุณ**")
        st.dataframe(pd.DataFrame(priv_history)[["รายการ", "กำหนดส่ง", "เสร็จแล้ว"]], hide_index=True, use_container_width=True)