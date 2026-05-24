import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getUserProfile, updateUserProfile, updatePreferences, getStatistics } from '@/api/users'
import { getToken, setToken, removeToken, getUserInfo, setUserInfo, removeUserInfo, getPreferences, setPreferences } from '@/utils/storage'

export const useUserStore = defineStore('user', () => {
  const token = ref(getToken())
  const userInfo = ref(getUserInfo() || {})
  const preferences = ref(getPreferences() || {
    diet_type: 'omnivore',
    disliked: [],
    skill_level: 'beginner',
    flavor_pref: [],
  })
  const stats = ref({
    totalMeals: 0,
    streakDays: 0,
    savedItems: 0,
  })

  const isLoggedIn = computed(() => !!token.value)
  const nickname = computed(() => userInfo.value.nickname || '美食家')
  const avatarUrl = computed(() => userInfo.value.avatar_url || '')

  async function login(jwt, user) {
    token.value = jwt
    userInfo.value = user
    setToken(jwt)
    setUserInfo(user)
  }

  function logout() {
    token.value = ''
    userInfo.value = {}
    removeToken()
    removeUserInfo()
  }

  async function fetchProfile() {
    try {
      const res = await getUserProfile()
      userInfo.value = res
      setUserInfo(res)
    } catch (e) {
      console.error('获取用户信息失败', e)
    }
  }

  async function updateProfile(data) {
    const res = await updateUserProfile(data)
    userInfo.value = { ...userInfo.value, ...res }
    setUserInfo(userInfo.value)
    return res
  }

  async function savePreferences(data) {
    const res = await updatePreferences(data)
    preferences.value = { ...preferences.value, ...res }
    setPreferences(preferences.value)
    return res
  }

  async function fetchStatistics() {
    try {
      const res = await getStatistics()
      stats.value = res
    } catch (e) {
      console.error('获取统计数据失败', e)
    }
  }

  return {
    token, userInfo, preferences, stats,
    isLoggedIn, nickname, avatarUrl,
    login, logout, fetchProfile, updateProfile, savePreferences, fetchStatistics,
  }
})