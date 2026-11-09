<template>
  <div class="alert-page">
    <div class="page-header">
      <h2>⚠️ 风险告警中心</h2>
      <p class="subtitle">高风险客户自动告警，支持人工复核与闭环管理</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card total">
          <div class="stat-icon">📋</div>
          <div class="stat-info">
            <div class="stat-value">{{ total }}</div>
            <div class="stat-label">告警总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card pending">
          <div class="stat-icon">🔴</div>
          <div class="stat-info">
            <div class="stat-value">{{ pendingCount }}</div>
            <div class="stat-label">待复核</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card reviewed">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <div class="stat-value">{{ reviewedCount }}</div>
            <div class="stat-label">已复核</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card ignored">
          <div class="stat-icon">⚪</div>
          <div class="stat-info">
            <div class="stat-value">{{ ignoredCount }}</div>
            <div class="stat-label">已忽略</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 筛选和操作栏 -->
    <div class="filter-bar">
      <el-radio-group v-model="statusFilter" @change="fetchAlerts" size="default">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="pending">待复核</el-radio-button>
        <el-radio-button label="reviewed">已复核</el-radio-button>
        <el-radio-button label="ignored">已忽略</el-radio-button>
      </el-radio-group>
      <el-button type="primary" @click="fetchAlerts" :loading="loading">
        <span>🔄</span> 刷新
      </el-button>
    </div>

    <!-- 告警列表 -->
    <div class="table-container">
      <el-table :data="alerts" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="customer_id" label="客户编号" width="140">
          <template #default="{ row }">
            <span class="customer-id">{{ row.customer_id || '匿名' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="违约概率" width="180">
          <template #default="{ row }">
            <div class="prob-bar">
              <div class="prob-fill" :style="{ width: (row.predicted_proba * 100) + '%' }"></div>
              <span class="prob-text">{{ (row.predicted_proba * 100).toFixed(1) }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="模型" width="130" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="dark" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="告警时间" width="170" />
        <el-table-column prop="reviewed_at" label="复核时间" width="170">
          <template #default="{ row }">
            {{ row.reviewed_at || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" size="small" @click="openReviewDialog(row, 'reviewed')">复核通过</el-button>
              <el-button type="info" size="small" @click="openReviewDialog(row, 'ignored')">忽略</el-button>
            </template>
            <template v-else>
              <el-button type="primary" size="small" @click="viewDetail(row)">查看详情</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          background
          layout="prev, pager, next, total"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 复核对话框 -->
    <el-dialog v-model="reviewDialogVisible" title="告警复核" width="500px" class="review-dialog">
      <div v-if="currentAlert" class="review-content">
        <div class="review-row">
          <span class="review-label">客户编号：</span>
          <span class="review-value">{{ currentAlert.customer_id || '匿名' }}</span>
        </div>
        <div class="review-row">
          <span class="review-label">违约概率：</span>
          <span class="review-value high">{{ (currentAlert.predicted_proba * 100).toFixed(1) }}%</span>
        </div>
        <div class="review-row">
          <span class="review-label">使用模型：</span>
          <span class="review-value">{{ currentAlert.model_name }}</span>
        </div>
        <div class="review-row">
          <span class="review-label">告警时间：</span>
          <span class="review-value">{{ currentAlert.created_at }}</span>
        </div>
        <div class="review-row">
          <span class="review-label">复核备注：</span>
        </div>
        <el-input
          v-model="reviewNote"
          type="textarea"
          :rows="3"
          placeholder="请输入复核意见（选填）..."
          class="review-note-input"
        />
      </div>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button :type="reviewAction === 'reviewed' ? 'success' : 'info'" @click="submitReview" :loading="submitting">
          {{ reviewAction === 'reviewed' ? '确认复核通过' : '确认忽略' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="告警详情" width="600px">
      <div v-if="currentAlert" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="告警ID">{{ currentAlert.id }}</el-descriptions-item>
          <el-descriptions-item label="客户编号">{{ currentAlert.customer_id || '匿名' }}</el-descriptions-item>
          <el-descriptions-item label="违约概率">{{ (currentAlert.predicted_proba * 100).toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="使用模型">{{ currentAlert.model_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentAlert.status_display }}</el-descriptions-item>
          <el-descriptions-item label="告警时间">{{ currentAlert.created_at }}</el-descriptions-item>
          <el-descriptions-item label="复核时间" :span="2">{{ currentAlert.reviewed_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="复核备注" :span="2">{{ currentAlert.review_note || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAlerts, reviewAlert } from '../api'

export default {
  name: 'Alert',
  setup() {
    const alerts = ref([])
    const total = ref(0)
    const pendingCount = ref(0)
    const reviewedCount = ref(0)
    const ignoredCount = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const statusFilter = ref('all')
    const loading = ref(false)
    const reviewDialogVisible = ref(false)
    const detailDialogVisible = ref(false)
    const currentAlert = ref(null)
    const reviewAction = ref('reviewed')
    const reviewNote = ref('')
    const submitting = ref(false)

    async function fetchAlerts() {
      loading.value = true
      try {
        const res = await getAlerts({
          status: statusFilter.value,
          page: currentPage.value,
          page_size: pageSize.value
        })
        alerts.value = res.data.results
        total.value = res.data.total
        pendingCount.value = res.data.pending_count
        // 估算已复核和已忽略数量
        reviewedCount.value = Math.max(0, total.value - pendingCount.value - ignoredCount.value)
      } catch (e) {
        ElMessage.error('获取告警列表失败')
      } finally {
        loading.value = false
      }
    }

    function statusTagType(status) {
      const map = { pending: 'danger', reviewed: 'success', ignored: 'info' }
      return map[status] || 'info'
    }

    function handlePageChange(page) {
      currentPage.value = page
      fetchAlerts()
    }

    function openReviewDialog(alert, action) {
      currentAlert.value = alert
      reviewAction.value = action
      reviewNote.value = ''
      reviewDialogVisible.value = true
    }

    function viewDetail(alert) {
      currentAlert.value = alert
      detailDialogVisible.value = true
    }

    async function submitReview() {
      if (!currentAlert.value) return
      submitting.value = true
      try {
        await reviewAlert(currentAlert.value.id, {
          action: reviewAction.value,
          note: reviewNote.value
        })
        ElMessage.success(reviewAction.value === 'reviewed' ? '复核通过' : '已忽略')
        reviewDialogVisible.value = false
        fetchAlerts()
      } catch (e) {
        ElMessage.error('操作失败')
      } finally {
        submitting.value = false
      }
    }

    onMounted(() => {
      fetchAlerts()
    })

    return {
      alerts, total, pendingCount, reviewedCount, ignoredCount,
      currentPage, pageSize, statusFilter, loading,
      reviewDialogVisible, detailDialogVisible, currentAlert,
      reviewAction, reviewNote, submitting,
      fetchAlerts, statusTagType, handlePageChange,
      openReviewDialog, viewDetail, submitReview
    }
  }
}
</script>

<style scoped>
.alert-page { padding: 25px; min-height: 100vh; background: #0a1929; }
.page-header { margin-bottom: 20px; }
.page-header h2 { color: #fff; font-size: 24px; margin-bottom: 5px; }
.subtitle { color: #8ab4f8; font-size: 13px; }

.stat-row { margin-bottom: 20px; }
.stat-card {
  background: linear-gradient(135deg, rgba(13,33,55,0.9), rgba(10,25,41,0.95));
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s;
}
.stat-card:hover { border-color: rgba(0,212,255,0.5); transform: translateY(-2px); }
.stat-icon { font-size: 36px; }
.stat-value { font-size: 28px; font-weight: bold; color: #00d4ff; }
.stat-label { font-size: 13px; color: #8ab4f8; margin-top: 3px; }
.stat-card.pending .stat-value { color: #ff4757; }
.stat-card.reviewed .stat-value { color: #2ed573; }
.stat-card.ignored .stat-value { color: #a4b0be; }

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.table-container {
  background: rgba(13,33,55,0.6);
  border: 1px solid rgba(0,212,255,0.15);
  border-radius: 12px;
  padding: 15px;
}
:deep(.el-table) { background: transparent !important; }
:deep(.el-table tr) { background: transparent !important; }
:deep(.el-table th) { background: rgba(0,212,255,0.1) !important; color: #00d4ff !important; }
:deep(.el-table td) { border-bottom: 1px solid rgba(0,212,255,0.08) !important; color: #e0e0e0 !important; }
:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) { background: rgba(0,212,255,0.03) !important; }

.customer-id { color: #00d4ff; font-family: monospace; }

.prob-bar {
  position: relative;
  width: 100%;
  height: 22px;
  background: rgba(255,71,87,0.15);
  border-radius: 11px;
  overflow: hidden;
}
.prob-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffa502, #ff4757);
  border-radius: 11px;
  transition: width 0.3s;
}
.prob-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: bold;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.pagination { margin-top: 15px; display: flex; justify-content: flex-end; }
:deep(.el-pagination) { --el-pagination-bg-color: transparent; --el-pagination-text-color: #8ab4f8; }
:deep(.el-pagination button) { background: rgba(0,212,255,0.1) !important; color: #8ab4f8 !important; }
:deep(.el-pagination .is-active) { background: #00d4ff !important; color: #0a1929 !important; }

.review-dialog :deep(.el-dialog) { background: #0d2137 !important; border: 1px solid rgba(0,212,255,0.3); }
.review-dialog :deep(.el-dialog__title) { color: #00d4ff !important; }
.review-content { padding: 10px 0; }
.review-row { display: flex; margin-bottom: 12px; align-items: center; }
.review-label { color: #8ab4f8; width: 90px; flex-shrink: 0; }
.review-value { color: #fff; }
.review-value.high { color: #ff4757; font-weight: bold; font-size: 18px; }
.review-note-input { margin-top: 8px; width: 100%; }

.detail-content :deep(.el-descriptions__label) { background: rgba(0,212,255,0.1) !important; color: #00d4ff !important; }
.detail-content :deep(.el-descriptions__content) { background: transparent !important; color: #e0e0e0 !important; }
</style>
