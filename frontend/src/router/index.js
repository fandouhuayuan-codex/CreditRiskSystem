import { createRouter, createWebHistory } from 'vue-router'
import Upload from '../views/Upload.vue'
import Train from '../views/Train.vue'
import Predict from '../views/Predict.vue'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/upload', component: Upload },
  { path: '/train', component: Train },
  { path: '/predict', component: Predict },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})
export default router
