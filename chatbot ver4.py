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

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Le Vu Intelligence",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. KHỞI TẠO BIẾN ---
TRIAL_LIMIT = 3
if "trial_count" not in st.session_state: st.session_state.trial_count = 0
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "extra_knowledge" not in st.session_state:
    st.session_state.extra_knowledge = [
        "Tôi là trí tuệ nhân tạo được phát triển bởi Admin Lê Vũ.",
        "Tên đầy đủ của người tạo ra tôi là Lê Văn Vũ, Admin đẹp trai nhất Thanh Hóa.",
        "SDT liên hệ Admin: 0376274345."
    ]

# --- 3. CẤU HÌNH ADMIN ---
FILE_DATA = "key_data.json"
SDT_ADMIN = "0376274345"
ADMIN_PASSWORD = "levudepzai"

# --- 4. ĐỊNH NGHĨA HÀM ---
def load_data():
    if not os.path.exists(FILE_DATA):
        with open(FILE_DATA, 'w', encoding='utf-8') as f: json.dump({}, f)
        return {}
    try:
        with open(FILE_DATA, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_data(data):
    with open(FILE_DATA, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

def kiem_tra_sdt_vietnam(sdt):
    return bool(re.fullmatch(r'0\d{9}', sdt))

def tao_key_moi(sdt_khach, ghi_chu, so_ngay_dung):
    data = load_data()
    phan_duoi = secrets.token_hex(4).upper()
    new_key = f"KEY-{phan_duoi[:4]}-{phan_duoi[4:]}"
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    ngay_hien_tai = datetime.now(vietnam_tz)
    ngay_het_han = ngay_hien_tai + timedelta(days=so_ngay_dung)
    data[new_key] = {
        "status": "active", "sdt": sdt_khach, 
        "created_at": ngay_hien_tai.strftime("%d/%m/%Y %H:%M"),
        "expiry_date": ngay_het_han.strftime("%d/%m/%Y %H:%M"), "note": ghi_chu
    }
    save_data(data)
    return new_key, ngay_het_han.strftime("%d/%m/%Y")

def khoa_sdt_trial(sdt_input):
    data = load_data()
    for key, info in data.items():
        if info.get("sdt") == sdt_input: return True, "🔑 SĐT này đã mua Key, vui lòng đăng nhập!"
    if "TRIAL_LOCK" not in data: data["TRIAL_LOCK"] = {}
    if sdt_input in data["TRIAL_LOCK"]: return True, "❌ Hết lượt dùng thử! Vui lòng mua Key."
    data["TRIAL_LOCK"][sdt_input] = True
    save_data(data)
    return False, None

def kiem_tra_dang_nhap(input_key, input_sdt):
    if input_key == ADMIN_PASSWORD and input_sdt == SDT_ADMIN: return True, "admin", "Chào Sếp Vũ!"
    data = load_data()
    if input_key in data:
        thong_tin = data[input_key]
        if thong_tin.get("sdt") != input_sdt: return False, None, f"❌ Sai SĐT đăng ký!"
        han_su_dung_str = thong_tin.get("expiry_date")
        if han_su_dung_str:
            vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            try:
                han_su_dung = datetime.strptime(han_su_dung_str, "%d/%m/%Y %H:%M").replace(tzinfo=vietnam_tz)
            except:
                han_su_dung = datetime.strptime(han_su_dung_str, "%Y-%m-%d %H:%M").replace(tzinfo=vietnam_tz)
            if datetime.now(vietnam_tz) > han_su_dung: return False, None, f"⚠️ Key đã HẾT HẠN!"
        return True, "user", f"Xin chào {input_sdt}!"
    return False, None, f"❌ Key không tồn tại!"

def get_audio_html(text, lang='vi'):
    """Chuyển text thành giọng nói (Bot Voice)"""
    if not text or len(text.strip()) == 0: return ""
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        # Thanh audio nhỏ gọn cho bot
        return f"""<audio controls class="stAudio" src="data:audio/mp3;base64,{b64}" style="width: 100%; height: 30px; margin-top: 5px; opacity: 0.8;"></audio>"""
    except: return ""

# --- 5. KHỞI TẠO MODEL GEMINI ---
if "chat_session" not in st.session_state:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        base_instruction = """
        Bạn là Lê Vũ Intelligence. Trợ lý AI của Admin Lê Vũ.
        Phong cách: Ngầu, súc tích, hữu ích. Luôn trả lời bằng tiếng Việt.
        """
        # SỬ DỤNG TÊN CHUẨN (KHÔNG CÓ 'models/') ĐỂ TRÁNH LỖI 404
        model = genai.GenerativeModel(
            'gemini-1.5-flash', 
            system_instruction=base_instruction
        )
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"Lỗi API: {e}")

# --- 6. CSS GIAO DIỆN ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4); z-index: -1; pointer-events: none;
    }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* NEON BORDER */
    body::before, body::after {
        content: ""; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 9999; pointer-events: none;
        padding: 2px; background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
    }
    body::after { filter: blur(20px); opacity: 0.7; z-index: 9998; }
    @property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
    @keyframes spin { to { --angle: 360deg; } }

    /* CHAT BUBBLE */
    .liquid-glass {
        position: relative; background: rgba(255, 255, 255, 0.01); 
        backdrop-filter: blur(2px); border-radius: 35px; padding: 12px 25px; margin-bottom: 15px; 
        color: white; font-weight: 500; border: 1px solid rgba(255,255,255,0.05); width: fit-content; max-width: 85%;
    }
    .user-row { display: flex; justify-content: flex-end; }
    .bot-row { display: flex; justify-content: flex-start; }
    
    /* LOGO & FOOTER */
    .logo-glow {
        text-align: center; font-size: 2.5rem; font-weight: 800; color: white;
        text-shadow: 0 0 12px rgba(65, 105, 225, 1), 0 0 20px rgba(65, 105, 225, 1);
        margin-bottom: 30px;
    }
    .header-logo-fixed { position: fixed; top: 20px; right: 40px; z-index: 1000; font-size: 1.5rem; }
    .footer-text-fixed { position: fixed; bottom: 15px; left: 20px; z-index: 1000; font-size: 0.8rem; color: white; opacity: 0.9; }
    
    [data-testid="stAlert"] { background-color: rgba(0, 0, 0, 0.5) !important; border: 1px solid #00C6FF !important; color: white !important; }
    .block-container { padding-bottom: 100px !important; }
</style>
""", unsafe_allow_html=True)

# --- 7. MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class="logo-glow">LE VU INTELLIGENCE</div>""", unsafe_allow_html=True)
        input_sdt = st.text_input("Số điện thoại:", placeholder="Nhập SĐT...")
        input_key = st.text_input("Mã Key:", type="password", placeholder="Nhập Key...", label_visibility="visible")
        
        if st.button("ĐĂNG NHẬP 🚀", use_container_width=True):
            success, role, msg = kiem_tra_dang_nhap(input_key, input_sdt)
            if success:
                st.session_state.logged_in = True; st.session_state.user_role = role; st.success(msg); st.rerun()
            else: st.error(msg)
            
        if st.button(f"DÙNG THỬ ({TRIAL_LIMIT} câu)", use_container_width=True):
            if not input_sdt or not kiem_tra_sdt_vietnam(input_sdt): st.error("⚠️ SĐT không hợp lệ (10 số)"); st.stop()
            is_locked, lock_msg = khoa_sdt_trial(input_sdt)
            if is_locked: st.error(lock_msg); st.stop()
            st.session_state.logged_in = True; st.session_state.user_role = 'trial'; st.session_state.trial_count = 0; st.success("Chào mừng!"); st.rerun()
            
        if st.button(f"MUA KEY / LH ZALO", use_container_width=True):
             st.markdown(f"""<a href="https://zalo.me/{SDT_ADMIN}" target="_blank"><button style="width:100%; background:#0088ff; color:white; border:none; padding:10px; border-radius:5px;">CHAT ZALO ADMIN</button></a>""", unsafe_allow_html=True)
    st.stop()

