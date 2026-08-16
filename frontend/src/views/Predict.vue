<template>
<el-card>
  <el-form :model="form">
    <el-form-item label="LIMIT_BAL"><el-input v-model.number="form.LIMIT_BAL"></el-input></el-form-item>
    <el-form-item label="SEX"><el-input-number v-model.number="form.SEX" :min="0" :max="2"></el-input-number></el-form-item>
    <el-form-item label="年龄"><el-input-number v-model.number="form.AGE"></el-input-number></el-form-item>
    <el-form-item label="阈值"><el-input-number v-model.number="threshold" :min="0" :max="1" :step="0.01"></el-input-number></el-form-item>
    <el-button type="primary" @click="doPredict">预测</el-button>
  </el-form>
  <div v-if="result"><p>标签：{{ result.label }}</p><p>概率：{{ result.proba }}</p></div>
</el-card>
</template>
<script>
import { ref } from 'vue'
import { predictSingle } from '../api'
export default {
  setup(){
    const form=ref({ LIMIT_BAL:20000, SEX:1, AGE:35 });
    const threshold=ref(0.5);
    const result=ref(null);
    async function doPredict(){
      try{
        const resp=await predictSingle({ features: form.value, model_name: 'XGBoost', threshold: threshold.value });
        result.value=resp.data
      }catch(e){
        alert('预测失败:'+e)
      }
    }
    return { form, threshold, doPredict, result }
  }
}
</script>
