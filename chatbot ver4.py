import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB ---
# Sử dụng theme mặc định (light) của Streamlit để giống ảnh mẫu
st.set_page_config(page_title="Lê Vũ AI Chat", page_icon="🤖")

# --- 2. CSS GIAO DIỆN MỚI (SẠCH SẼ - LIGHT MODE) ---
st.markdown("""
<style>
    /* --- CẤU HÌNH CHUNG --- */
    /* Ẩn header và footer mặc định của Streamlit cho gọn */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tăng khoảng cách dướí cùng để không bị che bởi thanh nhập liệu */
    .block-container {
        padding-bottom: 120px;
    }

    /* --- STYLE CHO BONG BÓNG CHAT --- */
    
    /* Container chung cho các dòng chat để căn chỉnh khoảng cách */
    .chat-row {
        display: flex;
        margin-bottom: 20px;
        align-items: flex-start; /* Căn hàng trên cùng */
    }

    /* --- USER (Người dùng) --- */
    .user-row {
        justify-content: flex-end; /* Căn phải */
    }
    .user-bubble {
        background-color: #0084ff; /* Màu xanh dương giống Messenger/ảnh mẫu */
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px; /* Bo góc tạo hình bong bóng thoại */
        max-width: 80%;
        word-wrap: break-word;
        font-size: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    /* --- BOT (Trợ lý AI) --- */
    .bot-row {
        justify-content: flex-start; /* Căn trái */
    }
    /* Icon robot bên cạnh tin nhắn bot */
    .bot-icon {
        width: 35px;
        height: 35px;
        margin-right: 10px;
        border-radius: 50%;
        /* Dùng ảnh icon robot (Sếp có thể thay link khác nếu thích) */
        background-image: url('https://cdn-icons-png.flaticon.com/512/4712/4712139.png');
        background-size: cover;
    }
    .bot-bubble {
        background-color: #f0f2f5; /* Màu xám nhạt */
        color: #050505; /* Chữ màu đen */
        padding: 12px 18px;
        border-radius: 4px 18px 18px 18px; /* Bo góc ngược lại với User */
        max-width: 80%;
        word-wrap: break-word;
        font-size: 16px;
    }
    
    /* --- TIÊU ĐỀ --- */
    .main-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 30px;
    }

    /* --- TÙY CHỈNH THANH NHẬP LIỆU (Cho gọn hơn) --- */
    .stChatInputContainer {
        padding-bottom: 30px;
    }
    [data-testid="stChatInput"] {
        border-radius: 25px;
        border: 1px solid #ddd;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN TIÊU ĐỀ (Đơn giản hóa) ---
st.markdown('<div class="main-title">🤖 Lê Vũ AI Assistant</div>', unsafe_allow_html=True)


# --- 4. CẤU HÌNH API (GIỮ NGUYÊN) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa có chìa khóa! Vào Settings -> Secrets để điền API Key.")
    st.stop()

# --- 5. KHỞI TẠO BOT (GIỮ NGUYÊN) ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        # Cập nhật lại prompt một chút cho phù hợp với giao diện nghiêm túc hơn (tùy Sếp)
        system_instruction="Bạn là trợ lý AI ảo của Lê Vũ. Bạn thông minh, hữu ích và trả lời ngắn gọn, đi thẳng vào vấn đề. Nếu có ảnh, hãy phân tích nó."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. NÚT GỬI ẢNH (GIỮ NGUYÊN CHỨC NĂNG) ---
# Dùng expander mặc định của Streamlit, nó sẽ tự ăn theo giao diện sáng
with st.expander("📸 Tải ảnh lên (Nếu cần)"):
    uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg", "png", "jpeg"])
    image_to_send = None
    if uploaded_file:
        image_to_send = Image.open(uploaded_file)
        st.image(image_to_send, width=200, caption="Ảnh đã chọn")

# --- 7. HIỂN THỊ LỊCH SỬ CHAT (CẬP NHẬT HTML/CSS MỚI) ---
for message in st.session_state.messages:
    if message["role"] == "user":
        # Tin nhắn người dùng (Xanh, phải)
        st.markdown(f"""
            <div class="chat-row user-row">
                <div class="user-bubble">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Tin nhắn Bot (Xám, trái, có icon)
        st.markdown(f"""
            <div class="chat-row bot-row">
                <div class="bot-icon"></div>
                <div class="bot-bubble">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 8. XỬ LÝ GỬI TIN (GIỮ NGUYÊN LOGIC) ---
user_input = st.chat_input("Nhập tin nhắn của bạn...")

# Logic gửi: Bấm Enter hoặc bấm nút "Gửi ảnh ngay"
send_button = False
if image_to_send: 
    send_button = st.button("Gửi ảnh ngay")

if user_input or (image_to_send and send_button):
    
    display_text = user_input if user_input else "[Đã gửi một hình ảnh]"
    
    # 1. Hiện tin nhắn User ngay lập tức (Giao diện mới)
    st.markdown(f"""
        <div class="chat-row user-row">
            <div class="user-bubble">{display_text}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Hiện ảnh nếu có (Dùng component chuẩn của Streamlit cho đẹp)
    if image_to_send:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.image(image_to_send, width=300)

    st.session_state.messages.append({"role": "user", "content": display_text})

    # 3. Gửi Gemini và chờ phản hồi
    try:
        inputs = []
        if user_input:
            inputs.append(user_input)
        else:
            inputs.append("Hãy nhận xét về bức ảnh này.")
            
        if image_to_send:
            inputs.append(image_to_send)

        # Spinner mặc định sẽ đẹp hơn trên nền sáng
        with st.spinner("Đang suy nghĩ..."):
            response = st.session_state.chat_session.send_message(inputs)
            bot_reply = response.text
        
        # 4. Hiện phản hồi của Bot (Giao diện mới)
        st.markdown(f"""
            <div class="chat-row bot-row">
                <div class="bot-icon"></div>
                <div class="bot-bubble">{bot_reply}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")