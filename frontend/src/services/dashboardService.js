import api from './api'

export async function fetchDashboardStats() {
  const { data } = await api.get('/dashboard')
  return data
}
