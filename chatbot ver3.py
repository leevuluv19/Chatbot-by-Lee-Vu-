import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (LIQUID GLASS + FIX LAYOUT + POPOVER) ---
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

    /* --- TỐI ƯU KHOẢNG CÁCH ĐỂ KHÔNG BỊ CHE --- */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 120px !important; /* Chừa chỗ cho thanh chat ở dưới */
    }

    /* --- ẨN GIAO DIỆN THỪA --- */
    #MainMenu, footer {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- ANIMATION VIỀN CHẠY --- */
    @property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
    @keyframes rainbow-spin { to { --angle: 360deg; } }

    /* --- KHUNG CHAT (LIQUID GLASS) --- */
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
        overflow: visible !important; /* Để viền sáng không bị cắt */
    }

    /* Viền 7 màu */
    .liquid-glass::before {
        content: ""; position: absolute; inset: 0; border-radius: 35px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        pointer-events: none; z-index: -1; filter: blur(2px);
    }
    
    /* Glow */
    .liquid-glass::after {
        content: ""; position: absolute; inset: -2px; border-radius: 35px; z-index: -2;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
        filter: blur(10px); opacity: 0.6;
    }

    .icon { margin-right: 12px; font-size: 1.6rem; }
    .user-row { display: flex; justify-content: flex-end; margin-bottom: 15px; }
    .bot-row { display: flex; justify-content: flex-start; margin-bottom: 15px; }

    /* --- NÚT CÔNG CỤ (+) POPOVER --- */
    /* Ghim nút này xuống góc dưới bên trái */
    [data-testid="stPopover"] {
        position: fixed;
        bottom: 30px;
        left: 20px;
        z-index: 99999;
    }
    /* Làm đẹp nút + */
    [data-testid="stPopover"] button {
        border-radius: 50%;
        width: 50px; height: 50px;
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        font-size: 24px;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
    }
    [data-testid="stPopover"] button:hover {
        border-color: #00FFFF;
        color: #00FFFF;
        transform: scale(1.1);
    }

    /* --- KHUNG NHẬP LIỆU --- */
    .stChatInputContainer {
        padding-bottom: 30px;
        padding-left: 80px; /* Chừa chỗ cho nút dấu cộng */
    }
    .stChatInputContainer > div {
        position: relative; border-radius: 35px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 33px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important; backdrop-filter: blur(10px);
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
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. MENU CÔNG CỤ (NÚT DẤU CỘNG) ---
# Dùng st.popover để tạo menu bật lên gọn gàng
with st.popover("➕", help="Tải ảnh lên"):
    st.write("📸 **Chọn ảnh để gửi:**")
    uploaded_file = st.file_uploader("Chọn file ảnh", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    # Mẹo dán ảnh
    st.caption("💡 Mẹo: Bấm vào ô chọn file ở trên, rồi nhấn **Ctrl+V** để dán ảnh từ bộ nhớ tạm.")

# Xử lý ảnh (Lưu vào session để nhớ là đang có ảnh chờ gửi)
if uploaded_file:
    image = Image.open(uploaded_file)
    st.session_state.pending_image = image
    # Hiện ảnh nhỏ góc dưới để biết là đã chọn
    st.toast("✅ Đã tải ảnh! Hãy nhập nội dung và bấm Gửi.", icon="📸")
else:
    st.session_state.pending_image = None

# --- 7. HIỂN THỊ LỊCH SỬ ---
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

# --- 8. XỬ LÝ GỬI TIN NHẮN ---
user_input = st.chat_input("Nhập tin nhắn...")

if user_input:
    # Kiểm tra xem có ảnh đang chờ gửi không
    img_to_send = st.session_state.get("pending_image", None)
    
    display_text = user_input
    if img_to_send:
        display_text = f"[Đã gửi 1 ảnh] <br> {user_input}"
    
    # 1. Hiện User
    st.markdown(f"""
        <div class="user-row">
            <div class="liquid-glass">
                <span class="icon">🔴</span> <div>{display_text}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Hiện ảnh nếu có
    if img_to_send:
        with st.chat_message("user", avatar=None):
            st.image(img_to_send, width=300)

    st.session_state.messages.append({"role": "user", "content": display_text})

    # 3. Gửi Gemini
    try:
        inputs = [user_input]
        if img_to_send:
            inputs.append(img_to_send)
            st.session_state.pending_image = None # Gửi xong thì xóa ảnh chờ

        with st.spinner("Đang trả lời..."):
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