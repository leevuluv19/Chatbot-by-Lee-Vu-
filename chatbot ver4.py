import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP ---
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
        background: rgba(0, 0, 0, 0.4); z-index: -1; pointer-events: none;
    }

    /* --- CẤU HÌNH CHUNG --- */
    #MainMenu, footer {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}
    
    /* Animation xoay cho Bot */
    @property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
    @keyframes rainbow-spin { to { --angle: 360deg; } }

    /* --- STYLE KHUNG CHAT CƠ BẢN (BOT DÙNG CÁI NÀY) --- */
    .liquid-glass {
        position: relative;
        background: rgba(0, 0, 0, 0.3); /* Nền tối cho Bot */
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 12px 20px;
        color: #ffffff; font-weight: 500;
        display: flex; align-items: center; z-index: 1;
        width: fit-content; max-width: 85%;
        overflow: visible !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* VIỀN CẦU VỒNG CHẠY (Mặc định cho Bot) */
    .liquid-glass::before {
        content: ""; position: absolute; inset: 0; border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude; pointer-events: none; z-index: -1;
    }
    /* GLOW CẦU VỒNG */
    .liquid-glass::after {
        content: ""; position: absolute; inset: -3px; border-radius: 30px; z-index: -2;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite; filter: blur(15px); opacity: 0.5;
    }

    /* ================================================================= */
    /* === ĐÂY LÀ ĐOẠN SẾP CẦN: MÀU NHẸ NHÀNG CHO BÊN PHẢI (USER) === */
    /* ================================================================= */
    
    /* 1. Đổi màu nền bên trong nhẹ hơn */
    .user-row .liquid-glass {
        background: rgba(0, 100, 255, 0.15) !important; /* Xanh dương nhạt trong suốt */
        border: 1px solid rgba(137, 247, 254, 0.3) !important;
    }

    /* 2. Đổi màu viền (Không xoay nữa, dùng Gradient tĩnh nhẹ nhàng) */
    .user-row .liquid-glass::before {
        background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%) !important;
        animation: none !important; /* Tắt xoay cho đỡ chóng mặt */
        padding: 1.5px !important; /* Viền mỏng hơn chút */
    }

    /* 3. Đổi màu Glow (Tỏa sáng nhẹ màu xanh) */
    .user-row .liquid-glass::after {
        background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%) !important;
        animation: none !important;
        filter: blur(10px) !important;
        opacity: 0.4 !important; /* Glow nhẹ hơn */
    }
    /* ================================================================= */

    .icon { margin-right: 12px; font-size: 1.5rem; }
    .user-row { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 15px; }
    .bot-row { display: flex; justify-content: flex-start; width: 100%; margin-bottom: 15px; }

    /* --- STYLE KHUNG CÔNG CỤ & INPUT --- */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.1) !important; border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.2) !important; color: white !important; font-weight: 500 !important;
    }
    [data-testid="stExpander"] { border: none !important; box-shadow: none !important; margin-bottom: 10px; }
    [data-testid="stExpander"] .streamlit-expanderContent {
        background-color: rgba(0,0,0,0.3) !important; border-radius: 0 0 15px 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important; border-top: none !important;
    }
    
    .stChatInputContainer { padding-bottom: 30px; }
    .stChatInputContainer > div {
        border-radius: 30px; padding: 2px;
        /* Thanh nhập liệu vẫn giữ màu cầu vồng cho đẹp */
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important; background: rgba(0, 0, 0, 0.7) !important;
        color: white !important; border: none !important; padding-left: 15px !important;
    }
    .block-container { padding-bottom: 100px !important; }
    
    /* Tiêu đề */
    .title-container { text-align: center; margin-bottom: 20px; margin-top: -20px; }
    .main-title { font-size: 2.5rem; font-weight: 800; color: white; text-shadow: 0 0 15px rgba(255,255,255,0.4); }
    .sub-title { font-size: 1rem; color: rgba(255,255,255,0.8); letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- 3. TIÊU ĐỀ ---
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
    st.error("⚠️ Chưa có chìa khóa! Vào Settings -> Secrets để điền API Key.")
    st.stop()

# --- 5. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. LỊCH SỬ CHAT ---
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            # User: Dùng icon Xanh cho hợp màu mới
            st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔵</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)
        else:
            # Bot: Vẫn icon Robot
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)

# --- 7. KHU VỰC NHẬP LIỆU ---
with st.container():
    with st.expander("📸 Tải ảnh lên (Nếu cần)", expanded=False):
        uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        image_to_send = None
        if uploaded_file:
            image_to_send = Image.open(uploaded_file)
            st.image(image_to_send, width=150, caption="Ảnh đã chọn")
            st.caption("✅ Ảnh đã sẵn sàng. Hãy nhập tin nhắn và nhấn Enter để gửi.")

    user_input = st.chat_input("Nhập tin nhắn của bạn...")

# --- 8. XỬ LÝ GỬI ---
if user_input:
    display_text = user_input
    if image_to_send:
        display_text = f"[Đã gửi kèm ảnh] <br> {user_input}"

    # Hiện User (Màu xanh nhẹ)
    with chat_container:
        st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔵</span> <div>{display_text}</div></div></div>""", unsafe_allow_html=True)
        if image_to_send:
            with st.chat_message("user", avatar=None):
                st.image(image_to_send, width=300)
    
    st.session_state.messages.append({"role": "user", "content": display_text})

    try:
        inputs = [user_input]
        if image_to_send:
            inputs.append(image_to_send)

        with chat_container:
            with st.spinner("Đang suy nghĩ..."):
                response = st.session_state.chat_session.send_message(inputs)
                bot_reply = response.text
        
        # Hiện Bot (Vẫn màu Cầu vồng Neon)
        with chat_container:
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{bot_reply}</div></div></div>""", unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        with chat_container:
            st.error(f"Lỗi: {e}")