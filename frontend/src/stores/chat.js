import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const isLoading = ref(false)
  const awaitingConfirmation = ref(false)  // 是否正在等待确认

  function addUserMessage(content) {
    messages.value.push({
      id: Date.now(),
      type: 'user',
      content,
      timestamp: new Date().toISOString()
    })
  }

  function addBotMessage(content, needConfirm = false, sessionId = null) {
    messages.value.push({
      id: Date.now(),
      type: 'bot',
      content,
      timestamp: new Date().toISOString(),
      needConfirm,
      sessionId,
      confirmed: false  // 标记是否已确认/修改过
    })
    // 更新等待确认状态
    awaitingConfirmation.value = needConfirm
  }

  function addLoadingMessage() {
    messages.value.push({
      id: Date.now(),
      type: 'loading',
      content: '正在分组...',
      timestamp: new Date().toISOString()
    })
  }

  function removeLastMessage() {
    messages.value.pop()
  }

  function clearMessages() {
    messages.value = []
    awaitingConfirmation.value = false
  }

  function confirmMessage(messageId) {
    const message = messages.value.find(m => m.id === messageId)
    if (message) {
      message.confirmed = true
      message.needConfirm = false
    }
    awaitingConfirmation.value = false
  }

  return {
    messages,
    isLoading,
    awaitingConfirmation,
    addUserMessage,
    addBotMessage,
    addLoadingMessage,
    removeLastMessage,
    clearMessages,
    confirmMessage
  }
})
