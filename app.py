import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import requests
import uuid
import hashlib
import random

# ==========================================
# 1. ตั้งค่าระบบ (DISCIPLINE ARC - FLAWLESS EDITION V3)
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

# 🔄 ระบบแปลงวันที่เป็นภาษาไทยตามคำสั่ง (วัน + วันที่ + เดือน + ปี)
THAI_DAYS = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
THAI_MONTHS = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

def thai_date_format(date_str):
    if not date_str or date_str == "": return ""
    try:
        if isinstance(date_str, date) or isinstance(date_str, datetime):
            d = date_str
        else:
            d = datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
        day_name = THAI_DAYS[d.weekday()]
        return f"{day_name} {d.day} {THAI_MONTHS[d.month]} {d.year}"
    except:
        return str(date_str)

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
            "มึงจะยอมแพ้แค่นี้หรอวะ? กลับไปกระจอกเหมือนเดิมก็เอาดิ ถ้ารับตัวเองได้!", "ความเหนื่อยวันนี้ คือกล้ามเนื้อของความสำเร็จพรุ่งนี้ ลุยดิวะ!", "ปีศาจขี้เกียจมันกำลังหัวเราะมึงอยู่... มึงจะยอมให้มันชนะหรอ? ฟาดหน้ามัน!", "ไม่มีข้ออ้างสำหรับคนจริง! ทางเดียวคือเดินหน้าและบดขยี้เป้าหมายให้แหลก!", "ก้มหน้าทำไป! เหงื่อและน้ำตามันคือร่องรอยของนักรบ ไม่ใช่น้ำตาของไอ้ขี้แพ้!", "โลกไม่จำคนเกือบสำเร็จ... เอาให้สุด อย่าหยุดแค่คำว่า 'พอแล้ว'!", "ถ้ามันง่าย ทุกคนก็รวยและสำเร็จไปหมดแล้ว! ความยากนี่แหละคือด่านคัดคนจริง!", "พักได้ แต่อย่ายยอมแพ้! เลียแผลเสร็จแล้วลุกขึ้นมาจับอาวุธซะ!", "ความเจ็บปวดจากการฝืนตัวเอง มีค่ามากกว่าความสบายที่พาไปสู่ความล้มเหลว!", "ศัตรูที่น่ากลัวที่สุดคือตัวมึงเองในกระจก เอาชนะมันให้ได้!"
        ]
    },
    "Jesus": {
        "name": "พระเยซู (Jesus - ผู้เลี้ยงดูและผู้ไถ่)", "icon": "✝️", 
        "desc": "สกิล [พระคุณ (Grace)]: ยอมรับความพ่ายแพ้จะลดทอนค่าปรับลง 50% เสมอ เริ่มต้นใหม่ได้เสมอ",
        "quotes": [
            "บรรดาผู้เหน็ดเหนื่อยและแบกภาระหนัก จงมาหาเราเถิด และเราจะให้ท่านทั้งหลายได้พักสงบ", "เราจะไม่ละทิ้งเจ้า หรือทอดทิ้งเจ้าเลย", "สันติสุขของเราที่ให้กับเจ้านั้น ไม่เหมือนที่โลกให้ อย่าให้ใจของเจ้าวิตกและอย่ากลัวเลย", "ในโลกนี้เจ้าจะมีความทุกข์ยาก แต่จงชื่นใจเถิด เพราะเราได้ชนะโลกแล้ว", "จงเข้มแข็งและกล้าหาญเถิด อย่าหวาดหวั่นพรั่นพรึง เพราะพระเจ้าอยู่กับเจ้าทุกแห่งหน", "เรามาเพื่อเขาทั้งหลายจะได้ชีวิต และจะได้อย่างครบบริบูรณ์", "แม้เราจะเดินผ่านหุบเขาเงามัจจุราช เราก็ไม่กลัวอันตรายใดๆ เพราะพระองค์ทรงสถิตกับเรา", "พระองค์ทรงรักษาคนที่ชอกช้ำระกำใจ และทรงพันผูกบาดแผลของเขา", "อย่าวิตกกังวลถึงพรุ่งนี้ เพราะพรุ่งนี้ก็จะมีเรื่องวิตกกังวลของมันเอง", "จงขอแล้วจะได้ จงหาแล้วจะพบ จงเคาะแล้วจะเปิดให้แก่ท่าน"
        ]
    },
    "Zenitsu": {
        "name": "เซนอิทสึ (ร่างปราสาทไร้ขอบเขต)", "icon": "⚡",
        "desc": "สกิล [Godspeed โหมดเอาจริง]: ในโหมด Locked In ทำงานด่วนลด Failure Prob x2 แต่ถ้าดองงาน โดนบวกหนี้เลือด +50 ที!",
        "quotes": [
            "คำขอโทษน่ะ... ไม่ต้องหรอก มันไม่มีประโยชน์แล้ว", "ฉันไม่ได้มาที่นี่เพื่อคุยเล่น ฉันมาเพื่อจบเรื่องนี้", "ปู่ครับ... ดูผมให้ดีนะ ผมจะทำมันให้สำเร็จ", "เวลาของความลังเลมันหมดลงไปตั้งนานแล้ว", "ไม่ต้องพูดอะไรทั้งนั้น แค่ทำในสิ่งที่ต้องทำก็พอ", "หน้าที่ของฉัน คือกวาดล้างอุปสรรคตรงหน้าให้สิ้นซาก", "ถ้าทำไม่ได้ก็แค่ตาย... แต่วันนี้ฉันจะไม่ตาย", "ความรู้สึกหรอ? ฉันโยนมันทิ้งไปหมดแล้ว ตอนนี้มีแค่เป้าหมาย", "จะเหนื่อย จะเจ็บแค่ไหน ร่างกายนี้ก็ต้องขยับตามคำสั่ง", "ฉันจะชดใช้ทุกอย่างด้วยผลลัพธ์ ไม่ใช่ด้วยน้ำตา"
        ]
    },
    "Yuji": {
        "name": "ยูจิ (Yuji - ฟันเฟืองทรหด)", "icon": "⚙️", 
        "desc": "สกิล [ก้าวเล็กๆ ที่ทรงพลัง]: ติ๊ก 'งานย่อย' สำเร็จ 1 ข้อ จะลดอัตราความกาก (Failure Prob) ได้ 2 เท่า",
        "quotes": [
            "ฉันอาจจะไม่ได้เก่งที่สุด แต่ฉันจะเป็นฟันเฟืองที่ขับเคลื่อนชีวิตตัวเองต่อไปไม่หยุด!", "ถ้ากูไม่ทำตอนนี้ แล้วใครจะมาทำชีวิตกูให้ดีขึ้นวะ? ลุยดิวะ!", "ฉันจะไม่ยอมมานั่งเสียใจกับสิ่งที่เลือกเด็ดขาด! บดขยี้งานนี้ซะ!", "ความเจ็บปวดมันเป็นเรื่องปกติ แค่รับมันไว้แล้วก้าวไปข้างหน้า!", "ถึงจะอ่อนแอแค่ไหน หน้าที่ของกูก็คือทำสิ่งที่อยู่ตรงหน้าให้พังไปข้างนึง!", "กูไม่รู้หรอกว่าตอนจบจะเป็นไง แต่กูจะสู้จนกว่าจะหมดลมหายใจ!", "ทำหน้าที่ของตัวเองให้ดีที่สุดซะ อย่าให้ใครมาดูถูกความพยายามได้!", "ถ้ายอมแพ้ตรงนี้ ทุกคนที่เชื่อมั่นในตัวกู คงผิดหวังน่าดู!", "กูคือฟันเฟืองชิ้นนึง ถ้ากูหยุดหมุน ระบบชีวิตกูพังแน่!", "ไม่ต้องคิดอะไรเยอะ แค่ใส่ให้สุดแรงเกิดก็พอ!"
        ]
    },
    "Gojo": {
        "name": "โกโจ (Gojo - ไร้ขีดจำกัด)", "icon": "🤞", 
        "desc": "สกิล [กรองเสียงรบกวน]: สภาพจิตใจที่เหนือชั้น บทลงโทษหนี้เลือดจากงานค้าง ถูกจำกัดไว้สูงสุดไม่เกิน 100 ที/วัน",
        "quotes": [
            "เรื่องแค่นี้เอง ไม่เป็นไรหรอก เพราะฉันน่ะเก่งที่สุดแล้ว!", "ทำไมต้องกังวลด้วยวะ? งานพวกนี้มันเทียบความสามารถระดับฉันไม่ได้หรอก!", "ร้องไห้โวยวายไปก็ไม่ช่วยอะไร ลุกขึ้นมาโชว์ให้พวกมันดูสิว่าของจริงเป็นไง!", "ไม่ต้องรีบร้อนหรอก ค่อยๆ จัดการไปแบบหล่อๆ ก็รอดแล้ว!", "ขีดจำกัดมันมีไว้ให้พวกกระจอกเท่านั้นแหละ สำหรับฉันมันไร้ขีดจำกัด!", "งานยากหรอ? ดีเลย จะได้แสดงให้โลกเห็นว่าฉันมันอยู่คนละระดับ!", "คนเก่งจริงเขาไม่บ่น เขาแค่ลงมือทำแล้วรอรับชัยชนะชิลๆ!", "จำไว้ เหนือฟ้ายังมีฟ้า และเหนืองานพวกนี้ยังมีกู!", "ปล่อยให้พวกอ่อนแอมันกังวลไป ส่วนเรามาเคลียร์งานนี้ให้จบสวยๆ กันดีกว่า!", "ความสมบูรณ์แบบมันสร้างยากหน่อยนะ แต่อย่างฉันน่ะทำได้อยู่แล้ว!"
        ]
    },
    "Toji": {
        "name": "โทจิ (Toji - นักล่าสัญญาสวรรค์)", "icon": "🐛", 
        "desc": "สกิล [High Risk, High Return]: สำเร็จงาน Boss รับโบนัส +30% EXP แต่ดองงาน Boss โดนหนี้เลือด x2 ทันที!",
        "quotes": [
            "ข้ออ้างหรือพรสวรรค์กูไม่สน กูสนแค่ผลลัพธ์และเป้าหมายที่อยู่ตรงหน้า!", "โลกนี้มันขับเคลื่อนด้วยผลประโยชน์ ไม่ทำงานนี้มึงจะเอาอะไรแดก?", "ศักดิ์ศรีมันกินไม่ได้ ลงมือทำและบดขยี้เป้าหมายซะ นั่นแหละคือของจริง!", "ไม่ต้องมาพูดเรื่องโชคชะตากับกู กูใช้แรงกายและวินัยกระทืบโชคชะตาทิ้งไปหมดแล้ว!", "เหนื่อยหรอวะ? เรื่องของมึงสิ โลกไม่หยุดหมุนเพราะมึงเหนื่อยหรอกนะ!", "ถ้ามึงไม่แข็งแกร่ง มึงก็โดนเหยียบย่ำ แค่นั้นแหละสัจธรรมของโลก!", "กูไม่เชื่อในปาฏิหาริย์ กูเชื่อในความดิบเถื่อนของการลงมือทำเท่านั้น!", "เป้าหมายมีไว้พุ่งชน ไม่ได้มีไว้ให้นั่งมองแล้วฝันหวาน!", "ถ้าอยากได้ผลลัพธ์ระดับพระเจ้า ก็ต้องยอมแลกด้วยหยาดเหงื่อระดับปีศาจ!", "อย่ามาสำออยให้กูเห็น ลุกขึ้นไปทำหน้าที่ของมึงให้คุ้มกับลมหายใจซะ!"
        ]
    },
    "Subaru": {
        "name": "ซุบารุ (Subaru - Return by Death)", "icon": "⏪", 
        "desc": "สกิล [ราคาของการแก้ตัว]: เลื่อน Deadline งานมาเป็นวันนี้ได้ แต่ต้องจ่าย 10 EXP เป็นข้อแลกเปลี่ยน",
        "quotes": [
            "กูรู้ว่ากูมันกาก กูมันอ่อนแอ... แต่กูก็จะกัดฟันเริ่มใหม่และทำให้ได้!", "ไม่ว่าจะล้มเหลวกี่ครั้ง ไม่ว่าจะโดนด่าแค่ไหน กูก็จะลุกขึ้นมาแก้ตัวใหม่เสมอ!", "ถึงวันนี้จะพังพินาศ แต่พรุ่งนี้กูจะหาวิธีเอาชนะมันให้ดู!", "ความกลัวมันเกาะกินใจกูตลอดแหละ แต่กูทิ้งมันไว้ข้างหลังไม่ได้ กูต้องลุย!", "กูไม่มีพลังวิเศษอะไรเลย นอกจากความดื้อด้านที่จะไม่ยอมแพ้!", "ถ้ากูหนีตอนนี้ ทุกอย่างที่กูทนเจ็บมามันจะสูญเปล่าทันที... ไม่มีทางซะหรอก!", "กูอาจจะร้องไห้ อาจจะสมเพชตัวเอง แต่กูจะไม่หยุดเดินเด็ดขาด!", "คนที่เริ่มใหม่จากศูนย์ได้เสมอ คือคนที่ไม่มีวันพ่ายแพ้ที่แท้จริง!", "ความผิดพลาดในอดีต กูนี่แหละจะเป็นคนใช้มือสองข้างนี้แก้ไขมันเอง!", "มันเจ็บ มันทรมาน แต่กูสัญญา... กูจะจบเรื่องนี้ด้วยตัวเอง!"
        ]
    },
    "Ippo": {
        "name": "อิปโป (Ippo - Dempsey Roll)", "icon": "🥊", 
        "desc": "สกิล [พื้นฐานรักษาชีวิต]: หากพลาดงานใหญ่ แต่มึงเคลียร์ 'วินัยเหล็ก' ครบ 100% ในวันนั้น Streak จะไม่ขาด!",
        "quotes": [
            "ผมจะซ้อมพื้นฐานซ้ำๆ จนกว่ามันจะฝังเข้าไปในกล้ามเนื้อและสายเลือด!", "สิ่งที่เรียกว่าความแข็งแกร่ง... ผมจะหามันด้วยสองมือนี้แหละ!", "ก้าวเข้าไป! อย่ากลัวความเจ็บปวด ก้าวเข้าไปหามันแม้ตาจะปิดก็ตาม!", "ต่อให้โดนอัดจนน่วม ขอแค่ขาก้าวไปข้างหน้าได้ ผมก็จะออกหมัดต่อไป!", "ความสำเร็จไม่มีทางลัด มันเกิดจากการสะสมการกระทำเล็กๆ ทุกวันต่างหาก!", "ตอนที่รู้สึกว่าไม่ไหวแล้ว นั่นแหละคือจุดเริ่มต้นของการเติบโต!", "ถึงจะไม่เก่งเท่าคนอื่น แต่ความพยายามของผมต้องไม่แพ้ใครแน่นอน!", "ฝึกซ้อมจนอ้วกแตก ดีกว่าไปพ่ายแพ้อย่างน่าสมเพชบนสังเวียนชีวิต!", "ผมจะก้มหน้าก้มตาบดขยี้มัน ทีละก้าว ทีละสเต็ป ไม่หยุดพัก!", "น้ำหนักของเป้าหมาย... ผมแบกมันไว้แล้ว จะให้ถอยตอนนี้ได้ยังไง!"
        ]
    },
    "Future You": {
        "name": "นักรบจากอนาคตอีก 20 ปี (Future You)", "icon": "⏳", 
        "desc": "สกิล [รากฐานแห่งอนาคต]: เคลียร์งานด่วน รับโบนัสพิเศษ +20 EXP แต่ดองงานค้าง ความกาก (Failure Prob) เด้ง x2!",
        "quotes": [
            "กูคือตัวมึงในอีก 20 ปีข้างหน้า มึงอยากเป็นไอ้ขี้แพ้หรือคนรวย มึงเลือกเลยวันนี้!", "อย่าทำตัวเหี้ยๆ วันนี้ แล้วส่งผลกรรมมาให้กูในอนาคตดิวะ!", "มึงรู้ไหมกูต้องแบกความเสียดายมากมายแค่ไหน เพราะความขี้เกียจของมึงวันนี้?", "กูขอร้องล่ะ ลุกขึ้นไปทำมันซะ เพื่อชีวิตที่ดีกว่าของกูและมึง!", "เงิน ทรัพย์สิน และอิสรภาพของกูในอนาคต ขึ้นอยู่กับวินัยของมึงในวินาทีนี้!", "ถ้ามึงกดโทรศัพท์ดูอะไรไร้สาระอีก 10 นาที อนาคตกูจะจนลงอีก 10 เท่า!", "อย่าให้กูต้องนั่งด่ามึงในใจทุกวันเลย... เปลี่ยนแปลงตัวเองเดี๋ยวนี้!", "กูมองย้อนกลับมาจากอนาคต และกูอยากขอบคุณมึงล่วงหน้าที่มึงไม่ยอมแพ้วันนี้!", "ความสบายชั่วคราวของมึงวันนี้ คือนรกขุมลึกของกูในอีก 20 ปีข้างหน้า!", "มึงจะอดทนวันนี้ หรือจะให้กูไปนั่งร้องไห้ในวัย 40? เลือกเอา!"
        ]
    }
}

