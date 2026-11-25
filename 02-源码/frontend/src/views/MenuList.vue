<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>菜单管理</h2>
        <span class="muted" style="margin-left:auto">visible=0 的菜单不在侧边栏显示，但可被权限引用</span>
      </div>
      <el-table :data="rows" border>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="menuName" label="菜单名称" min-width="130" />
        <el-table-column prop="menuType" label="类型" width="80" />
        <el-table-column prop="path" label="路由" min-width="150" />
        <el-table-column prop="perms" label="权限标识" min-width="160" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="显示" width="90"><template #default="{ row }"><el-tag :type="row.visible === 1 ? 'success' : 'info'" effect="light">{{ row.visible === 1 ? '显示' : '隐藏' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }"><el-button link type="primary" @click="toggle(row)">{{ row.visible === 1 ? '隐藏' : '显示' }}</el-button></template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const rows = ref([])
async function load() { rows.value = await request.get('/api/menu/tree') }
async function toggle(row) {
  await request.put('/api/menu/' + row.id, { visible: row.visible === 1 ? 0 : 1 })
  ElMessage.success('已更新')
  load()
}
onMounted(load)
</script>
