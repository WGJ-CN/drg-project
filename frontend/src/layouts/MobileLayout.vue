<template>
  <div class="mobile-layout">
    <header class="header">
      <div class="header-content">
        <div class="logo-container">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 4v4m0 8v4M8 12H4m16 0h-4"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </div>
          <h1 class="title">DRG 分组助手</h1>
        </div>
      </div>
    </header>
    <main class="main-content">
      <ChatComponent />
    </main>
  </div>
</template>

<script setup>
import ChatComponent from '../components/chat/ChatComponent.vue'
</script>

<style scoped>
.mobile-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 3px 10px rgba(24, 144, 255, 0.3);
}

.logo-icon svg {
  width: 18px;
  height: 18px;
}

.title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.main-content {
  flex: 1;
  overflow: hidden;
  padding: 16px;
}

.main-content :deep(.chat-container) {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.main-content :deep(.chat-messages) {
  padding: 16px;
  gap: 16px;
}

.main-content :deep(.avatar) {
  width: 36px;
  height: 36px;
}

.main-content :deep(.message-content-wrapper) {
  max-width: 85%;
}

.main-content :deep(.message-content) {
  padding: 14px 18px;
  border-radius: 16px;
}

.main-content :deep(.chat-input) {
  padding: 16px;
}

.main-content :deep(.message-input) {
  font-size: 16px;
  padding: 16px;
  border-radius: 14px;
}

.main-content :deep(.send-button) {
  padding: 14px 28px;
  font-size: 16px;
  border-radius: 30px;
}

.main-content :deep(.result-grid) {
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.main-content :deep(.result-card) {
  padding: 12px;
}

.main-content :deep(.card-value) {
  font-size: 18px;
}
</style>