import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import json
import os
import uuid
import hashlib
import random

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="DUALITY WAR HQ", layout="wide", page_icon="⚔️")
DB_FILE = "duality_war_db.json"
today_str = str(date.today())

# ฟังก์ชันจัดการฐานข้อมูล
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"users": {}, "missions": {}, "squad_log": {}, "dopamine_trap": {}, "ghost_exp": 0}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()

# ระบบ AUTH
if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.title("⚔️ สงครามในสมอง: THE DUALITY WAR")
    email = st.text_input("อีเมล:")
    if st.button("เข้าสู่สมรภูมิ"):
        if email not in db["users"]:
            db["users"][email] = {"exp": 0, "level": 1, "blood_debt": 0, "cage": False, "streak": 0}
            save_db(db)
        st.session_state.user = email
        st.rerun()
    st.stop()

email = st.session_state.user
u = db["users"][email]

# แบ่งหน้าจอ 2 ฝั่ง
col1, col2 = st.columns(2)

with col1:
    st.error("### ⬅️ THE LEFT-WING BITCH ZONE (ฆ่าร่างขยะ)")
    st.write("บันทึกข้ออ้างขยะๆ ของมึงที่นี่!")
    excuse = st.text_input("ข้ออ้างวันนี้:")
    if st.button("บันทึกความกาก"):
        st.error("ความล้มเหลวพุ่งสูงขึ้น 20% แล้วไอ้ขี้แพ้!")
    
    st.write("---")
    st.write("### 🗑️ Dopamine Trap")
    if st.button("กูไปเสพโดพามีนขยะมา..."):
        u["exp"] = 0
        u["blood_debt"] += 50
        st.error("มึงกำลังขายอนาคตตัวเองให้ความฟิน 5 วินาที!")
        save_db(db)

with col2:
    st.success("### ➡️ THE RIGHT-WING SAVAGE ZONE (วัย 20 ปีที่เหนือกว่า)")
    st.write("ตารางรบวันนี้:")
    task = st.text_input("ภารกิจท่อนซุง:")
    if st.button("Tick! ทำเสร็จแล้ว"):
        u["exp"] += 20
        st.success("นักรบทำสำเร็จ! มึงกำลังชนะร่างเก่า!")
        save_db(db)
    
    st.write("---")
    st.write("### 🍪 คลังแสงความสำเร็จ (Cookie Jar)")
    st.file_uploader("อัปโหลดหลักฐานความถึก (รูปภาพ):")

st.write("---")

# ระบบนาฬิกานรก
st.markdown("### ⏳ Countdown to Regret")
st.warning("เวลาที่มึงเอาแต่เพ้อ คือเวลาที่มึงกำลังส่งตัวเองลงนรก!")

# ระบบปุ่มสับหน้า
if st.button("I'M A BITCH!", type="primary"):
    punishment = random.choice(["ไปดันพื้น 50 ทีเดี๋ยวนี้!", "ไปวิ่งรอบบ้าน 10 รอบ!", "ปิดคอมแล้วไปอ่านหนังสือซะ!"])
    st.error(f"🔥 สั่งจากนักรบ: {punishment}")

# ระบบเถียงกัน
st.write("---")
st.markdown("### 🗣️ สงครามโต้ตอบ")
left_thought = st.text_input("ร่างขี้แพ้เถียง:")
right_thought = st.text_input("นักรบโต้ตอบ:")
if st.button("ฉะกัน!"):
    st.write(f"ขี้แพ้: {left_thought}")
    st.write(f"นักรบ: มึงมันก็แค่ขยะ {right_thought} ไร้สาระชิบหาย!")

# ระบบ Ghost
st.sidebar.metric("ร่างทอง (Ghost of You)", f"Lv.{u['level']+1}")