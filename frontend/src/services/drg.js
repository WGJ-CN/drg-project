import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'text/plain'
  }
})

export async function groupDRG(data) {
  try {
    const response = await api.post('/group/raw', data)
    return response.data
  } catch (error) {
    console.error('DRG分组请求失败:', error)
    throw error
  }
}

export async function chatDRG(message, sessionId = null) {
  try {
    const response = await api.post('/chat', {
      message: message,
      session_id: sessionId
    }, {
      headers: { 'Content-Type': 'application/json' }
    })
    return response.data
  } catch (error) {
    console.error('对话请求失败:', error)
    throw error
  }
}

export async function clearDRG(sessionId, fields = null) {
  try {
    const response = await api.post('/clear', {
      session_id: sessionId,
      fields: fields
    }, {
      headers: { 'Content-Type': 'application/json' }
    })
    return response.data
  } catch (error) {
    console.error('清除请求失败:', error)
    throw error
  }
}

export default api
