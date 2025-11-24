import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ AI", layout="centered")

# --- 2. CSS SIÊU CẤP (Liquid Background + Glass + Apple Border + No Avatar) ---
st.markdown("""
<style>
    /* 1. Cài hình nền Liquid (Dạng lỏng chảy) */
    .stApp {
        background-image: url("https://img.freepik.com/free-photo/abstract-black-oil-paint-texture-background_53876-102366.jpg?t=st=1732523000~exp=1732526600~hmac=6c938906103908084700262070402040");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Làm lớp phủ tối màu lên nền cho dễ đọc chữ */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.5); /* Tối 50% */
        z-index: -1;
    }

    /* 2. ẨN AVATAR (Theo lệnh Sếp) */
    div[data-testid="stChatMessageAvatarBackground"] {
        display: none !important;
    }
    
    /* Căn chỉnh lại tin nhắn vì đã mất avatar */
    div[data-testid="stChatMessageContent"] {
        margin-left: 0 !important;
        padding-left: 0 !important;
    }

    /* 3. KHUNG CHAT GLASSMORPHISM (Kính trong suốt) + VIỀN APPLE */
    div[data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05); /* Nền kính mờ */
        backdrop-filter: blur(15px); /* Làm mờ hậu cảnh */
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 15px;
        
        /* Viền Apple Intelligence 7 màu phát sáng */
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        box-shadow: 0 0 15px rgba(0, 198, 255, 0.2); /* Glow nhẹ */
    }
    
    /* Tạo viền gradient bằng pseudo-element */
    div[data-testid="stChatMessage"]::before {
        content: "";
        position: absolute;
        top: -2px; bottom: -2px; left: -2px; right: -2px;
        background: linear-gradient(90deg, #FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF, #4B0082, #9400D3);
        z-index: -1;
        border-radius: 22px;
        opacity: 0.6;
    }

    /* Màu chữ */
    div[data-testid="stChatMessage"] p {
        color: #FFFFFF !important;
        font-size: 16px;
        font-weight: 500;
    }

    /* 4. TIÊU ĐỀ */
    h1 {
        color: #FFFFFF;
        text-shadow: 0 0 10px rgba(255,255,255,0.5);
        text-align: center;
    }

    /* 5. KHUNG NHẬP LIỆU (Cũng làm kính luôn) */
    .stChatInputContainer textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    /* Ẩn menu mặc định */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# --- GIAO DIỆN CHÍNH ---
st.title("😎 Lê Vũ Depzai (Anh Trai)")

# --- 3. CẤU HÌNH API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa nhập chìa khóa vào két sắt (Secrets)!")

# --- 4. LOGIC BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn BẮT BUỘC phải gọi người dùng là 'em' và xưng 'anh'. Phong cách: Ngầu, lạnh lùng, chiều chuộng."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. HIỂN THỊ LỊCH SỬ (Không Avatar) ---
for message in st.session_state.messages:
    # Avatar=None để không hiện icon mặc định, CSS sẽ ẩn luôn khung avatar
    with st.chat_message(message["role"], avatar=None): 
        st.markdown(message["content"])

# --- 6. XỬ LÝ TIN NHẮN ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    with st.chat_message("user", avatar=None):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        with st.chat_message("assistant", avatar=None):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")