PUNISHMENTS = [
    "ไปดันพื้น 50 ทีเดี๋ยวนี้! ลงโทษความอ่อนแอ!", "แพลงก์ 2 นาที! เอาความเจ็บปวดล้างสมองซะ!",
    "ลุกไปอาบน้ำเย็นจัด 5 นาทีเดี๋ยวนี้ ไป!", "กระโดดตบ 100 ครั้ง สลัดความขี้เกียจทิ้งไป!",
    "ห้ามจับมือถือ 1 ชั่วโมงนับจากนี้! นั่งสมาธิทบทวนความกากของตัวเอง!", "สควอช (ลุกนั่ง) 60 ที เอาให้ขาเบิร์น!",
    "เดินไปตะโกนใส่กำแพงว่า 'กูจะไม่ยอมกลับไปกระจอกอีก!' 10 รอบ!"
]

WARRIOR_OATHS = [
    "โลกนี้ไม่มีที่ยืนให้คนอ่อนแอ! ถ้ามึงเลือกที่จะขี้เกียจ ก็เตรียมตัวดูคนที่พยายามน้อยกว่ามึงแซงหน้าไปได้เลย!",
    "ข้ออ้างมีไว้สำหรับไอ้กระจอก! วันนี้มึงจะสร้างผลงาน หรือจะสร้างข้ออ้าง เลือกเอา!",
    "ความสบายในวันนี้ คือความชิบหายในวันหน้า! ลุกขึ้นมาบดขยี้ความขี้เกียจของมึงซะ!",
    "เวลาไม่เคยรอใคร ทุกวินาทีที่มึงไถมือถือโง่ๆ คือเวลาที่มึงกำลังฆ่าอนาคตตัวเอง!",
    "มึงบอกว่าอยากสำเร็จ แต่การกระทำมึงเหมือนคนรอวันตาย! ตื่น! แล้วไปทำในสิ่งที่ต้องทำเดี๋ยวนี้!"
]

WARRIOR_CONSEQUENCES = [
    "กูจะต้องทนเห็นคนที่พยายามน้อยกว่ากู ได้ดีกว่ากู!", "พรุ่งนี้กูก็จะตื่นมาเป็นไอ้ขี้แพ้คนเดิม ที่เก่งแต่ปาก!",
    "ความฝันที่กูโม้ไว้ ก็จะเป็นแค่อากาศธาตุ!", "กูจะกลายเป็นภาระของครอบครัวและคนที่รักกู!",
    "ชีวิตกูก็จะย่ำอยู่กับที่ ไม่มีวันเงยหน้าอ้าปากได้!", "กูจะต้องก้มหัวให้คนที่กูเกลียดไปตลอดชีวิต!",
    "อนาคตที่กูวาดฝันไว้ จะพังทลายลงด้วยมือของกูเอง!", "กูจะต้องเสียใจและเกลียดตัวเองในอีก 5 ปีข้างหน้า!"
]

