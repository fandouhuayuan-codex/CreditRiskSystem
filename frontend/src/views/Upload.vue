<template>
<el-card>
  <el-upload drag :auto-upload="false" :file-list="fileList" :on-change="handleChange" :on-remove="handleRemove">
    <i class="el-icon-upload"></i>
    <div class="el-upload__text">将 CSV / Excel 文件拖拽至此，或点击上传</div>
  </el-upload>
  <el-button type="primary" @click="doUpload" :disabled="!file">上传并导入</el-button>
</el-card>
</template>
<script>
import { ref } from 'vue'
import { uploadFile } from '../api'
export default {
  setup() {
    const file=ref(null);
    const fileList=ref([]);
    function handleChange(fileItem){
      file.value=fileItem.raw;
      fileList.value=[fileItem]
    }
    function handleRemove(){
      file.value=null;
      fileList.value=[]
    }
    async function doUpload(){
      if(!file.value) return;
      try{
        const resp=await uploadFile(file.value);
        alert(JSON.stringify(resp.data))
      }catch(e){
        alert('上传失败:'+e)
      }
    }
    return { file, fileList, handleChange, handleRemove, doUpload }
  }
}
</script>
