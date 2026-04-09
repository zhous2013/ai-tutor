"""
SUTD AI 课程助教
基于苏格拉底式提问法的智能辅导系统
"""

import streamlit as st
from zhipuai import ZhipuAI

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

# 存储智谱 API Key（从 Secrets 优先读取）
try:
    # 尝试从 Streamlit Cloud Secrets 读取
    if "zhipu_api_key" not in st.session_state:
        st.session_state.zhipu_api_key = st.secrets["ZHIPUAI_API_KEY"]
except KeyError:
    # 如果没有 Secrets，使用空值
    if "zhipu_api_key" not in st.session_state:
        st.session_state.zhipu_api_key = ""

# 存储选择的模型名称
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "glm-4.7"  # 默认选中 glm-4.7

# 存储智谱 AI 客户端实例（避免重复创建）
if "zhipu_client" not in st.session_state:
    st.session_state.zhipu_client = None

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

def initialize_zhipu_client(api_key):
    """
    初始化智谱 AI 客户端

    Args:
        api_key: 智谱 API Key

    Returns:
        ZhipuAI 客户端实例
    """
    try:
        return ZhipuAI(api_key=api_key)
    except Exception as e:
        st.error(f"❌ 初始化客户端失败: {str(e)}")
        return None


def get_ai_response(client, model_name, messages):
    """
    调用智谱 AI 大模型获取回复

    Args:
        client: ZhipuAI 客户端实例
        model_name: 模型名称（glm-4.7 或 glm-4-flash）
        messages: 对话历史列表

    Returns:
        AI 的回复文本，或错误信息字符串
    """
    # 构建完整的对话列表，包含 System Prompt
    full_conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    full_conversation.extend(messages)

    try:
        # 调用智谱 AI API
        response = client.chat.completions.create(
            model=model_name,
            messages=full_conversation,
            temperature=0.7,  # 稍高的温度值，保持一定的创造性
        )
        # 返回 AI 的回复内容
        return response.choices[0].message.content
    except Exception as e:
        # 拦截异常并返回友好的错误信息
        error_msg = str(e)
        # 检查是否是 API Key 相关错误
        if "API" in error_msg or "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            return f"⚠️ 智谱 API Key 验证失败，请检查左侧配置的 API Key 是否正确。"
        # 检查是否是模型相关错误
        elif "model" in error_msg:
            return f"⚠️ 模型调用失败，请尝试切换其他模型。"
        # 其他错误
        else:
            return f"⚠️ 调用智谱 API 时发生错误: {error_msg}"


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
    # 1. API Key 配置
    # --------------------
    st.subheader("🔑 API 配置")

    zhipu_api_key = st.text_input(
        label="智谱 API Key",
        type="password",
        value=st.session_state.zhipu_api_key,
        placeholder="请输入智谱海外版 API Key",
        help="获取地址: https://z.ai/manage-apikey/apikey-list"
    )

    # 保存用户输入的 API Key 到 Session State
    if zhipu_api_key != st.session_state.zhipu_api_key:
        st.session_state.zhipu_api_key = zhipu_api_key
        # 当 API Key 变化时，清除旧的客户端实例
        st.session_state.zhipu_client = None

    st.divider()

    # --------------------
    # 2. 模型选择
    # --------------------
    st.subheader("🤖 模型选择")

    available_models = ["glm-4.7", "glm-4-flash"]

    # 使用 selectbox 让用户选择模型，默认选中 glm-4.7
    selected_model = st.selectbox(
        label="选择大模型",
        options=available_models,
        index=0 if st.session_state.selected_model not in available_models else available_models.index(st.session_state.selected_model),
        help="glm-4.7: 更强大的模型；glm-4-flash: 快速响应的模型"
    )

    # 保存用户选择的模型到 Session State
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model

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
    if not st.session_state.zhipu_api_key:
        st.warning("⚠️ 请先在左侧边栏输入智谱 API Key 后再开始对话")
        st.stop()

    # 初始化智谱 AI 客户端（如果尚未初始化）
    if st.session_state.zhipu_client is None:
        st.session_state.zhipu_client = initialize_zhipu_client(st.session_state.zhipu_api_key)

    # 检查客户端是否成功初始化
    if st.session_state.zhipu_client is None:
        st.error("❌ 无法初始化智谱 AI 客户端，请检查 API Key 是否正确")
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
                client=st.session_state.zhipu_client,
                model_name=st.session_state.selected_model,
                messages=st.session_state.messages
            )
            st.markdown(ai_response)

    # 将 AI 回复添加到对话历史
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
