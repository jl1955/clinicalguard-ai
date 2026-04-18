import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000' })

export const getLogs    = (limit = 100) => api.get(`/audit/logs?limit=${limit}`)
export const getStats   = ()            => api.get('/audit/stats')
export const postQuery  = (payload)     => api.post('/proxy/query', payload)
export const postReview = (id, action)  => api.post(`/audit/review/${id}`, { action })
