import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const isLoading = ref(false)

  function addUserMessage(content) {
    messages.value.push({
      id: Date.now(),
      type: 'user',
      content,
      timestamp: new Date().toISOString()
    })
  }

  function addBotMessage(content) {
    messages.value.push({
      id: Date.now(),
      type: 'bot',
      content,
      timestamp: new Date().toISOString()
    })
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
  }

  return {
    messages,
    isLoading,
    addUserMessage,
    addBotMessage,
    addLoadingMessage,
    removeLastMessage,
    clearMessages
  }
})