<template>
  <div class="page-container">
    <div class="page-header"><h2>🔮 风险预测</h2><p>单条/批量预测客户违约风险</p></div>
    <el-tabs v-model="activeTab" class="pred-tabs">
      <el-tab-pane label="单条预测" name="single">
        <div class="predict-layout">
          <div class="form-panel">
            <h3>客户信息录入</h3>
            <el-form :model="form" label-position="top">
              <el-row :gutter="20">
                <el-col :span="12"><el-form-item label="信用额度 LIMIT_BAL"><el-input-number v-model.number="form.LIMIT_BAL" :min="0" :max="1000000" style="width:100%" /></el-form-item></el-col>
                <el-col :span="12"><el-form-item label="性别 SEX (1=男,2=女)"><el-input-number v-model.number="form.SEX" :min="1" :max="2" style="width:100%" /></el-form-item></el-col>
                <el-col :span="12"><el-form-item label="教育程度 EDUCATION"><el-input-number v-model.number="form.EDUCATION" :min="0" :max="6" style="width:100%" /></el-form-item></el-col>
                <el-col :span="12"><el-form-item label="婚姻 MARRIAGE"><el-input-number v-model.number="form.MARRIAGE" :min="0" :max="3" style="width:100%" /></el-form-item></el-col>
                <el-col :span="12"><el-form-item label="年龄 AGE"><el-input-number v-model.number="form.AGE" :min="18" :max="100" style="width:100%" /></el-form-item></el-col>
                <el-col :span="12"><el-form-item label="预测阈值 Threshold"><el-slider v-model="threshold" :min="0.1" :max="0.9" :step="0.05" show-input /></el-form-item></el-col>
              </el-row>
              <el-form-item label="选择模型">
                <el-select v-model="modelName" style="width:100%">
                  <el-option label="XGBoost（推荐）" value="XGBoost" />
                  <el-option label="LightGBM" value="LightGBM" />
                  <el-option label="随机森林" value="RandomForest" />
                  <el-option label="逻辑回归" value="LogisticRegression" />
                  <el-option label="SVM" value="SVM" />
                </el-select>
              </el-form-item>
              <el-button type="primary" size="large" @click="doPredict" :loading="predicting" style="width:100%">🎯 开始预测</el-button>
            </el-form>
          </div>
          <div class="result-panel">
            <h3>预测结果</h3>
            <div v-if="!result" class="empty-state"><div class="empty-icon">🔍</div><p>填写信息后点击预测</p></div>
            <div v-else class="result-card" :class="riskClass">
              <div class="result-icon">{{ riskIcon }}</div>
              <div class="result-label" :style="{color: result.risk_color}">{{ result.risk_level || (result.label===1?'高风险':'低风险') }}</div>
              <div class="proba-text">违约概率</div>
              <div class="proba-value" :style="{color: result.risk_color}">{{ (result.proba*100).toFixed(2) }}%</div>
              <el-progress :percentage="result.proba*100" :color="result.risk_color || (result.label===1?'#ff4757':'#00ff88')" :stroke-width="20" />
              <div class="risk-bars">
                <div class="risk-bar-item" :class="{active: result.proba < 0.3}"><span>低风险</span><small>&lt;30%</small></div>
                <div class="risk-bar-item" :class="{active: result.proba >= 0.3 && result.proba < 0.7}"><span>中风险</span><small>30%-70%</small></div>
                <div class="risk-bar-item" :class="{active: result.proba >= 0.7}"><span>高风险</span><small>&gt;70%</small></div>
              </div>
              <div class="result-tip">{{ riskTip }}</div>
            </div>
            <div v-if="shapData" class="shap-box">
              <h4>SHAP 因素分析 Top 10</h4>
              <div v-for="(v,k) in shapData" :key="k" class="shap-row">
                <span class="shap-label">{{ k }}</span>
                <div class="shap-bar-wrap"><div class="shap-bar" :class="v>0?'pos':'neg'" :style="{width:Math.abs(v*200)+'%'}"></div></div>
                <span class="shap-val">{{ v>0?'+':'' }}{{ v.toFixed(4) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="批量预测" name="batch">
        <div class="form-panel">
          <h3>📁 批量文件预测</h3>
          <el-upload drag :auto-upload="false" :on-change="handleBatchFile" accept=".csv,.xlsx,.xls">
            <div class="empty-icon">📄</div><div>上传客户数据文件进行批量预测</div>
          </el-upload>
          <div class="batch-controls">
            <el-select v-model="batchModel" style="width:200px">
              <el-option label="XGBoost" value="XGBoost" /><el-option label="LightGBM" value="LightGBM" />
              <el-option label="随机森林" value="RandomForest" /><el-option label="逻辑回归" value="LogisticRegression" /><el-option label="SVM" value="SVM" />
            </el-select>
            <el-button type="primary" @click="doBatchPredict" :loading="batchLoading" :disabled="!batchFile">批量预测</el-button>
          </div>
          <div v-if="batchResult" class="batch-summary">
            <div class="batch-stats">
              <div class="batch-stat-item"><span>总样本</span><b>{{ batchResult.total }}</b></div>
              <div class="batch-stat-item high"><span>高风险</span><b>{{ batchResult.high_risk }}</b></div>
              <div class="batch-stat-item mid"><span>中风险</span><b>{{ batchResult.mid_risk }}</b></div>
              <div class="batch-stat-item low"><span>低风险</span><b>{{ batchResult.low_risk }}</b></div>
            </div>
            <el-table :data="batchResult.results.slice(0,20)" size="small" max-height="400" stripe>
              <el-table-column prop="index" label="序号" width="80" />
              <el-table-column prop="label" label="预测标签" width="100" />
              <el-table-column prop="proba" label="违约概率" width="120" />
              <el-table-column prop="risk" label="风险等级">
                <template #default="{ row }">
                  <span :style="{color: row.proba>=0.7?'#ff4757':(row.proba>=0.3?'#ffa502':'#00ff88'), fontWeight:'bold'}">{{ row.risk }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script>
import { ref, computed } from 'vue'
import { predictSingle, getSHAP, batchPredict } from '../api'
import { ElMessage } from 'element-plus'
export default {
  setup() {
    const activeTab = ref('single')
    const form = ref({ LIMIT_BAL: 200000, SEX: 2, EDUCATION: 2, MARRIAGE: 1, AGE: 35 })
    const threshold = ref(0.5), modelName = ref('XGBoost')
    const result = ref(null), shapData = ref(null), predicting = ref(false)
    const batchFile = ref(null), batchModel = ref('XGBoost'), batchLoading = ref(false), batchResult = ref(null)
    const riskClass = computed(() => {
      if (!result.value) return 'safe'
      if (result.value.proba >= 0.7) return 'danger'
      if (result.value.proba >= 0.3) return 'warning'
      return 'safe'
    })
    const riskIcon = computed(() => {
      if (!result.value) return '✅'
      if (result.value.proba >= 0.7) return '🚨'
      if (result.value.proba >= 0.3) return '⚠️'
      return '✅'
    })
    const riskTip = computed(() => {
      if (!result.value) return ''
      if (result.value.proba >= 0.7) return '高风险：建议拒绝或要求增加担保/抵押'
      if (result.value.proba >= 0.3) return '中风险：建议人工复核，补充收入证明'
      return '低风险：建议正常审批流程'
    })
    async function doPredict() {
      predicting.value = true; result.value = null; shapData.value = null
      try {
        const resp = await predictSingle({ features: form.value, model_name: modelName.value, threshold: threshold.value })
        result.value = resp.data
        try { const s = await getSHAP({ features: form.value, model_name: modelName.value }); shapData.value = s.data.shap_values } catch(e) {}
      } catch(e) { ElMessage.error(e.response?.data?.error || '预测失败') }
      finally { predicting.value = false }
    }
    function handleBatchFile(f) { batchFile.value = f.raw; batchResult.value = null }
    async function doBatchPredict() {
      if (!batchFile.value) { ElMessage.warning('请先上传文件'); return }
      batchLoading.value = true
      try { const r = await batchPredict(batchFile.value, batchModel.value, threshold.value); batchResult.value = r.data; ElMessage.success('批量预测完成') }
      catch(e) { ElMessage.error(e.response?.data?.error || '批量预测失败') }
      finally { batchLoading.value = false }
    }
    return { activeTab, form, threshold, modelName, result, shapData, predicting, batchFile, batchModel, batchLoading, batchResult, riskClass, riskIcon, riskTip, doPredict, handleBatchFile, doBatchPredict }
  }
}
</script>
<style scoped>
.page-container { padding: 30px; min-height: 100vh; background: linear-gradient(135deg, #0a1929 0%, #1a2a4a 100%); color: #fff; }
.page-header h2 { font-size: 28px; color: #00d4ff; margin: 0 0 8px 0; }
.page-header p { color: #8ab4f8; margin: 0 0 20px 0; }
.predict-layout { display: grid; grid-template-columns: 1fr 400px; gap: 25px; }
.form-panel, .result-panel { background: rgba(0,20,40,0.6); border: 1px solid rgba(0,212,255,0.2); border-radius: 12px; padding: 25px; }
.form-panel h3, .result-panel h3 { color: #00d4ff; margin: 0 0 20px 0; }
.empty-state { text-align: center; padding: 80px 20px; color: #8ab4f8; }
.empty-icon { font-size: 64px; margin-bottom: 15px; }
.result-card { text-align: center; padding: 30px 20px; border-radius: 12px; }
.result-card.danger { background: rgba(255,71,87,0.15); border: 1px solid rgba(255,71,87,0.4); }
.result-card.warning { background: rgba(255,165,2,0.15); border: 1px solid rgba(255,165,2,0.4); }
.result-card.safe { background: rgba(0,255,136,0.15); border: 1px solid rgba(0,255,136,0.4); }
.result-icon { font-size: 64px; margin-bottom: 15px; }
.result-label { font-size: 20px; font-weight: bold; margin-bottom: 15px; }
.result-card.danger .result-label { color: #ff4757; }
.result-card.safe .result-label { color: #00ff88; }
.proba-text { font-size: 14px; color: #8ab4f8; }
.proba-value { font-size: 42px; font-weight: bold; font-family: monospace; margin: 10px 0 20px; }
.result-card.danger .proba-value { color: #ff4757; }
.result-card.safe .proba-value { color: #00ff88; }
.result-tip { margin-top: 20px; font-size: 14px; color: #8ab4f8; }
.risk-bars { display: flex; gap: 8px; margin-top: 15px; }
.risk-bar-item { flex: 1; padding: 8px 4px; border-radius: 6px; text-align: center; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); transition: all 0.3s; }
.risk-bar-item span { display: block; font-size: 12px; color: #8ab4f8; }
.risk-bar-item small { font-size: 10px; color: #5a7a9a; }
.risk-bar-item.active { border-color: #00d4ff; background: rgba(0,212,255,0.15); }
.risk-bar-item.active span { color: #00d4ff; font-weight: bold; }
.batch-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.batch-stat-item { background: rgba(0,212,255,0.08); padding: 15px; border-radius: 8px; text-align: center; }
.batch-stat-item span { display: block; color: #8ab4f8; font-size: 12px; margin-bottom: 6px; }
.batch-stat-item b { font-size: 24px; color: #00d4ff; }
.batch-stat-item.high b { color: #ff4757; }
.batch-stat-item.mid b { color: #ffa502; }
.batch-stat-item.low b { color: #00ff88; }
.shap-box { margin-top: 25px; padding: 15px; background: rgba(0,212,255,0.05); border-radius: 8px; }
.shap-box h4 { color: #00d4ff; margin: 0 0 12px 0; }
.shap-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; font-size: 12px; }
.shap-label { width: 130px; color: #8ab4f8; }
.shap-bar-wrap { flex: 1; height: 8px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; }
.shap-bar { height: 100%; }
.shap-bar.pos { background: #ff4757; }
.shap-bar.neg { background: #00ff88; }
.shap-val { width: 70px; text-align: right; font-family: monospace; }
.batch-controls { margin-top: 20px; display: flex; gap: 15px; justify-content: center; align-items: center; }
.batch-summary { margin-top: 20px; color: #8ab4f8; }
:deep(.el-form-item__label) { color: #fff !important; }
</style>
