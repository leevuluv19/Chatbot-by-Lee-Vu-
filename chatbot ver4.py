import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (LIQUID GLASS + NEON + THANH CÔNG CỤ GỌN) ---
st.markdown("""
<style>
    /* --- NỀN FULL MÀN HÌNH --- */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.3); z-index: -1; pointer-events: none;
    }

    /* --- ẨN GIAO DIỆN THỪA --- */
    #MainMenu, footer {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- ANIMATION VIỀN CHẠY --- */
    @property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
    @keyframes rainbow-spin { to { --angle: 360deg; } }

    /* --- STYLE KHUNG CHAT (LIQUID GLASS) --- */
    .liquid-glass {
        position: relative; background: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border-radius: 35px; padding: 12px 20px; color: #ffffff; font-weight: 500;
        display: flex; align-items: center; z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: fit-content; max-width: 85%;
        overflow: visible !important;
    }
    .liquid-glass::before {
        content: ""; position: absolute; inset: 0; border-radius: 35px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude; pointer-events: none; z-index: -1; filter: blur(2px);
    }
    .liquid-glass::after {
        content: ""; position: absolute; inset: -2px; border-radius: 35px; z-index: -2;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite; filter: blur(10px); opacity: 0.6;
    }
    .icon { margin-right: 12px; font-size: 1.6rem; }
    .user-row { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 15px; }
    .bot-row { display: flex; justify-content: flex-start; width: 100%; margin-bottom: 15px; }

    /* --- KHU VỰC NHẬP LIỆU & CÔNG CỤ (GIỐNG ẢNH 2 NHƯNG STYLE NEON) --- */
    
    /* Đẩy nội dung lên để không bị che */
    .block-container { padding-bottom: 150px !important; }

    /* Style cho Expander (Nút mở rộng upload) */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        font-size: 14px !important;
    }
    
    /* Khung upload bên trong */
    [data-testid="stFileUploader"] {
        padding: 10px;
        background: rgba(0,0,0,0.3);
        border-radius: 10px;
    }
    [data-testid="stFileUploader"] button {
        width: 100%;
    }

    /* Thanh Chat Input */
    .stChatInputContainer {
        padding-bottom: 30px;
    }
    .stChatInputContainer > div {
        border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important; padding-left: 15px !important;
    }

    /* TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 20px; margin-top: -30px; }
    .main-title { font-size: 2.2rem; font-weight: 800; color: white; text-shadow: 0 0 15px rgba(255,255,255,0.4); }
    .sub-title { font-size: 0.9rem; color: rgba(255,255,255,0.8); }
</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN TIÊU ĐỀ ---
st.markdown("""
    <div class="title-container">
        <div class="main-title">😎 Lê Vũ Depzai</div>
        <div class="sub-title">Trò chuyện & Phân tích ảnh</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. CẤU HÌNH API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa có chìa khóa!")
    st.stop()

# --- 5. BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. LỊCH SỬ CHAT ---
# Tạo container riêng cho lịch sử chat
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔴</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)

# --- 7. KHU VỰC NHẬP LIỆU & CÔNG CỤ (CỐ ĐỊNH Ở ĐÁY) ---
# Tạo container cố định ở dưới cùng
with st.container():
    # Thanh công cụ upload (dùng expander để thu gọn giống ảnh 2)
    with st.expander("📸 Tải ảnh lên (Nếu cần)"):
        uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        image_to_send = None
        if uploaded_file:
            image_to_send = Image.open(uploaded_file)
            st.image(image_to_send, width=150, caption="Ảnh đã chọn")

    # Thanh Chat Input (Nằm ngay dưới expander)
    user_input = st.chat_input("Nhập tin nhắn của bạn...")

# --- 8. XỬ LÝ LOGIC ---
if user_input: # Chỉ gửi khi bấm Enter ở thanh chat
    
    display_text = user_input
    if image_to_send:
        display_text = f"[Đã gửi một hình ảnh] <br> {user_input}"

    # Hiện User (vào container lịch sử)
    with chat_container:
        st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔴</span> <div>{display_text}</div></div></div>""", unsafe_allow_html=True)
        if image_to_send:
            with st.chat_message("user", avatar=None):
                st.image(image_to_send, width=250)
    
    st.session_state.messages.append({"role": "user", "content": display_text})

    # Gửi Gemini
    try:
        inputs = [user_input]
        if image_to_send:
            inputs.append(image_to_send)

        with st.spinner("..."):
            response = st.session_state.chat_session.send_message(inputs)
            bot_reply = response.text
        
        # Hiện Bot
        with chat_history_container:
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{bot_reply}</div></div></div>""", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")