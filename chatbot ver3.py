import streamlit as st
import google.generativeai as genai
from PIL import Image # <--- THÊM THƯ VIỆN XỬ LÝ ẢNH

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (GIỮ NGUYÊN KHÔNG CHỈNH SỬA GÌ CỦA SẾP) ---
st.markdown("""
<style>
    /* --- FIX NỀN FULL 100% --- */
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

    /* --- TỐI ƯU CHO ĐIỆN THOẠI --- */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important; padding-right: 0.5rem !important;
            padding-top: 1rem !important; padding-bottom: 5rem !important;
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

    #MainMenu, footer {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}

    /* --- ANIMATION --- */
    @property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
    @keyframes rainbow-spin { to { --angle: 360deg; } }

    /* --- STYLE KHUNG CHAT (LIQUID GLASS) --- */
    .liquid-glass {
        position: relative;
        background: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border-radius: 35px;
        padding: 12px 20px;
        margin-bottom: 20px;
        color: #ffffff; font-weight: 500;
        display: flex; align-items: center;
        z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        width: fit-content;
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

    .icon { margin-right: 12px; font-size: 1.6rem; filter: drop-shadow(0 0 5px rgba(255,255,255,0.8)); }
    .user-row { display: flex; justify-content: flex-end; padding-right: 5px; }
    .bot-row { display: flex; justify-content: flex-start; padding-left: 5px; }

    /* --- KHUNG INPUT --- */
    .stChatInputContainer { padding-bottom: 30px; }
    .stChatInputContainer > div {
        position: relative; border-radius: 35px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 3s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 33px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important; backdrop-filter: blur(10px);
    }
    
    /* --- STYLE NÚT UPLOAD ẢNH (MỚI THÊM) --- */
    .stFileUploader { padding: 10px; background: rgba(255,255,255,0.1); border-radius: 15px; backdrop-filter: blur(5px); }
    /* Ẩn label mặc định cho gọn */
    .stFileUploader label { display: none; } 

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
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, quan tâm, ngắn gọn. Nếu có ảnh, hãy nhận xét ảnh thật chất."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. NÚT GỬI ẢNH (THÊM VÀO ĐÂY) ---
# Dùng expander để giấu nút upload cho gọn, không phá vỡ giao diện
with st.expander("📸 Gửi ảnh (Bấm để mở)"):
    uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg", "png", "jpeg"])
    image_to_send = None
    if uploaded_file:
        image_to_send = Image.open(uploaded_file)
        st.image(image_to_send, width=200, caption="Ảnh đã chọn")

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

# --- 8. XỬ LÝ GỬI TIN (CÓ ẢNH HOẶC KHÔNG) ---
user_input = st.chat_input("Nói gì với anh đi em...")

# Logic: Gửi khi bấm Enter (có chữ) HOẶC bấm nút "Gửi ảnh ngay" (nếu có ảnh)
send_button = False
if image_to_send: 
    send_button = st.button("Gửi ảnh ngay") # Nút này chỉ hiện khi đã chọn ảnh

if user_input or (image_to_send and send_button):
    
    # Nội dung hiển thị phía User
    display_text = user_input if user_input else "[Đã gửi một hình ảnh]"
    
    # 1. Hiện khung chat của User
    st.markdown(f"""
        <div class="user-row">
            <div class="liquid-glass">
                <span class="icon">🔴</span> <div>{display_text}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Nếu có ảnh thì hiện ảnh ra màn hình chat (dùng container mặc định để hiện ảnh)
    if image_to_send:
        with st.chat_message("user", avatar=None):
            st.image(image_to_send, width=250)

    st.session_state.messages.append({"role": "user", "content": display_text})

    # 3. Gửi qua Gemini
    try:
        inputs = []
        if user_input:
            inputs.append(user_input)
        else:
            inputs.append("Hãy nhận xét về bức ảnh này.") # Lời dẫn mặc định
            
        if image_to_send:
            inputs.append(image_to_send)

        response = st.session_state.chat_session.send_message(inputs)
        bot_reply = response.text
        
        # 4. Hiện câu trả lời của Bot
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