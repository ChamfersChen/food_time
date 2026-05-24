import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCookingLogs, getCookingLog, createCookingLog } from '@/api/cooking_logs'
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

  return {
    logs, loading, currentLog,
    groupedLogs, totalMeals,
    fetchLogs, fetchLog, createLog,
  }
})