import api from './api'

export async function listDocuments() {
  const { data } = await api.get('/documents')
  return data
}

export async function uploadDocument(file, title) {
  const formData = new FormData()
  formData.append('file', file)
  if (title) formData.append('title', title)
  const { data } = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteDocument(id) {
  await api.delete(`/documents/${id}`)
}
