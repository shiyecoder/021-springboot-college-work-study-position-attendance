<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>角色与数据范围</h2><el-button type="primary" size="small" style="margin-left:auto" @click="openAdd">新增角色</el-button></div>
      <el-table :data="rows" border>
        <el-table-column prop="roleCode" label="角色编码" min-width="120" />
        <el-table-column prop="roleName" label="角色名称" min-width="150" />
        <el-table-column prop="dataScope" label="数据范围" min-width="130" />
        <el-table-column label="状态" width="92"><template #default="{ row }"><el-tag :type="row.status === '1' ? 'success' : 'info'" effect="light">{{ row.status === '1' ? '启用' : '停用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openAssign(row)">分配菜单</el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dlg" :title="form.id ? '编辑角色' : '新增角色'" width="480px">
      <el-form label-width="96px">
        <el-form-item label="角色编码"><el-input v-model="form.roleCode" /></el-form-item>
        <el-form-item label="角色名称"><el-input v-model="form.roleName" /></el-form-item>
        <el-form-item label="数据范围">
          <el-select v-model="form.dataScope" style="width:100%">
            <el-option label="本人 SELF" value="SELF" />
            <el-option label="本部门 DEPT" value="DEPT" />
            <el-option label="全部 ALL" value="ALL" />
            <el-option label="只读全部 ALL_READONLY" value="ALL_READONLY" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg = false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="assignDlg" :title="'为「' + (cur.roleName || '') + '」分配菜单'" width="520px">
      <el-tree ref="tree" :data="menuTree" show-checkbox node-key="id" :props="{ label: 'menuName', children: 'children' }"
               default-expand-all :default-checked-keys="checked" />
      <template #footer>
        <el-button @click="assignDlg = false">取消</el-button>
        <el-button type="primary" @click="saveAssign">保存授权</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const rows = ref([]); const menus = ref([]); const menuTree = ref([])
const dlg = ref(false); const assignDlg = ref(false); const tree = ref(); const cur = ref({})
const checked = ref([])
const form = reactive({})

async function load() {
  const d = await request.get('/api/role/page', { params: { page: 1, size: 20 } })
  rows.value = d.list || []
}
async function loadMenus() {
  menus.value = await request.get('/api/menu/tree')
}
function openAdd() { Object.keys(form).forEach((k) => delete form[k]); form.dataScope = 'SELF'; dlg.value = true }
function openEdit(row) { Object.keys(form).forEach((k) => delete form[k]); Object.assign(form, row); dlg.value = true }
async function save() {
  if (form.id) await request.put('/api/role/' + form.id, form)
  else await request.post('/api/role', form)
  ElMessage.success('已保存'); dlg.value = false; load()
}
async function openAssign(row) {
  cur.value = row
  const ids = await request.get('/api/role/' + row.id + '/menus')
  checked.value = ids || []
  assignDlg.value = true
  setTimeout(() => tree.value && tree.value.setCheckedKeys(checked.value), 60)
}
async function saveAssign() {
  const ids = tree.value.getCheckedKeys().concat(tree.value.getHalfCheckedKeys())
  await request.put('/api/role/' + cur.value.id + '/menus', ids)
  ElMessage.success('授权已保存，重新登录后生效')
  assignDlg.value = false
}
onMounted(async () => {
  await Promise.all([load(), loadMenus()])
  const roots = []
  const map = {}
  menus.value.forEach((m) => { map[m.id] = { ...m, children: [] } })
  menus.value.forEach((m) => {
    if (m.parentId && map[m.parentId]) map[m.parentId].children.push(map[m.id])
    else roots.push(map[m.id])
  })
  menuTree.value = roots
})
</script>
