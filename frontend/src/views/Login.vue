<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-header">
        <div class="logo-icon">🏦</div>
        <h1>银行信贷风险评估系统</h1>
        <p>Credit Risk Assessment System</p>
      </div>
      <el-form :model="form" @submit.prevent="doLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password @keyup.enter="doLogin" />
        </el-form-item>
        <el-button type="primary" size="large" style="width:100%" :loading="loading" @click="doLogin">登 录</el-button>
      </el-form>
      <div class="login-tip">默认账号 admin / admin123</div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { login } from '../api'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  setup() {
    const router = useRouter()
    const form = ref({ username: '', password: '' })
    const loading = ref(false)
    async function doLogin() {
      if (!form.value.username || !form.value.password) { ElMessage.warning('请输入用户名和密码'); return }
      loading.value = true
      try {
        const resp = await login(form.value)
        localStorage.setItem('auth_token', resp.data.token || 'logged_in')
        localStorage.setItem('username', resp.data.username)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (e) {
        ElMessage.error(e.response?.data?.error || '登录失败')
      } finally { loading.value = false }
    }
    return { form, loading, doLogin }
  }
}
</script>

<style scoped>
.login-page { min-height: 100vh; background: linear-gradient(135deg, #0a1929 0%, #1a3a5c 50%, #0a1929 100%); display: flex; align-items: center; justify-content: center; }
.login-box { width: 400px; padding: 40px; background: rgba(0,20,40,0.85); border: 1px solid rgba(0,212,255,0.3); border-radius: 16px; box-shadow: 0 0 40px rgba(0,212,255,0.2); }
.login-header { text-align: center; margin-bottom: 30px; }
.logo-icon { font-size: 56px; margin-bottom: 10px; }
.login-header h1 { font-size: 22px; color: #00d4ff; margin: 0 0 8px 0; }
.login-header p { color: #8ab4f8; font-size: 12px; letter-spacing: 2px; margin: 0; }
.login-tip { text-align: center; color: #5a7a9a; font-size: 11px; margin-top: 20px; }
</style>
