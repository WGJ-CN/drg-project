<template>
  <div class="chat-container">
    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="message in chatStore.messages"
        :key="message.id"
        :class="['message', message.type]"
      >
        <div v-if="message.type === 'bot'" class="avatar bot-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
            <circle cx="9" cy="9" r="1"/>
            <circle cx="15" cy="9" r="1"/>
          </svg>
        </div>
        
        <div class="message-content-wrapper">
          <div class="message-content">
            <div v-if="message.type === 'loading'" class="loading-spinner">
              <div class="spinner-ring">
                <div class="spinner-core"></div>
              </div>
              <span>{{ message.content }}</span>
            </div>
            
            <div v-else-if="message.type === 'bot' && typeof message.content === 'object'" class="drg-result">
              <div class="result-header">
                <div class="result-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  </svg>
                </div>
                <span class="result-title">DRG 分组结果</span>
              </div>
              
              <div class="result-grid">
                <div class="result-card mdc-card">
                  <div class="card-label">MDC</div>
                  <div class="card-value">{{ message.content.MDC }}</div>
                </div>
                
                <div class="result-card adrg-card">
                  <div class="card-label">ADRG</div>
                  <div class="card-value">{{ message.content.ADRG }}</div>
                </div>
                
                <div class="result-card drg-card">
                  <div class="card-label">DRG</div>
                  <div class="card-value">{{ message.content.DRG }}</div>
                </div>
                
                <div class="result-card complication-card">
                  <div class="card-label">并发症等级</div>
                  <div class="card-value complication-badge" :class="message.content.COMPLICATION.toLowerCase()">
                    {{ getComplicationText(message.content.COMPLICATION) }}
                  </div>
                </div>
              </div>
              
              <div class="result-details">
                <div class="detail-item">
                  <span class="detail-label">ADRG名称:</span>
                  <span class="detail-value">{{ message.content.ADRG_NAME }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">DRG名称:</span>
                  <span class="detail-value">{{ message.content.DRG_NAME }}</span>
                </div>
              </div>
            </div>
            
            <div v-else class="text-content">
              {{ message.content }}
            </div>
            
            <div class="message-time">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>
        </div>
        
        <div v-if="message.type === 'user'" class="avatar user-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
      </div>
    </div>

    <div class="chat-input">
      <div class="input-wrapper">
        <textarea
          v-model="inputText"
          placeholder="请输入诊断信息，例如：主诊断：S01.800x011 其他诊断：S21.100x002 年龄：35岁"
          @keydown.ctrl.enter="handleSend"
          :disabled="chatStore.isLoading"
          rows="3"
          class="message-input"
        ></textarea>
        <div class="input-actions">
          <span class="shortcut-hint">Ctrl + Enter 发送</span>
          <button
            @click="handleSend"
            :disabled="chatStore.isLoading || !inputText.trim()"
            class="send-button"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <span>发送</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '../../stores/chat'
import { groupDRG } from '../../services/drg'

const chatStore = useChatStore()
const inputText = ref('')
const messagesContainer = ref(null)

watch(() => chatStore.messages.length, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})

function getComplicationText(code) {
  const map = {
    'CC': 'CC - 合并症',
    'MCC': 'MCC - 严重合并症',
    'NCC': 'NCC - 无合并症'
  }
  return map[code] || code
}

function formatTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function handleSend() {
  if (!inputText.value.trim() || chatStore.isLoading) return

  const message = inputText.value.trim()
  chatStore.addUserMessage(message)
  inputText.value = ''

  chatStore.addLoadingMessage()

  try {
    const result = await groupDRG(message)
    chatStore.removeLastMessage()
    chatStore.addBotMessage(result)
  } catch (error) {
    chatStore.removeLastMessage()
    chatStore.addBotMessage('抱歉，分组失败，请稍后重试。')
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  width: 100%;
  gap: 12px;
}

.message.user {
  flex-direction: row;
  justify-content: flex-end;
}

.message.bot {
  flex-direction: row;
}

.message.loading {
  flex-direction: row;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.bot-avatar {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: #fff;
}

.user-avatar {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  color: #fff;
}

.avatar svg {
  width: 20px;
  height: 20px;
}

.message-content-wrapper {
  max-width: 75%;
  display: flex;
  flex-direction: column;
}

.message.user .message-content-wrapper {
  align-items: flex-end;
}

.message-content {
  padding: 16px 20px;
  border-radius: 20px;
  word-wrap: break-word;
  position: relative;
  transition: all 0.3s ease;
}

.message.user .message-content {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: #fff;
  border-radius: 20px 20px 20px 4px;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.3);
}

.message.bot .message-content {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 20px 20px 20px 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.message.loading .message-content {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 20px 20px 20px 4px;
}

.message-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 6px;
  padding: 0 8px;
}

.message.user .message-time {
  color: rgba(255, 255, 255, 0.6);
}

.loading-spinner {
  display: flex;
  align-items: center;
  gap: 12px;
}

.spinner-ring {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  animation: spin 1.5s linear infinite;
  padding: 3px;
}

.spinner-core {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #fff;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.drg-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.result-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.result-icon svg {
  width: 16px;
  height: 16px;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.result-card {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  padding: 14px;
  text-align: center;
  border: 1px solid #e2e8f0;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.card-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.mdc-card .card-value {
  color: #1890ff;
}

.adrg-card .card-value {
  color: #52c41a;
}

.drg-card .card-value {
  color: #7c3aed;
}

.complication-card .card-value {
  font-size: 14px;
}

.complication-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
}

.complication-badge.cc {
  background: #dbeafe;
  color: #2563eb;
}

.complication-badge.mcc {
  background: #fee2e2;
  color: #dc2626;
}

.complication-badge.ncc {
  background: #dcfce7;
  color: #22c55e;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 8px;
  border-top: 1px dashed #e2e8f0;
}

.detail-item {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.detail-value {
  font-size: 13px;
  color: #334155;
}

.text-content {
  font-size: 14px;
  line-height: 1.6;
}

.message.user .text-content {
  color: #fff;
}

.chat-input {
  padding: 20px 24px;
  background: #fff;
  border-top: 1px solid #e2e8f0;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-input {
  width: 100%;
  padding: 14px 18px;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  resize: none;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.5;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.message-input:focus {
  outline: none;
  border-color: #1890ff;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

.message-input::placeholder {
  color: #94a3b8;
}

.message-input:disabled {
  background: #f1f5f9;
  cursor: not-allowed;
  opacity: 0.7;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.shortcut-hint {
  font-size: 12px;
  color: #94a3b8;
}

.send-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: #fff;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 14px rgba(24, 144, 255, 0.3);
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(24, 144, 255, 0.4);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
}

.send-button:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  box-shadow: none;
}

.send-button svg {
  width: 16px;
  height: 16px;
}
</style>