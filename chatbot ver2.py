import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_paste_button import paste_image_button

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP: MÀU GRADIENT CHUẨN ẢNH MẪU ---
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

    /* --- STYLE CHUNG CHO KHUNG CHAT (HÌNH DÁNG) --- */
    .liquid-glass {
        position: relative;
        border-radius: 35px;
        padding: 12px 25px;
        color: #ffffff;
        font-weight: 500;
        display: flex;
        align-items: center;
        z-index: 1;
        width: fit-content;
        max-width: 85%;
        backdrop-filter: blur(15px); /* Kính mờ */
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.1); /* Viền kính mỏng */
    }

    /* ================= MÀU SẮC RIÊNG BIỆT (THEO ẢNH) ================= */

    /* --- 1. BOT (BÊN TRÁI): XANH DƯƠNG - TÍM (AURORA) --- */
    .bot-row .liquid-glass {
        /* Nền loang màu Xanh - Tím nhẹ bên trong */
        background: linear-gradient(135deg, rgba(0, 198, 255, 0.2), rgba(142, 45, 226, 0.2));
    }
    /* Viền phát sáng của Bot */
    .bot-row .liquid-glass::before {
        content: ""; position: absolute; inset: -2px; border-radius: 35px; z-index: -1;
        /* Gradient viền Xanh -> Tím */
        background: linear-gradient(90deg, #00C6FF, #0072FF, #8E2DE2);
        filter: blur(10px); /* Làm nhòe tạo hào quang */
        opacity: 0.7;
    }

    /* --- 2. USER (BÊN PHẢI): ĐỎ - TÍM THAN (SUNSET) --- */
    .user-row .liquid-glass {
        /* Nền loang màu Đỏ - Tối nhẹ bên trong */
        background: linear-gradient(135deg, rgba(255, 81, 47, 0.2), rgba(221, 36, 118, 0.2));
    }
    /* Viền phát sáng của User */
    .user-row .liquid-glass::before {
        content: ""; position: absolute; inset: -2px; border-radius: 35px; z-index: -1;
        /* Gradient viền Đỏ -> Hồng Tím */
        background: linear-gradient(90deg, #FF512F, #DD2476, #FF0000);
        filter: blur(10px); /* Làm nhòe tạo hào quang */
        opacity: 0.7;
    }

    /* ================================================================= */

    .icon { margin-right: 12px; font-size: 1.6rem; filter: drop-shadow(0 0 2px rgba(255,255,255,0.5)); }
    .user-row { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 15px; }
    .bot-row { display: flex; justify-content: flex-start; width: 100%; margin-bottom: 15px; }

    /* --- THANH CÔNG CỤ & INPUT --- */
    .block-container { padding-bottom: 140px !important; }
    
    /* Nút Paste */
    button[title="Paste image"] {
        width: 40px !important; height: 40px !important; border-radius: 50% !important;
        background: rgba(255, 100, 0, 0.5) !important; 
        color: transparent !important; border: 1px solid rgba(255, 100, 0, 0.8) !important;
    }
    button[title="Paste image"]::after {
        content: "📋"; color: white; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.2rem;
    }
    
    /* Nút Upload */
    [data-testid="stFileUploader"] { width: 40px; margin-top: -18px; }
    [data-testid="stFileUploader"] section { padding: 0; background: transparent; border: none; min-height: 0; }
    [data-testid="stFileUploader"] button {
        width: 40px !important; height: 40px !important; border-radius: 50% !important;
        background: rgba(0, 150, 255, 0.5) !important;
        color: transparent !important; border: 1px solid rgba(0, 150, 255, 0.8) !important;
        padding: 0 !important;
    }
     [data-testid="stFileUploader"] button::after {
        content: "📁"; color: white; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.2rem;
    }
    [data-testid="stUploadDropzone"] { display: none; } 
    [data-testid="stFileUploader"] small { display: none; }
    [data-testid="stFileUploader"] span { display: none !important; }

    /* Thanh Input - Màu Cầu Vồng */
    .stChatInputContainer { padding-bottom: 20px; margin-left: 60px; width: calc(100% - 80px) !important; }
    .stChatInputContainer > div {
        border-radius: 30px; padding: 2px;
        background: linear-gradient(90deg, #00C6FF, #0072FF, #8E2DE2, #F80759, #FF8C00); /* Gradient tĩnh cho input */
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important; padding-left: 15px !important;
    }
    .tool-bar-container { display: flex; gap: 10px; margin-bottom: -15px; z-index: 10; position: relative; padding-left: 10px; }

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

# --- 6. LỊCH SỬ CHAT ---
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            # User: Icon Đỏ
            st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔴</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)
        else:
            # Bot: Icon Xanh hoặc Robot
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)

# --- 7. CÔNG CỤ ---
with st.container():
    st.markdown('<div class="tool-bar-container">', unsafe_allow_html=True)
    col_tools = st.columns([1, 1, 10])
    img_data = None
    
    with col_tools[0]: 
        paste_result = paste_image_button(label="📋", background_color="transparent", hover_background_color="transparent")
        if paste_result.image_data is not None:
            img_data = paste_result.image_data
            st.session_state.temp_img = img_data
            st.toast("Đã dán ảnh!", icon="✅")

    with col_tools[1]: 
        uploaded_file = st.file_uploader("Tải", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if uploaded_file:
            img_data = Image.open(uploaded_file)
            st.session_state.temp_img = img_data

    st.markdown('</div>', unsafe_allow_html=True)

    current_img = img_data if img_data else st.session_state.get("temp_img", None)
    if current_img:
        st.image(current_img, width=80, caption="Gửi cái này?")

# --- 8. GỬI TIN ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input or (current_img and user_input is not None):
    display_text = user_input if user_input else "[Đã gửi một hình ảnh]"
    
    with chat_container:
        st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">🔴</span> <div>{display_text}</div></div></div>""", unsafe_allow_html=True)
        if current_img:
            with st.chat_message("user", avatar=None):
                st.image(current_img, width=250)
    
    st.session_state.messages.append({"role": "user", "content": display_text})
    st.session_state.temp_img = None 

    try:
        inputs = []
        if user_input: inputs.append(user_input)
        else: inputs.append("Hãy nhận xét ảnh này.")
        if current_img: inputs.append(current_img)

        with chat_container:
            with st.spinner("..."):
                response = st.session_state.chat_session.send_message(inputs)
                bot_reply = response.text
        
        with chat_container:
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{bot_reply}</div></div></div>""", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")