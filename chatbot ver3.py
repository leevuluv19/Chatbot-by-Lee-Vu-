import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (FIX LỖI MẤT NÚT UPLOAD) ---
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

    /* --- KHUNG NHẬP LIỆU --- */
    .stChatInputContainer {
        padding-bottom: 20px !important;
        margin-left: 60px !important; /* Đẩy sang phải để chừa chỗ cho nút ảnh */
        width: calc(100% - 80px) !important; 
        z-index: 999 !important;
    }
    .stChatInputContainer > div {
        border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important;
    }

    /* --- [FIX QUAN TRỌNG] ĐƯA NÚT ẢNH NỔI LÊN TRÊN --- */
    [data-testid="stFileUploader"] {
        position: fixed !important; /* Cố định vị trí */
        bottom: 28px !important;    /* Cách đáy 28px */
        left: 20px !important;      /* Cách trái 20px */
        width: 45px !important;
        height: 45px !important;
        z-index: 999999 !important; /* Lớp cao nhất, đè lên tất cả */
        background-color: transparent !important;
    }
    
    /* Ẩn các phần thừa của uploader */
    [data-testid="stFileUploader"] section { padding: 0 !important; min-height: 0 !important; }
    [data-testid="stFileUploader"] span { display: none !important; } /* Ẩn chữ Drag drop */

    /* Tạo hình cái nút tròn */
    [data-testid="stFileUploader"] button {
        border-radius: 50% !important;
        width: 45px !important; 
        height: 45px !important;
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        color: transparent !important; /* Ẩn chữ Browse files */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        margin: 0 !important;
        backdrop-filter: blur(10px);
    }
    
    /* Thêm icon Máy ảnh vào giữa */
    [data-testid="stFileUploader"] button::after {
        content: "📸"; 
        color: white; 
        font-size: 22px;
        visibility: visible !important;
        position: absolute;
    }
    
    /* Hiệu ứng hover */
    [data-testid="stFileUploader"] button:hover {
        background: rgba(0, 255, 255, 0.3) !important;
        border-color: #00ffff !important;
        transform: scale(1.1);
    }

    /* Preview ảnh nhỏ */
    [data-testid="stImage"] {
        position: fixed; bottom: 85px; left: 20px; z-index: 99999;
        border-radius: 10px; border: 2px solid #00ff00; background: rgba(0,0,0,0.8);
        padding: 5px; max-width: 100px !important;
    }
    
    /* Đẩy nội dung lên để không bị che */
    .block-container { padding-bottom: 120px !important; }

    /* TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 20px; margin-top: -30px; }
    .main-title { font-size: 2.2rem; font-weight: 800; color: white; text-shadow: 0 0 15px rgba(255,255,255,0.4); }
    .sub-title { font-size: 0.9rem; color: rgba(255,255,255,0.8); }
</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN ---
st.markdown("""
    <div class="title-container">
        <div class="main-title">😎 Lê Vũ Depzai</div>
        <div class="sub-title">Trò chuyện & Phân tích ảnh</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. API ---
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

# --- 6. LỊCH SỬ ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔴</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)

# --- 7. NÚT TẢI ẢNH (Nằm ngoài container để CSS định vị) ---
uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

image_to_send = None
if uploaded_file:
    image_to_send = Image.open(uploaded_file)
    st.image(image_to_send, width=100, caption="Đã chọn")

# --- 8. GỬI TIN ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input or (image_to_send and user_input is not None):
    display_text = user_input if user_input else "[Đã gửi một hình ảnh]"
    
    st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔴</span> <div>{display_text}</div></div></div>""", unsafe_allow_html=True)
    
    if image_to_send:
        with st.chat_message("user", avatar=None):
            st.image(image_to_send, width=250)

    st.session_state.messages.append({"role": "user", "content": display_text})

    try:
        inputs = []
        if user_input: inputs.append(user_input)
        else: inputs.append("Hãy nhận xét ảnh này.")
        if image_to_send: inputs.append(image_to_send)

        with st.spinner("..."):
            response = st.session_state.chat_session.send_message(inputs)
            bot_reply = response.text
        
        st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{bot_reply}</div></div></div>""", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")