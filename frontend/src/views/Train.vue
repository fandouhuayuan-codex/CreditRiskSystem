<template>
  <div class="page-container">
    <div class="page-header"><h2>🧠 模型训练</h2><p>配置参数，训练 5 种机器学习模型并自动评估</p></div>
    <div class="train-layout">
      <div class="config-panel">
        <h3>训练参数配置</h3>
        <el-form label-position="top">
          <el-form-item label="SMOTE 过采样比例">
            <el-slider v-model="smoteRatio" :min="0.3" :max="1.0" :step="0.05" show-input />
            <div class="hint">少数类目标占比，建议 0.5</div>
          </el-form-item>
          <el-form-item label="调参方式">
            <el-radio-group v-model="useGrid">
              <el-radio :label="false">默认参数（快，推荐）</el-radio>
              <el-radio :label="true">GridSearchCV（慢，更准）</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-button type="primary" size="large" @click="doTrain" :loading="training" style="width:100%">
            {{ training ? '训练中，请耐心等待（SVM较慢）...' : '🚀 开始训练' }}
          </el-button>
          <div class="tip-box">
            💡 提示：5个模型中SVM训练最慢（约5-10分钟），其余约1-2分钟。请耐心等待不要关闭页面。
          </div>
        </el-form>
      </div>
      <div class="result-panel">
        <h3>训练结果</h3>
        <div v-if="!metrics" class="empty-state">
          <div class="empty-icon">📈</div>
          <p>配置参数后点击「开始训练」</p>
        </div>
        <div v-else>
          <el-table :data="tableData" stripe size="default">
            <el-table-column prop="model" label="模型" width="160" />
            <el-table-column prop="accuracy" label="准确率" />
            <el-table-column prop="precision" label="精确率" />
            <el-table-column prop="recall" label="召回率" />
            <el-table-column prop="f1" label="F1分数" />
            <el-table-column prop="auc" label="AUC" />
            <el-table-column prop="pr_auc" label="PR-AUC" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="primary" link @click="$router.push(`/model/${scope.row.model}`)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="best-model">
            🏆 最佳模型：<span>{{ bestModel }}</span>，AUC = <span>{{ bestAuc }}</span>
          </div>
          <div class="dist-section">
            <h4>SMOTE 采样前后训练集类别分布对比</h4>
            <div ref="distChart" class="dist-chart"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { trainModels } from '../api'
import { ElMessage } from 'element-plus'
export default {
  setup() {
    const useGrid = ref(false), smoteRatio = ref(0.5), metrics = ref(null), training = ref(false)
    const distChart = ref(null)
    const tableData = computed(() => {
      if (!metrics.value) return []
      return Object.entries(metrics.value).map(([model, m]) => ({
        model, accuracy: (m.accuracy*100).toFixed(2)+'%', precision: (m.precision*100).toFixed(2)+'%',
        recall: (m.recall*100).toFixed(2)+'%', f1: (m.f1*100).toFixed(2)+'%', auc: m.auc.toFixed(4),
        pr_auc: (m.pr_auc ?? 0).toFixed(4)
      }))
    })
    const bestModel = computed(() => Object.entries(metrics.value||{}).sort((a,b)=>b[1].auc-a[1].auc)[0]?.[0] || '-')
    const bestAuc = computed(() => (Object.values(metrics.value||[]).sort((a,b)=>b.auc-a.auc)[0]?.auc || 0).toFixed(4))
    function renderDistChart(dist) {
      if (!dist || !distChart.value) return
      const chart = echarts.init(distChart.value)
      chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: ['SMOTE 采样前', 'SMOTE 采样后'], textStyle: { color: '#cfd8e3' } },
        grid: { left: 60, right: 30, top: 40, bottom: 40 },
        xAxis: { type: 'category', data: ['正常客户', '违约客户'], axisLabel: { color: '#cfd8e3' } },
        yAxis: {
          type: 'value', name: '样本数', nameTextStyle: { color: '#8ab4f8' },
          axisLabel: { color: '#cfd8e3' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } }
        },
        series: [
          {
            name: 'SMOTE 采样前', type: 'bar', barWidth: 42,
            data: [dist.before.negative, dist.before.positive],
            itemStyle: { color: '#5b8ff9' },
            label: { show: true, position: 'top', color: '#cfd8e3' }
          },
          {
            name: 'SMOTE 采样后', type: 'bar', barWidth: 42,
            data: [dist.after.negative, dist.after.positive],
            itemStyle: { color: '#ff9d4d' },
            label: { show: true, position: 'top', color: '#cfd8e3' }
          }
        ]
      })
    }
    async function doTrain() {
      training.value = true
      try {
        const resp = await trainModels({ use_gridsearch: useGrid.value, smote_ratio: smoteRatio.value })
        metrics.value = resp.data.metrics
        ElMessage.success('训练完成！')
        await nextTick()
        renderDistChart(resp.data.class_distribution)
      } catch(e) { ElMessage.error('训练失败：' + (e.response?.data?.error || e.message)) }
      finally { training.value = false }
    }
    return { useGrid, smoteRatio, metrics, training, tableData, bestModel, bestAuc, doTrain, distChart }
  }
}
</script>
<style scoped>
.page-container { padding: 30px; min-height: 100vh; background: linear-gradient(135deg, #0a1929 0%, #1a2a4a 100%); color: #fff; }
.page-header h2 { font-size: 28px; color: #00d4ff; margin: 0 0 8px 0; }
.page-header p { color: #8ab4f8; margin: 0 0 25px 0; }
.train-layout { display: grid; grid-template-columns: 400px 1fr; gap: 25px; }
.config-panel, .result-panel { background: rgba(0,20,40,0.6); border: 1px solid rgba(0,212,255,0.2); border-radius: 12px; padding: 25px; }
.config-panel h3, .result-panel h3 { color: #00d4ff; margin: 0 0 20px 0; }
.hint { font-size: 12px; color: #8ab4f8; margin-top: 5px; }
.tip-box { margin-top: 20px; padding: 12px; background: rgba(255,215,0,0.08); border: 1px solid rgba(255,215,0,0.2); border-radius: 8px; color: #ffd700; font-size: 13px; line-height: 1.6; }
.empty-state { text-align: center; padding: 60px 20px; color: #8ab4f8; }
.empty-icon { font-size: 64px; margin-bottom: 15px; }
.best-model { margin-top: 20px; padding: 15px; background: rgba(0,212,255,0.1); border-radius: 8px; text-align: center; font-size: 16px; }
.best-model span { color: #00d4ff; font-weight: bold; }
.dist-section { margin-top: 25px; }
.dist-section h4 { color: #00d4ff; margin: 0 0 10px 0; font-size: 16px; }
.dist-chart { width: 100%; height: 320px; }
:deep(.el-form-item__label) { color: #fff !important; }
:deep(.el-radio) { color: #fff !important; margin-right: 15px; }
</style>
