<template>
  <div class="dashboard-screen">
    <!-- 顶部标题栏 -->
    <div class="header">
      <div class="title">
        <span class="main-title">银行信贷风险评估系统</span>
        <span class="sub-title">CREDIT RISK ASSESSMENT DASHBOARD</span>
      </div>
      <div style="display:flex;align-items:center;gap:15px">
        <el-button type="primary" @click="exportReport">📥 导出报告</el-button>
        <el-button @click="$router.push('/history')">📜 训练历史</el-button>
        <div class="header-time">{{ currentTime }}</div>
      </div>
    </div>

    <!-- 顶部数据卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总客户数</div>
        </div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.positive }}</div>
          <div class="stat-label">违约客户</div>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.negative }}</div>
          <div class="stat-label">正常客户</div>
        </div>
      </div>
      <div class="stat-card danger">
        <div class="stat-icon">📈</div>
        <div class="stat-info">
          <div class="stat-value">{{ defaultRate }}%</div>
          <div class="stat-label">违约率</div>
        </div>
      </div>
      <div class="stat-card primary">
        <div class="stat-icon">🎯</div>
        <div class="stat-info">
          <div class="stat-value">{{ bestAuc }}</div>
          <div class="stat-label">最佳模型AUC</div>
        </div>
      </div>
    </div>

    <!-- 中间图表区域 -->
    <div class="charts-row">
      <div class="chart-box">
        <div class="chart-title">模型 AUC 对比</div>
        <div ref="aucChart" class="chart-container"></div>
      </div>
      <div class="chart-box">
        <div class="chart-title">违约分布</div>
        <div ref="distChart" class="chart-container"></div>
      </div>
      <div class="chart-box">
        <div class="chart-title">模型综合指标</div>
        <div ref="metricChart" class="chart-container"></div>
      </div>
    </div>

    <!-- 底部图表区域 -->
    <div class="charts-row">
      <div class="chart-box wide">
        <div class="chart-title">特征重要性 TOP10 (XGBoost)</div>
        <div ref="featChart" class="chart-container"></div>
      </div>
      <div class="chart-box">
        <div class="chart-title">模型性能雷达图</div>
        <div ref="radarChart" class="chart-container"></div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { onMounted, ref, onUnmounted } from 'vue'
import { getDashboard } from '../api'

