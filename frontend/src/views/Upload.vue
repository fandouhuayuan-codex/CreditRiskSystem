<template>
  <div class="page-container">
    <div class="page-header"><h2>📤 数据管理</h2><p>上传、预览和管理信贷风险数据集</p></div>
    <div class="stats-row">
      <div class="stat-card"><div class="stat-icon">📊</div><div class="stat-info"><div class="stat-value">{{ stats.total }}</div><div class="stat-label">总数据量</div></div></div>
      <div class="stat-card warning"><div class="stat-icon">⚠️</div><div class="stat-info"><div class="stat-value">{{ stats.positive }}</div><div class="stat-label">违约样本</div></div></div>
      <div class="stat-card success"><div class="stat-icon">✅</div><div class="stat-info"><div class="stat-value">{{ stats.negative }}</div><div class="stat-label">正常样本</div></div></div>
      <div class="stat-card primary"><div class="stat-icon">🕐</div><div class="stat-info"><div class="stat-value small">{{ stats.latest_upload || '暂无' }}</div><div class="stat-label">最近上传</div></div></div>
    </div>
    <div class="content-row">
      <div class="panel">
        <h3>📁 上传数据集</h3>
        <el-upload drag :auto-upload="false" :file-list="fileList" :on-change="handleChange" :on-remove="handleRemove" accept=".csv,.xlsx,.xls">
          <div class="upload-icon">📁</div>
          <div class="upload-text">将文件拖拽到此处，或<em>点击上传</em></div>
          <div class="upload-hint">支持 CSV / Excel</div>
        </el-upload>
        <div class="upload-actions">
          <el-button type="primary" size="large" @click="doUpload" :loading="uploading" :disabled="!file">🚀 上传并导入</el-button>
          <el-button size="large" @click="clearFile" :disabled="!file">清空选择</el-button>
        </div>
        <div class="action-item danger" style="margin-top:20px">
          <div class="action-info"><div class="action-title">清空所有数据</div><div class="action-desc">删除所有客户数据、训练记录（不可恢复）</div></div>
          <el-button type="danger" @click="handleDeleteAll" :loading="deleting" :disabled="stats.total===0">🗑️ 清空数据</el-button>
        </div>
      </div>
      <div class="panel">
        <h3>👁️ 数据预览（前10条）</h3>
        <el-button size="small" @click="loadPreview" style="margin-bottom:10px">🔄 刷新预览</el-button>
        <div v-if="previewData.length" class="preview-wrap">
          <el-table :data="previewData" size="small" max-height="400" stripe>
            <el-table-column v-for="col in previewColumns.slice(0,8)" :key="col" :prop="col" :label="col" :width="110" show-overflow-tooltip />
          </el-table>
        </div>
        <div v-else class="empty">暂无数据</div>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, onMounted } from 'vue'
import { uploadFile, deleteAllData, getDataStats, getDataPreview } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
export default {
  setup() {
    const file = ref(null), fileList = ref([]), uploading = ref(false), deleting = ref(false)
    const stats = ref({ total: 0, positive: 0, negative: 0, latest_upload: null })
    const previewData = ref([]), previewColumns = ref([])
    async function loadStats() { try { const r = await getDataStats(); stats.value = r.data } catch(e) {} }
    async function loadPreview() {
      try { const r = await getDataPreview(10); previewData.value = r.data.data; previewColumns.value = r.data.columns } catch(e) {}
    }
    function handleChange(f) { file.value = f.raw; fileList.value = [f] }
    function handleRemove() { file.value = null; fileList.value = [] }
    function clearFile() { file.value = null; fileList.value = [] }
    async function doUpload() {
      if (!file.value) { ElMessage.warning('请先选择文件'); return }
      uploading.value = true
      try { const r = await uploadFile(file.value); ElMessage.success(r.data.message); file.value = null; fileList.value = []; loadStats(); loadPreview() }
      catch(e) { ElMessage.error('上传失败：' + (e.response?.data?.error || e.message)) }
      finally { uploading.value = false }
    }
    async function handleDeleteAll() {
      try {
        await ElMessageBox.confirm('确定清空所有数据？不可恢复！', '确认', { type: 'warning' })
        deleting.value = true; const r = await deleteAllData(); ElMessage.success(r.data.message); loadStats(); loadPreview()
      } catch(e) { if (e !== 'cancel') ElMessage.error('删除失败') }
      finally { deleting.value = false }
    }
    onMounted(() => { loadStats(); loadPreview() })
    return { file, fileList, uploading, deleting, stats, previewData, previewColumns, loadStats, loadPreview, handleChange, handleRemove, clearFile, doUpload, handleDeleteAll }
  }
}
</script>
<style scoped>
.page-container { padding: 30px; min-height: 100vh; background: linear-gradient(135deg, #0a1929 0%, #1a2a4a 100%); color: #fff; }
.page-header h2 { font-size: 28px; color: #00d4ff; margin: 0 0 8px 0; }
.page-header p { color: #8ab4f8; margin: 0 0 20px 0; }
.stats-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 15px; margin-bottom: 25px; }
.stat-card { background: linear-gradient(135deg, rgba(0,102,255,0.15), rgba(0,212,255,0.05)); border: 1px solid rgba(0,212,255,0.3); border-radius: 10px; padding: 18px; display: flex; align-items: center; gap: 12px; }
.stat-card.warning { background: linear-gradient(135deg, rgba(255,165,0,0.15), rgba(255,100,0,0.05)); border-color: rgba(255,165,0,0.3); }
.stat-card.success { background: linear-gradient(135deg, rgba(0,255,136,0.15), rgba(0,200,100,0.05)); border-color: rgba(0,255,136,0.3); }
.stat-card.primary { background: linear-gradient(135deg, rgba(162,155,254,0.15), rgba(108,92,231,0.05)); border-color: rgba(162,155,254,0.3); }
.stat-icon { font-size: 32px; }
.stat-value { font-size: 26px; font-weight: bold; color: #00d4ff; font-family: monospace; }
.stat-value.small { font-size: 13px; }
.stat-card.warning .stat-value { color: #ffa500; }
.stat-card.success .stat-value { color: #00ff88; }
.stat-card.primary .stat-value { color: #a29bfe; }
.stat-label { font-size: 13px; color: #8ab4f8; margin-top: 4px; }
.content-row { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.panel { background: rgba(0,20,40,0.6); border: 1px solid rgba(0,212,255,0.2); border-radius: 12px; padding: 25px; }
.panel h3 { color: #00d4ff; margin: 0 0 15px 0; }
.upload-icon { font-size: 48px; margin-bottom: 10px; }
.upload-text { font-size: 16px; color: #fff; margin-bottom: 8px; }
.upload-text em { color: #00d4ff; font-style: normal; }
.upload-hint { font-size: 12px; color: #8ab4f8; }
.upload-actions { margin-top: 20px; display: flex; gap: 15px; justify-content: center; }
.action-item { display: flex; justify-content: space-between; align-items: center; padding: 15px; background: rgba(255,71,87,0.08); border: 1px solid rgba(255,71,87,0.2); border-radius: 8px; }
.action-title { font-size: 15px; color: #fff; }
.action-desc { font-size: 12px; color: #8ab4f8; margin-top: 4px; }
.preview-wrap { overflow-x: auto; }
.empty { text-align: center; padding: 40px; color: #8ab4f8; }
</style>
