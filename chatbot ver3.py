import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (LIQUID GLASS + NEON BORDER + FULL MÀN HÌNH + FILE UPLOAD STYLE) ---
st.markdown("""
<style>
    /* --- FIX NỀN FULL 100% KHÔNG CÓ VIỀN TRẮNG --- */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    
    /* Lớp phủ tối */
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.3); z-index: -1; pointer-events: none;
    }

    /* --- TỐI ƯU CHO ĐIỆN THOẠI --- */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 1rem !important;
            padding-bottom: 8rem !important; /* Tăng padding bottom để chứa thêm nút upload */
        }
        .liquid-glass { max-width: 90% !important; }
    }

    /* --- FIX LỖI LỘ VIỀN (OVERFLOW) --- */
    .element-container, .stMarkdown, div[data-testid="stChatMessageContent"] {
        overflow: visible !important;
    }
    div[data-testid="stChatMessage"] {
        overflow: visible !important; background-color: transparent !important; border: none !important;
    }

    /* Ẩn giao diện cũ */
    #MainMenu, footer {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}

    /* --- ANIMATION VIỀN CHẠY --- */
    @property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
    @keyframes rainbow-spin { to { --angle: 360deg; } }

    /* --- STYLE KHUNG CHAT (LIQUID GLASS) --- */
    .liquid-glass {
        position: relative;
        background: rgba(0, 0, 0, 0.2); /* Kính trong suốt */
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border-radius: 35px; /* Bo tròn viên thuốc */
        padding: 12px 20px;
        margin-bottom: 20px;
        color: #ffffff; font-weight: 500;
        display: flex; align-items: center;
        z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        width: fit-content;
        overflow: visible !important;
    }

    /* VIỀN 7 MÀU CHẠY */
    .liquid-glass::before {
        content: ""; position: absolute; inset: 0; border-radius: 35px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        pointer-events: none; z-index: -1;
        filter: blur(2px); /* Làm mềm viền */
    }
    
    /* HIỆU ỨNG GLOW (LOE SÁNG) */
    .liquid-glass::after {
        content: ""; position: absolute; inset: -2px; border-radius: 35px; z-index: -2;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
        filter: blur(10px); opacity: 0.6; /* Sáng mờ ảo */
    }

    .icon { margin-right: 12px; font-size: 1.6rem; filter: drop-shadow(0 0 5px rgba(255,255,255,0.8)); }
    .user-row { display: flex; justify-content: flex-end; padding-right: 5px; }
    .bot-row { display: flex; justify-content: flex-start; padding-left: 5px; }

    /* --- KHUNG NHẬP LIỆU --- */
    .stChatInputContainer { padding-bottom: 10px; } /* Giảm padding để nút upload gần hơn */
    .stChatInputContainer > div {
        position: relative; border-radius: 35px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 3s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 33px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important; backdrop-filter: blur(10px);
    }
    
    /* --- STYLE CHO KHUNG TẢI ẢNH (CUSTOM FILE UPLOADER) --- */
    .custom-file-upload {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin-top: -5px;
        margin-bottom: 10px;
        padding: 5px 0;
    }

    /* Biến cái file uploader mặc định thành một nút nhỏ gọn */
    .stFileUploader {
        width: auto !important;
    }
    .stFileUploader > div {
        padding: 5px 10px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        color: rgba(255, 255, 255, 0.7);
    }
    .stFileUploader > div:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.4);
        color: white;
    }
    /* Ẩn label "Drag and drop..." mặc định */
    .stFileUploader span {
        font-size: 0.9rem;
    }
    .stFileUploader small {
        display: none;
    }
    /* Ẩn icon upload mặc định */
    .stFileUploader div[data-testid="stUploadDropzone"] > div:first-child {
        display: none;
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
    st.error("⚠️ Chưa có chìa khóa! Vào Settings -> Secrets để điền API Key.")
    st.stop()

# --- 5. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, quan tâm, ngắn gọn. Nếu có ảnh, hãy nhận xét ảnh thật chất hoặc giải bài tập nếu có."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. HIỂN THỊ LỊCH SỬ CHAT ---
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

# --- 7. XỬ LÝ GỬI TIN VÀ TẢI ẢNH ---

# Nơi chứa thanh chat và nút tải ảnh
chat_container = st.container()

with chat_container:
    # 7.1. Thanh chat
    user_input = st.chat_input("Nói gì với anh đi em...")
    
    # 7.2. Nút tải ảnh (nằm ngay dưới thanh chat)
    st.markdown('<div class="custom-file-upload">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("🖼️ Tải ảnh lên", type=["jpg", "png", "jpeg"], label_visibility="visible")
    st.markdown('</div>', unsafe_allow_html=True)

# Xử lý logic gửi
image_to_send = None
if uploaded_file:
    image_to_send = Image.open(uploaded_file)
    # Hiển thị ảnh đã chọn (preview)
    with st.chat_message("user", avatar=None):
        st.image(image_to_send, width=200, caption="Ảnh đã chọn")

send_button = False
if image_to_send: 
    send_button = st.button("Gửi ảnh ngay")

if user_input or (image_to_send and send_button):
    
    display_text = user_input if user_input else "[Đã gửi một hình ảnh]"
    
    # 1. Hiện User
    st.markdown(f"""
        <div class="user-row">
            <div class="liquid-glass">
                <span class="icon">🔴</span> <div>{display_text}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Hiện ảnh (nếu có và user bấm gửi)
    if image_to_send and send_button:
        with st.chat_message("user", avatar=None):
            st.image(image_to_send, width=250)

    st.session_state.messages.append({"role": "user", "content": display_text})

    # 3. Gửi Gemini
    try:
        inputs = []
        if user_input:
            inputs.append(user_input)
        else:
            inputs.append("Hãy nhận xét về bức ảnh này.")
            
        if image_to_send and send_button:
            inputs.append(image_to_send)

        with st.spinner("Đang xử lý..."):
            response = st.session_state.chat_session.send_message(inputs)
            bot_reply = response.text
        
        # 4. Hiện Bot
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