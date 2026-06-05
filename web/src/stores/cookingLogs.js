import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCookingLogs, getCookingLog, createCookingLog, updateCookingLog, deleteCookingLog } from '@/api/cooking_logs'
import { groupLogsByDate } from '@/utils/date'

export const useCookingLogsStore = defineStore('cookingLogs', () => {
  const logs = ref([])
  const loading = ref(false)
  const currentLog = ref(null)

  const groupedLogs = computed(() => groupLogsByDate(logs.value))

  const totalMeals = computed(() => logs.value.length)

  async function fetchLogs(params = {}) {
    loading.value = true
    try {
      const res = await getCookingLogs(params)
      logs.value = res.list || res || []
    } catch (e) {
      console.error('获取烹饪记录失败', e)
    } finally {
      loading.value = false
    }
  }

  async function appendLogs(params = {}) {
    loading.value = true
    try {
      const res = await getCookingLogs(params)
      const list = res.list || res || []
      const seen = new Set(logs.value.map(l => l.id))
      const fresh = list.filter(l => !seen.has(l.id))
      logs.value = [...logs.value, ...fresh]
      return { list: fresh, total: res.total ?? list.length }
    } catch (e) {
      console.error('加载更多烹饪记录失败', e)
      return { list: [], total: 0 }
    } finally {
      loading.value = false
    }
  }

  async function fetchLog(id) {
    try {
      const res = await getCookingLog(id)
      currentLog.value = res
      return res
    } catch (e) {
      console.error('获取烹饪记录详情失败', e)
      throw e
    }
  }

  async function createLog(data) {
    const res = await createCookingLog(data)
    logs.value.unshift(res)
    return res
  }

  async function updateLog(id, data) {
    const res = await updateCookingLog(id, data)
    const idx = logs.value.findIndex(l => l.id === id)
    if (idx !== -1) {
      logs.value[idx] = { ...logs.value[idx], ...res }
    }
    if (currentLog.value?.id === id) {
      currentLog.value = { ...currentLog.value, ...res }
    }
    return res
  }

  async function removeLog(id) {
    await deleteCookingLog(id)
    logs.value = logs.value.filter(l => l.id !== id)
    if (currentLog.value?.id === id) {
      currentLog.value = null
    }
  }

  return {
    logs, loading, currentLog,
    groupedLogs, totalMeals,
    fetchLogs, appendLogs, fetchLog, createLog, updateLog, removeLog,
  }
})