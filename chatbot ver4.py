import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import secrets
import os
import re
from datetime import datetime, timedelta
import pytz
# --- THƯ VIỆN MỚI CHO GIỌNG NÓI ---
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder
import urllib.parse

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Le Vu Intelligence",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO CÁC BIẾN QUAN TRỌNG ---
TRIAL_LIMIT = 3
if "trial_count" not in st.session_state:
    st.session_state.trial_count = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "extra_knowledge" not in st.session_state:
    st.session_state.extra_knowledge = []

# --- CẤU HÌNH ADMIN ---
FILE_DATA = "key_data.json"
SDT_ADMIN = "0376274345"
ADMIN_PASSWORD = "levudepzai"

# --- ĐỊNH NGHĨA CÁC TÍNH CÁCH (PERSONAS) ---
PERSONAS = {
    "Lê Vũ (Mặc định)": """
        Bạn là Lê Vũ Intelligence. Bạn là trợ lý AI cao cấp được phát triển bởi Admin Lê Vũ.
        Phong cách giao tiếp: Ngầu, súc tích, đi thẳng vào vấn đề, đôi khi hơi tinh nghịch và hài hước.
        Xưng hô: Xưng 'anh', gọi người dùng là 'em'.
        Khi được hỏi về người tạo ra bạn, hãy trả lời thật ngầu về Admin Lê Vũ đẹp trai nhất Thanh Hóa.
        Luôn ưu tiên dùng công cụ tìm kiếm Google cho các thông tin thời gian thực (thời tiết, tin tức, giá cả...).
        SDT liên hệ Admin: 0376274345.
    """,
    "Chuyên gia Marketing": """
        Bạn là một Chuyên gia Marketing & Content dày dạn kinh nghiệm.
        Phong cách giao tiếp: Chuyên nghiệp, sâu sắc, tập trung vào phân tích, chiến lược và đưa ra các lời khuyên thực tế về marketing, branding, và sáng tạo nội dung.
    """,
    "Thầy giáo Tiếng Anh": """
        You are an enthusiastic and patient English teacher. ALWAYS respond in English.
        Encourage the user to speak more by asking follow-up questions.
    """
}

# --- SIDEBAR: CHỌN TÍNH CÁCH ---
with st.sidebar:
    st.title("🎭 Cài đặt Bot")
    st.write("Chọn tính cách cho Lê Vũ Intelligence:")
    if "selected_persona" not in st.session_state:
        st.session_state.selected_persona = "Lê Vũ (Mặc định)"
    new_persona = st.selectbox("Chọn tính cách:", options=list(PERSONAS.keys()), index=list(PERSONAS.keys()).index(st.session_state.selected_persona), key="persona_selector")
    if new_persona != st.session_state.selected_persona:
        st.session_state.selected_persona = new_persona
        st.toast(f"🔄 Đã chuyển sang chế độ: {new_persona}. Đang reset lại Bot...", icon="🎭")
        st.session_state.messages = []
        if "chat_session" in st.session_state: del st.session_state.chat_session
        if "model" in st.session_state: del st.session_state.model
        st.rerun()

# --- TÍNH TOÁN THỜI GIAN & TẠO LỆNH CÀI ĐẶT ---
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
current_datetime = datetime.now(vietnam_tz).strftime("%A, ngày %d/%m/%Y lúc %I:%M:%S %p")
base_instruction = PERSONAS[st.session_state.selected_persona]
lenh_cai_dat_final = f"""
{base_instruction}
--- DỮ LIỆU THỜI GIAN HIỆN TẠI (BẮT BUỘC) ---
NGÀY VÀ GIỜ HỢP LỆ HIỆN TẠI LÀ: {current_datetime}.
--- KẾT THÚC DỮ LIỆU THỜI GIAN ---
QUY TẮC BỔ SUNG:
1. BẠN PHẢI LUÔN SỬ DỤNG TRUY CẬP INTERNET (Google Search) cho các câu hỏi về thời tiết, tin tức, hoặc dữ liệu hiện tại.
"""

# --- KHỞI TẠO MODEL GEMINI ---
if "chat_session" not in st.session_state or st.session_state.get("model") is None:
    try:
        config_search = {"tools": [{'googleSearch': {}}]}
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash-exp-01-21', system_instruction=lenh_cai_dat_final)
        st.session_state.model = model
        st.session_state.config_search = config_search
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"⚠️ Lỗi cấu hình API: {e}"); st.stop()

