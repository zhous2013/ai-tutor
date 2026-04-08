import streamlit as st
from openai import OpenAI

# 页面配置
st.set_page_config(
    page_title="AI 教育助手",
    page_icon="🎓",
    layout="wide"
)

# 从 secrets 读取 API Key（部署时使用）
try:
    if not st.session_state.get("api_key"):
        st.session_state.api_key = st.secrets["OPENAI_API_KEY"]
except (KeyError, FileNotFoundError):
    pass

# 初始化 session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
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

def get_ai_response(api_key, messages, system_prompt):
    """调用 OpenAI API 获取响应"""
    client = OpenAI(api_key=api_key)

    # 添加系统提示词
    conversation = [{"role": "system", "content": system_prompt}]
    conversation.extend(messages)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 发生错误: {str(e)}"

# 侧边栏
with st.sidebar:
    st.title("⚙️ 设置")

    # API Key 输入
    try:
        default_key = st.secrets["OPENAI_API_KEY"]
        placeholder = "已从配置读取"
    except (KeyError, FileNotFoundError):
        default_key = ""
        placeholder = "sk-..."

    api_key = st.text_input(
        "OpenAI API Key",
        value=default_key,
        type="password",
        placeholder=placeholder,
        help="部署时会从 secrets 自动读取"
    )

    # 保存 API Key 到 session state
    if api_key:
        st.session_state.api_key = api_key

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

# 聊天历史显示
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👨‍🏫" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# 用户输入
prompt = st.chat_input("请输入你的问题...")
if prompt:
    if not st.session_state.api_key:
        st.error("⚠️ 请先在左侧边栏输入你的 OpenAI API Key")
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
                st.session_state.messages,
                st.session_state.system_prompt
            )
            st.markdown(response)

    # 添加 AI 响应到历史
    st.session_state.messages.append({"role": "assistant", "content": response})
