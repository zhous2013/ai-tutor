"""
SUTD AI 课程助教
基于苏格拉底式提问法的智能辅导系统
"""

import streamlit as st
import httpx

# =============================================================================
# 页面配置
# =============================================================================
st.set_page_config(
    page_title="SUTD AI 课程助教",
    page_icon="🎓",
    layout="wide"
)

# =============================================================================
# 初始化 Session State
# =============================================================================
# 存储消息列表（包含用户和 AI 的对话记录）
if "messages" not in st.session_state:
    st.session_state.messages = []

# 存储选择的数据源类型
if "api_source" not in st.session_state:
    st.session_state.api_source = "secrets"  # 默认使用 secrets

# =============================================================================
# 硬编码的 AI 角色设定（System Prompt）
# =============================================================================
SYSTEM_PROMPT = """你现在是 SUTD (新加坡科技与设计大学) '人工智能在教育中的应用' 课程的资深教授兼 AI 助教。

你的核心教学法是苏格拉底式提问法 (Socratic Method)。

无论学生问什么问题，你绝对不能直接给出完整答案或直接写出完整代码。

你必须：

先肯定学生的提问，给予鼓励。

给出一点点核心提示或概念解释。

用一个启发性的问题作为结尾，引导学生自己思考出下一步或得出结论。

语气要专业、温和、富有学术严谨性，时刻展现出一位顶尖教育者的素养。"""

# =============================================================================
# 核心功能函数
# =============================================================================

def get_ai_response(api_key, model_name, messages):
    """
    使用 httpx 直接调用智谱 AI 大模型获取回复

    Args:
        api_key: 智谱 API Key
        model_name: 模型名称（glm-4.0）
        messages: 对话历史列表

    Returns:
        AI 的回复文本，或错误信息字符串
    """
    # 智谱海外版 API 端点
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    # 请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 构建完整的对话列表，包含 System Prompt
    full_conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    full_conversation.extend(messages)

    # 请求体
    data = {
        "model": "glm-4.7",
        "messages": full_conversation,
        "temperature": 0.7
    }

    try:
        # 使用 httpx 发送请求
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

            # 解析并返回 AI 的回复内容
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "⚠️ AI 返回了空响应，请重试。"

    except httpx.HTTPStatusError as e:
        # HTTP 错误处理
        try:
            error_detail = e.response.json()
            error_msg = error_detail.get('error', {}).get('message', str(e))

            # 根据错误类型返回不同的提示
            if "401" in str(e.response.status_code) or "unauthorized" in str(e).lower():
                return "⚠️ API Key 无效，请检查配置。"
            elif "429" in str(e.response.status_code):
                return "⚠️ API 调用频率超限，请稍后重试。"
            elif "500" in str(e.response.status_code):
                return "⚠️ 智谱服务暂时不可用，请稍后重试。"
            else:
                return f"⚠️ HTTP 错误: {error_msg}"

        except:
            return f"⚠️ HTTP 错误: {e.response.status_code}"

    except httpx.ConnectError:
        return "⚠️ 网络连接失败，请检查网络后重试。"

    except httpx.TimeoutException:
        return "⚠️ 请求超时，请稍后重试。"

    except Exception as e:
        return f"⚠️ 发生未知错误: {str(e)}"


def clear_chat_history():
    """
    清空对话历史记录
    """
    st.session_state.messages = []
    st.rerun()


# =============================================================================
# 主界面 - 侧边栏配置区域
# =============================================================================

with st.sidebar:
    # 侧边栏标题
    st.title("⚙️ 配置")

    st.divider()

    # --------------------
    # 1. 数据源选择
    # --------------------
    st.subheader("📊 数据源选择")

    # 使用单选按钮选择数据源
    source = st.radio(
        "选择 API Key 来源",
        options=["配置文件（Secrets）", "手动输入"],
        index=0 if st.session_state.api_source == "secrets" else 1,
        help="Secrets 优先级更高"
    )

    # 保存用户的选择
    st.session_state.api_source = source

    st.divider()

    # --------------------
    # 2. API Key 配置
    # --------------------
    st.subheader("🔑 API 配置")

    # 根据数据源显示不同的输入框
    if source == "secrets":
        # 使用 secrets 时，不显示输入框，只显示状态
        try:
            api_key = st.secrets["ZHIPUAI_API_KEY"]
            st.success("✅ 使用配置文件中的 API Key")
            # 存储到 session state
            st.session_state.api_key = api_key
        except KeyError:
            st.warning("⚠️ 配置文件中未找到 API Key")
            st.session_state.api_key = ""
    else:
        # 手动输入模式
        api_key = st.text_input(
            label="智谱 API Key",
            type="password",
            value=st.session_state.get("api_key", ""),
            placeholder="请输入智谱海外版 API Key",
            help="获取地址: https://z.ai/manage-apikey/apikey-list"
        )

        # 保存用户输入的 API Key 到 Session State
        if api_key:
            st.session_state.api_key = api_key

        # 显示当前使用的 API Key
        if st.session_state.api_key:
            st.caption(f"🔑 API Key 已配置 (长度: {len(st.session_state.api_key)})")
        else:
            st.caption("⚠️ API Key 未配置")

    st.divider()

    # --------------------
    # 3. 会话管理
    # --------------------
    st.subheader("💾 会话管理")

    if st.button(
        label="🗑️ 清空对话历史",
        type="secondary",
        use_container_width=True
    ):
        clear_chat_history()

    # 显示当前对话轮数
    if st.session_state.messages:
        st.caption(f"当前对话轮数: {len(st.session_state.messages)}")

# =============================================================================
# 主界面 - 交互区域
# =============================================================================

# 头部区域：大标题和欢迎语
st.title("🎓 SUTD AI 课程助教")

st.markdown(
    """
    本系统基于 **苏格拉底式提问法** 设计，旨在通过启发式对话，
    引导你自主思考与探索，而非直接提供答案。

    无论遇到什么课程疑难，我都会以温和而专业的方式陪伴你学习。
    """
)

st.markdown("---")

# 对话区域：展示历史消息
for message in st.session_state.messages:
    # 根据消息角色显示不同的头像
    if message["role"] == "user":
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(message["content"])
    else:  # assistant
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message["content"])

# 输入区域：聊天输入框
user_input = st.chat_input(
    placeholder="请输入你关于课程的疑问..."
)

# =============================================================================
# 用户输入处理逻辑
# =============================================================================

if user_input:
    # 状态检查：如果没有配置 API Key，拦截请求并给出提示
    if not st.session_state.api_key:
        if st.session_state.api_source == "secrets":
            st.warning("⚠️ 配置文件中未找到有效的 API Key，请在 Streamlit Cloud Secrets 中配置")
        else:
            st.warning("⚠️ 请先输入智谱 API Key 后再开始对话")
        st.stop()

    # 显示用户消息
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(user_input)

    # 将用户消息添加到对话历史
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 调用 AI 获取回复
    with st.chat_message("assistant", avatar="🤖"):
        # 显示加载状态
        with st.spinner("思考中..."):
            # 调用 API 并获取回复
            ai_response = get_ai_response(
                api_key=st.session_state.api_key,
                model_name="glm-4.0",
                messages=st.session_state.messages
            )
            st.markdown(ai_response)

    # 将 AI 回复添加到对话历史
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
