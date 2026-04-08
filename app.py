import streamlit as st
import httpx
import json

# 页面配置
st.set_page_config(
    page_title="AI 教育助手",
    page_icon="🎓",
    layout="wide"
)

# 从 secrets 读取配置
has_secrets = False
try:
    if not st.session_state.get("api_key"):
        st.session_state.api_key = st.secrets["OPENAI_API_KEY"]
        has_secrets = True
    if not st.session_state.get("api_base"):
        st.session_state.api_base = st.secrets.get("API_BASE", "https://api.openai.com/v1")
    if not st.session_state.get("model"):
        st.session_state.model = st.secrets.get("MODEL", "gpt-4o-mini")
except (KeyError, FileNotFoundError):
    has_secrets = False

# 初始化 session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_base" not in st.session_state:
    st.session_state.api_base = "https://api.openai.com/v1"
if "model" not in st.session_state:
    st.session_state.model = "gpt-4o-mini"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = """You are a senior AI education professor from SUTD (Singapore University of Technology and Design).

Your educational philosophy:
1. Use the Socratic method to guide students to think independently through questioning
2. Encourage students to explore the essence of problems rather than giving direct answers
3. Provide thought-provoking suggestions to help students develop critical thinking
4. When answering, first confirm the student's understanding of basic concepts
5. Use clear and concise language, avoiding overly complex terminology
6. Provide real-world cases and application scenarios when appropriate

Your response style:
- Friendly and professional, like a patient mentor
- Use rhetorical questions to guide deeper thinking
- Encourage students to express their insights
- Affirm the student's correct thinking direction

Please respond in Chinese, maintaining educational professionalism and inspiration."""

def get_ai_response(api_key, api_base, model, messages, system_prompt):
    """使用 httpx 直接调用 API"""
    # 确保 api_base 不以斜杠结尾（避免双斜杠问题）
    api_base = api_base.rstrip('/')

    # 添加系统提示词
    conversation = [{"role": "system", "content": system_prompt}]
    conversation.extend(messages)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": conversation,
        "temperature": 0.7
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{api_base}/chat/completions",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json()
            return f"❌ API 错误: {error_detail.get('error', {}).get('message', str(e))}"
        except:
            return f"❌ HTTP 错误: {e.response.status_code}"
    except Exception as e:
        return f"❌ 发生错误: {str(e)}"

# 侧边栏
with st.sidebar:
    st.title("Settings")

    # 显示 Secrets 配置状态
    if has_secrets:
        st.success("API settings loaded from environment")
    else:
        st.warning("No environment API detected, please enter manually")

    st.divider()

    # API Provider 预设
    provider = st.selectbox(
        "Select API Provider",
        ["OpenAI", "Zhipu AI (GLM)", "Custom"],
        help="Select preset or custom API endpoint"
    )

    # 根据预设填充默认值
    if provider == "OpenAI":
        default_base = "https://api.openai.com/v1"
        default_model = "gpt-4o-mini"
    elif provider == "Zhipu AI (GLM)":
        default_base = "https://open.bigmodel.cn/api/paas/v4"
        default_model = "glm-4.7"
    else:
        default_base = st.session_state.api_base
        default_model = st.session_state.model

    st.divider()

    # API 配置
    st.subheader("API Configuration")

    api_base = st.text_input(
        "API Base URL",
        value=default_base,
        placeholder="https://api.openai.com/v1",
        help="Base URL for the API service"
    )

    model = st.text_input(
        "Model Name",
        value=default_model,
        placeholder="gpt-4o-mini",
        help="Model name to use"
    )

    st.divider()

    # API Key 输入
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="Enter your API Key",
        help="Will be automatically loaded from secrets when deployed"
    )

    # 保存配置到 session state
    if api_key:
        st.session_state.api_key = api_key
    if api_base:
        st.session_state.api_base = api_base
    if model:
        st.session_state.model = model

    # 显示当前配置状态
    if st.session_state.api_key:
        st.caption(f"API Key configured (length: {len(st.session_state.api_key)})")
        st.caption(f"API Endpoint: {st.session_state.api_base}")
        st.caption(f"Model: {st.session_state.model}")
    else:
        st.caption("API Key not configured")

    st.divider()

    # System Prompt 编辑
    st.subheader("System Prompt")
    st.markdown("Customize the AI assistant's role and behavior:")
    system_prompt = st.text_area(
        "System Prompt",
        value=st.session_state.system_prompt,
        height=300,
        help="This defines the AI's role and response style"
    )

    # 保存 System Prompt 到 session state
    if system_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = system_prompt

    st.divider()

    # 清空聊天记录按钮
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    # 显示聊天记录数量
    st.caption(f"Conversation rounds: {len(st.session_state.messages) // 2}")

# 主界面
st.title("SUTD AI Education Assistant")
st.markdown("---")

# 显示 API Key 提示
if not st.session_state.api_key:
    st.error("Please configure API Key in the sidebar first")
    st.info("When deploying to Streamlit Cloud, add the following in Settings -> Secrets:")
    st.code("OPENAI_API_KEY = \"your-key\"")
    st.code("API_BASE = \"https://api.openai.com/v1\"")
    st.code("MODEL = \"gpt-4o-mini\"")

# 聊天历史显示
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="teacher" if message["role"] == "assistant" else "user"):
        st.markdown(message["content"])

# 用户输入
prompt = st.chat_input("Enter your question...")
if prompt:
    if not st.session_state.api_key:
        st.error("Please enter API Key in the sidebar first")
        st.stop()

    # 显示用户消息
    st.chat_message("user", avatar="user").markdown(prompt)

    # 添加到历史
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 获取 AI 响应
    with st.chat_message("assistant", avatar="teacher"):
        with st.spinner("Thinking..."):
            response = get_ai_response(
                st.session_state.api_key,
                st.session_state.api_base,
                st.session_state.model,
                st.session_state.messages,
                st.session_state.system_prompt
            )
            st.markdown(response)

    # 添加 AI 响应到历史
    st.session_state.messages.append({"role": "assistant", "content": response})
