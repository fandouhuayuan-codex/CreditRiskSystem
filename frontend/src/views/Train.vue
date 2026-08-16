<template>
<el-card>
  <div style="margin-bottom:16px;">
    <el-checkbox v-model="useGrid">使用 GridSearchCV</el-checkbox>
    <el-input-number v-model="smoteRatio" :min="0.05" :max="0.5" :step="0.05"></el-input-number>
    <el-button type="primary" @click="doTrain">开始训练</el-button>
  </div>
  <div v-if="metrics">{{ metrics }}</div>
</el-card>
</template>
<script>
import { ref } from 'vue'
import { trainModels } from '../api'
export default {
  setup(){
    const useGrid=ref(true);
    const smoteRatio=ref(0.25);
    const metrics=ref(null);
    async function doTrain(){
      try{
        const resp=await trainModels({ use_gridsearch: useGrid.value, smote_ratio: smoteRatio.value });
        metrics.value=resp.data.metrics;
        alert('训练完成')
      }catch(e){
        alert('训练失败:'+e)
      }
    }
    return { useGrid, smoteRatio, doTrain, metrics }
  }
}
</script>
