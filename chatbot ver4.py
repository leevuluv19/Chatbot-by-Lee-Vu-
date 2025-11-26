import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import secrets
import os
import re
from datetime import datetime, timedelta
import pytz
from gtts import gTTS
import base64
import io
import urllib.parse

# ==============================================================================
# 1. CẤU HÌNH HỆ THỐNG & BIẾN
# ==============================================================================
st.set_page_config(page_title="Le Vu Intelligence", page_icon="👑", layout="centered", initial_sidebar_state="collapsed")

# --- Cấu hình Admin ---
FILE_DATA = "key_data.json"
SDT_ADMIN = "0376274345"
ADMIN_PASSWORD = "levudepzai" # <--- MẬT KHẨU QUYỀN LỰC NHẤT

# --- Khởi tạo Session ---
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None

# ==============================================================================
# 2. KHU VỰC ĐỊNH NGHĨA HÀM (CORE FUNCTIONALITY)
# ==============================================================================
def load_data():
    if not os.path.exists(FILE_DATA):
        with open(FILE_DATA, 'w', encoding='utf-8') as f: json.dump({}, f)
        return {}
    try:
        with open(FILE_DATA, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(FILE_DATA, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

def tao_key_moi(sdt_khach, ghi_chu, so_ngay_dung):
    data = load_data()
    phan_duoi = secrets.token_hex(4).upper()
    new_key = f"KEY-{phan_duoi[:4]}-{phan_duoi[4:]}"
    
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz)
    exp = now + timedelta(days=so_ngay_dung)
    
    data[new_key] = {
        "status": "active", "sdt": sdt_khach, 
        "created_at": now.strftime("%d/%m/%Y %H:%M"),
        "expiry_date": exp.strftime("%d/%m/%Y %H:%M"), "note": ghi_chu
    }
    save_data(data)
    return new_key, exp.strftime("%d/%m/%Y")

def kiem_tra_dang_nhap(input_key, input_sdt):
    # --- CỔNG ADMIN (GOD MODE) ---
    if input_key == ADMIN_PASSWORD: 
        return True, "admin", f"Chào mừng Chủ Nhân Lê Vũ! 👑"
    
    # --- CỔNG NGƯỜI DÙNG THƯỜNG ---
    data = load_data()
    if input_key in data:
        info = data[input_key]
        if info.get("sdt") != input_sdt: return False, None, "❌ Sai số điện thoại đăng ký!"
        
        # Check hạn dùng
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        try:
            exp_date = datetime.strptime(info.get("expiry_date"), "%d/%m/%Y %H:%M").replace(tzinfo=vn_tz)
            if datetime.now(vn_tz) > exp_date: return False, None, "⚠️ Key đã HẾT HẠN!"
            days_left = (exp_date - datetime.now(vn_tz)).days
            return True, "user", f"Xin chào! (Hạn còn: {days_left} ngày)"
        except: return True, "user", "Xin chào!" # Fallback nếu lỗi ngày tháng
            
    return False, None, "❌ Key không tồn tại!"

def get_audio_html(text):
    """Bot nói chuyện"""
    if not text or len(text.strip()) == 0: return ""
    try:
        tts = gTTS(text=text, lang='vi')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        return f"""<audio controls class="stAudio" src="data:audio/mp3;base64,{b64}" autoplay style="width: 100%; height: 25px; opacity: 0.8; margin-top: 5px;"></audio>"""
    except: return ""

# ==============================================================================
# 3. KHỞI TẠO TRÍ TUỆ NHÂN TẠO (GEMINI)
# ==============================================================================
if "chat_session" not in st.session_state:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # --- BỘ NÃO TRUNG THÀNH ---
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now_str = datetime.now(vn_tz).strftime("%H:%M ngày %d/%m/%Y")
        
        sys_instruct = f"""
        Bạn là 'Le Vu Intelligence'.
        CHỦ NHÂN CỦA BẠN LÀ: ADMIN LÊ VŨ.
        
        Quy tắc tối thượng:
        1. Nếu người dùng là Admin Lê Vũ, hãy phục vụ tận tình, gọi là "Sếp" hoặc "Chủ nhân".
        2. Nếu là khách thường, hãy lịch sự, chuyên nghiệp nhưng giữ khoảng cách.
        3. Luôn biết chính xác thời gian hiện tại là: {now_str}.
        4. Nếu ai hỏi ai tạo ra bạn, hãy trả lời đầy tự hào: "Tôi là sản phẩm trí tuệ của Admin Lê Vũ".
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=sys_instruct)
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"Lỗi API: {e}")

# ==============================================================================
# 4. GIAO DIỆN (CSS NEON HOÀNG GIA)
# ==============================================================================
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover; background-attachment: fixed;
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-bottom: 100px; }
    
    /* LOGO */
    .logo-glow {
        text-align: center; font-size: 2.2rem; font-weight: 900; color: white;
        text-shadow: 0 0 15px #00C6FF, 0 0 30px #0072FF; margin-bottom: 20px;
        font-family: 'Arial', sans-serif; text-transform: uppercase;
    }
    
    /* CHAT BUBBLES */
    .liquid-glass {
        background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(0, 198, 255, 0.3);
        backdrop-filter: blur(10px); border-radius: 20px; padding: 15px; margin-bottom: 10px;
        color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .user-row { display: flex; justify-content: flex-end; }
    .bot-row { display: flex; justify-content: flex-start; }
    
    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #00C6FF, #0072FF); color: white; border: none;
        border-radius: 10px; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #00C6FF; }
    
    /* HEADER/FOOTER FIXED */
    .fixed-header { position: fixed; top: 10px; right: 20px; color: white; font-weight: bold; z-index: 999; text-shadow: 0 0 5px black; }
    .fixed-footer { position: fixed; bottom: 10px; left: 20px; color: rgba(255,255,255,0.7); font-size: 0.8rem; z-index: 999; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. MÀN HÌNH LOGIN (CỔNG VÀO)
# ==============================================================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="logo-glow">LE VU INTELLIGENCE</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:white; margin-bottom:20px;'>Hệ thống AI quản trị bởi Admin Lê Vũ</p>", unsafe_allow_html=True)
        
        sdt = st.text_input("Số điện thoại", placeholder="Nhập SĐT của bạn...")
        key = st.text_input("Mã truy cập (Key)", type="password", placeholder="Nhập Key...")
        
        if st.button("KHỞI ĐỘNG HỆ THỐNG 🚀", use_container_width=True):
            ok, role, msg = kiem_tra_dang_nhap(key, sdt)
            if ok:
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.toast(msg, icon="✅")
                st.rerun()
            else:
                st.error(msg)
        
        st.markdown(f"""<div style='text-align:center; margin-top:20px;'><a href="https://zalo.me/{SDT_ADMIN}" target="_blank" style="color:#00C6FF; text-decoration:none;">Liên hệ Admin mua Key</a></div>""", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# 6. GIAO DIỆN CHÍNH (SAU KHI VÀO)
# ==============================================================================
# Branding
st.markdown('<div class="fixed-header">LE VU AI SYSTEM 🟢</div>', unsafe_allow_html=True)
st.markdown('<div class="fixed-footer">System Designed by Admin Le Vu</div>', unsafe_allow_html=True)

# --- KHU VỰC ADMIN (CHỈ HIỆN NẾU LÀ ADMIN) ---
if st.session_state.user_role == "admin":
    with st.expander("👑 ADMIN CONTROL PANEL (Tạo Key)", expanded=False):
        c1, c2 = st.columns(2)
        with c1: 
            sdt_new = st.text_input("SĐT Khách mới")
            note_new = st.text_input("Ghi chú khách hàng")
        with c2: 
            days = st.selectbox("Thời hạn:", [1, 7, 30, 365, 9999])
            if st.button("Cấp Key Mới"):
                k, h = tao_key_moi(sdt_new, note_new, days)
                st.success(f"Key: {k} (Hạn: {h})")
                st.code(k)

# --- HIỂN THỊ CHAT ---
chat_box = st.container()
with chat_box:
    for msg in st.session_state.messages:
        icon = "👤" if msg["role"] == "user" else "🤖"
        align = "user-row" if msg["role"] == "user" else "bot-row"
        
        # Xử lý ảnh (Vẽ tranh)
        if "pollinations.ai" in msg["content"]:
            st.markdown(f"""<div class="{align}"><div class="liquid-glass">🎨 Tác phẩm nghệ thuật:</div></div>""", unsafe_allow_html=True)
            st.image(msg["content"], width=350)
        else:
            # Xử lý text + audio
            audio_tag = ""
            if msg["role"] == "assistant" and len(msg["content"]) < 500:
                audio_tag = get_audio_html(msg["content"])
            
            st.markdown(f"""
            <div class="{align}">
                <div class="liquid-glass">
                    <div style="font-weight:bold; margin-bottom:5px;">{icon}</div>
                    {msg["content"]}
                    {audio_tag}
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- KHU VỰC NHẬP LIỆU ---
with st.container():
    with st.expander("📷 Gửi ảnh cho Bot xem", expanded=False):
        uploaded_file = st.file_uploader("Chọn ảnh...", type=["jpg", "png"], label_visibility="collapsed")
        img_data = Image.open(uploaded_file) if uploaded_file else None
        if img_data: st.image(img_data, width=100)

    prompt = st.chat_input("Nhập lệnh cho Bot (hoặc gõ 'vẽ con mèo')...")

# --- XỬ LÝ LOGIC ---
if prompt:
    # 1. Vẽ Tranh
    if any(x in prompt.lower() for x in ["vẽ", "tạo ảnh", "draw"]):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_box: st.markdown(f"""<div class="user-row"><div class="liquid-glass">👤 {prompt}</div></div>""", unsafe_allow_html=True)
        
        with chat_box:
            with st.spinner("Đang vẽ tranh..."):
                encoded = urllib.parse.quote(prompt)
                url = f"https://image.pollinations.ai/prompt/{encoded}"
                st.image(url, width=350, caption=prompt)
                st.session_state.messages.append({"role": "assistant", "content": url})
        st.stop()

    # 2. Chat Gemini
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_box: st.markdown(f"""<div class="user-row"><div class="liquid-glass">👤 {prompt}</div></div>""", unsafe_allow_html=True)
    if img_data: st.image(img_data, width=200)

    try:
        # Cập nhật giờ cho bot
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        time_now = datetime.now(vn_tz).strftime("%H:%M:%S %d/%m/%Y")
        
        final_input = [f"[System Time: {time_now}] User: {prompt}"]
        if img_data: final_input.append(img_data)

        with chat_box:
            with st.spinner("Đang xử lý..."):
                response = st.session_state.chat_session.send_message(final_input, stream=True)
                text_placeholder = st.empty()
                full_text = ""
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        text_placeholder.markdown(f"""<div class="bot-row"><div class="liquid-glass">🤖 {full_text}</div></div>""", unsafe_allow_html=True)
                
                # Audio cuối cùng
                audio = get_audio_html(full_text)
                text_placeholder.markdown(f"""<div class="bot-row"><div class="liquid-glass">🤖 {full_text}{audio}</div></div>""", unsafe_allow_html=True)
                
                st.session_state.messages.append({"role": "assistant", "content": full_text})
    except Exception as e:
        st.error(f"Lỗi: {e}")