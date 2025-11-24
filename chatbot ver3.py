import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB & API ---
st.set_page_config(page_title="Gemini-Style Chat", page_icon="✨", layout="centered")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa có chìa khóa! Vào Settings -> Secrets để điền API Key.")
    st.stop()

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel('models/gemini-1.5-flash') # Dùng 1.5 Flash cho nhanh
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. CSS SIÊU CẤP (GIAO DIỆN GEMINI DARK MODE) ---
st.markdown("""
<style>
    /* --- TỔNG THỂ & NỀN --- */
    [data-testid="stAppViewContainer"] {
        background-color: #131314; /* Màu nền đen xám chuẩn Gemini */
        color: #E3E3E3;
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    
    /* Ẩn các phần thừa */
    #MainMenu, footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* --- THANH CUỘN CHAT (QUAN TRỌNG ĐỂ KHÔNG BỊ CHE) --- */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 160px !important; /* Chừa khoảng trống lớn ở dưới cho thanh nhập liệu */
        max-width: 800px; /* Giới hạn chiều rộng để dễ đọc như Gemini */
    }

    /* --- STYLE BONG BÓNG CHAT --- */
    /* Loại bỏ style mặc định */
    .stChatMessage { background-color: transparent !important; border: none !important; }
    [data-testid="stChatMessageAvatarBackground"] { display: none; }

    /* Style cho User (bên phải) */
    [data-testid="stChatMessage"][data-testid="user"] {
        justify-content: flex-end;
        padding-right: 0;
    }
    [data-testid="stChatMessage"][data-testid="user"] [data-testid="stChatMessageContent"] {
        background-color: #303136; /* Màu xám đậm của User */
        color: #E3E3E3;
        border-radius: 20px 20px 5px 20px; /* Bo tròn góc */
        padding: 10px 15px;
        max-width: 80%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    /* Style cho Bot (bên trái) */
    [data-testid="stChatMessage"][data-testid="assistant"] [data-testid="stChatMessageContent"] {
        background-color: transparent; /* Bot nền trong suốt */
        color: #E3E3E3;
        padding: 0;
        max-width: 100%;
    }
    /* Thêm icon Gemini trước câu trả lời */
    [data-testid="stChatMessage"][data-testid="assistant"] [data-testid="stChatMessageContent"]::before {
        content: "✨";
        margin-right: 10px;
        font-size: 1.2rem;
    }

    /* --- KHU VỰC NHẬP LIỆU CỐ ĐỊNH Ở ĐÁY (GEMINI STYLE) --- */
    
    /* 1. Style nút Upload cho nhỏ gọn */
    [data-testid="stFileUploader"] {
        padding-bottom: 5px;
    }
    [data-testid="stFileUploader"] section {
        padding: 0;
        background-color: transparent;
        border: none;
        min-height: 0px;
    }
    /* Ẩn icon và chữ mặc định to đùng */
    [data-testid="stFileUploader"] [data-testid="stUploadDropzone"] > div:first-child,
    [data-testid="stFileUploader"] small {
         display: none;
    }
    /* Style lại nút bấm "Browse files" thành icon nhỏ */
    [data-testid="stFileUploader"] button {
        background: transparent;
        color: #A8C7FA; /* Màu xanh Gemini */
        border: 1px solid #A8C7FA;
        border-radius: 20px;
        padding: 5px 15px;
        font-size: 0.8rem;
        transition: all 0.3s;
    }
    [data-testid="stFileUploader"] button:hover {
        background: rgba(168, 199, 250, 0.1);
    }
    /* Thay chữ "Browse files" bằng icon */
    [data-testid="stFileUploader"] button::before { content: "🖼️ Thêm ảnh "; }
    [data-testid="stFileUploader"] button div { display: none; }


    /* 2. Style thanh Chat Input */
    .stChatInputContainer {
        padding-bottom: 20px;
        background-color: #131314; /* Nền trùng màu app để che nội dung khi cuộn */
        pt
    }
    [data-testid="stChatInput"] {
        background-color: #303136; /* Nền thanh input xám */
        border-radius: 30px;
        border: 1px solid #444746;
        color: white;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #A8C7FA; /* Viền xanh khi gõ */
    }
    [data-testid="stChatInput"] textarea {
        color: white !important;
    }
    /* Nút gửi */
    [data-testid="stChatInputSubmitButton"] {
        color: #A8C7FA !important;
    }

    /* Ảnh preview nhỏ */
    .img-preview {
        border-radius: 10px;
        border: 2px solid #A8C7FA;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. TIÊU ĐỀ (Đơn giản) ---
st.markdown("<h2 style='text-align: center; color: #E3E3E3;'>✨ Gemini Chat Lite</h2>", unsafe_allow_html=True)


# --- 4. HIỂN THỊ LỊCH SỬ CHAT ---
# Tạo container để đẩy nội dung lên trên, không bị thanh input che
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Nếu nội dung là list (chứa ảnh)
            if isinstance(message["content"], list):
                for item in message["content"]:
                    if isinstance(item, str):
                        st.markdown(item)
                    elif isinstance(item, Image.Image):
                        st.image(item, width=300)
            # Nếu nội dung là text thường
            else:
                st.markdown(message["content"])


# --- 5. KHU VỰC NHẬP LIỆU Ở ĐÁY ---
# Dùng container cố định để tạo cảm giác giống app
with st.container():
    # 5.1. Nút upload file (Đã style nhỏ gọn bằng CSS)
    uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

    img_data = None
    # Nếu có ảnh, hiện preview nhỏ ngay trên thanh chat
    if uploaded_file:
        img_data = Image.open(uploaded_file)
        st.image(img_data, width=80, caption="Sẵn sàng gửi", output_format="PNG", className="img-preview")

    # 5.2. Thanh nhập liệu chính
    if prompt := st.chat_input("Nhập tin nhắn hoặc gửi ảnh..."):
        # --- XỬ LÝ KHI BẤM GỬI ---
        
        # 1. Chuẩn bị nội dung gửi và hiển thị cho User
        content_to_send = []
        content_to_display = []

        if prompt:
            content_to_send.append(prompt)
            content_to_display.append(prompt)
        
        if img_data:
            content_to_send.append(img_data)
            content_to_display.append(img_data)
            # Nếu chỉ gửi ảnh mà không gõ chữ
            if not prompt:
                 content_to_send.insert(0, "Hãy mô tả bức ảnh này.") # Thêm prompt mặc định cho Gemini

        # Hiển thị ngay lập tức tin nhắn của user
        with chat_container:
            with st.chat_message("user"):
                if prompt: st.markdown(prompt)
                if img_data: st.image(img_data, width=300)
        
        # Lưu vào lịch sử (lưu nội dung hiển thị)
        st.session_state.messages.append({"role": "user", "content": content_to_display})

        # 2. Gửi cho Gemini và chờ phản hồi
        try:
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Đang suy nghĩ..."):
                        response = st.session_state.chat_session.send_message(content_to_send)
                        st.markdown(response.text)
            
            # Lưu phản hồi của bot
            st.session_state.messages.append({"role": "assistant", "content": response.text})

        except Exception as e:
            with chat_container:
                 st.error(f"Lỗi: {e}")

# Lưu ý: Để giao diện này hoạt động hoàn hảo, cần một chút thủ thuật CSS để ẩn đi
# các phần tử mặc định của file uploader và thay bằng icon.
# Code trên đã bao gồm CSS đó.