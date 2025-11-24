import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_paste_button import paste_image_button

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (GIAO DIỆN LIQUID CŨ + TỐI ƯU THANH CÔNG CỤ) ---
st.markdown("""
<style>
    /* --- NỀN LIQUID FULL --- */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
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
        position: relative;
        background: rgba(0, 0, 0, 0.2); /* Kính trong suốt */
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border-radius: 35px; padding: 12px 20px;
        color: #ffffff; font-weight: 500;
        display: flex; align-items: center; z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        width: fit-content; max-width: 85%;
        overflow: visible !important;
    }
    .liquid-glass::before {
        content: ""; position: absolute; inset: 0; border-radius: 35px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        pointer-events: none; z-index: -1; filter: blur(2px);
    }
    .liquid-glass::after {
        content: ""; position: absolute; inset: -2px; border-radius: 35px; z-index: -2;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
        filter: blur(10px); opacity: 0.6;
    }
    .icon { margin-right: 12px; font-size: 1.6rem; }
    .user-row { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 15px; }
    .bot-row { display: flex; justify-content: flex-start; width: 100%; margin-bottom: 15px; }

    /* --- TỐI ƯU THANH CHAT & CÔNG CỤ --- */
    .block-container { padding-bottom: 150px !important; } /* Chừa chỗ cho cụm công cụ */
    
    /* Khung nhập liệu */
    .stChatInputContainer { padding-bottom: 20px; }
    .stChatInputContainer > div {
        border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important;
    }

    /* Nút Dán ảnh (Paste) */
    button[title="Paste image"] {
        background-color: rgba(255, 69, 0, 0.8) !important;
        color: white !important; border-radius: 15px !important; border: none !important;
        font-size: 0.8rem !important; height: 40px;
    }
    
    /* Nút Tải ảnh (Upload) - Thu gọn lại */
    [data-testid="stFileUploader"] { margin-top: -20px; }
    [data-testid="stFileUploader"] section { padding: 0; background: transparent; border: none; }
    [data-testid="stFileUploader"] button {
        background-color: rgba(0, 191, 255, 0.8) !important;
        color: white !important; border-radius: 15px !important; border: none !important;
        width: 100%; height: 40px;
    }
    /* Ẩn icon dropzone to đùng */
    [data-testid="stUploadDropzone"] div { display: none; }
    [data-testid="stFileUploader"] small { display: none; }

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

# --- 6. LỊCH SỬ CHAT ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="user-row">
                <div class="liquid-glass">
                    <span class="icon">🔴</span> <div>{message["content"]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="bot-row">
                <div class="liquid-glass">
                    <span class="icon">🤖</span> <div>{message["content"]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. KHU VỰC CÔNG CỤ (TOOLBAR) ---
# Tạo một container dính liền ngay trên thanh chat
with st.container():
    col1, col2, col3 = st.columns([1, 1, 3])
    
    img_data = None
    
    # Nút Dán Ảnh
    with col1:
        paste_result = paste_image_button(
            label="📋 Dán Ảnh",
            background_color="rgba(255, 69, 0, 0.8)",
            hover_background_color="rgba(255, 69, 0, 1)",
        )
        if paste_result.image_data is not None:
            img_data = paste_result.image_data
            
    # Nút Tải Ảnh (Đã thu gọn bằng CSS)
    with col2:
        uploaded_file = st.file_uploader("Tải", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if uploaded_file:
            img_data = Image.open(uploaded_file)

    # Hiển thị Preview nếu có ảnh
    if img_data:
        st.image(img_data, width=100, caption="Sẵn sàng gửi")
        st.session_state.temp_img = img_data # Lưu tạm

# --- 8. XỬ LÝ GỬI TIN ---
user_input = st.chat_input("Nhập tin nhắn...")

# Kiểm tra có ảnh trong session không
final_img = img_data if img_data else st.session_state.get("temp_img", None)

# Nút gửi ảnh phụ trợ (nếu chỉ gửi ảnh không gõ chữ)
send_click = False
if final_img and not user_input:
    send_click = st.button("🚀 Gửi ảnh ngay")

if user_input or (final_img and send_click):
    display_text = user_input if user_input else "[Đã gửi một hình ảnh]"
    
    # Hiện User Bubble
    st.markdown(f"""
        <div class="user-row">
            <div class="liquid-glass">
                <span class="icon">🔴</span> <div>{display_text}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Hiện ảnh
    if final_img:
        with st.chat_message("user", avatar=None):
            st.image(final_img, width=250)
        st.session_state.temp_img = None # Xóa ảnh sau khi gửi

    st.session_state.messages.append({"role": "user", "content": display_text})

    # Gửi Gemini
    try:
        inputs = []
        if user_input: inputs.append(user_input)
        else: inputs.append("Hãy nhận xét ảnh này.")
        
        if final_img: inputs.append(final_img)

        with st.spinner("..."):
            response = st.session_state.chat_session.send_message(inputs)
            bot_reply = response.text
        
        # Hiện Bot Bubble
        st.markdown(f"""
            <div class="bot-row">
                <div class="liquid-glass">
                    <span class="icon">🤖</span> <div>{bot_reply}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")