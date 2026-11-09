<template>
  <div class="page-container">
    <div class="page-header">
      <h2>📜 训练历史</h2>
      <p>查看历次模型训练记录与性能对比</p>
    </div>
    <div v-if="history.length === 0" class="empty">暂无训练记录，请先训练模型</div>
    <div v-else class="history-list">
      <div v-for="item in history" :key="item.id" class="history-card">
        <div class="card-header">
          <span class="time">🕐 {{ item.created_at }}</span>
          <span class="best">🏆 最佳: {{ item.best_model }} (AUC: {{ item.best_auc.toFixed(4) }})</span>
        </div>
        <el-table :data="tableData(item)" size="small" stripe>
          <el-table-column prop="model" label="模型" width="160" />
          <el-table-column prop="accuracy" label="准确率" />
          <el-table-column prop="precision" label="精确率" />
          <el-table-column prop="recall" label="召回率" />
          <el-table-column prop="f1" label="F1" />
          <el-table-column prop="auc" label="AUC" />
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button type="primary" link @click="$router.push(`/model/${scope.row.model}`)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, onMounted } from 'vue'
import { getTrainingHistory } from '../api'
export default {
  setup() {
    const history = ref([])
    function tableData(item) {
      return Object.entries(item.models_metrics).map(([model, m]) => ({
        model, accuracy: (m.accuracy*100).toFixed(2)+'%', precision: (m.precision*100).toFixed(2)+'%',
        recall: (m.recall*100).toFixed(2)+'%', f1: (m.f1*100).toFixed(2)+'%', auc: m.auc.toFixed(4)
      }))
    }
    onMounted(async () => {
      try { const resp = await getTrainingHistory(); history.value = resp.data } catch(e) { console.error(e) }
    })
    return { history, tableData }
  }
}
</script>
<style scoped>
.page-container { padding: 30px; min-height: 100vh; background: linear-gradient(135deg, #0a1929 0%, #1a2a4a 100%); color: #fff; }
.page-header h2 { font-size: 28px; color: #00d4ff; margin: 0 0 8px 0; }
.page-header p { color: #8ab4f8; margin: 0 0 25px 0; }
.empty { text-align: center; padding: 80px; color: #8ab4f8; font-size: 18px; }
.history-card { background: rgba(0,20,40,0.6); border: 1px solid rgba(0,212,255,0.2); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
.card-header { display: flex; justify-content: space-between; margin-bottom: 15px; }
.time { color: #8ab4f8; font-size: 14px; }
.best { color: #ffd700; font-weight: bold; }
</style>
