import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (FINAL STABLE VERSION) ---
st.markdown("""
<style>
    /* --- NỀN FULL MÀN HÌNH --- */
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
        background: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border-radius: 35px;
        padding: 12px 20px;
        color: #ffffff; font-weight: 500;
        display: flex; align-items: center;
        z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        width: fit-content; max-width: 85%;
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

    /* --- [QUAN TRỌNG] BIẾN HÌNH NÚT UPLOAD THÀNH ICON BÊN CẠNH CHAT --- */
    
    /* 1. Định vị nút upload xuống góc dưới cùng bên trái */
    [data-testid="stFileUploader"] {
        position: fixed;
        bottom: 20px; /* Cách đáy 20px (ngang hàng với thanh chat) */
        left: 20px;   /* Cách trái 20px */
        width: 50px;  /* Thu nhỏ lại */
        z-index: 99999;
    }
    
    /* 2. Ẩn hết chữ nghĩa rườm rà */
    [data-testid="stFileUploader"] section { padding: 0; min-height: 0; background: transparent; border: none; }
    [data-testid="stFileUploader"] div[data-testid="stUploadDropzone"] { display: none; }
    [data-testid="stFileUploader"] small { display: none; }
    
    /* 3. Style cái nút bấm thành hình tròn đẹp */
    [data-testid="stFileUploader"] button {
        border-radius: 50% !important;
        width: 50px !important; height: 50px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: transparent !important; /* Ẩn chữ 'Browse files' */
        backdrop-filter: blur(10px);
        transition: all 0.3s;
    }
    
    /* 4. Thêm icon Máy ảnh vào giữa nút */
    [data-testid="stFileUploader"] button::after {
        content: "📸";
        color: white;
        font-size: 24px;
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        cursor: pointer;
    }
    
    /* Hiệu ứng khi di chuột vào nút ảnh */
    [data-testid="stFileUploader"] button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: #00ffff !important;
        transform: scale(1.1);
    }

    /* --- ĐẨY THANH CHAT SANG PHẢI ĐỂ KHÔNG ĐÈ LÊN NÚT ẢNH --- */
    .stChatInputContainer {
        padding-bottom: 20px;
        margin-left: 60px; /* Đẩy sang phải 60px tránh nút ảnh */
        width: calc(100% - 80px) !important; /* Tính toán lại chiều rộng */
    }
    
    /* Style thanh chat */
    .stChatInputContainer > div {
        border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important;
    }

    /* --- STYLE ẢNH PREVIEW (HIỆN NHỎ GÓC TRÁI) --- */
    [data-testid="stImage"] {
        position: fixed;
        bottom: 80px;
        left: 20px;
        z-index: 99998;
        border-radius: 10px;
        border: 2px solid #00ff00;
        background: rgba(0,0,0,0.8);
        padding: 5px;
        max-width: 100px !important;
    }
    
    /* Tối ưu khoảng trắng nội dung */
    .block-container { padding-bottom: 100px !important; }

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
        <div class="sub-title">Trò chuyện & Giải bài tập</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. CẤU HÌNH API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa có chìa khóa!")
    st.stop()

# --- 5. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, quan tâm, ngắn gọn. Nếu có ảnh, hãy nhận xét hoặc giải bài tập."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. NÚT TẢI ẢNH (ĐƯỢC CSS ĐỊNH VỊ CỐ ĐỊNH GÓC TRÁI DƯỚI) ---
uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

# Xử lý ảnh preview
image_to_send = None
if uploaded_file:
    image_to_send = Image.open(uploaded_file)
    # Ảnh này sẽ tự động bay xuống góc trái dưới nhờ CSS [data-testid="stImage"]
    st.image(image_to_send, width=100, caption="Đã chọn")

# --- 7. HIỂN THỊ LỊCH SỬ CHAT ---
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

# --- 8. XỬ LÝ GỬI TIN ---
user_input = st.chat_input("Nói gì với anh đi em...")

# Logic gửi: Có chữ HOẶC (có ảnh VÀ bấm enter gửi)
# Lưu ý: Với chat_input, user phải bấm Enter hoặc nút gửi trên bàn phím
if user_input or (image_to_send and user_input is not None):
    
    display_text = user_input if user_input else "[Đã gửi một hình ảnh]"
    
    # Hiện User
    st.markdown(f"""
        <div class="user-row">
            <div class="liquid-glass">
                <span class="icon">🔴</span> <div>{display_text}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Hiện ảnh trong lịch sử chat (dùng container chuẩn để hiển thị đẹp)
    if image_to_send:
        with st.chat_message("user", avatar=None):
            st.image(image_to_send, width=250)

    st.session_state.messages.append({"role": "user", "content": display_text})

    # Gửi Gemini
    try:
        inputs = []
        if user_input: inputs.append(user_input)
        else: inputs.append("Hãy nhận xét ảnh này.")
        if image_to_send: inputs.append(image_to_send)

        with st.spinner("..."):
            response = st.session_state.chat_session.send_message(inputs)
            bot_reply = response.text
        
        # Hiện Bot
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