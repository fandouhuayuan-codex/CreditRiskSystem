<template>
<el-row :gutter="20">
  <el-col :span="12"><el-card><div ref="aucChart" style="height:300px;"></div></el-card></el-col>
  <el-col :span="12"><el-card><div ref="distChart" style="height:300px;"></div></el-card></el-col>
  <el-col :span="24" style="margin-top:20px;"><el-card><div ref="featChart" style="height:400px;"></div></el-card></el-col>
</el-row>
</template>
<script>
import * as echarts from 'echarts'
import { onMounted, ref } from 'vue'
import { getDashboard } from '../api'
export default {
  setup(){
    const aucChart=ref(null);
    const distChart=ref(null);
    const featChart=ref(null);
    async function render(){
      const resp=await getDashboard();
      const data=resp.data;
      const models=Object.keys(data.metrics || {});
      const aucs=models.map(m => (data.metrics[m] && data.metrics[m].auc) ? data.metrics[m].auc : 0);
      const aucInstance=echarts.init(aucChart.value);
      aucInstance.setOption({
        title:{text:'模型 AUC 对比'},
        xAxis:{type:'category', data:models},
        yAxis:{type:'value'},
        series:[{type:'bar', data:aucs}]
      });

      const distInstance=echarts.init(distChart.value);
      distInstance.setOption({
        title:{text:'违约分布'},
        series:[{name:'分布', type:'pie', radius:'50%', data:[
          {value:data.distribution.negative, name:'正常'},
          {value:data.distribution.positive, name:'违约'}
        ]}]
      });

      const feat=data.feature_importance || {};
      const keys=Object.keys(feat).slice(0,10);
      const vals=keys.map(k=>feat[k]);
      const featInstance=echarts.init(featChart.value);
      featInstance.setOption({
        title:{text:'特征重要性前10名（XGBoost）'},
        xAxis:{type:'value'},
        yAxis:{type:'category', data:keys},
        series:[{type:'bar', data:vals}]
      });
    }
    onMounted(()=>{ render() })
    return { aucChart, distChart, featChart }
  }
}
</script>