export default {
  setup() {
    const aucChart = ref(null)
    const distChart = ref(null)
    const featChart = ref(null)
    const metricChart = ref(null)
    const radarChart = ref(null)

    const stats = ref({ total: 0, positive: 0, negative: 0 })
    const currentTime = ref('')
    let timer = null
    let chartInstances = []

    const defaultRate = ref('0.00')
    const bestAuc = ref('0.00')

    function updateTime() {
      const now = new Date()
      currentTime.value = now.toLocaleString('zh-CN', { hour12: false })
    }

    async function loadData() {
      try {
        const resp = await getDashboard()
        const data = resp.data
        stats.value = data.distribution || { total: 0, positive: 0, negative: 0 }

        if (stats.value.total > 0) {
          defaultRate.value = ((stats.value.positive / stats.value.total) * 100).toFixed(2)
        }

        const metrics = data.metrics || {}
        const aucs = Object.values(metrics).map(m => m.auc || 0)
        bestAuc.value = aucs.length ? Math.max(...aucs).toFixed(4) : '0.0000'

        renderCharts(data)
      } catch (e) {
        console.error('加载数据失败', e)
      }
    }

    function renderCharts(data) {
      const metrics = data.metrics || {}
      const models = Object.keys(metrics)
      const aucs = models.map(m => metrics[m].auc || 0)
      const accuracies = models.map(m => metrics[m].accuracy || 0)
      const f1s = models.map(m => metrics[m].f1 || 0)
      const recalls = models.map(m => metrics[m].recall || 0)
      const precisions = models.map(m => metrics[m].precision || 0)

      // AUC 对比图
      if (aucChart.value) {
        const aucInstance = echarts.init(aucChart.value)
        chartInstances.push(aucInstance)
        aucInstance.setOption({
          tooltip: { trigger: 'axis' },
          grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
          xAxis: { type: 'category', data: models, axisLabel: { color: '#8ab4f8', fontSize: 11 } },
          yAxis: { type: 'value', min: 0.5, max: 1, axisLabel: { color: '#8ab4f8' }, splitLine: { lineStyle: { color: 'rgba(138,180,248,0.1)' } } },
          series: [{
            type: 'bar',
            data: aucs,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#00d4ff' },
                { offset: 1, color: '#0066ff' }
              ]),
              borderRadius: [4, 4, 0, 0]
            },
            label: { show: true, position: 'top', color: '#00d4ff', fontSize: 11, formatter: '{c}' }
          }]
        })
      }

      // 违约分布饼图
      if (distChart.value) {
        const distInstance = echarts.init(distChart.value)
        chartInstances.push(distInstance)
        distInstance.setOption({
          tooltip: { trigger: 'item' },
          legend: { bottom: '5%', left: 'center', textStyle: { color: '#8ab4f8' } },
          series: [{
            name: '违约分布',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 8, borderColor: '#0a1929', borderWidth: 2 },
            label: { show: true, color: '#fff', formatter: '{b}\n{d}%' },
            data: [
              { value: stats.value.negative, name: '正常', itemStyle: { color: '#00ff88' } },
              { value: stats.value.positive, name: '违约', itemStyle: { color: '#ff4757' } }
            ]
          }]
        })
      }

      // 综合指标对比图
      if (metricChart.value) {
        const metricInstance = echarts.init(metricChart.value)
        chartInstances.push(metricInstance)
        metricInstance.setOption({
          tooltip: { trigger: 'axis' },
          legend: { data: ['Accuracy', 'Precision', 'Recall', 'F1'], textStyle: { color: '#8ab4f8', fontSize: 10 }, top: 0 },
          grid: { left: '3%', right: '4%', bottom: '3%', top: '20%', containLabel: true },
          xAxis: { type: 'category', data: models, axisLabel: { color: '#8ab4f8', fontSize: 10 } },
          yAxis: { type: 'value', min: 0, max: 1, axisLabel: { color: '#8ab4f8' }, splitLine: { lineStyle: { color: 'rgba(138,180,248,0.1)' } } },
          series: [
            { name: 'Accuracy', type: 'line', data: accuracies, smooth: true, itemStyle: { color: '#00d4ff' } },
            { name: 'Precision', type: 'line', data: precisions, smooth: true, itemStyle: { color: '#ffd700' } },
            { name: 'Recall', type: 'line', data: recalls, smooth: true, itemStyle: { color: '#ff6b6b' } },
            { name: 'F1', type: 'line', data: f1s, smooth: true, itemStyle: { color: '#a29bfe' } }
          ]
        })
      }

      // 特征重要性
      if (featChart.value) {
        const feat = data.feature_importance || {}
        const keys = Object.keys(feat).slice(0, 10).reverse()
        const vals = keys.map(k => feat[k])
        const featInstance = echarts.init(featChart.value)
        chartInstances.push(featInstance)
        featInstance.setOption({
          tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
          grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
          xAxis: { type: 'value', axisLabel: { color: '#8ab4f8' }, splitLine: { lineStyle: { color: 'rgba(138,180,248,0.1)' } } },
          yAxis: { type: 'category', data: keys, axisLabel: { color: '#8ab4f8', fontSize: 11 } },
          series: [{
            type: 'bar',
            data: vals,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#0066ff' },
                { offset: 1, color: '#00d4ff' }
              ]),
              borderRadius: [0, 4, 4, 0]
            },
            label: { show: true, position: 'right', color: '#00d4ff', fontSize: 11 }
          }]
        })
      }

      // 雷达图（取XGBoost或第一个模型）
      if (radarChart.value && models.length > 0) {
        const bestModel = models.find(m => m === 'XGBoost') || models[0]
        const m = metrics[bestModel] || {}
        const radarInstance = echarts.init(radarChart.value)
        chartInstances.push(radarInstance)
        radarInstance.setOption({
          tooltip: {},
          radar: {
            indicator: [
              { name: 'Accuracy', max: 1 },
              { name: 'Precision', max: 1 },
              { name: 'Recall', max: 1 },
              { name: 'F1', max: 1 },
              { name: 'AUC', max: 1 }
            ],
            axisName: { color: '#8ab4f8', fontSize: 11 },
            splitLine: { lineStyle: { color: 'rgba(138,180,248,0.2)' } },
            splitArea: { areaStyle: { color: ['rgba(0,102,255,0.05)', 'rgba(0,212,255,0.05)'] } }
          },
          series: [{
            type: 'radar',
            data: [{
              value: [m.accuracy || 0, m.precision || 0, m.recall || 0, m.f1 || 0, m.auc || 0],
              name: bestModel,
              areaStyle: { color: 'rgba(0,212,255,0.3)' },
              lineStyle: { color: '#00d4ff' },
              itemStyle: { color: '#00d4ff' }
            }]
          }]
        })
      }
    }

    function exportReport() {
      window.open('http://localhost:8000/api/export-report/', '_blank')
    }

    function handleResize() {
      chartInstances.forEach(c => c.resize())
    }

    onMounted(() => {
      updateTime()
      timer = setInterval(updateTime, 1000)
      loadData()
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      clearInterval(timer)
      window.removeEventListener('resize', handleResize)
      chartInstances.forEach(c => c.dispose())
    })

    return {
      aucChart, distChart, featChart, metricChart, radarChart,
      stats, currentTime, defaultRate, bestAuc, exportReport
    }
  }
}
</script>

