<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Moon, Sunny } from '@element-plus/icons-vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { ElMessage } from 'element-plus';
import 'element-plus/theme-chalk/dark/css-vars.css';

import { login, streamChat } from './api/client';
import type { AgentStep, ChatResponse, UiMessage } from './types';

const username = ref('admin');
const password = ref('admin123456');
const token = ref(localStorage.getItem('token') ?? '');

const userId = ref('u001');
const sessionId = ref('s001');
const department = ref('cs');
const prompt = ref('');
const loading = ref(false);
const streamBuffer = ref('');
const messages = ref<UiMessage[]>([]);
const currentTrace = ref<AgentStep[]>([]);

const darkMode = ref(localStorage.getItem('theme') === 'dark');

const isAuthed = computed(() => token.value.length > 0);

const markdown = (content: string) => DOMPurify.sanitize(marked.parse(content, { breaks: true }) as string);

const applyTheme = () => {
  document.documentElement.classList.toggle('dark', darkMode.value);
  localStorage.setItem('theme', darkMode.value ? 'dark' : 'light');
};

onMounted(() => {
  applyTheme();
});

const toggleTheme = () => {
  darkMode.value = !darkMode.value;
  applyTheme();
};

const doLogin = async () => {
  try {
    const res = await login(username.value, password.value);
    token.value = res.access_token;
    localStorage.setItem('token', res.access_token);
    ElMessage.success('登录成功，已启用 JWT 会话。');
  } catch (error) {
    console.error(error);
    ElMessage.error('登录失败，请检查账号密码。');
  }
};

const submit = async () => {
  if (!prompt.value.trim()) {
    return;
  }

  if (!token.value) {
    ElMessage.warning('请先登录。');
    return;
  }

  const currentPrompt = prompt.value.trim();
  prompt.value = '';
  loading.value = true;
  streamBuffer.value = '';
  currentTrace.value = [];

  messages.value.push({ role: 'user', content: currentPrompt });
  const assistantMessage: UiMessage = { role: 'assistant', content: '' };
  messages.value.push(assistantMessage);

  try {
    await streamChat(
      {
        user_id: userId.value,
        session_id: sessionId.value,
        message: currentPrompt,
        department: department.value
      },
      token.value,
      {
        onToken(tokenChunk) {
          streamBuffer.value += tokenChunk;
          assistantMessage.content = streamBuffer.value;
        },
        onTrace(raw) {
          try {
            const step = JSON.parse(raw) as AgentStep;
            currentTrace.value.push(step);
            assistantMessage.trace = [...currentTrace.value];
          } catch {
            // Ignore malformed trace payload.
          }
        },
        onDone(payload: ChatResponse) {
          assistantMessage.content = payload.answer;
          assistantMessage.trace = payload.trace;
        }
      }
    );
  } catch (error) {
    console.error(error);
    assistantMessage.content = '流式请求失败，请检查网关或后端服务状态。';
    ElMessage.error('流式对话失败');
  } finally {
    loading.value = false;
  }
};

const logout = () => {
  token.value = '';
  localStorage.removeItem('token');
  ElMessage.success('已退出登录。');
};
</script>

<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="title-wrap">
        <h1>Enterprise RAG + ReAct Assistant</h1>
        <p>Vue3 + Element Plus + SSE + JWT + Observability</p>
      </div>
      <div class="header-actions">
        <el-button circle @click="toggleTheme">
          <el-icon>
            <component :is="darkMode ? Sunny : Moon" />
          </el-icon>
        </el-button>
        <el-button v-if="isAuthed" type="danger" plain @click="logout">退出</el-button>
      </div>
    </el-header>

    <el-main class="main-grid">
      <el-card class="panel auth-panel">
        <template #header>
          <strong>认证与会话</strong>
        </template>

        <el-form label-position="top">
          <el-form-item label="Username">
            <el-input v-model="username" autocomplete="off" />
          </el-form-item>
          <el-form-item label="Password">
            <el-input v-model="password" type="password" show-password autocomplete="off" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="doLogin">登录获取 JWT</el-button>
          </el-form-item>
        </el-form>

        <el-divider />

        <el-form label-position="top">
          <el-form-item label="User ID">
            <el-input v-model="userId" />
          </el-form-item>
          <el-form-item label="Session ID">
            <el-input v-model="sessionId" />
          </el-form-item>
          <el-form-item label="Department">
            <el-input v-model="department" />
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="panel chat-panel">
        <template #header>
          <strong>智能对话（Markdown + 流式 SSE）</strong>
        </template>

        <div class="chat-window">
          <div v-for="(message, idx) in messages" :key="idx" class="chat-item" :class="message.role">
            <div class="bubble">
              <div class="role">{{ message.role === 'user' ? '你' : '助手' }}</div>
              <div class="markdown" v-html="markdown(message.content)" />
              <el-collapse v-if="message.trace?.length" class="trace-box">
                <el-collapse-item title="ReAct Trace">
                  <pre>{{ JSON.stringify(message.trace, null, 2) }}</pre>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </div>

        <div class="composer">
          <el-input
            v-model="prompt"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="输入问题，例如：请帮我看下下周课程并生成学习周报"
          />
          <el-button type="primary" :loading="loading" @click="submit">发送（SSE）</el-button>
        </div>
      </el-card>
    </el-main>
  </el-container>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  background: linear-gradient(160deg, #e8f2ff 0%, #f7f9fc 45%, #e6fff5 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
}

.title-wrap h1 {
  margin: 0;
  font-size: 24px;
}

.title-wrap p {
  margin: 4px 0 0;
  color: #667085;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.main-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 16px;
  padding: 0 24px 24px;
}

.panel {
  border-radius: 16px;
}

.chat-window {
  height: 58vh;
  overflow-y: auto;
  padding-right: 8px;
}

.chat-item {
  display: flex;
  margin-bottom: 12px;
}

.chat-item.user {
  justify-content: flex-end;
}

.chat-item.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: min(740px, 90%);
  padding: 12px;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.08);
}

.chat-item.user .bubble {
  background: #0ea5e9;
  color: #ffffff;
}

.role {
  margin-bottom: 6px;
  font-size: 12px;
  opacity: 0.8;
}

.markdown :deep(p) {
  margin: 0 0 8px;
}

.trace-box {
  margin-top: 8px;
}

.trace-box pre {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
}

.composer {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

@media (max-width: 980px) {
  .main-grid {
    grid-template-columns: 1fr;
  }

  .chat-window {
    height: 46vh;
  }
}

:global(html.dark) .layout {
  background: linear-gradient(160deg, #0d1b2a 0%, #111827 45%, #0f172a 100%);
}

:global(html.dark) .title-wrap p {
  color: #94a3b8;
}

:global(html.dark) .bubble {
  background: #1f2937;
  color: #e5e7eb;
}

:global(html.dark) .chat-item.user .bubble {
  background: #0369a1;
}
</style>
