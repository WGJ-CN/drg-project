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
            
            <!-- Confirmation Buttons -->
            <div v-if="message.type === 'bot' && message.needConfirm && !message.confirmed" class="confirmation-buttons">
              <button @click="handleConfirm(message.id, message.sessionId)" class="confirm-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span>确认</span>
              </button>
              <button @click="handleModify(message.id, message.sessionId)" class="modify-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 20h9"/>
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                </svg>
                <span>修改</span>
              </button>
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
          @keydown.ctrl.enter="handleSend"
          :disabled="chatStore.isLoading || chatStore.awaitingConfirmation"
          :placeholder="chatStore.awaitingConfirmation ? '请先确认或修改信息' : '请输入诊断信息，例如：主诊断：S01.800x011 其他诊断：S21.100x002 年龄：35岁'"
          rows="3"
          class="message-input"
        ></textarea>
        <div class="input-actions">
          <div class="clear-dropdown">
            <button 
              @click="toggleClearMenu" 
              class="clear-button"
              :disabled="!sessionId || chatStore.awaitingConfirmation"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              <span>清除</span>
            </button>
            <div v-if="showClearMenu" class="clear-menu">
              <div class="clear-menu-item" @click="handleClear(['main_diag'])">清除主要诊断</div>
              <div class="clear-menu-item" @click="handleClear(['other_diags'])">清除次要诊断</div>
              <div class="clear-menu-item" @click="handleClear(['main_proc'])">清除主要手术</div>
              <div class="clear-menu-item" @click="handleClear(['other_procs'])">清除其他手术</div>
              <div class="clear-menu-item" @click="handleClear(['age_days'])">清除年龄</div>
              <div class="clear-menu-divider"></div>
              <div class="clear-menu-item clear-all" @click="handleClear(null)">全部清除</div>
            </div>
          </div>
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
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../../stores/chat'
import { chatDRG, clearDRG } from '../../services/drg'

const sessionId = ref(null)
const chatStore = useChatStore()
const inputText = ref('')
const messagesContainer = ref(null)
const showClearMenu = ref(false)

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

function toggleClearMenu() {
  showClearMenu.value = !showClearMenu.value
}

function closeClearMenu() {
  showClearMenu.value = false
}

async function handleClear(fields) {
  if (!sessionId.value) return
  
  closeClearMenu()
  
  try {
    const response = await clearDRG(sessionId.value, fields)
    // 判断是否需要确认（清除部分字段且满足分组条件）
    const needConfirm = response.is_complete && fields  // 清除部分字段且满足条件才需要确认
    chatStore.addBotMessage(response.reply, needConfirm, response.session_id)
  } catch (error) {
    chatStore.addBotMessage('清除失败，请稍后重试。')
  }
}

async function handleSend() {
  // 如果正在等待确认，则禁止发送
  if (chatStore.awaitingConfirmation) {
    return
  }
  
  if (!inputText.value.trim() || chatStore.isLoading) return

  const message = inputText.value.trim()
  chatStore.addUserMessage(message)
  inputText.value = ''

  chatStore.addLoadingMessage()

  try {
    const response = await chatDRG(message, sessionId.value)
    sessionId.value = response.session_id
    chatStore.removeLastMessage()
    // 添加机器人回复
    chatStore.addBotMessage(response.reply, response.need_confirm, response.session_id)
    // 如果有分组结果，也添加结果卡片
    if (response.result) {
      chatStore.addBotMessage(response.result)
    }
  } catch (error) {
    chatStore.removeLastMessage()
    chatStore.addBotMessage('抱歉，对话失败，请稍后重试。')
  }
}

async function handleConfirm(messageId, sessionIdValue) {
  // 立即隐藏按钮
  chatStore.confirmMessage(messageId)
  
  chatStore.addLoadingMessage()

  try {
    const response = await chatDRG('__CONFIRM__', sessionIdValue)
    sessionId.value = response.session_id
    chatStore.removeLastMessage()
    chatStore.addBotMessage(response.reply)
    if (response.result) {
      chatStore.addBotMessage(response.result)
    }
  } catch (error) {
    chatStore.removeLastMessage()
    chatStore.addBotMessage('抱歉，分组失败，请稍后重试。')
  }
}

async function handleModify(messageId, sessionIdValue) {
  // 立即隐藏按钮
  chatStore.confirmMessage(messageId)
  
  chatStore.addLoadingMessage()

  try {
    const response = await chatDRG('__MODIFY__', sessionIdValue)
    sessionId.value = response.session_id
    chatStore.removeLastMessage()
    chatStore.addBotMessage(response.reply)
  } catch (error) {
    chatStore.removeLastMessage()
    chatStore.addBotMessage('抱歉，操作失败，请稍后重试。')
  }
}

// 点击外部关闭菜单
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

function handleClickOutside(event) {
  if (showClearMenu.value && !event.target.closest('.clear-dropdown')) {
    closeClearMenu()
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

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
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
  max-width: 70%;
}

.message.user .message-content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-content {
  padding: 14px 18px;
  border-radius: 18px;
  position: relative;
}

.message.bot .message-content {
  background: #fff;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message.user .message-content {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: #fff;
  border-bottom-right-radius: 4px;
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
  width: 18px;
  height: 18px;
}

.result-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
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

.result-card .card-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.result-card .card-value {
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
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-all;
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
  position: relative;
}

.clear-dropdown {
  position: relative;
}

.clear-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.clear-button:hover:not(:disabled) {
  background: #e2e8f0;
  color: #475569;
}

.clear-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clear-button svg {
  width: 14px;
  height: 14px;
}

.clear-menu {
  position: absolute;
  bottom: 100%;
  left: 0;
  margin-bottom: 8px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  min-width: 160px;
  z-index: 100;
  overflow: hidden;
}

.clear-menu-item {
  padding: 12px 16px;
  font-size: 13px;
  color: #334155;
  cursor: pointer;
  transition: background 0.2s;
}

.clear-menu-item:hover {
  background: #f1f5f9;
}

.clear-menu-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 4px 0;
}

.clear-all {
  color: #dc2626;
  font-weight: 500;
}

.clear-all:hover {
  background: #fef2f2;
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

.confirmation-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: flex-end;
}

.confirm-btn,
.modify-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.confirm-btn {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3);
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(96, 165, 250, 0.4);
}

.confirm-btn:active {
  transform: translateY(0);
}

.confirm-btn svg {
  width: 14px;
  height: 14px;
}

.modify-btn {
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.modify-btn:hover {
  background: #e2e8f0;
  color: #475569;
}

.modify-btn svg {
  width: 14px;
  height: 14px;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
  text-align: right;
}

.message.user .message-time {
  color: rgba(255, 255, 255, 0.6);
}
</style>
