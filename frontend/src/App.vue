<template>
  <div v-if="isLoginPage" class="login-layout"><router-view /></div>
  <div v-else class="app-layout">
    <div class="sidebar">
      <div class="logo">
        <span class="logo-icon">🏦</span>
        <span class="logo-text">信贷风控系统</span>
      </div>
      <el-menu :default-active="$route.path" router background-color="transparent" text-color="#8ab4f8" active-text-color="#00d4ff">
        <el-menu-item index="/"><span>📊</span><span>仪表盘</span></el-menu-item>
        <el-menu-item index="/upload"><span>📤</span><span>数据管理</span></el-menu-item>
        <el-menu-item index="/train"><span>🧠</span><span>模型训练</span></el-menu-item>
        <el-menu-item index="/predict"><span>🔮</span><span>风险预测</span></el-menu-item>
        <el-menu-item index="/alerts" class="alert-menu-item">
          <span>⚠️</span><span>风险告警</span>
          <el-badge v-if="pendingAlertCount > 0" :value="pendingAlertCount" class="alert-badge" />
        </el-menu-item>
        <el-menu-item index="/history"><span>📜</span><span>训练历史</span></el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <div class="user-info">👤 {{ username }}</div>
        <el-button size="small" type="danger" @click="doLogout">退出登录</el-button>
      </div>
    </div>
    <div class="main-content"><router-view /></div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAlerts } from './api'

export default {
  setup() {
    const route = useRoute()
    const router = useRouter()
    const username = ref(localStorage.getItem('username') || 'admin')
    const isLoginPage = computed(() => route.path === '/login')
    const pendingAlertCount = ref(0)
    let alertTimer = null

    async function fetchAlertCount() {
      try {
        const res = await getAlerts({ status: 'pending', page_size: 1 })
        pendingAlertCount.value = res.data.pending_count || 0
      } catch (e) { /* 静默失败 */ }
    }

    onMounted(() => {
      if (!isLoginPage.value) {
        fetchAlertCount()
        alertTimer = setInterval(fetchAlertCount, 30000)
      }
    })

    onUnmounted(() => {
      if (alertTimer) clearInterval(alertTimer)
    })

    function doLogout() {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('username')
      if (alertTimer) clearInterval(alertTimer)
      ElMessage.success('已退出')
      router.push('/login')
    }

    return { username, isLoginPage, doLogout, pendingAlertCount }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Microsoft YaHei', sans-serif; }
.app-layout { display: flex; min-height: 100vh; background: #0a1929; color: #fff; }
.sidebar { width: 220px; background: linear-gradient(180deg, #0a1929 0%, #0d2137 100%); border-right: 1px solid rgba(0,212,255,0.2); display: flex; flex-direction: column; position: fixed; height: 100vh; left: 0; top: 0; z-index: 100; }
.logo { padding: 25px 20px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid rgba(0,212,255,0.15); }
.logo-icon { font-size: 28px; }
.logo-text { font-size: 16px; font-weight: bold; background: linear-gradient(90deg, #00d4ff, #0066ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.sidebar .el-menu { flex: 1; border-right: none !important; padding-top: 15px; }
.sidebar .el-menu-item { height: 50px; line-height: 50px; margin: 5px 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px; }
.sidebar .el-menu-item:hover { background: rgba(0,212,255,0.1) !important; }
.sidebar .el-menu-item.is-active { background: linear-gradient(90deg, rgba(0,212,255,0.2), transparent) !important; border-left: 3px solid #00d4ff; }
.sidebar-footer { padding: 15px; border-top: 1px solid rgba(0,212,255,0.15); display: flex; flex-direction: column; gap: 10px; align-items: center; }
.user-info { color: #00d4ff; font-size: 13px; }
.main-content { flex: 1; margin-left: 220px; min-height: 100vh; }
.alert-menu-item { position: relative; }
.alert-badge { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); }
</style>
