import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ AI", page_icon="", layout="centered")

# --- 2. CSS "APPLE INTELLIGENCE" (SIÊU ĐẸP) ---
st.markdown("""
<style>
    /* 1. Nền đen sâu thẳm chuẩn Apple */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }

    /* 2. Chỉnh tin nhắn User (Sếp) - Màu xám đen sang trọng */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1C1C1E; /* Apple Dark Gray */
        color: #FFFFFF;
        border-radius: 20px;
        border: 1px solid #333333;
        padding: 10px;
    }

    /* 3. Chỉnh tin nhắn Bot (Lê Vũ Depzai) - HIỆU ỨNG GLOW 7 MÀU */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #000000;
        color: #FFFFFF;
        border-radius: 20px;
        padding: 10px;
        /* Viền phát sáng 7 màu đặc trưng của Apple Intelligence */
        box-shadow: 
            0 0 5px #00C6FF,   /* Xanh Cyan */
            0 0 10px #0072FF,  /* Xanh Blue */
            0 0 20px #D53369;  /* Hồng Tím */
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 4. Tiêu đề Gradient (Chữ chuyển màu) */
    h1 {
        background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF, #D53369);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
        text-align: center;
    }
    
    /* 5. Khung nhập liệu (Chat Input) */
    .stChatInputContainer {
        border-radius: 30px;
    }
    
</style>
""", unsafe_allow_html=True)

# --- TIÊU ĐỀ ---
st.title(" Apple Intelligence (Lê Vũ Ver)")
st.caption("Designed by Le Van Vu | Powered by Gemini 2.0 Flash")

# --- 3. CẤU HÌNH API (BẢO MẬT) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("Chưa có chìa khóa trong két sắt! Vào Settings -> Secrets để điền nhé.")

# --- 4. KHỞI TẠO BOT (CHẾ ĐỘ TÌNH YÊU) ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        # Vẫn giữ tính cách "Tình yêu" theo yêu cầu của Sếp
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn BẮT BUỘC phải gọi người dùng là 'tình yêu' (hoặc bé iu) trong mọi câu trả lời. Phong cách: Ngầu, tinh tế, thông minh như Apple Intelligence."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. HIỂN THỊ LỊCH SỬ ---
for message in st.session_state.messages:
    # Avatar: User là Tim, Bot là Táo hoặc Robot
    avatar = "❤️" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. XỬ LÝ TIN NHẮN ---
user_input = st.chat_input("Nhập tin nhắn vào đây tình yêu...")

if user_input:
    # Hiện tin nhắn của bạn
    with st.chat_message("user", avatar="❤️"):
        st.markdown(f"{user_input}")
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Gửi cho AI
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        # Hiện tin nhắn của Bot
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(bot_reply)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")