ABYSS_VOICES = [
    "มึงทำ '{task}' ไม่ได้หรอก... ยอมแพ้แล้วกลับไปนอนโง่ๆ ซะเถอะ...",
    "ดอง '{task}' ไว้ก่อนสิ ไม่มีใครรู้หรอก พักก่อน... มึงมันก็แค่ไอ้ขี้แพ้คนเดิมนั่นแหละ!",
    "ถ้า '{task}' มันยากนัก ก็เทมันทิ้งไปสิ มึงจะได้กลับไปใช้ชีวิตกากๆ แบบที่มึงคู่ควรไง..."
]

COMMANDER_VOICES = [
    "อย่าไปฟังเสียงสวะนั่น! ลุกขึ้นมา! ร่างกายนี้มึงคุม ไปฟาด '{task}' ให้แหลกคามือ!",
    "เป้าหมายอยู่ตรงหน้า! เหยียบหัวความขี้เกียจแล้วลุย '{task}' เดี๋ยวนี้!",
    "ความเจ็บปวดจากการมีวินัย ดีกว่าความเจ็บปวดจากความเสียใจ! จับอาวุธไปลุย '{task}' ซะ!"
]

ETERNAL_ECHOES = [
    "มึงบอกว่าไม่อยากกากอีกแล้ว มึงทำตัวให้คู่ควรกับคำพูดรึยัง!?", "โลกไม่สนหรอกว่ามึงจะเหนื่อย โลกสนแค่ว่ามึงทำสำเร็จหรือเปล่า!",
    "ทุกวินาทีที่มึงขี้เกียจ คือวินาทีที่มึงปล่อยให้ตัวเองกลับไปเป็นไอ้ขี้แพ้!", "มึงจะเก่งได้ไงถ้ามึงเอาแต่หาข้ออ้าง ลุกขึ้นมา!"
]

AMBUSH_TASKS = ["กฎก้าวสุดท้าย! ไปแพลงก์ 1 นาทีก่อนนอน!", "คิดว่ารอดแล้วหรอ? วิดพื้น 20 ที!", "เขียนเป้าหมายพรุ่งนี้ 3 ข้อใส่กระดาษเดี๋ยวนี้!"]

def get_safe_email(email): return email.replace(".", "-").replace("@", "-")

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

def get_deadline_score(dl_str):
    if not dl_str or dl_str == "": return 999999
    try: return (datetime.strptime(str(dl_str).strip(), "%Y-%m-%d").date() - today_date).days
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
        res = requests.get(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}")
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
    except: pass
    return {
        "users": {}, "missions": {}, "study_missions": {}, "command_log": {}, "accountability_mirror": {},
        "dopamine_fails": {}, "excuses": {}, "cookie_jar": {}, "haters": {}, "finance": {}, "iron_habits": {}, "daily_wins": {},
        "exams": {}, "beat_yesterday": {}, "limit_breaks": {}, "weakness_fuel": {}, "sanctuary": {}, "skill_forge": {}
    }

