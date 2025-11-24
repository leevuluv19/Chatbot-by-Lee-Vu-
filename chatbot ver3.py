import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Gemini Clone", page_icon="✨", layout="centered")

# --- 2. CSS SIÊU CẤP (GIAO DIỆN GEMINI + MENU NỔI) ---
st.markdown("""
<style>
    /* --- NỀN TRẮNG/SÁNG SẠCH SẼ (STYLE GEMINI) --- */
    .stApp {
        background-color: #ffffff; /* Nền trắng (hoặc #f0f4f9 cho giống Gemini web) */
        color: #1f1f1f;
    }
    
    /* Nếu Sếp thích Dark Mode thì bỏ comment đoạn dưới này: */
    /*
    .stApp { background-color: #131314; color: #e3e3e3; }
    */

    /* --- ẨN GIAO DIỆN CŨ --- */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- STYLE BONG BÓNG CHAT --- */
    /* User (Sếp) - Màu Xám Nhạt, Bo tròn */
    .user-bubble {
        background-color: #f0f4f9; /* Màu xám xanh nhạt của Gemini */
        color: #1f1f1f;
        padding: 12px 20px;
        border-radius: 20px 20px 5px 20px; /* Bo góc kiểu hội thoại */
        margin-bottom: 10px;
        display: inline-block;
        max-width: 85%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Bot (Gemini) - Không nền, chỉ có Icon và chữ */
    .bot-bubble {
        background-color: transparent;
        color: #1f1f1f;
        padding: 0px;
        margin-bottom: 10px;
        display: flex;
        gap: 15px;
        line-height: 1.6;
    }

    /* --- CĂN CHỈNH --- */
    .user-row { display: flex; justify-content: flex-end; }
    .bot-row { display: flex; justify-content: flex-start; }

    /* --- ICON CÔNG CỤ (+) NỔI --- */
    /* Định vị nút Popover xuống góc dưới trái */
    [data-testid="stPopover"] {
        position: fixed;
        bottom: 35px; /* Canh vừa tầm với thanh chat */
        left: 20px;
        z-index: 10000; /* Nằm trên cùng */
    }
    
    /* Style cho nút (+) */
    [data-testid="stPopover"] button {
        border-radius: 50%;
        width: 45px;
        height: 45px;
        background-color: #f0f4f9; /* Nền xám nhạt */
        border: none;
        color: #444746;
        font-size: 24px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s;
    }
    [data-testid="stPopover"] button:hover {
        background-color: #d3e3fd; /* Hover đổi màu xanh nhạt */
        color: #0b57d0;
    }

    /* --- THANH NHẬP LIỆU (INPUT BAR) --- */
    .stChatInputContainer {
        padding-bottom: 30px;
        padding-left: 60px; /* Chừa chỗ cho nút (+) bên trái */
    }
    
    .stChatInputContainer > div {
        background-color: #f0f4f9; /* Nền thanh chat */
        border-radius: 30px; /* Bo tròn viên thuốc */
        border: 1px solid transparent;
        transition: border 0.3s;
    }
    
    /* Khi bấm vào thì viền sáng lên */
    .stChatInputContainer > div:focus-within {
        background-color: #ffffff;
        border: 1px solid #0b57d0; /* Viền xanh Gemini */
        box-shadow: 0 1px 5px rgba(0,0,0,0.1);
    }

    .stChatInputContainer textarea {
        background-color: transparent !important;
        color: #1f1f1f !important;
        border: none !important;
        font-size: 16px;
    }
    
    /* Nút Gửi (Mũi tên) */
    .stChatInputContainer button[kind="primary"] {
        background: transparent !important;
        color: #0b57d0 !important; /* Màu xanh Gemini */
        border: none !important;
    }

    /* TIÊU ĐỀ */
    .title-area {
        text-align: center; margin-top: 20px; margin-bottom: 40px;
    }
    .gemini-title {
        font-size: 3rem; font-weight: 500;
        background: -webkit-linear-gradient(0deg, #4285f4, #9b72cb, #d96570); /* Màu logo Google */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. TIÊU ĐỀ TRANG ---
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.markdown("""
        <div class="title-area">
            <div class="gemini-title">Xin chào, Sếp Vũ</div>
            <div style="color: #888; font-size: 1.5rem;">Hôm nay tôi có thể giúp gì cho bạn?</div>
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
    
# Biến lưu ảnh tạm thời
if "uploaded_img" not in st.session_state:
    st.session_state.uploaded_img = None

# --- 6. MENU CÔNG CỤ (NÚT + NỔI) ---
# Đây là cái nút tròn dấu cộng ở góc dưới
with st.popover("➕", help="Thêm tài liệu"):
    st.markdown("### 📂 Công cụ & Tệp")
    
    # 1. Upload Ảnh/File
    uploaded_file = st.file_uploader("Tải ảnh/tệp lên", type=["jpg", "png", "jpeg", "txt", "pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        try:
            img = Image.open(uploaded_file)
            st.session_state.uploaded_img = img
            st.success("✅ Đã tải ảnh! Hãy gõ nội dung bên dưới để gửi.")
            st.image(img, width=150)
        except:
            st.warning("File này chưa hỗ trợ xem trước, nhưng vẫn gửi được.")

    st.divider()
    
    # 2. Các nút chức năng giả lập (cho giống ảnh)
    col1, col2 = st.columns(2)
    with col1:
        st.button("🔍 Deep Research", use_container_width=True)
        st.button("🎨 Tạo hình ảnh", use_container_width=True)
    with col2:
        st.button("📊 Phân tích Data", use_container_width=True)
        st.button("💻 Viết Code", use_container_width=True)

# --- 7. HIỂN THỊ LỊCH SỬ CHAT ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="user-row">
                <div class="user-bubble">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Icon Google Gemini
        icon_url = "https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg"
        st.markdown(f"""
            <div class="bot-row">
                <img src="{icon_url}" width="30" height="30" style="margin-top: 5px;">
                <div class="bot-bubble">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 8. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nhập câu lệnh tại đây...")

if user_input:
    # Xử lý hiển thị phía User
    display_text = user_input
    if st.session_state.uploaded_img:
        display_text = f"[Đã gửi 1 ảnh] <br> {user_input}"
        # Hiển thị ảnh nhỏ trong khung chat
        st.markdown(f"""
            <div class="user-row">
                <div class="user-bubble">{display_text}</div>
            </div>
        """, unsafe_allow_html=True)
        # Show ảnh ra màn hình chính (dùng st.image cho đẹp)
        with st.chat_message("user", avatar=None):
            st.image(st.session_state.uploaded_img, width=300)
    else:
        st.markdown(f"""
            <div class="user-row">
                <div class="user-bubble">{user_input}</div>
            </div>
        """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": display_text})

    # Gửi qua Gemini
    try:
        inputs = [user_input]
        if st.session_state.uploaded_img:
            inputs.append(st.session_state.uploaded_img)
            # Reset ảnh sau khi gửi để không gửi lại lần sau
            st.session_state.uploaded_img = None 

        with st.spinner("Gemini đang suy nghĩ..."):
            response = st.session_state.chat_session.send_message(inputs)
            bot_reply = response.text
        
        # Hiển thị Bot trả lời
        icon_url = "https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg"
        st.markdown(f"""
            <div class="bot-row">
                <img src="{icon_url}" width="30" height="30" style="margin-top: 5px;">
                <div class="bot-bubble">{bot_reply}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")