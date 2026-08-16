import axios from 'axios'
const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 60000
})

export function uploadFile(file) {
  const form = new FormData();
  form.append('file', file);
  return api.post('upload/', form, { headers: {'Content-Type':'multipart/form-data'} })
}

export function trainModels(params) {
  return api.post('train/', params)
}

export function predictSingle(payload) {
  return api.post('predict/', payload)
}

export function getDashboard() {
  return api.get('dashboard/')
}

export default api
