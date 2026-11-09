import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 600000
})

export function login(data) { return api.post('auth/login/', data) }
export function logout() { return api.post('auth/logout/') }
export function getUserInfo() { return api.get('auth/user/') }
export function uploadFile(file) {
  const form = new FormData(); form.append('file', file)
  return api.post('upload/', form, { headers: {'Content-Type':'multipart/form-data'} })
}
export function getDataPreview(limit = 10) { return api.get(`preview/?limit=${limit}`) }
export function deleteAllData() { return api.delete('delete-all/') }
export function getDataStats() { return api.get('stats/') }
export function trainModels(params) { return api.post('train/', params) }
export function getTrainingHistory() { return api.get('training-history/') }
export function predictSingle(payload) { return api.post('predict/', payload) }
export function batchPredict(file, model_name, threshold) {
  const form = new FormData(); form.append('file', file); form.append('model_name', model_name); form.append('threshold', threshold)
  return api.post('batch-predict/', form, { headers: {'Content-Type':'multipart/form-data'} })
}
export function getModelDetail(model_name) { return api.get(`model-detail/${model_name}/`) }
export function getSHAP(payload) { return api.post('shap/', payload) }
export function getDashboard() { return api.get('dashboard/') }
export function getExportReportUrl() { return 'http://localhost:8000/api/export-report/' }
export function getAlerts(params) { return api.get('alerts/', { params }) }
export function reviewAlert(alertId, data) { return api.post(`alerts/${alertId}/review/`, data) }
export default api
