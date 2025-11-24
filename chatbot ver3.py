import streamlit as st
import google.generativeai as genai
from PIL import Image


st.set_page_config(page_title="Lê Vũ Depzai", layout="centered")


st.markdown("""
<style>
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
        background: rgba(0, 0, 0, 0.4); z-index: -1; pointer-events: none;
    }
    .title-container { text-align: center; margin-bottom: 30px; margin-top: -20px; }
    .main-title { font-size: 2.5rem; font-weight: 800; color: white; text-shadow: 0 0 15px rgba(255,255,255,0.4); }
    .sub-title { font-size: 1rem; color: rgba(255,255,255,0.8); letter-spacing: 1px; }


    #MainMenu, footer {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

            /* --- VIỀN NEON 7 MÀU CHẠY (MỎNG NHƯNG TỎA SÁNG MẠNH) --- */
    
    /* LỚP 1: SỢI DÂY NGUỒN (Nét căng, chạy màu) */
    body::before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 9999;
        pointer-events: none;
        
        padding: 4px; /* ĐỘ DÀY VIỀN CHỈ 4PX THÔI */
        
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        animation: spin 4s linear infinite;
        
        /* Mask để đục thủng giữa */
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    
    /* LỚP 2: ÁNH SÁNG TỎA RA (GLOW) */
    body::after {
        content: "";
        position: fixed;
        /* Phủ trùm lên viền chính */
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 9998;
        pointer-events: none;
        
        padding: 4px; /* Dày bằng viền chính */
        
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        animation: spin 4s linear infinite;
        
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;

        /* ĐÂY LÀ PHÉP THUẬT: Làm nhòe cực mạnh để tạo sương */
        filter: blur(20px); 
        opacity: 1; /* Tăng độ sáng lên tối đa */
    }
    /* ẨN GIAO DIỆN CŨ */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- ANIMATION GÓC XOAY --- */
    @property --angle {
      syntax: '<angle>';
      initial-value: 0deg;
      inherits: false;
    }
    @keyframes spin {
        to { --angle: 360deg; }
    }
    .liquid-glass {
        position: relative;
        background: rgba(255, 255, 255, 0.001); 
        
        backdrop-filter: blur(2px); 
        -webkit-backdrop-filter: blur(2px);
        
        border-radius: 35px;
        padding: 12px 25px;
        margin-bottom: 15px;
        color: white;
        font-weight: 500;
        display: flex; align-items: center;
        z-index: 1;
        
        border: 1px solid rgba(255,255,255,0.05);
        
        width: fit-content; max-width: 85%;
    }
    .liquid-glass::before {
        content: "";
        position: absolute;
        inset: 0;
        z-index: -1;
        border-radius: 35px; 
        padding: 2px;
        
        /* Quan trọng: Màu đầu (#00C6FF) và màu cuối (#00C6FF) PHẢI GIỐNG NHAU để xoay không bị giật */
        background: conic-gradient(
            from var(--angle), 
            #00C6FF, #0072FF, #8E2DE2, #F80759, #FF8C00, #E0C3FC, #00C6FF
        );
        
        animation: spin 6s linear infinite;
        
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        
        /* Glow nhẹ */
        filter: blur(10px);
    }
    
    /* Lớp Glow loe sáng bên ngoài */
    .liquid-glass::after {
        content: "";
        position: absolute;
        inset: -4px;
        z-index: -4;
        border-radius: 35px;
        background: conic-gradient(
            from var(--angle), 
            #00C6FF, #0072FF, #8E2DE2, #F80759, #FF8C00, #E0C3FC, #00C6FF
        );
        animation: spin 4s linear infinite;
        filter: blur(20px); /* Độ loe sáng */
        opacity: 0.7;
    }

    /* Căn chỉnh hàng chat */
    .icon { margin-right: 12px; font-size: 1.5rem; }
    .user-row { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 15px; }
    .bot-row { display: flex; justify-content: flex-start; width: 100%; margin-bottom: 15px; }

    /* ================= GIAO DIỆN NHƯ ẢNH 2 ================= */
    /* --- Style cho Thanh công cụ Upload (Expander) --- */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.1) !important; /* Nền trong suốt nhẹ */
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        font-weight: 500 !important;
    }
    [data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 10px; /* Khoảng cách với thanh chat */
    }
    /* Nội dung bên trong expander */
    [data-testid="stExpander"] .streamlit-expanderContent {
        background-color: rgba(0,0,0,0.3) !important;
        border-radius: 0 0 15px 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-top: none !important;
    }
    
    /* --- Style cho Thanh Chat Input --- */
    .stChatInputContainer {
        padding-bottom: 30px;
    }
    /* Áp dụng style Neon cho khung nhập liệu */
    .stChatInputContainer > div {
        border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important;
        background: rgba(0, 0, 0, 0.7) !important; /* Nền tối hơn chút để dễ đọc chữ */
        color: white !important;
        border: none !important;
        padding-left: 15px !important;
    }

    /* Tối ưu khoảng cách container chính */
    .block-container { padding-bottom: 100px !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. TIÊU ĐỀ (NHƯ ẢNH 1) ---
st.markdown("""
    <div class="title-container">
        <div class="main-title"> Lê Vũ Depzai</div>
        <div class="sub-title">Trí tuệ nhân tạo của Lê Vũ</div>
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

# --- 6. LỊCH SỬ CHAT (STYLE NHƯ ẢNH 3) ---
# Tạo container để chứa lịch sử chat, nằm bên trên khu vực nhập liệu
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">⭐</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)

# --- 7. KHU VỰC NHẬP LIỆU (BỐ CỤC NHƯ ẢNH 2) ---
# Tạo container cố định ở đáy để chứa công cụ và thanh chat
with st.container():
    # 7.1. Thanh công cụ upload (Dạng Expander nằm trên)
    with st.expander("📸 Tải ảnh lên (Nếu cần)", expanded=False):
        uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        image_to_send = None
        if uploaded_file:
            image_to_send = Image.open(uploaded_file)
            st.image(image_to_send, width=150, caption="Ảnh đã chọn")
            st.caption("✅ Ảnh đã sẵn sàng. Nhấn Enter để gửi.")

    # 7.2. Thanh Chat Input (Nằm ngay dưới)
    user_input = st.chat_input("Nhập tin nhắn của bạn...")

# --- 8. XỬ LÝ LOGIC GỬI TIN ---
if user_input: # Chỉ gửi khi người dùng nhập chữ và nhấn Enter
    
    display_text = user_input
    if image_to_send:
        display_text = f"[Đã gửi kèm ảnh] <br> {user_input}"

    # Hiện tin nhắn User ngay lập tức vào lịch sử
    with chat_container:
        st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">⭐</span> <div>{display_text}</div></div></div>""", unsafe_allow_html=True)
        if image_to_send:
            with st.chat_message("user", avatar=None): # Dùng container chuẩn để hiện ảnh cho đẹp
                st.image(image_to_send, width=300)
    
    # Lưu vào session state
    st.session_state.messages.append({"role": "user", "content": display_text})

    # Gửi qua Gemini
    try:
        inputs = [user_input]
        if image_to_send:
            inputs.append(image_to_send)

        # Hiển thị spinner trong lúc chờ
        with chat_container:
            with st.spinner("Le Vu Intelligence đang suy nghĩ...."):
                response = st.session_state.chat_session.send_message(inputs)
                bot_reply = response.text
        
        # Hiện tin nhắn Bot
        with chat_container:
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{bot_reply}</div></div></div>""", unsafe_allow_html=True)
        
        # Lưu vào session state
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        with chat_container:
            st.error(f"Lỗi: {e}")