<style scoped>
.dashboard-screen {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a1929 0%, #1a2a4a 50%, #0d1b2a 100%);
  padding: 20px;
  box-sizing: border-box;
  color: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
}

.title {
  display: flex;
  flex-direction: column;
}

.main-title {
  font-size: 28px;
  font-weight: bold;
  background: linear-gradient(90deg, #00d4ff, #0066ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 2px;
}

.sub-title {
  font-size: 12px;
  color: #8ab4f8;
  letter-spacing: 3px;
  margin-top: 4px;
}

.header-time {
  font-size: 16px;
  color: #00d4ff;
  font-family: 'Courier New', monospace;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.15), rgba(0, 212, 255, 0.05));
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 10px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
}

.stat-card.warning {
  background: linear-gradient(135deg, rgba(255, 165, 0, 0.15), rgba(255, 100, 0, 0.05));
  border-color: rgba(255, 165, 0, 0.3);
}

.stat-card.success {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.15), rgba(0, 200, 100, 0.05));
  border-color: rgba(0, 255, 136, 0.3);
}

.stat-card.danger {
  background: linear-gradient(135deg, rgba(255, 71, 87, 0.15), rgba(255, 100, 100, 0.05));
  border-color: rgba(255, 71, 87, 0.3);
}

.stat-card.primary {
  background: linear-gradient(135deg, rgba(162, 155, 254, 0.15), rgba(108, 92, 231, 0.05));
  border-color: rgba(162, 155, 254, 0.3);
}

.stat-icon {
  font-size: 32px;
}

.stat-value {
  font-size: 26px;
  font-weight: bold;
  color: #00d4ff;
  font-family: 'Courier New', monospace;
}

.stat-card.warning .stat-value { color: #ffa500; }
.stat-card.success .stat-value { color: #00ff88; }
.stat-card.danger .stat-value { color: #ff4757; }
.stat-card.primary .stat-value { color: #a29bfe; }

.stat-label {
  font-size: 13px;
  color: #8ab4f8;
  margin-top: 4px;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.chart-box {
  background: rgba(0, 20, 40, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 10px;
  padding: 15px;
}

.chart-box.wide {
  grid-column: span 2;
}

.chart-title {
  font-size: 15px;
  color: #00d4ff;
  margin-bottom: 10px;
  padding-left: 10px;
  border-left: 3px solid #00d4ff;
}

.chart-container {
  width: 100%;
  height: 280px;
}
</style>
