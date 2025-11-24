import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_paste_button import paste_image_button
import io

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (LIQUID NEON + TỐI ƯU THANH CÔNG CỤ CHAT) ---
st.markdown("""
<style>
    /* --- NỀN LIQUID FULL --- */
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
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: fit-content; max-width: 85%; overflow: visible !important;
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

    /* --- TỐI ƯU KHU VỰC NHẬP LIỆU DƯỚI ĐÁY --- */
    .block-container { padding-bottom: 140px !important; } /* Chừa chỗ cho cụm công cụ */

    /* 1. Thanh công cụ (Dán & Tải) */
    .tool-bar-container {
        display: flex;
        gap: 10px;
        margin-bottom: -15px; /* Kéo sát vào thanh chat */
        z-index: 10; position: relative;
        padding-left: 10px;
    }
    
    /* Style chung cho nút icon */
    .tool-icon-btn {
        width: 40px; height: 40px;
        border-radius: 50% !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        display: flex; justify-content: center; align-items: center;
        font-size: 1.2rem; cursor: pointer;
        backdrop-filter: blur(5px); transition: all 0.3s;
    }
    .tool-icon-btn:hover { transform: scale(1.1); border-color: white !important;}

    /* Nút Dán (Paste) - Custom lại thư viện */
    button[title="Paste image"] {
        width: 40px !important; height: 40px !important; border-radius: 50% !important;
        background: rgba(255, 100, 0, 0.5) !important; /* Cam trong suốt */
        color: transparent !important; /* Ẩn chữ mặc định */
        position: relative; border: 1px solid rgba(255, 100, 0, 0.8) !important;
    }
    button[title="Paste image"]::after {
        content: "📋"; color: white; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.2rem;
    }
    
    /* Nút Tải (Upload) - Biến hình */
    [data-testid="stFileUploader"] { width: 40px; }
    [data-testid="stFileUploader"] section { padding: 0; background: transparent; border: none; min-height: 0; }
    [data-testid="stFileUploader"] button {
        width: 40px !important; height: 40px !important; border-radius: 50% !important;
        background: rgba(0, 150, 255, 0.5) !important; /* Xanh trong suốt */
        color: transparent !important; border: 1px solid rgba(0, 150, 255, 0.8) !important;
        position: relative; padding: 0 !important;
    }
     [data-testid="stFileUploader"] button::after {
        content: "📁"; color: white; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.2rem;
    }
    [data-testid="stUploadDropzone"] div, [data-testid="stFileUploader"] small { display: none; }

    /* 2. Thanh Input Chat */
    .stChatInputContainer { padding-bottom: 20px; }
    .stChatInputContainer > div {
        border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important; padding-left: 15px !important;
    }

    /* Ảnh Preview nhỏ */
    .preview-img {
        border-radius: 10px; border: 2px solid #00ff00; margin-left: 10px; margin-bottom: 5px;
    }

    /* Title */
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

# --- 6. LỊCH SỬ CHAT (Container để cuộn) ---
chat_history_container = st.container()
with chat_history_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔴</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)

# --- 7. KHU VỰC NHẬP LIỆU TÍCH HỢP (Ở đáy) ---
with st.container():
    # Hàng công cụ (Nút tròn)
    st.markdown('<div class="tool-bar-container">', unsafe_allow_html=True)
    col_tools = st.columns([1, 1, 10])
    img_data = None
    
    with col_tools[0]: # Nút Dán (Paste)
        paste_result = paste_image_button(label="📋", background_color="transparent", hover_background_color="transparent")
        if paste_result.image_data is not None:
            img_data = paste_result.image_data
            st.session_state.temp_img = img_data
            st.toast("Đã dán ảnh! 📋", icon="✅")

    with col_tools[1]: # Nút Tải (Upload)
        uploaded_file = st.file_uploader("📁", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if uploaded_file:
            img_data = Image.open(uploaded_file)
            st.session_state.temp_img = img_data

    st.markdown('</div>', unsafe_allow_html=True)

    # Preview ảnh nếu có (Hiện ngay trên thanh chat)
    current_img = img_data if img_data else st.session_state.get("temp_img", None)
    if current_img:
        st.image(current_img, width=60, caption="Gửi cái này?", className="preview-img")

# --- 8. THANH CHAT INPUT ---
user_input = st.chat_input("Nhập tin nhắn...")

# XỬ LÝ GỬI
if user_input or (current_img and user_input is not None): # Chỉ gửi khi bấm Enter ở thanh chat
    
    display_text = user_input if user_input else "[Đã gửi một hình ảnh]"
    final_img_to_send = current_img

    # 1. Hiện User (vào container lịch sử)
    with chat_history_container:
        st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔴</span> <div>{display_text}</div></div></div>""", unsafe_allow_html=True)
        if final_img_to_send:
            with st.chat_message("user", avatar=None):
                st.image(final_img_to_send, width=250)
    
    st.session_state.messages.append({"role": "user", "content": display_text})
    st.session_state.temp_img = None # Reset ảnh sau khi gửi

    # 2. Gửi Gemini
    try:
        inputs = []
        if user_input: inputs.append(user_input)
        else: inputs.append("Hãy nhận xét ảnh này.")
        if final_img_to_send: inputs.append(final_img_to_send)

        with st.spinner("..."):
            response = st.session_state.chat_session.send_message(inputs)
            bot_reply = response.text
        
        # 3. Hiện Bot
        with chat_history_container:
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{bot_reply}</div></div></div>""", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")