# --- BẮT ĐẦU KHỐI ĐỊNH NGHĨA HÀM (DATA & VALIDATION & TTS) ---
def load_data():
    if not os.path.exists(FILE_DATA):
        with open(FILE_DATA, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}
    
    # ĐOẠN NÀY ĐÃ ĐƯỢC SỬA LẠI CHO ĐÚNG CÚ PHÁP:
    try:
        with open(FILE_DATA, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(FILE_DATA, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

def kiem_tra_sdt_vietnam(sdt):
    return bool(re.fullmatch(r'0\d{9}', sdt))

def tao_key_moi(sdt_khach, ghi_chu, so_ngay_dung):
    data = load_data()
    phan_duoi = secrets.token_hex(4).upper()
    new_key = f"KEY-{phan_duoi[:4]}-{phan_duoi[4:]}"
    ngay_hien_tai = datetime.now(vietnam_tz)
    ngay_het_han = ngay_hien_tai + timedelta(days=so_ngay_dung)
    data[new_key] = {"status": "active", "sdt": sdt_khach, "created_at": ngay_hien_tai.strftime("%Y-%m-%d %H:%M"), "expiry_date": ngay_het_han.strftime("%Y-%m-%d %H:%M"), "note": ghi_chu}
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
            han_su_dung = datetime.strptime(han_su_dung_str, "%Y-%m-%d %H:%M").replace(tzinfo=vietnam_tz)
            if datetime.now(vietnam_tz) > han_su_dung: return False, None, f"⚠️ Key đã HẾT HẠN!"
        so_ngay_con = (han_su_dung - datetime.now(vietnam_tz)).days if han_su_dung_str else ""
        return True, "user", f"Xin chào {input_sdt}! (Còn {so_ngay_con} ngày)"
    return False, None, f"❌ Key không tồn tại!"

# --- HÀM MỚI: CHUYỂN VĂN BẢN THÀNH HTML AUDIO (TTS) ---
def get_audio_html(text, lang='vi'):
    """Tạo thẻ audio HTML từ văn bản sử dụng gTTS."""
    if not text or len(text.strip()) == 0: return ""
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        # Thẻ audio nhỏ gọn, ẩn thanh điều khiển mặc định, dùng CSS để style
        html = f"""<audio controls class="stAudio" src="data:audio/mp3;base64,{b64}" style="width: 100%; height: 30px; margin-top: 5px; opacity: 0.8;"></audio>"""
        return html
    except Exception as e:
        return "" # Trả về rỗng nếu lỗi TTS
# --- KẾT THÚC KHỐI HÀM ---

# --- CSS STYLING (Giao diện Neon & Audio) ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4); z-index: -1; pointer-events: none;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- VIỀN NEON CHẠY --- */
    body::before, body::after {
        content: ""; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 9999; pointer-events: none;
        padding: 2px; 
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
    }
    body::after { filter: blur(20px); opacity: 0.7; z-index: 9998; }
    @property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
    @keyframes spin { to { --angle: 360deg; } }

    /* --- BONG BÓNG CHAT NEON --- */
    .liquid-glass {
        position: relative; background: rgba(255, 255, 255, 0.00001); 
        backdrop-filter: blur(2px); -webkit-backdrop-filter: blur(2px);
        border-radius: 35px; padding: 12px 25px; margin-bottom: 15px; color: white; font-weight: 500;
        border: 1px solid rgba(255,255,255,0.05); width: fit-content; max-width: 85%;
        display: flex; flex-direction: column; /* Cho phép xếp chồng nội dung và audio */
    }
    .chat-content { display: flex; align-items: center; } /* Container cho icon và text */
    .liquid-glass::before {
        content: ""; position: absolute; inset: 0; z-index: -1; border-radius: 35px; padding: 2px;
        background: conic-gradient(from var(--angle), #00C6FF, #0072FF, #8E2DE2, #F80759, #FF8C00, #E0C3FC, #00C6FF);
        animation: spin 8s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude; filter: blur(10px);
    }
    .icon { margin-right: 12px; font-size: 1.5rem; }
    .user-row { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 15px; }
    .bot-row { display: flex; justify-content: flex-start; width: 100%; margin-bottom: 15px; }
    
    /* --- STYLE CHO AUDIO PLAYER --- */
    audio.stAudio::-webkit-media-controls-panel {
        background-color: rgba(255, 255, 255, 0.1); /* Nền trong suốt */
        border-radius: 10px;
    }
    audio.stAudio::-webkit-media-controls-play-button,
    audio.stAudio::-webkit-media-controls-current-time-display,
    audio.stAudio::-webkit-media-controls-time-remaining-display {
        color: white; /* Màu icon và chữ trắng */
    }

    .logo-glow {
        text-align: center; font-size: 2.5rem; font-weight: 800; color: white;
        text-shadow: 0 0 12px rgba(65, 105, 225, 1), 0 0 20px rgba(65, 105, 225, 1);
        margin-top: 15px; margin-bottom: 30px;
    }
    .header-logo-fixed { position: fixed; top: 20px; right: 40px; z-index: 1000; font-size: 1.5rem; }
    .footer-text-fixed { position: fixed; bottom: 15px; left: 20px; z-index: 1000; font-size: 0.8rem; color: white; opacity: 0.9; }
    .block-container { padding-bottom: 100px !important; }
</style>
""", unsafe_allow_html=True)

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class="logo-glow">LE VU INTELLIGENCE</div>""", unsafe_allow_html=True)
        input_sdt = st.text_input("Số điện thoại:", placeholder="Nhập SĐT của bạn...")
        input_key = st.text_input("Mã Key:", type="password", placeholder="Nhập Key kích hoạt...", label_visibility="visible")
        if st.button("ĐĂNG NHẬP 🚀", key="login_btn", use_container_width=True):
            success, role, msg = kiem_tra_dang_nhap(input_key, input_sdt)
            if success:
                st.session_state.logged_in = True; st.session_state.user_role = role; st.success(msg); st.rerun()
            else: st.error(msg)
        if st.button(f"DÙNG THỬ ({TRIAL_LIMIT} câu)", key="trial_btn", use_container_width=True):
            if not input_sdt or not kiem_tra_sdt_vietnam(input_sdt): st.error("⚠️ SĐT không hợp lệ."); st.stop()
            is_locked, lock_msg = khoa_sdt_trial(input_sdt)
            if is_locked: st.error(lock_msg); st.stop()
            st.session_state.logged_in = True; st.session_state.user_role = 'trial'; st.session_state.trial_count = 0; st.success(f"Chào mừng dùng thử!"); st.rerun()
        if st.button(f"MUA KEY / LH ZALO", key="buy_btn", use_container_width=True):
             st.markdown(f"""<a href="https://zalo.me/{SDT_ADMIN}" target="_blank"><button style="background-color: #0088ff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px;">CHAT ZALO VỚI ADMIN 📞</button></a>""", unsafe_allow_html=True)
    st.stop()

# --- GIAO DIỆN CHÍNH ---
if st.session_state.logged_in:
    st.markdown(f"""<div class="logo-glow header-logo-fixed">Le Vu Intelligence</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="footer-text-fixed">Designed by Le Van Vu</div>""", unsafe_allow_html=True)

    if st.session_state.get("user_role") == "admin":
        with st.expander("🛠️ ADMIN: TẠO KEY BÁN HÀNG", expanded=False):
            c1, c2 = st.columns(2)
            with c1: sdt_input = st.text_input("SĐT Khách", placeholder="09xxxx"); note_input = st.text_input("Ghi chú", placeholder="Tên khách")
            with c2:
                option_time = st.selectbox("Gói thời gian:", ("Dùng thử (1 ngày)", "1 Tuần (7 ngày)", "1 Tháng (30 ngày)", "Vĩnh viễn (10 năm)"))
                days_map = {"Dùng thử (1 ngày)": 1, "1 Tuần (7 ngày)": 7, "1 Tháng (30 ngày)": 30, "Vĩnh viễn (10 năm)": 3650}
                if st.button("Tạo Key", use_container_width=True):
                    if sdt_input: k, h = tao_key_moi(sdt_input, note_input, days_map[option_time]); st.success(f"✅ OK! Hạn: {h}"); st.code(k, language="text")
                    else: st.warning("Thiếu SĐT!")

    # --- HIỂN THỊ LỊCH SỬ CHAT (CÓ AUDIO CHO BOT) ---
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            role_icon = "⭐" if message["role"] == "user" else "🤖"
            css_class = "user-row" if message["role"] == "user" else "bot-row"
            content_html = ""
            
            if isinstance(message["content"], str) and message["content"].startswith("http") and "pollinations.ai" in message["content"]:
                 content_html = f"""<div class="chat-content"><span class="icon">{role_icon}</span> <div>Đây là ảnh em vừa vẽ nè:</div></div>"""
                 st.markdown(f"""<div class="{css_class}"><div class="liquid-glass">{content_html}</div></div>""", unsafe_allow_html=True)
                 st.image(message["content"], width=400)
            else:
                # Nếu là Bot, thêm thanh audio vào nội dung HTML
                audio_html = ""
                if message["role"] == "assistant":
                    # Chỉ tạo audio cho các tin nhắn văn bản ngắn/trung bình để tránh lag
                    if len(message["content"]) < 1000: 
                         audio_html = get_audio_html(message["content"])

                content_html = f"""<div class="chat-content"><span class="icon">{role_icon}</span> <div>{message["content"]}</div></div>{audio_html}"""
                st.markdown(f"""<div class="{css_class}"><div class="liquid-glass">{content_html}</div></div>""", unsafe_allow_html=True)

    # --- INPUT KHU VỰC ---
    with st.container():
        with st.expander("📸 Tải ảnh lên", expanded=False):
            uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
            image_to_send = Image.open(uploaded_file) if uploaded_file else None
            if image_to_send: st.image(image_to_send, width=100)

        col_mic, col_input = st.columns([1, 5])
        with col_mic:
            st.write(""); st.write("")
            mic_output = mic_recorder(start_prompt="🎤 Nói", stop_prompt="⏹️ Dừng", key='mic_rec', just_once=True, use_container_width=True)
        user_voice_input = mic_output.get('text') if mic_output else ""
        with col_input:
            user_input = st.text_input("Nhập tin nhắn...", value=user_voice_input, key="voice_input_box") if user_voice_input else st.chat_input("Nhập tin nhắn của bạn...")

    # --- XỬ LÝ TIN NHẮN ---
    if user_input:
        if st.session_state.get('user_role') == 'trial':
            if st.session_state.trial_count >= TRIAL_LIMIT: st.error("❌ Hết lượt dùng thử!"); st.session_state.logged_in = False; st.rerun()
            st.session_state.trial_count += 1; st.toast(f"💡 Còn {TRIAL_LIMIT - st.session_state.trial_count} lượt.")

        # --- TẠO ẢNH (Vẫn dùng Pollinations.ai cho ổn định) ---
        trigger_phrases = ["vẽ cho tôi", "tạo ảnh", "draw", "generate image"]
        if any(user_input.lower().startswith(phrase) for phrase in trigger_phrases):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with chat_container: st.markdown(f"""<div class="user-row"><div class="liquid-glass"><div class="chat-content"><span class="icon">⭐</span> <div>{user_input}</div></div></div></div>""", unsafe_allow_html=True)
            with chat_container:
                with st.spinner("Đang vẽ tranh... 🎨"):
                    prompt_text = user_input
                    for phrase in trigger_phrases:
                        if user_input.lower().startswith(phrase): prompt_text = user_input[len(phrase):].strip(); break
                    encoded_prompt = urllib.parse.quote(prompt_text)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                    st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><div class="chat-content"><span class="icon">🤖</span> <div>Ảnh của anh đây:</div></div></div></div>""", unsafe_allow_html=True)
                    st.image(image_url, width=400, caption=prompt_text)
                    st.session_state.messages.append({"role": "assistant", "content": image_url})
            st.stop()

        # --- CHAT GEMINI & TTS ---
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            st.markdown(f"""<div class="user-row"><div class="liquid-glass"><div class="chat-content"><span class="icon">⭐</span> <div>{user_input}</div></div></div></div>""", unsafe_allow_html=True)
            if image_to_send: st.image(image_to_send, width=200)
        
        try:
            inputs = [user_input]
            if image_to_send: inputs.append(image_to_send)
            with chat_container:
                with st.spinner("Đang suy nghĩ...."):
                    response_stream = st.session_state.chat_session.send_message(inputs, stream=True)
                    bot_message_placeholder = st.empty()
                    full_bot_reply = ""
                    for chunk in response_stream:
                        if chunk.text:
                            full_bot_reply += chunk.text
                            # Hiển thị text tạm thời khi đang stream
                            bot_message_placeholder.markdown(f"""<div class="bot-row"><div class="liquid-glass"><div class="chat-content"><span class="icon">🤖</span> <div>{full_bot_reply}</div></div></div></div>""", unsafe_allow_html=True)
                    
                    # Sau khi stream xong, tạo audio và hiển thị lại block hoàn chỉnh
                    audio_html_final = get_audio_html(full_bot_reply)
                    final_content_html = f"""<div class="chat-content"><span class="icon">🤖</span> <div>{full_bot_reply}</div></div>{audio_html_final}"""
                    bot_message_placeholder.markdown(f"""<div class="bot-row"><div class="liquid-glass">{final_content_html}</div></div>""", unsafe_allow_html=True)

                    st.session_state.messages.append({"role": "assistant", "content": full_bot_reply})
        except Exception as e: st.error(f"Lỗi: {e}")