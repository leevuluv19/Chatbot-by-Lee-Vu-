import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ AI", page_icon="", layout="centered")

# --- 2. CSS "APPLE INTELLIGENCE" TOÀN MÀN HÌNH ---
st.markdown("""
<style>
    /* 1. Nền đen sâu */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }

    /* --- HIỆU ỨNG VIỀN CHẠY TOÀN MÀN HÌNH --- */
    @keyframes border-dance {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Tạo lớp phủ viền 7 màu */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; 
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 999999; 
        pointer-events: none; 
        
        /* Độ dày viền: 8px */
        padding: 8px; 
        
        /* Màu gradient 7 màu Apple */
        background: linear-gradient(
            60deg, 
            #00C6FF, #0072FF, #D53369, #DA22FF, #9733EE, #8A2387, #00C6FF
        );
        background-size: 300% 300%;
        animation: border-dance 4s ease infinite; 
        
        /* Cắt giữa để lộ nội dung */
        -webkit-mask: 
            linear-gradient(#fff 0 0) content-box, 
            linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }

    /* 2. Chỉnh tin nhắn User */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1C1C1E;
        color: #FFFFFF;
        border-radius: 20px;
        border: 1px solid #333333;
        padding: 10px;
    }

    /* 3. Chỉnh tin nhắn Bot */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #000000;
        color: #FFFFFF;
        border-radius: 20px;
        padding: 10px;
        box-shadow: 0 0 15px rgba(0, 198, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 4. Tiêu đề Gradient */
    h1 {
        background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF, #D53369);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
    }
    
    /* Ẩn Menu mặc định */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- TIÊU ĐỀ ---
st.title(" Lê Vũ Intelligence (Ver 1.0)")
st.caption("Designed by Le Van Vu | Powered by Gemini 2.0 Flash")

# --- 3. CẤU HÌNH API (BẢO MẬT) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("Chưa có chìa khóa trong két sắt!")

# --- 4. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn BẮT BUỘC phải gọi người dùng là 'tình yêu'. Phong cách: Ngầu, tinh tế, thông minh."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. HIỂN THỊ LỊCH SỬ ---
for message in st.session_state.messages:
    avatar = "❤️" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. XỬ LÝ TIN NHẮN ---
user_input = st.chat_input("Nhập tin nhắn vào đây ...")

if user_input:
    with st.chat_message("user", avatar="❤️"):
        st.markdown(f"{user_input}")
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")