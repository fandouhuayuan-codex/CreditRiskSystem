<template>
  <div class="page-container">
    <div class="page-header">
      <el-button @click="$router.back()">← 返回</el-button>
      <h2>📊 {{ modelName }} 模型详情</h2>
    </div>
    <div v-if="detail" class="detail-grid">
      <div class="panel">
        <h3>性能指标</h3>
        <div class="metric-grid">
          <div class="metric-item"><span>准确率</span><b>{{ (detail.metrics.accuracy*100).toFixed(2) }}%</b></div>
          <div class="metric-item"><span>精确率</span><b>{{ (detail.metrics.precision*100).toFixed(2) }}%</b></div>
          <div class="metric-item"><span>召回率</span><b>{{ (detail.metrics.recall*100).toFixed(2) }}%</b></div>
          <div class="metric-item"><span>F1分数</span><b>{{ (detail.metrics.f1*100).toFixed(2) }}%</b></div>
          <div class="metric-item"><span>AUC</span><b>{{ detail.metrics.auc.toFixed(4) }}</b></div>
          <div class="metric-item"><span>KS值</span><b>{{ detail.metrics.ks ? detail.metrics.ks.toFixed(4) : '-' }}</b></div>
        </div>
      </div>
      <div class="panel">
        <h3>混淆矩阵</h3>
        <div v-if="detail.confusion_matrix" class="confusion-matrix">
          <div class="cm-row cm-header"><div></div><div>预测正常</div><div>预测违约</div></div>
          <div class="cm-row"><div class="cm-label">实际正常</div><div class="cm-cell tn">{{ detail.confusion_matrix.tn }}</div><div class="cm-cell fp">{{ detail.confusion_matrix.fp }}</div></div>
          <div class="cm-row"><div class="cm-label">实际违约</div><div class="cm-cell fn">{{ detail.confusion_matrix.fn }}</div><div class="cm-cell tp">{{ detail.confusion_matrix.tp }}</div></div>
        </div>
        <div v-else class="empty">无混淆矩阵数据</div>
      </div>
      <div class="panel full-width">
        <h3>ROC 曲线</h3>
        <div ref="rocChart" style="height: 400px;"></div>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getModelDetail } from '../api'
import * as echarts from 'echarts'
export default {
  setup() {
    const route = useRoute()
    const modelName = ref(route.params.model_name)
    const detail = ref(null)
    const rocChart = ref(null)
    onMounted(async () => {
      try {
        const resp = await getModelDetail(modelName.value)
        detail.value = resp.data
        await nextTick()
        renderRocChart()
      } catch(e) { console.error(e) }
    })
    function renderRocChart() {
      if (!detail.value || !detail.value.roc || !rocChart.value) return
      const chart = echarts.init(rocChart.value)
      const roc = detail.value.roc
      const data = roc.fpr.map((f, i) => [f, roc.tpr[i]])
      chart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            const p = params[0]
            return `FPR: ${p.value[0].toFixed(4)}<br/>TPR: ${p.value[1].toFixed(4)}`
          }
        },
        grid: { left: 60, right: 30, top: 30, bottom: 50 },
        xAxis: {
          type: 'value',
          name: '假正率 (FPR)',
          nameTextStyle: { color: '#8ab4f8' },
          axisLine: { lineStyle: { color: '#8ab4f8' } },
          axisLabel: { color: '#8ab4f8' },
          splitLine: { lineStyle: { color: 'rgba(138,180,248,0.1)' } }
        },
        yAxis: {
          type: 'value',
          name: '真正率 (TPR)',
          nameTextStyle: { color: '#8ab4f8' },
          axisLine: { lineStyle: { color: '#8ab4f8' } },
          axisLabel: { color: '#8ab4f8' },
          splitLine: { lineStyle: { color: 'rgba(138,180,248,0.1)' } }
        },
        series: [
          {
            name: 'ROC曲线',
            type: 'line',
            data: data,
            smooth: true,
            lineStyle: { color: '#00d4ff', width: 3 },
            areaStyle: { color: 'rgba(0,212,255,0.15)' },
            symbol: 'none'
          },
          {
            name: '随机猜测',
            type: 'line',
            data: [[0,0],[1,1]],
            lineStyle: { color: '#8ab4f8', type: 'dashed', width: 1 },
            symbol: 'none'
          }
        ]
      })
    }
    return { modelName, detail, rocChart }
  }
}
</script>
<style scoped>
.page-container { padding: 30px; min-height: 100vh; background: linear-gradient(135deg, #0a1929 0%, #1a2a4a 100%); color: #fff; }
.page-header { display: flex; align-items: center; gap: 15px; margin-bottom: 25px; }
.page-header h2 { font-size: 24px; color: #00d4ff; margin: 0; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.panel { background: rgba(0,20,40,0.6); border: 1px solid rgba(0,212,255,0.2); border-radius: 12px; padding: 25px; }
.panel.full-width { grid-column: 1 / -1; }
.panel h3 { color: #00d4ff; margin: 0 0 20px 0; }
.metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
.metric-item { background: rgba(0,212,255,0.08); padding: 15px; border-radius: 8px; text-align: center; }
.metric-item span { display: block; color: #8ab4f8; font-size: 12px; margin-bottom: 8px; }
.metric-item b { font-size: 22px; color: #00d4ff; }
.confusion-matrix { max-width: 350px; }
.cm-row { display: grid; grid-template-columns: 100px 1fr 1fr; gap: 5px; margin-bottom: 5px; }
.cm-header div { text-align: center; color: #8ab4f8; font-size: 13px; padding: 8px; }
.cm-label { display: flex; align-items: center; justify-content: center; color: #8ab4f8; font-size: 13px; }
.cm-cell { padding: 20px; text-align: center; font-size: 24px; font-weight: bold; border-radius: 6px; }
.tn { background: rgba(0,255,136,0.2); color: #00ff88; }
.fp { background: rgba(255,165,0,0.2); color: #ffa500; }
.fn { background: rgba(255,71,87,0.2); color: #ff4757; }
.tp { background: rgba(0,212,255,0.2); color: #00d4ff; }
.empty { text-align: center; color: #8ab4f8; padding: 40px; }
</style>
