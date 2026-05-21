<template>
  <div class="pc-layout">
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
      <div class="chat-wrapper">
        <ChatComponent />
      </div>
    </main>
  </div>
</template>

<script setup>
import ChatComponent from '../components/chat/ChatComponent.vue'
</script>

<style scoped>
.pc-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  padding: 24px 32px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.logo-icon svg {
  width: 22px;
  height: 22px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.header-subtitle {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
  font-weight: 400;
}

.main-content {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 32px;
  overflow: hidden;
}

.chat-wrapper {
  width: 100%;
  max-width: 800px;
  height: calc(100vh - 150px);
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}
</style>