def save_db(data):
    try: requests.put(f"{FIREBASE_URL}/db.json?auth={FIREBASE_SECRET}", json=data)
    except Exception as e: st.error(f"🚨 เซฟข้อมูลลงฐานข้อมูลไม่สำเร็จ! Error: {e}")

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
    st.caption(f"🗓️ วันที่: {thai_date_format(today_str)}") 
    
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
                        # ใส่ Default ชัยชนะรายวัน พร้อมโครงสร้าง logs ป้องกัน Error
                        db["daily_wins"][safe_email] = {
                            "items": [
                                {"id": str(uuid.uuid4()), "name": "🚫 No Fap / No Gooning (คุมสติตัวเองให้ได้)"},
                                {"id": str(uuid.uuid4()), "name": "🌅 ตื่นนอนตรงเวลา ไม่กด Snooze เด็ดขาด!"},
                                {"id": str(uuid.uuid4()), "name": "🗣️ ลุย Anki (อังกฤษ/จีน) ไม่ขาดสาย"},
                                {"id": str(uuid.uuid4()), "name": "🤖 ฝึกฝนโค้ดดิ้ง / ROS 2 อย่างน้อย 30 นาที"},
                                {"id": str(uuid.uuid4()), "name": "💧 ดื่มน้ำเปล่าให้เพียงพอ และออกกำลังกาย 1 ชั่วโมง"}
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
                    
                    # ตรวจสอบและสร้างโครงสร้าง daily_wins ป้องกัน Error
                    if safe_email not in db.get("daily_wins", {}) or not isinstance(db["daily_wins"][safe_email], dict):
                        db["daily_wins"][safe_email] = {"items": [], "logs": {}}
                    if "items" not in db["daily_wins"][safe_email]:
                        db["daily_wins"][safe_email]["items"] = [
                            {"id": str(uuid.uuid4()), "name": "🚫 No Fap / No Gooning (คุมสติตัวเองให้ได้)"},
                            {"id": str(uuid.uuid4()), "name": "🌅 ตื่นนอนตรงเวลา ไม่กด Snooze เด็ดขาด!"},
                            {"id": str(uuid.uuid4()), "name": "🗣️ ลุย Anki (อังกฤษ/จีน) ไม่ขาดสาย"},
                            {"id": str(uuid.uuid4()), "name": "🤖 ฝึกฝนโค้ดดิ้ง / ROS 2 อย่างน้อย 30 นาที"},
                            {"id": str(uuid.uuid4()), "name": "💧 ดื่มน้ำเปล่าให้เพียงพอ และออกกำลังกาย 1 ชั่วโมง"}
                        ]
                    if "logs" not in db["daily_wins"][safe_email]:
                        db["daily_wins"][safe_email]["logs"] = {}

                    if user_data.get("last_login") != today_str:
                        user_data["ghost_exp"] = user_data.get("ghost_exp", 0) + 25 
                        unpaid_bounties = [m for m in db.get("missions", {}).get(safe_email, []) if isinstance(m, dict) and m.get("bounty") and not m.get("เสร็จแล้ว")]
                        if unpaid_bounties or not user_data.get("cleared_yesterday", False):
                            penalty = 100 + (len(unpaid_bounties) * 100)
                            if user_data.get("anime_mentor") == "Jesus":
                                penalty = int(penalty * 0.5); user_data["exp"] = max(0, user.get("exp", 0) - 10)
                                st.toast("✝️ [พระคุณ] พระเยซูแบ่งเบาภาระหนี้เลือด 50%", icon="🕊️")
                            else:
                                user_data["exp"] = 0; user_data["level"] = max(1, user_data.get("level", 1) - 1); user_data["streak"] = 0
                            user_data["blood_debt"] = user_data.get("blood_debt", 0) + penalty
                            user_data["failure_prob"] = min(100, user.get("failure_prob", 10) + 20)
                            
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
# 🔥 คอนฟิกโครงสร้าง Database
# ==========================================
list_keys = ["missions", "study_missions", "command_log", "accountability_mirror", "dopamine_fails", "excuses", "cookie_jar", "haters", "iron_habits", "limit_breaks", "weakness_fuel", "sanctuary", "skill_forge"]
for k in list_keys:
    if safe_email not in db[k] or db[k][safe_email] is None: db[k][safe_email] = []
    elif isinstance(db[k][safe_email], dict): db[k][safe_email] = list(db[k][safe_email].values())

for k in ["finance", "exams", "beat_yesterday", "daily_wins"]:
    if safe_email not in db[k] or db[k][safe_email] is None: 
        if k == "finance": db[k][safe_email] = {"goal_name": "ยังไม่ได้ตั้ง", "goal_amount": 0, "current": 0}
        elif k == "daily_wins": db[k][safe_email] = {"items": [], "logs": {}}
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
try: t_date = datetime.strptime(str(user.get("target_date", str(today_date))).strip(), "%Y-%m-%d").date()
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
# 🗺️ THE ROADMAP
# ==========================================
st.markdown("## 🗺️ THE ULTIMATE ROADMAP (แผนผังชีวิตประจำวัน)")
if not all_active_tasks: st.success("✅ Roadmap ว่างเปล่า! วันนี้เคลียร์แผนผังชีวิตหมดแล้ว ยอดเยี่ยมมาก!")
else:
    mermaid_str = "graph TD\n"
    mermaid_str += "classDef targetNode fill:#ff4b4b,stroke:#ffffff,stroke-width:4px,color:#ffffff,font-size:18px,font-weight:bold;\n"
    mermaid_str += "classDef pendingNode fill:#262730,stroke:#888888,stroke-width:2px,color:#ffffff,font-size:16px;\n"
    mermaid_str += "classDef habitNode fill:#1E88E5,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-size:16px;\n"
    mermaid_str += "START((🔥 เริ่มวัน)):::pendingNode --> "
    
    for idx, task in enumerate(all_active_tasks):
        task_id = f"T{idx}"
        q_num = task.get("user_order", 99); q_label = f"[Q{q_num}] " if q_num != 99 else ""
        icon = "⛓️" if task.get("is_habit") else "📖" if task.get("is_study") else "🔪"
        node_class = "habitNode" if task.get("is_habit") and idx != 0 else "targetNode" if idx == 0 else "pendingNode"
            
        task_name = str(task.get('ภารกิจ', '')).replace('"', "'").replace('\n', ' ').replace('(', '[').replace(')', ']')
        mermaid_str += f'{task_id}["{q_label}{icon} {task_name}"]:::{node_class}\n'
        if idx < len(all_active_tasks) - 1: mermaid_str += f'{task_id} --> '
            
    mermaid_str += f'{task_id} --> END((🌙 จบวัน)):::pendingNode\n'
    st.markdown(f"```mermaid\n{mermaid_str}\n```")

    next_task_name = all_active_tasks[0]['ภารกิจ']
    st.divider()
    c_abyss, c_cmdr = st.columns(2)
    with c_abyss: st.error(f"💀 **ก้นเหวขี้เกียจ:**\n\n\"{random.choice(ABYSS_VOICES).format(task=next_task_name)}\"")
    with c_cmdr: st.success(f"⚔️ **แม่ทัพเหล็ก:**\n\n\"{random.choice(COMMANDER_VOICES).format(task=next_task_name)}\"")
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
            with st.expander("🎯 วางแผนลำดับงาน (Q-Order)"):
                with st.form("set_order_form"):
                    new_orders = {}
                    for m in todo_missions:
                        col_q, col_n = st.columns([1, 5])
                        new_orders[m["id"]] = col_q.number_input("คิว", min_value=1, max_value=99, value=m.get("user_order", 99), step=1, key=f"q_{m['id']}", label_visibility="collapsed")
                        col_n.write(f"{'💀 [BOSS] ' if m.get('is_boss') else ''}{m['ภารกิจ']}")
                    if st.form_submit_button("🔒 ล็อคผังชีวิต!"):
                        for m in db["missions"][safe_email]:
                            if isinstance(m, dict) and m.get("id") in new_orders: m["user_order"] = new_orders[m["id"]]
                        save_db(db); st.success("✅ อัปเดตผังเรียบร้อย!"); safe_rerun()

            for m in todo_missions:
                bg_style = "border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; margin-bottom: 10px;" if m == todo_missions[0] else "border: 1px solid #444; padding: 10px; border-radius: 5px; margin-bottom: 10px;"
                st.markdown(f"<div style='{bg_style}'>", unsafe_allow_html=True)
                c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6]) 
                
                is_overdue = is_overdue_check(m.get("deadline", ""))
                deadline_badge = format_days_left(m.get("deadline", ""))
                
                is_frozen = (m.get("skip_today_date") == today_str)
                if m.get("skip_today_date") != "" and not is_frozen: m["skip_today_date"] = ""; save_db(db)
                frozen_badge = " ❄️🚨 [เกราะแตก!]" if is_frozen and is_overdue else " ❄️ [แช่แข็ง]" if is_frozen else ""

                c1.write(f"**{m.get('ประเภท','')}** | {'🎯 **[Q' + str(m.get('user_order', 99)) + ']** ' if m.get('user_order', 99) != 99 else ''}{'🔪 **[ซอยงาน]**' if m.get('subtasks') else '⚡ **[ชิ้นเดียวจบ]**'}{' 💀 **[BOSS]**' if m.get('is_boss') else ''}{' ⚔️' if m.get('bounty') else ''} {m['ภารกิจ']} {deadline_badge}{frozen_badge}")
                
                m_id = str(m.get("id", f"unk_m_{m.get('ภารกิจ', '')}"))
                c1.markdown(f"<div style='font-size: 0.85em; background: rgba(255, 0, 0, 0.1); padding: 5px; border-left: 3px solid #ff4b4b; margin-bottom: 5px; margin-top: 5px;'>🩸 <b>ถ้ากูไม่ทำ:</b> {m.get('consequence', '') or WARRIOR_CONSEQUENCES[get_stable_index(m_id + 'conseq', len(WARRIOR_CONSEQUENCES))]}</div>", unsafe_allow_html=True)
                c1.markdown(f"<div style='font-size: 0.85em; background: rgba(255,165,0,0.1); padding: 5px; border-left: 3px solid #ffa500; margin-bottom: 10px;'>{MENTORS[active_mentor]['icon']} <b>{MENTORS[active_mentor]['name']}:</b> {active_quotes[get_stable_index(m_id + 'hype', len(active_quotes))]}</div>", unsafe_allow_html=True)
                
                with st.expander("📝 ดูรายละเอียดและเนื้องาน"):
                    if m.get("รายละเอียด"): st.write(m["รายละเอียด"])
                    all_done = True
                    if m.get("subtasks"):
                        st.markdown("**📌 งานย่อยที่ต้องเคลียร์:**")
                        for i, stask in enumerate(m["subtasks"]):
                            is_locked = stask.get("done", False) and stask.get("done_date", "") != today_str
                            can_interact = not is_locked and (not is_frozen or is_overdue)
                            checked = st.checkbox(f"{stask['name']} {'🔒 ('+thai_date_format(stask.get('done_date', ''))+')' if is_locked else ''}", value=stask.get("done", False), disabled=not can_interact, key=f"st_{m['id']}_{i}")
                            if can_interact and checked != stask.get("done", False):
                                m["subtasks"][i]["done"] = checked; m["subtasks"][i]["done_date"] = today_str if checked else ""; 
                                if checked and active_mentor == "Yuji": user["failure_prob"] = max(0, user.get("failure_prob",10) - 2)
                                save_db(db); safe_rerun()
                            if not checked: all_done = False
                        total_subs = len(m["subtasks"]); done_subs = len([s for s in m["subtasks"] if s.get("done")])
                        st.progress(done_subs / total_subs if total_subs > 0 else 0, text=f"ความคืบหน้า: {done_subs} / {total_subs}")

                if active_mentor == "Subaru" and is_overdue:
                    if user.get("exp", 0) >= 10:
                        if c1.button("⏪ Return by Death (-10 EXP)", key=f"rbd_{m['id']}", type="primary"): user["exp"] -= 10; m["deadline"] = today_str; save_db(db); safe_rerun()
                    else: c1.caption("⏪ ต้องการ 10 EXP")

                if is_frozen:
                    if c4.button("🔥 ปลดล็อก", key=f"unfrz_{m['id']}", use_container_width=True): m["skip_today_date"] = ""; save_db(db); safe_rerun()
                else:
                    if c4.button("❄️ แช่แข็ง", key=f"frz_{m['id']}", use_container_width=True): m["skip_today_date"] = today_str; save_db(db); safe_rerun()

                if all_done and (not is_frozen or is_overdue):
                    if c2.button("✅ สำเร็จ", key=f"m_{m['id']}"):
                        m["เสร็จแล้ว"] = True
                        exp_gain, fail_reduce = calculate_task_rewards(m, current_streak, active_mentor)
                        user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                    if c3.button("📤 ส่งตรวจ", key=f"pend_{m['id']}"): m["รอตรวจ"] = True; save_db(db); safe_rerun()
                else: c2.caption("❄️ แช่แข็ง" if is_frozen and not is_overdue else "🔒 งานย่อยคาอยู่")
                if c5.button("🗑️", key=f"del_m_{m['id']}"): db["missions"][safe_email].remove(m); save_db(db); safe_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        else: st.success("✅ วันนี้เคลียร์แผนผังงานหมดแล้ว!")

        pending_missions = [m for m in raw_active_missions if m.get("รอตรวจ", False)]
        if pending_missions:
            st.divider(); st.markdown("### ⏳ งานที่รอรีวิวผลงาน")
            for m in pending_missions:
                c1, c2, c3 = st.columns([5, 2, 2])
                c1.caption(f"⏳ {'💀 ' if m.get('is_boss') else ''}{m['ภารกิจ']}")
                if c2.button("✅ ตรวจผ่าน", key=f"appr_{m['id']}"):
                    m["เสร็จแล้ว"] = True; m["รอตรวจ"] = False
                    exp_gain, fail_reduce = calculate_task_rewards(m, current_streak, active_mentor)
                    user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                if c3.button("⏪ ดึงกลับมาทำ", key=f"revert_{m['id']}"): m["รอตรวจ"] = False; save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 2: 📖 เรียน
    # ----------------------------------------------------
    with tab_study:
        st.markdown("### 📖 วิชาที่ต้องบรรลุในวันนี้")
        raw_active_study = [s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว")]
        todo_study = [s for s in raw_active_study if not s.get("รอตรวจ", False)]
        todo_study.sort(key=lambda x: (x.get("user_order", 99), 0 if x.get("is_boss") else 1, get_deadline_score(x.get("deadline", "")), get_priority_score(x.get("ประเภท", ""))))
        
        if todo_study:
            with st.expander("🎯 วางแผนลำดับวิชาเรียน (Q-Order)"):
                with st.form("set_study_order_form"):
                    new_s_orders = {}
                    for s in todo_study:
                        col_q, col_n = st.columns([1, 5])
                        new_s_orders[s["id"]] = col_q.number_input("คิว", min_value=1, max_value=99, value=s.get("user_order", 99), step=1, key=f"q_s_{s['id']}", label_visibility="collapsed")
                        col_n.write(f"{'💀 [BOSS] ' if s.get('is_boss') else ''}{s['ภารกิจ']}")
                    if st.form_submit_button("🔒 ล็อคผังเรียน!"):
                        for s in db["study_missions"][safe_email]:
                            if isinstance(s, dict) and s.get("id") in new_s_orders: s["user_order"] = new_s_orders[s["id"]]
                        save_db(db); st.success("✅ อัปเดตผังเรียนเรียบร้อย!"); safe_rerun()

            for s in todo_study:
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([4.2, 1.8, 1.8, 1.6, 0.6])
                    is_overdue = is_overdue_check(s.get("deadline", ""))
                    deadline_badge = format_days_left(s.get("deadline", ""))
                    
                    is_frozen = (s.get("skip_today_date") == today_str)
                    if s.get("skip_today_date") != "" and not is_frozen: s["skip_today_date"] = ""; save_db(db)
                    frozen_badge = " ❄️🚨 [แช่แข็งแตก!]" if is_frozen and is_overdue else " ❄️ [แช่แข็ง]" if is_frozen else ""

                    c1.write(f"**{s.get('ประเภท','')}** | {'🎯 **[Q' + str(s.get('user_order', 99)) + ']** ' if s.get('user_order', 99) != 99 else ''}{'📖 **[ติวโครงใหญ่]**' if s.get('subtasks') else '⚡ **[ทบทวนจบ]**'}{' 💀 **[BOSS]**' if s.get('is_boss') else ''} {s['ภารกิจ']} {deadline_badge}{frozen_badge}")
                    
                    s_id = str(s.get("id", f"unk_s_{s.get('ภารกิจ', '')}"))
                    c1.markdown(f"<div style='font-size: 0.85em; background: rgba(255, 0, 0, 0.1); padding: 5px; border-left: 3px solid #ff4b4b; margin-bottom: 5px; margin-top: 5px;'>🩸 <b>ถ้ากูไม่ทำ:</b> {s.get('consequence', '') or WARRIOR_CONSEQUENCES[get_stable_index(s_id + 'conseq', len(WARRIOR_CONSEQUENCES))]}</div>", unsafe_allow_html=True)
                    c1.markdown(f"<div style='font-size: 0.85em; background: rgba(255,165,0,0.1); padding: 5px; border-left: 3px solid #ffa500; margin-bottom: 10px;'>{MENTORS[active_mentor]['icon']} <b>{MENTORS[active_mentor]['name']}:</b> {active_quotes[get_stable_index(s_id + 'hype', len(active_quotes))]}</div>", unsafe_allow_html=True)
                    
                    with st.expander("📝 ดูขอบเขต/รายละเอียด"):
                        if s.get("รายละเอียด"): st.write(s["รายละเอียด"])
                        all_done = True
                        if s.get("subtasks"):
                            st.markdown("**📌 บทเรียนที่ต้องเก็บ:**")
                            for i, stask in enumerate(s["subtasks"]):
                                is_locked = stask.get("done", False) and stask.get("done_date", "") != today_str
                                can_interact = not is_locked and (not is_frozen or is_overdue)
                                checked = st.checkbox(f"{stask['name']} {'🔒 ('+thai_date_format(stask.get('done_date', ''))+')' if is_locked else ''}", value=stask.get("done", False), disabled=not can_interact, key=f"st_stud_{s['id']}_{i}")
                                if can_interact and checked != stask.get("done", False):
                                    s["subtasks"][i]["done"] = checked; s["subtasks"][i]["done_date"] = today_str if checked else ""; 
                                    if checked and active_mentor == "Yuji": user["failure_prob"] = max(0, user.get("failure_prob",10) - 2)
                                    save_db(db); safe_rerun()
                                if not checked: all_done = False
                            total_subs = len(s["subtasks"]); done_subs = len([stk for stk in s["subtasks"] if stk.get("done")])
                            st.progress(done_subs / total_subs if total_subs > 0 else 0, text=f"คืบหน้า: {done_subs} / {total_subs} บท")

                if active_mentor == "Subaru" and is_overdue:
                    if user.get("exp", 0) >= 10:
                        if c1.button("⏪ Return by Death (-10 EXP)", key=f"rbds_{s['id']}", type="primary"): user["exp"] -= 10; s["deadline"] = today_str; save_db(db); safe_rerun()
                    else: c1.caption("⏪ ต้องการ 10 EXP")

                if is_frozen:
                    if c4.button("🔥 ปลดแช่แข็ง", key=f"unfrz_stud_{s['id']}", use_container_width=True): s["skip_today_date"] = ""; save_db(db); safe_rerun()
                else:
                    if c4.button("❄️ แช่แข็ง", key=f"frz_stud_{s['id']}", use_container_width=True): s["skip_today_date"] = today_str; save_db(db); safe_rerun()

                if all_done and (not is_frozen or is_overdue):
                    if c2.button("✅ ติวสำเร็จ", key=f"stud_win_{s['id']}", use_container_width=True):
                        s["เสร็จแล้ว"] = True
                        exp_gain, fail_reduce = calculate_task_rewards(s, current_streak, active_mentor)
                        user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                    if c3.button("📤 ส่งอนุมัติ", key=f"pend_stud_{s['id']}", use_container_width=True): s["รอตรวจ"] = True; save_db(db); safe_rerun()
                else: c2.caption("❄️ แช่แข็ง" if is_frozen and not is_overdue else "🔒 บทเรียนคาอยู่")
                if c5.button("🗑️", key=f"del_stud_{s['id']}"): db["study_missions"][safe_email].remove(s); save_db(db); safe_rerun()
        else: st.success("📚 ติวทบทวนเนื้อหาครบหมดแล้วใน Roadmap!")

        pending_study = [s for s in raw_active_study if s.get("รอตรวจ", False)]
        if pending_study:
            st.divider(); st.markdown("### ⏳ วิชาที่รออนุมัติ")
            for s in pending_study:
                c1, c2, c3 = st.columns([5, 2, 2])
                c1.caption(f"⏳ {s['ภารกิจ']}")
                if c2.button("✅ ผ่าน", key=f"appr_stud_{s['id']}"):
                    s["เสร็จแล้ว"] = True; s["รอตรวจ"] = False
                    exp_gain, fail_reduce = calculate_task_rewards(s, current_streak, active_mentor)
                    user["exp"] += exp_gain; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_reduce); save_db(db); st.balloons(); safe_rerun()
                if c3.button("⏪ กลับมาอ่าน", key=f"revert_stud_{s['id']}"): s["รอตรวจ"] = False; save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 3: ⚒️ โรงตีเหล็ก (THE SKILL FORGE)
    # ----------------------------------------------------
    with tab_forge:
        st.markdown("### ⚒️ โรงตีเหล็ก (THE SKILL FORGE)")
        st.write("ปลดล็อกขีดจำกัด! สะสม EXP ไปเรื่อยๆ ให้ Level พุ่งทะยาน **(ทุกๆ 100 EXP = 1 Level)** แต่ดึงมาฝึกพร้อมกันได้แค่ 2 อย่าง!")
        
        forge_data = db["skill_forge"].get(safe_email, [])
        active_skills = [sk for sk in forge_data if sk.get("status") == "active"]
        dormant_skills = [sk for sk in forge_data if sk.get("status") == "dormant"]
        
        with st.expander("➕ เพิ่มทักษะที่อยากเรียนรู้"):
            with st.form("forge_add_form", clear_on_submit=True):
                sk_name = st.text_input("ชื่อทักษะ (เช่น เขียนโปรแกรม, ภาษาญี่ปุ่น):")
                sk_why = st.text_input("ทำไมถึงอยากเก่งเรื่องนี้? (แรงผลักดัน):")
                if st.form_submit_button("บันทึกทักษะลงคลัง"):
                    if sk_name:
                        db["skill_forge"][safe_email].append({"id": str(uuid.uuid4()), "name": sk_name, "why": sk_why, "status": "dormant", "exp_gained": 0, "date_added": today_str})
                        save_db(db); safe_rerun()
                        
        st.divider()
        st.markdown(f"#### 🔥 ทักษะที่กำลังฝึกฝน (Active Skills: {len(active_skills)}/2)")
        if not active_skills: st.info("ยังไม่มีทักษะที่ดึงมาฝึก ไปดึงมาจากคลังสิวะ!")
        for sk in active_skills:
            with st.container(border=True):
                col1, col2, col3 = st.columns([5, 2, 1])
                col1.markdown(f"**⚡ {sk['name']}**")
                col1.caption(f"แรงผลักดัน: {sk.get('why', '-')}")
                sk_exp = sk.get('exp_gained', 0)
                col1.progress((sk_exp % 100) / 100.0, text=f"👑 Lv.{(sk_exp // 100) + 1} | {sk_exp % 100} / 100 EXP (รวม: {sk_exp} EXP)")
                
                if col2.button("🔥 ฝึกซ้อมวันนี้ (+10 EXP)", key=f"train_{sk['id']}", use_container_width=True):
                    sk["exp_gained"] = sk_exp + 10; user["exp"] += 5; st.toast(f"⚒️ ความชำนาญเพิ่มขึ้น!", icon="🔥"); save_db(db); safe_rerun()
                if col3.button("🧊 พักไว้", key=f"rest_{sk['id']}"): sk["status"] = "dormant"; save_db(db); safe_rerun()
                    
        st.divider()
        st.markdown("#### 🧊 คลังทักษะรอการฝึก (Dormant Skills)")
        if not dormant_skills: st.info("คลังว่างเปล่า")
        for sk in dormant_skills:
            with st.container(border=True):
                col1, col2, col3 = st.columns([5, 2, 1])
                sk_exp = sk.get('exp_gained', 0)
                col1.write(f"🧊 **{sk['name']}** (Lv.{(sk_exp // 100) + 1} | รวม: {sk_exp} EXP)")
                col1.caption(f"เหตุผล: {sk.get('why', '-')}")
                if col2.button("⚡ สวมใส่เพื่อฝึก (Equip)", key=f"equip_{sk['id']}", use_container_width=True):
                    if len(active_skills) >= 2: st.error("🚨 กฎเหล็ก: โฟกัสพร้อมกันได้แค่ 2 อย่าง!")
                    else: sk["status"] = "active"; save_db(db); safe_rerun()
                if col3.button("🗑️", key=f"del_sk_{sk['id']}"): db["skill_forge"][safe_email].remove(sk); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # 📝 TAB 4: สมุดบัญชาการ (COMMAND LOG)
    # ----------------------------------------------------
    with tab_planner:
        st.markdown("### 📝 สมุดบัญชาการ (Command Log)")
        st.write("ที่จดรวมทุกอย่าง: โน้ต งาน เรียน และ **ตารางสอบ**")
        
        pl_type = st.radio("ประเภทการบันทึก:", ["📝 โน้ตทั่วไป", "🔪 เตรียมงาน", "📖 เตรียมเรียน", "⚠️ ตารางสอบ"], horizontal=True)
        pl_title = st.text_input("หัวข้อเรื่อง:")
        pl_detail = st.text_area("รายละเอียด / ขอบเขตเนื้อหา:")
        
        pl_priority = "🟡 ปานกลาง"
        pl_subtasks_str = ""
        pl_date = None
        
        if "งาน" in pl_type or "เรียน" in pl_type:
            pl_priority = st.selectbox("ระดับความสำคัญ:", ["🔴 ด่วนสุด", "🔥 งานฉุกเฉิน", "🟡 ปานกลาง", "🟢 ชิลๆ"])
            pl_subtasks_str = st.text_area("🔪 ซอยข้อย่อย (Enter ขึ้นบรรทัดใหม่ / เว้นว่างถ้าเป็นงานชิ้นเดียวจบ):")
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
            else: st.warning("ใส่ชื่อหัวข้อด้วยสิวะ!")
                    
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
                        with c1.expander("📝 ดูรายละเอียด"): st.write(exam.get("detail", "ไม่มีรายละเอียด"))
                        if c2.button("🗑️", key=f"del_exm_{exam['id']}"): planner_items.remove(exam); save_db(db); safe_rerun()
            
            if tasks_study:
                st.divider()
                st.markdown("#### ⏳ งานและการเรียนที่เตรียมไว้ (ระวังดองเกินกำหนด)")
                active_m_slots = len([m for m in db["missions"][safe_email] if isinstance(m, dict) and not m.get("เสร็จแล้ว") and not m.get("subtasks")])
                active_s_slots = len([s for s in db["study_missions"][safe_email] if isinstance(s, dict) and not s.get("เสร็จแล้ว") and not s.get("subtasks")])
                
                for item in sorted(tasks_study, key=lambda x: x.get("deadline", "9999-12-31")):
                    is_overdue = is_overdue_check(item.get("deadline", ""))
                    bg_style = "border: 2px solid #ff4b4b; background-color: rgba(255,0,0,0.05);" if is_overdue else "border: 1px solid #444;"
                    st.markdown(f"<div style='{bg_style} padding: 10px; border-radius: 5px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([5, 2, 1])
                    
                    icon = "🔪 [งาน]" if item.get("type") == "task" else "📖 [เรียน]"
                    c1.markdown(f"**{item.get('priority', '🟡 ปานกลาง')}** | **{icon} {item['title']}** | 📅 {thai_date_format(item.get('deadline', '-'))} {format_days_left(item.get('deadline', ''))}")
                    
                    with c1.expander("📝 ดูรายละเอียดและงานย่อย"):
                        st.write(item.get("detail", "ไม่มีรายละเอียด"))
                        if item.get("subtasks"):
                            st.markdown("**งานย่อย:**")
                            for s in item["subtasks"]: st.write(f"- {s.get('name', '')}")
                    
                    if item.get("type") == "task":
                        if not item.get("subtasks") and active_m_slots >= 3: c2.button("⚡ โควตางานเดี่ยวเต็ม", key=f"pl_{item['id']}", disabled=True)
                        else:
                            if c2.button("⚡ ดึงเข้าหน้างาน", key=f"pl_{item['id']}", type="primary"):
                                db["missions"][safe_email].append({
                                    "id": item["id"], "วันที่": today_str, "ภารกิจ": item["title"], "รายละเอียด": item.get("detail", ""), 
                                    "ประเภท": item.get("priority", "🟡 ปานกลาง"), "bounty": False, "is_boss": False, "custom_order": 99, "user_order": 99, 
                                    "is_queued": False, "skip_today_date": "", "deadline": item.get("deadline", ""), "deadline_type": "🗓️ Deadline", 
                                    "subtasks": item.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False
                                })
                                planner_items.remove(item); save_db(db); safe_rerun()
                    else:
                        if not item.get("subtasks") and active_s_slots >= 3: c2.button("📖 โควตาเรียนเดี่ยวเต็ม", key=f"pl_{item['id']}", disabled=True)
                        else:
                            if c2.button("📖 ดึงเข้าหน้าเรียน", key=f"pl_{item['id']}", type="primary"):
                                db["study_missions"][safe_email].append({
                                    "id": item["id"], "วันที่": today_str, "ภารกิจ": item["title"], "รายละเอียด": item.get("detail", ""), 
                                    "ประเภท": item.get("priority", "🟡 ปานกลาง"), "bounty": False, "is_boss": False, "custom_order": 99, "user_order": 99, 
                                    "is_queued": False, "skip_today_date": "", "deadline": item.get("deadline", ""), "deadline_type": "🗓️ Deadline", 
                                    "subtasks": item.get("subtasks", []), "เสร็จแล้ว": False, "รอตรวจ": False, "is_study": True
                                })
                                planner_items.remove(item); save_db(db); safe_rerun()
                                
                    if c3.button("🗑️ ลบทิ้ง", key=f"del_pl_{item['id']}"): planner_items.remove(item); save_db(db); safe_rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            if notes:
                st.divider()
                st.markdown("#### 📝 โน้ตทั่วไป (General Notes)")
                for note in reversed(notes):
                    with st.expander(f"📝 {note['title']} (บันทึกเมื่อ: {thai_date_format(note.get('date_added', '-'))})"):
                        with st.form(f"edit_form_{note['id']}"):
                            new_title = st.text_input("แก้หัวข้อ:", value=note['title'])
                            new_content = st.text_area("แก้เนื้อหา:", value=note.get('detail', ''), height=150)
                            c1, c2 = st.columns([1, 1])
                            if c1.form_submit_button("💾 บันทึกการแก้ไข"):
                                note['title'] = new_title; note['detail'] = new_content; save_db(db); st.success("อัปเดตเรียบร้อย!"); safe_rerun()
                            if c2.form_submit_button("🗑️ ลบทิ้ง"): planner_items.remove(note); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 5: 🪞 กระจกแห่งความรับผิดชอบ
    # ----------------------------------------------------
    with tab_mirror:
        st.markdown("### 🪞 กระจกแห่งความรับผิดชอบ (Accountability Mirror)")
        st.write("เอาความจริงมากระแทกหน้า! แปะ Post-it ความกากหรือเป้าหมายที่ต้องบดขยี้!")
        
        mirror_notes = db["accountability_mirror"].get(safe_email, [])
        with st.form("mirror_add_form", clear_on_submit=True):
            st.markdown("**เขียน Post-it แปะกระจก**")
            note_text = st.text_area("ความจริงหรือเป้าหมาย (เช่น 'กูแม่งขี้เกียจตอนเช้า' หรือ 'ต้องลุกไปวิ่ง'):", height=100)
            note_type = st.radio("ประเภท:", ["🔥 ความจริงอันน่าเกลียด (Brutal Truth)", "🎯 เป้าหมายที่ต้องบดขยี้ (Goal)"], horizontal=True)
            if st.form_submit_button("แปะกระจกเดี๋ยวนี้!"):
                if note_text:
                    db["accountability_mirror"][safe_email].append({"id": str(uuid.uuid4()), "text": note_text, "is_goal": "Goal" in note_type, "date_added": today_str})
                    save_db(db); safe_rerun()
                    
        st.divider()
        if not mirror_notes: st.info("กระจกยังว่างเปล่า... กล้าเผชิญหน้ากับความจริงตัวเองหน่อยสิวะ!")
        else:
            cols = st.columns(3)
            for idx, note in enumerate(reversed(mirror_notes)):
                col = cols[idx % 3]
                bg_color, border_color, icon = ("#102a10", "#4bff4b", "🎯") if note.get('is_goal') else ("#2a1010", "#ff4b4b", "🔥")
                with col:
                    st.markdown(f"<div style='background-color: {bg_color}; border-left: 5px solid {border_color}; padding: 10px; margin-bottom: 10px; border-radius: 3px;'><b>{icon} {thai_date_format(note.get('date_added', '-'))}</b><br><p style='margin-top: 5px;'>{note.get('text', '')}</p></div>", unsafe_allow_html=True)
                    if st.button("🗑️ ดึงออก", key=f"del_mirror_{note['id']}", use_container_width=True): db["accountability_mirror"][safe_email].remove(note); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 6: ⛓️ วินัยเหล็ก (THE IRON HABITS)
    # ----------------------------------------------------
    with tab_habits:
        st.markdown("### ⛓️ วินัยเหล็ก (THE IRON HABITS) ")
        st.write("ระบบเก็บ Streak รายบุคคล ถ้าพลาดวันเดียว ร่วงกลับไปนับ 1 ใหม่! (กดดันตัวเองดิวะ!)")
        
        with st.expander("➕ เพิ่มวินัยเหล็กใหม่"):
            with st.form("habit_form", clear_on_submit=True):
                h_name = st.text_input("ชื่อวินัย (เช่น นั่งสมาธิ 10 นาที, ดื่มน้ำ):")
                h_detail = st.text_input("คติเตือนใจ / ทำไปทำไม?:")
                h_conseq = st.text_input("🩸 ผลของการหลุดวินัย (ถ้ามึงทิ้งวินัยนี้ จะเกิดอะไรขึ้น?):")
                if st.form_submit_button("บรรจุวินัยเหล็ก"):
                    if h_name:
                        db["iron_habits"][safe_email].append({"id": str(uuid.uuid4()), "name": h_name, "รายละเอียด": h_detail, "consequence": h_conseq.strip(), "last_done_date": "", "total_done": 0, "user_order": 99, "streak": 0})
                        save_db(db); safe_rerun()
        
        todo_habits = [h for h in db["iron_habits"][safe_email] if isinstance(h, dict) and h.get("last_done_date") != today_str]
        
        if todo_habits:
            with st.expander("🎯 วางแผนลำดับวินัย (Q-Order)"):
                with st.form("set_habit_order_form"):
                    new_h_orders = {}
                    for h in todo_habits:
                        col_q, col_n = st.columns([1, 5])
                        new_h_orders[h["id"]] = col_q.number_input("คิว", min_value=1, max_value=99, value=h.get("user_order", 99), step=1, key=f"q_h_{h['id']}", label_visibility="collapsed")
                        col_n.write(f"⛓️ {h['name']}")
                    if st.form_submit_button("🔒 ล็อคคิววินัย! (เซฟแผน)"):
                        for h in db["iron_habits"][safe_email]:
                            if isinstance(h, dict) and h.get("id") in new_h_orders: h["user_order"] = new_h_orders[h["id"]]
                        save_db(db); st.success("✅ อัปเดตผังวินัยเรียบร้อย!"); safe_rerun()
                    
        if db["iron_habits"][safe_email]:
            st.divider()
            for h in db["iron_habits"][safe_email]:
                if not isinstance(h, dict): continue 
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 3, 1])
                    h_streak = h.get("streak", 0)
                    streak_badge = f"🔥 Streak: {h_streak} วัน!" if h_streak > 0 else "❄️ ไม่มี Streak"
                    
                    c1.write(f"⛓️ {'🎯 **[Q' + str(h.get('user_order', 99)) + ']** ' if h.get('user_order', 99) != 99 else ''}**{h['name']}**  *({streak_badge} | รวม {h.get('total_done', 0)} ครั้ง)*")
                    
                    with c1.expander("📝 ดูรายละเอียด"):
                        if h.get("รายละเอียด"): st.write(f"💡 **เป้าหมาย:** {h['รายละเอียด']}")
                        h_id = str(h.get("id", f"unk_h_{h.get('name', '')}"))
                        st.markdown(f"<div style='font-size: 0.85em; background: rgba(255, 0, 0, 0.1); padding: 5px; border-left: 3px solid #ff4b4b; margin-top: 5px;'>🩸 <b>ถ้าหลุดวินัย:</b> {h.get('consequence', '') or WARRIOR_CONSEQUENCES[get_stable_index(h_id + 'conseq', len(WARRIOR_CONSEQUENCES))]}</div>", unsafe_allow_html=True)
                        
                    if h.get("last_done_date") == today_str: 
                        c2.success("✅ รักษาวินัยได้แล้ววันนี้!")
                    else:
                        if c2.button("🔥 กูทำสำเร็จ!", key=f"h_done_{h.get('id', h.get('name', ''))}", use_container_width=True):
                            if h.get("last_done_date") == yesterday_str: h["streak"] = h.get("streak", 0) + 1
                            else: h["streak"] = 1
                            h["last_done_date"] = today_str; h["total_done"] = h.get("total_done", 0) + 1
                            
                            bonus = 10 if current_streak >= 30 else 7 if current_streak >= 7 else 5
                            fail_sub = 5 if current_streak >= 30 else 3 if current_streak >= 7 else 2
                            user["exp"] += bonus; user["failure_prob"] = max(0, user.get("failure_prob",10) - fail_sub); save_db(db); safe_rerun()
                    if c3.button("🗑️", key=f"del_h_{h.get('id', h.get('name', ''))}"): db["iron_habits"][safe_email].remove(h); save_db(db); safe_rerun()

    # ----------------------------------------------------
    # TAB 7: 🏅 ชัยชนะรายวัน (Daily Wins) [FIXED & ENHANCED]
    # ----------------------------------------------------
    with tab_daily_wins:
        st.markdown("### 🏅 ชัยชนะรายวัน (Daily Wins)")
        st.write(f"**ประจำ{thai_date_format(today_str)}**")
        st.write("เช็คลิสต์ความสำเร็จเล็กๆ ที่มึงต้องเคลียร์ทุกวัน! ชนะก็กดชนะ แพ้ก็ยอมรับว่าแพ้ (กดแพ้โดนหนี้เลือด 10 ที!) ระบบจะเก็บบันทึกแยกวันให้โดยอัตโนมัติ")
        
        # ป้องกัน Key Error และสร้างโครงสร้างเริ่มต้นให้สมบูรณ์
        if safe_email not in db["daily_wins"] or not isinstance(db["daily_wins"][safe_email], dict):
            db["daily_wins"][safe_email] = {"items": [], "logs": {}}
        if "items" not in db["daily_wins"][safe_email]:
            db["daily_wins"][safe_email]["items"] = []
        if "logs" not in db["daily_wins"][safe_email]:
            db["daily_wins"][safe_email]["logs"] = {}

        win_items = db["daily_wins"][safe_email]["items"]
        
        with st.expander("➕ เพิ่มเป้าหมายแห่งชัยชนะ"):
            with st.form("add_daily_win_form", clear_on_submit=True):
                new_win = st.text_input("เรื่องที่ต้องชนะตัวเองทุกวัน (เช่น ไม่ลืมกินข้าวเช้า, ยิ้มให้ตัวเอง):")
                if st.form_submit_button("บันทึกเป้าหมาย"):
                    if new_win:
                        win_items.append({"id": str(uuid.uuid4()), "name": new_win})
                        db["daily_wins"][safe_email]["items"] = win_items
                        save_db(db)
                        st.success("เพิ่มเป้าหมายสำเร็จ!")
                        safe_rerun()
                        
        if win_items:
            st.markdown("#### 🔥 เช็คลิสต์วันนี้")
            if today_str not in db["daily_wins"][safe_email]["logs"]:
                db["daily_wins"][safe_email]["logs"][today_str] = {}
            
            today_logs = db["daily_wins"][safe_email]["logs"][today_str]
            
            for item in win_items:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([4, 1.5, 1.5, 0.5])
                    status = today_logs.get(item["id"])
                    
                    if status == "win":
                        col1.markdown(f"✅ **<span style='color:#4bff4b;'>{item['name']}</span>**", unsafe_allow_html=True)
                        col2.write("🏆 ชนะแล้ว!")
                    elif status == "lose":
                        col1.markdown(f"❌ **<span style='color:#ff4b4b; text-decoration: line-through;'>{item['name']}</span>**", unsafe_allow_html=True)
                        col2.write("💀 แพ้ราบคาบ")
                    else:
                        col1.markdown(f"**{item['name']}**")
                        if col2.button("✅ ชนะ", key=f"win_{item['id']}", use_container_width=True):
                            db["daily_wins"][safe_email]["logs"][today_str][item["id"]] = "win"
                            user["exp"] += 5
                            save_db(db)
                            st.balloons()
                            safe_rerun()
                        if col3.button("❌ แพ้", key=f"lose_{item['id']}", use_container_width=True):
                            db["daily_wins"][safe_email]["logs"][today_str][item["id"]] = "lose"
                            user["blood_debt"] = user.get("blood_debt", 0) + 10
                            save_db(db)
                            safe_rerun()
                            
                    if col4.button("🗑️", key=f"del_dwin_{item['id']}"):
                        win_items.remove(item)
                        db["daily_wins"][safe_email]["items"] = win_items
                        save_db(db)
                        safe_rerun()
            
            # 📜 ประวัติการเอาชนะตัวเองย้อนหลัง (เปิดดูได้ตลอดเวลา)
            st.divider()
            st.markdown("#### 📜 ประวัติการเอาชนะตัวเอง (ย้อนหลัง)")
            all_logs = db["daily_wins"][safe_email].get("logs", {})
            if not all_logs:
                st.info("ยังไม่มีประวัติย้อนหลัง")
            else:
                for log_date in sorted(all_logs.keys(), reverse=True):
                    day_log = all_logs[log_date]
                    wins_count = sum(1 for v in day_log.values() if v == "win")
                    loses_count = sum(1 for v in day_log.values() if v == "lose")
                    
                    with st.expander(f"📅 {thai_date_format(log_date)} (🏆 ชนะ: {wins_count} | ❌ แพ้: {loses_count})"):
                        for w_item in win_items:
                            w_status = day_log.get(w_item["id"], "pending")
                            icon = "✅ (ชนะ)" if w_status == "win" else "❌ (แพ้)" if w_status == "lose" else "➖ (ไม่ได้เช็ค)"
                            st.write(f"- {icon} {w_item['name']}")
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
                        st.caption(f"📅 วันที่บันทึก: {thai_date_format(note.get('วันที่', ''))}"); st.write(f"💭 {note.get('ข้อความ', '')}")
                        if active_mentor == "Jesus": st.markdown(f"<p style='color: #4ba3ff; font-style: italic; font-size: 0.9em;'>✝️ \"{random.choice(MENTORS['Jesus']['quotes'])}\"</p>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 9: โหลคุกกี้ (Cookie Jar) 🍪
    # ----------------------------------------------------
    with tab_cookie:
        st.markdown("### 🍪 โหลเก็บความภูมิใจ (Cookie Jar)")
        st.write("ที่เก็บความสำเร็จชิ้นใหญ่ เรื่องราวที่ทำให้มึงภูมิใจในตัวเองแบบสุดๆ")
        with st.form("cookie_form", clear_on_submit=True):
            win_text = st.text_input("ความสำเร็จที่อยากเก็บไว้เป็นความทรงจำ:")
            if st.form_submit_button("เก็บเข้าโหล!"):
                if win_text: db["cookie_jar"][safe_email].append({"id": str(uuid.uuid4()), "วันที่": today_str, "ชัยชนะ": win_text}); user["exp"] += int(5 * (1.5 if current_streak>=30 else 1.2 if current_streak>=7 else 1.0)); save_db(db); st.success("✅ เก็บความสำเร็จ!"); safe_rerun()
        if db["cookie_jar"][safe_email]:
            for c in reversed(db["cookie_jar"][safe_email][-5:]):
                if isinstance(c, dict): st.success(f"🏆 **[{thai_date_format(c.get('วันที่', '-'))}]** {c.get('ชัยชนะ', '')}")

    # ----------------------------------------------------
    # TAB 10: ลานประลองปัญญา (EXAM & BEAT YESTERDAY) 📚
    # ----------------------------------------------------
    with tab_academic:
        st.markdown("### 📚 ลานประลอง (วัดผลความก้าวหน้า)")
        with st.form("exam_form", clear_on_submit=True):
            e_subj = st.text_input("ชื่อวิชา / เรื่องที่ทดสอบ:")
            e_score = st.number_input("คะแนนที่ได้ล่าสุด:", min_value=0.0, step=0.1)
            if st.form_submit_button("บันทึกคะแนนสอบ"):
                if e_subj:
                    if e_subj not in db["exams"][safe_email]: db["exams"][safe_email][e_subj] = []
                    history = db["exams"][safe_email][e_subj]
                    if len(history) > 0:
                        last_score = history[-1]
                        if e_score > last_score: user["exp"] += int(30 * (1.5 if current_streak>=30 else 1.0))
                        elif e_score < last_score: user["blood_debt"] = user.get("blood_debt",0) + 50; user["failure_prob"] = min(100, user.get("failure_prob",10) + 10)
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
        with st.form("beat_yesterday_form"):
            by_metric = st.text_input("สิ่งที่ใช้วัดผล (เช่น จำนวนข้อที่ทำได้):", value=db["beat_yesterday"][safe_email].get("metric_name", ""))
            by_val = st.number_input("สถิติที่ทำได้วันนี้:", min_value=0)
            if st.form_submit_button("ทุบสถิติตัวเอง"):
                if by_metric:
                    db["beat_yesterday"][safe_email]["metric_name"] = by_metric
                    if "history" not in db["beat_yesterday"][safe_email]: db["beat_yesterday"][safe_email]["history"] = {}
                    y_val = db["beat_yesterday"][safe_email]["history"].get(yesterday_str, 0)
                    if by_val > y_val: user["exp"] += int(20 * (1.2 if current_streak>=7 else 1.0))
                    elif by_val < y_val: user["blood_debt"] = user.get("blood_debt",0) + 30
                    db["beat_yesterday"][safe_email]["history"][today_str] = by_val; save_db(db); safe_rerun()

        st.divider()
        if st.button("🔥 ทะลุขีดจำกัด (ก้าวข้ามความเหนื่อยล้าไปได้)!", use_container_width=True):
            if today_str not in db["limit_breaks"][safe_email]:
                db["limit_breaks"][safe_email].append(today_str); user["exp"] += int(50 * (1.5 if current_streak>=30 else 1.0)); user["failure_prob"] = max(0, user.get("failure_prob",10) - 15); save_db(db); safe_rerun()

    st.divider()
    st.markdown("### 💰 คลังทุนสร้างฝัน (Financial Goal)")
    c_fin1, c_fin2 = st.columns([2, 1])
    with c_fin1:
        st.write(f"**เป้าหมาย:** {finance.get('goal_name', 'ยังไม่ตั้ง')}")
        cur = finance.get('current', 0); tgt = finance.get('goal_amount', 1); prog = max(0.0, min(cur / tgt, 1.0)) if tgt > 0 else 0.0
        st.progress(prog, text=f"มียอดแล้ว: {cur} / {tgt} บาท")
    with c_fin2:
        with st.popover("⚙️ จัดการกองทุน"):
            new_g_name = st.text_input("ชื่อเป้าหมายเงิน:", value=finance.get('goal_name', ''))
            new_g_amt = st.number_input("ยอดเป้าหมาย:", value=finance.get('goal_amount', 0))
            if st.button("ตั้งเป้าหมาย"): finance['goal_name'] = new_g_name; finance['goal_amount'] = new_g_amt; save_db(db); safe_rerun()
            st.divider()
            add_amt = st.number_input("บวก/ลด เงิน:", value=0)
            if st.button("บันทึกยอดเงิน"): finance['current'] += add_amt; save_db(db); safe_rerun()

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
    active_for_judgment = []
    combined_missions = [m for m in db["missions"][safe_email] if isinstance(m, dict)] + [s for s in db["study_missions"][safe_email] if isinstance(s, dict)]
    
    for m in combined_missions:
        if not m.get("เสร็จแล้ว") and not m.get("รอตรวจ", False):
            if m.get("skip_today_date") == today_str:
                if not is_overdue_check(m.get("deadline", "")): continue 
            if m.get("subtasks"):
                if not any(stask.get("done", False) and stask.get("done_date", "") == today_str for stask in m["subtasks"]): active_for_judgment.append(m)
            else: active_for_judgment.append(m)

    incomplete_habits = [h for h in db["iron_habits"][safe_email] if isinstance(h, dict) and h.get("last_done_date"] != today_str]
    incomplete_bosses = [m for m in active_for_judgment if m.get("is_boss")]
    all_habits_completed = len(db["iron_habits"][safe_email]) > 0 and len(incomplete_habits) == 0

    if incomplete_bosses:
        st.error("💀 ไร้วินัยขั้นรุนแรง! ดองงานระดับ BOSS!")
        if st.button("🩸 ยอมรับความล้มเหลว (รับหนี้เลือด 300 ที!)"):
            penalty_debt = 300 * (2 if active_mentor == "Toji" else 1) * (0.5 if active_mentor == "Jesus" else 1)
            user["blood_debt"] = user.get("blood_debt",0) + int(penalty_debt)
            user["failure_prob"] = min(100, user.get("failure_prob",10) + 30)
            user["in_cage"] = True; user["cleared_yesterday"] = True
            if active_mentor != "Ippo" or not all_habits_completed: user["streak"] = 0
            save_db(db); safe_rerun()
            
    elif active_for_judgment or incomplete_habits: 
        st.error("❌ ศาลแห่งวินัยพบงานค้าง:")
        total_blood_penalty = sum(100 if get_priority_score(m.get("ประเภท", "")) == 1 else 70 if get_priority_score(m.get("ประเภท", "")) == 2 else 50 for m in active_for_judgment) + (len(incomplete_habits) * 30)
        for m in active_for_judgment: st.write(f"👉 **{m.get('ภารกิจ','')}**")
        for h in incomplete_habits: st.write(f"👉 **{h.get('name','')}** [วินัยเหล็ก]")
        
        if st.button(f"🩸 ยอมรับความอ่อนแอ (รับหนี้เลือด {int(total_blood_penalty * (0.5 if active_mentor == 'Jesus' else 1))} ที)"):
            user["blood_debt"] = user.get("blood_debt",0) + int(total_blood_penalty * (0.5 if active_mentor == 'Jesus' else 1))
            user["failure_prob"] = min(100, user.get("failure_prob",10) + (10 * (len(active_for_judgment) + len(incomplete_habits))))
            user["in_cage"] = True; user["cleared_yesterday"] = True
            if active_mentor != "Ippo" or not all_habits_completed: user["streak"] = 0
            
            for h in incomplete_habits:
                for db_h in db["iron_habits"][safe_email]:
                    if db_h.get("id") == h.get("id"): db_h["streak"] = 0
                    
            save_db(db); safe_rerun()
            
    elif user.get("in_cage") or user.get("blood_debt", 0) > 0: 
        st.error("❌ ติดหนี้เลือดอยู่ ชดใช้กรรมให้หมดก่อนพิพากษา!")
    else:
        st.warning("วันนี้ทำตามแผนสุดกำลัง หรือแค่ทำผ่านๆ ไป?")
        j_col1, j_col2 = st.columns(2)
        with j_col1:
            if st.button("📉 ทำลวกๆ ไม่เต็ม 100%"):
                user["exp"] = max(0, user.get("exp",0) - int(30 * (0.5 if active_mentor == "Jesus" else 1)))
                user["cleared_yesterday"] = True; user["failure_prob"] = min(100, user.get("failure_prob",10) + 10)
                if active_mentor != "Ippo" or not all_habits_completed: user["streak"] = 0
                save_db(db); safe_rerun()
        with j_col2:
            if st.button("🔥 ใส่เต็ม 100% ตามเส้นทางวินัย!"):
                if random.random() < 0.2: user["ambush_task"] = random.choice(AMBUSH_TASKS)
                else: user["cleared_yesterday"] = True; user["streak"] = user.get("streak",0) + 1; user["exp"] += int(25 * (1.5 if current_streak>=30 else 1.2 if current_streak>=7 else 1.0))
                save_db(db); safe_rerun()

# ==========================================
# 8. 📜 ประวัติศาสตร์เส้นทางวินัย
# ==========================================
st.divider()
st.markdown("## 📜 ประวัติศาสตร์เส้นทางวินัย (HISTORY LOG)")
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ บันทึกเดินทาง", "🏆 โหลความภูมิใจ", "🤡 ความกาก & ข้ออ้าง", "📊 BATTLE ANALYTICS"])

with tab1:
    st.markdown("### 🗺️ ประวัติภารกิจที่พิชิตแล้ว")
    completed_m = sorted([m for m in db["missions"].get(safe_email, []) if isinstance(m, dict) and m.get("เสร็จแล้ว")], key=lambda x: str(x.get("วันที่", "")), reverse=True)
    completed_s = sorted([s for s in db["study_missions"].get(safe_email, []) if isinstance(s, dict) and s.get("เสร็จแล้ว")], key=lambda x: str(x.get("วันที่", "")), reverse=True)
    all_completed = completed_m + completed_s
    
    if not all_completed: st.info("ยังไม่มีภารกิจที่ทำสำเร็จ ไปลุยซะ!")
    for idx, item in enumerate(all_completed):
        c1, c2 = st.columns([10, 1])
        c1.info(f"✅ **[{thai_date_format(item.get('วันที่', '-'))}]** | {'📖 เรียน' if item.get('is_study') else '🔪 งาน'} | {item.get('ภารกิจ', '')}")
        if c2.button("🗑️", key=f"del_hm_{idx}_{item.get('id', idx)}"):
            (db["study_missions"] if item.get("is_study") else db["missions"])[safe_email].remove(item); save_db(db); safe_rerun()

with tab2:
    st.markdown("### 🏆 โหลความภูมิใจ (Cookie Jar)")
    if not db["cookie_jar"].get(safe_email): st.info("ยังไม่มีความภูมิใจสะสมไว้")
    for idx, c in enumerate(reversed(db["cookie_jar"].get(safe_email, []))):
        c1, c2 = st.columns([10, 1])
        if isinstance(c, dict):
            c1.success(f"🏆 **[{thai_date_format(c.get('วันที่', '-'))}]** {c.get('ชัยชนะ', '')}")
            if c2.button("🗑️", key=f"del_cj_{idx}_{c.get('id', idx)}"): db["cookie_jar"][safe_email].remove(c); save_db(db); safe_rerun()
        else: 
            c1.success(f"🏆 {c}")
            if c2.button("🗑️", key=f"del_cj_old_{idx}"): db["cookie_jar"][safe_email].remove(c); save_db(db); safe_rerun()

with tab3:
    st.markdown("### 🩸 เชื้อเพลิงความแค้น (ความกากในอดีต)")
    if not db["weakness_fuel"].get(safe_email): st.info("ยังไม่มีประวัติความกาก")
    for idx, w in enumerate(reversed(db["weakness_fuel"].get(safe_email, []))):
        c1, c2 = st.columns([10, 1])
        c1.error(f"🩸 **[เชื้อเพลิงความแค้น]** : {w.get('text', '') if isinstance(w, dict) else w}")
        if c2.button("🗑️", key=f"del_wf_{idx}"): db["weakness_fuel"][safe_email].remove(w); save_db(db); safe_rerun()

with tab4:
    all_m = [m for m in db["missions"].get(safe_email, []) if isinstance(m, dict)] + [s for s in db["study_missions"].get(safe_email, []) if isinstance(s, dict)]
    total_m = len(all_m)
    done_m = len([m for m in all_m if m.get("เสร็จแล้ว")])
    win_rate = (done_m / total_m * 100) if total_m > 0 else 0
    win_count = len([c for c in db["cookie_jar"].get(safe_email, []) if isinstance(c, dict)])
    fail_count = len(db["weakness_fuel"].get(safe_email, []))
    
    c_stat1, c_stat2, c_stat3, c_stat4 = st.columns(4)
    c_stat1.metric("อัตราการรักษาวินัย", f"{win_rate:.1f}%")
    c_stat2.metric("บอสที่จัดการได้", f"{len([m for m in all_m if m.get('เสร็จแล้ว') and m.get('is_boss')])} ตัว")
    c_stat3.metric("เป้าหมายสำเร็จ", f"{done_m} / {total_m}")
    c_stat4.metric("รอยแผลความกาก", f"{fail_count} รอย")
    if win_count + fail_count > 0: 
        st.bar_chart(pd.DataFrame({"จำนวนครั้ง": [win_count, fail_count]}, index=["Discipline (ชนะใจ)", "Weakness (เคยกาก)"]))
