import api from './api'

export async function sendMessage(message, conversationId) {
  const { data } = await api.post('/chat', { message, conversation_id: conversationId })
  return data
}

export async function listConversations() {
  const { data } = await api.get('/chat/conversations')
  return data
}

export async function getConversation(id) {
  const { data } = await api.get(`/chat/conversations/${id}`)
  return data
}

export async function deleteConversation(id) {
  await api.delete(`/chat/conversations/${id}`)
}
