import { reactive } from 'vue'

/** 轻量全局状态：登录人、角色、动态菜单 */
export const store = reactive({
  user: JSON.parse(localStorage.getItem('ws_user') || 'null'),
  menus: JSON.parse(localStorage.getItem('ws_menus') || '[]'),
  setLogin(user, menus) {
    this.user = user
    this.menus = menus || []
    localStorage.setItem('ws_user', JSON.stringify(user || null))
    localStorage.setItem('ws_menus', JSON.stringify(menus || []))
  },
  setUser(user) {
    this.user = user
    localStorage.setItem('ws_user', JSON.stringify(user || null))
  },
  logout() {
    this.user = null
    this.menus = []
    localStorage.removeItem('ws_token')
    localStorage.removeItem('ws_user')
    localStorage.removeItem('ws_menus')
  }
})
