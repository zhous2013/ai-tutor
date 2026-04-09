# 部署指南

## Streamlit Cloud 部署

### 1. 配置 Secrets

访问你的 Streamlit Cloud 应用，进入 **Settings** → **Secrets**

#### 智谱海外版 (z.ai) 配置：

```toml
OPENAI_API_KEY = "你的智谱海外版API Key"
API_BASE = "https://api.z.ai/api/coding/paas/v4"
MODEL = "glm-4"
```

#### OpenAI 配置：

```toml
OPENAI_API_KEY = "sk-你的OpenAI密钥"
API_BASE = "https://api.openai.com/v1"
MODEL = "gpt-4o-mini"
```

### 2. 配置注意事项

1. **使用双引号**：`"` 不是单引号 `'`
2. **完整的 API Key**：确保从开头到结尾都复制了
3. **保存配置**：点击 Save 按钮确认
4. **等待生效**：配置后等待约 1 分钟，应用会自动重启

### 3. 常见问题

#### 问题：Secrets 不生效

**解决方案**：
1. 删除 Secrets 中的所有配置
2. 重新输入（确保格式正确）
3. 点击 Save 保存
4. 刷新应用页面
5. 查看左侧边栏是否显示 "✅ 已从环境配置读取 API 设置"

#### 问题：显示 OpenAI 错误但配置的是智谱

**解决方案**：
- 检查 Secrets 中的 `API_BASE` 是否正确设置为智谱的地址
- 确认 Secrets 配置格式没有多余的空格或引号
- 刷新应用让 Secrets 配置重新加载

### 4. 调试信息

应用会在错误消息中显示：
- 实际使用的 API 端点
- 实际使用的模型

通过这些信息可以确认配置是否正确加载。
