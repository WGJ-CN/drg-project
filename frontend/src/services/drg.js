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

export default api