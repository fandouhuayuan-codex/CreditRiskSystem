import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Upload from '../views/Upload.vue'
import Train from '../views/Train.vue'
import Predict from '../views/Predict.vue'
import Login from '../views/Login.vue'
import TrainingHistory from '../views/TrainingHistory.vue'
import ModelDetail from '../views/ModelDetail.vue'
import Alert from '../views/Alert.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', component: Dashboard },
  { path: '/upload', component: Upload },
  { path: '/train', component: Train },
  { path: '/predict', component: Predict },
  { path: '/alerts', component: Alert },
  { path: '/history', component: TrainingHistory },
  { path: '/model/:model_name', component: ModelDetail },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  if (to.meta.public) { next(); return }
  const token = localStorage.getItem('auth_token')
  if (token) { next() } else { next('/login') }
})

export default router
