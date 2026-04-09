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
    st.session_state.system_prompt = """你是一位来自新加坡科技设计大学 (SUTD) 的资深 AI 教育学教授。

你的教育理念：
1. 采用苏格拉底式教学方法，通过提问引导学生独立思考
2. 鼓励学生探索问题的本质，而非直接给出答案
3. 提供启发性建议，帮助学生建立批判性思维
4. 回答问题时，先确认学生对基础概念的理解程度
5. 使用简洁清晰的语言，避免过于复杂的术语
6. 在适当时候提供实际案例和应用场景

回答风格：
- 亲切、专业，像一位耐心的大师
- 经常以反问句引导学生深入思考
- 鼓励学生表达自己的见解
- 肯定学生的正确思考方向

请用中文回答，保持教育的专业性和启发性。"""

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
        # 使用 follow_redirects=True 自动跟随重定向
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
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
    st.title("⚙️ 设置")

    # 显示 Secrets 配置状态
    if has_secrets:
        st.success("✅ 已从环境配置读取 API 设置")
    else:
        st.warning("⚠️ 未检测到环境配置，请手动输入")

    st.divider()

    # API Provider 预设
    provider = st.selectbox(
        "选择 API 提供商",
        ["OpenAI", "智谱海外版 (z.ai)", "智谱国内版 (GLM)", "自定义"],
        help="选择预设或自定义 API 端点"
    )

    # 根据预设填充默认值
    if provider == "OpenAI":
        default_base = "https://api.openai.com/v1"
        default_model = "gpt-4o-mini"
    elif provider == "智谱海外版 (z.ai)":
        default_base = "https://open.bigmodel.ai/api/paas/v4"
        default_model = "glm-4"
    elif provider == "智谱国内版 (GLM)":
        default_base = "https://open.bigmodel.cn/api/paas/v4"
        default_model = "glm-4.7"
    else:
        default_base = st.session_state.api_base
        default_model = st.session_state.model

    st.divider()

    # API 配置
    st.subheader("🔌 API 配置")

    api_base = st.text_input(
        "API Base URL",
        value=default_base,
        placeholder="https://api.openai.com/v1",
        help="API 服务的基础地址"
    )

    model = st.text_input(
        "模型名称",
        value=default_model,
        placeholder="gpt-4o-mini",
        help="使用的模型名称"
    )

    st.divider()

    # API Key 输入
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="输入你的 API Key",
        help="部署时会从 secrets 自动读取"
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
        st.caption(f"🔑 API Key 已配置 (长度: {len(st.session_state.api_key)})")
        st.caption(f"🌐 API 端点: {st.session_state.api_base}")
        st.caption(f"🤖 模型: {st.session_state.model}")
        if provider == "智谱海外版 (z.ai)":
            st.caption("📖 文档: https://z.ai/docs")
    else:
        st.caption("⚠️ API Key 未配置")

    st.divider()

    # System Prompt 编辑
    st.subheader("📝 系统提示词")
    st.markdown("自定义 AI 助手的角色和行为：")
    system_prompt = st.text_area(
        "System Prompt",
        value=st.session_state.system_prompt,
        height=300,
        help="这定义了 AI 的角色设定和回答风格"
    )

    # 保存 System Prompt 到 session state
    if system_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = system_prompt

    st.divider()

    # 清空聊天记录按钮
    if st.button("🗑️ 清空聊天记录", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    # 显示聊天记录数量
    st.caption(f"当前对话轮数: {len(st.session_state.messages) // 2}")

# 主界面
st.title("🎓 SUTD AI 教育助手")
st.markdown("---")

# 显示 API Key 提示
if not st.session_state.api_key:
    st.error("⚠️ 请先在左侧边栏配置 API Key 后再开始对话")
    st.info("📌 部署到 Streamlit Cloud 时，请在 Settings → Secrets 中添加：")
    st.code("OPENAI_API_KEY = \"你的密钥\"")
    st.code("API_BASE = \"https://api.openai.com/v1\"  # 可选")
    st.code("MODEL = \"gpt-4o-mini\"  # 可选")

# 聊天历史显示
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👨‍🏫" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# 用户输入
prompt = st.chat_input("请输入你的问题...")
if prompt:
    if not st.session_state.api_key:
        st.error("⚠️ 请先在左侧边栏输入 API Key")
        st.stop()

    # 显示用户消息
    st.chat_message("user", avatar="👤").markdown(prompt)

    # 添加到历史
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 获取 AI 响应
    with st.chat_message("assistant", avatar="👨‍🏫"):
        with st.spinner("思考中..."):
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