# --- 8. GIAO DIỆN CHÍNH ---
if st.session_state.logged_in:
    st.markdown(f"""<div class="logo-glow header-logo-fixed">Le Vu Intelligence</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="footer-text-fixed">Designed by Le Van Vu</div>""", unsafe_allow_html=True)

    # Panel Admin
    if st.session_state.get("user_role") == "admin":
        with st.expander("🛠️ ADMIN PANEL", expanded=False):
            c1, c2 = st.columns(2)
            with c1: sdt_in = st.text_input("SĐT Khách"); note_in = st.text_input("Ghi chú")
            with c2: 
                days = st.selectbox("Hạn dùng:", [1, 7, 30, 365, 3650])
                if st.button("Tạo Key"): 
                    if sdt_in: k, h = tao_key_moi(sdt_in, note_in, days); st.success(f"OK! Hạn: {h}"); st.code(k)

    # Hiển thị Chat
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            role = message["role"]
            css = "user-row" if role == "user" else "bot-row"
            icon = "⭐" if role == "user" else "🤖"
            
            if isinstance(message["content"], str) and "pollinations.ai" in message["content"]:
                 st.markdown(f"""<div class="{css}"><div class="liquid-glass">🖼️ Ảnh em vẽ nè:</div></div>""", unsafe_allow_html=True)
                 st.image(message["content"], width=400)
            else:
                audio = ""
                if role == "assistant" and len(message["content"]) < 500: audio = get_audio_html(message["content"])
                st.markdown(f"""<div class="{css}"><div class="liquid-glass"><span class='icon'>{icon}</span> {message["content"]}</div>{audio}</div>""", unsafe_allow_html=True)

    # INPUT: CHỈ CÒN TẢI ẢNH & CHAT TEXT (ĐÃ BỎ MIC)
    with st.container():
        with st.expander("📸 Tải ảnh", expanded=False):
            uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg","png"], label_visibility="collapsed")
            img_send = Image.open(uploaded_file) if uploaded_file else None
            if img_send: st.image(img_send, width=100)

        # Input text bình thường
        user_input = st.chat_input("Nhập tin nhắn của bạn...")

    # Xử lý Logic
    if user_input:
        if st.session_state.get('user_role') == 'trial':
            if st.session_state.trial_count >= TRIAL_LIMIT: 
                st.error("Hết lượt dùng thử!"); st.session_state.logged_in = False; st.rerun()
            st.session_state.trial_count += 1

        # Vẽ tranh
        if any(x in user_input.lower() for x in ["vẽ", "tạo ảnh", "draw"]):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with chat_container: st.markdown(f"""<div class="user-row"><div class="liquid-glass">{user_input}</div></div>""", unsafe_allow_html=True)
            with chat_container:
                with st.spinner("Đang vẽ..."):
                    prompt = urllib.parse.quote(user_input)
                    url = f"https://image.pollinations.ai/prompt/{prompt}"
                    st.image(url, width=400)
                    st.session_state.messages.append({"role": "assistant", "content": url})
            st.stop()

        # Chat với Gemini
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container: st.markdown(f"""<div class="user-row"><div class="liquid-glass">{user_input}</div></div>""", unsafe_allow_html=True)
        if img_send: st.image(img_send, width=200)

        try:
            # Logic thời gian thực
            vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            now_str = datetime.now(vn_tz).strftime("%H:%M:%S ngày %d/%m/%Y")
            
            final_prompt = f"[{now_str}] Khách hỏi: {user_input}"
            if st.session_state.extra_knowledge:
                final_prompt = f"Kiến thức bổ sung:\n" + "\n".join(st.session_state.extra_knowledge) + "\n\n" + final_prompt

            inputs = [final_prompt]
            if img_send: inputs.append(img_send)

            with chat_container:
                with st.spinner("Thinking..."):
                    response = st.session_state.chat_session.send_message(inputs, stream=True)
                    placeholder = st.empty()
                    full_resp = ""
                    for chunk in response:
                        if chunk.text:
                            full_resp += chunk.text
                            placeholder.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class='icon'>🤖</span> {full_resp}</div></div>""", unsafe_allow_html=True)
                    
                    # Vẫn giữ Bot biết nói (TTS)
                    audio = get_audio_html(full_resp)
                    placeholder.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class='icon'>🤖</span> {full_resp}</div>{audio}</div>""", unsafe_allow_html=True)
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_resp})
        except Exception as e: st.error(f"Lỗi: {e}")