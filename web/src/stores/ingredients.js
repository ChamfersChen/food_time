import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getIngredients,
  getIngredient,
  addIngredient,
  updateIngredient,
  deleteIngredient,
  markConsumed as markConsumedApi,
} from '@/api/ingredients'

const CATEGORIES = [
  { value: 'vegetables', label: '蔬菜', icon: '🥬' },
  { value: 'meat', label: '肉类', icon: '🥩' },
  { value: 'seafood', label: '海鲜', icon: '🦐' },
  { value: 'dairy', label: '乳制品', icon: '🥛' },
  { value: 'fruit', label: '水果', icon: '🍎' },
  { value: 'condiment', label: '调料', icon: '🧂' },
  { value: 'beverage', label: '饮料', icon: '🧃' },
  { value: 'other', label: '其他', icon: '📦' },
]

const ZONES = [
  { value: 'refrigeration', label: '冷藏' },
  { value: 'freezing', label: '冷冻' },
  { value: 'room_temp', label: '常温' },
]

const UNITS = ['个', '克', '千克', '毫升', '升', '袋', '盒', '根', '片', '把', '瓶', '罐']

export const useIngredientsStore = defineStore('ingredients', () => {
  const list = ref([])
  const loading = ref(false)
  const currentFilter = ref('all')
  const currentZone = ref('refrigeration')
  const searchKeyword = ref('')

  const notConsumed = computed(() => list.value.filter(i => !i.is_consumed))

  const expiringItems = computed(() =>
    notConsumed.value.filter(i => i.freshness === 'expiring' || i.freshness === 'expired')
      .sort((a, b) => new Date(a.expire_date) - new Date(b.expire_date))
  )

  const expiredItems = computed(() =>
    notConsumed.value.filter(i => i.freshness === 'expired')
  )

  const byZone = computed(() => (zone) =>
    notConsumed.value.filter(i => i.zone === zone)
  )

  const byCategory = computed(() => (category) =>
    notConsumed.value.filter(i => i.category === category)
  )

  const categorySummary = computed(() => {
    const summary = {}
    CATEGORIES.forEach((cat) => { summary[cat.value] = 0 })
    notConsumed.value.forEach((item) => {
      if (summary[item.category] !== undefined) {
        summary[item.category]++
      } else {
        summary.other = (summary.other || 0) + 1
      }
    })
    return summary
  })

  const filteredList = computed(() => {
    let items = notConsumed.value
    if (currentZone.value !== 'all') {
      items = items.filter(i => i.zone === currentZone.value)
    }
    if (currentFilter.value !== 'all') {
      items = items.filter(i => i.category === currentFilter.value)
    }
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      items = items.filter(i => i.name.toLowerCase().includes(kw))
    }
    return items.sort((a, b) => new Date(a.expire_date) - new Date(b.expire_date))
  })

  async function fetchAll() {
    loading.value = true
    try {
      const res = await getIngredients({ is_consumed: false })
      list.value = res.list || res || []
    } catch (e) {
      console.error('获取食材列表失败', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    try {
      return await getIngredient(id)
    } catch (e) {
      console.error('获取食材详情失败', e)
      throw e
    }
  }

  async function addOne(data) {
    const res = await addIngredient(data)
    list.value.unshift(res)
    return res
  }

  async function editOne(id, data) {
    const res = await updateIngredient(id, data)
    const idx = list.value.findIndex(i => i.id === id)
    if (idx > -1) {
      list.value[idx] = { ...list.value[idx], ...res }
    }
    return res
  }

  async function markConsumed(id) {
    await markConsumedApi(id)
    const idx = list.value.findIndex(i => i.id === id)
    if (idx > -1) {
      list.value[idx].is_consumed = true
    }
  }

  async function removeOne(id) {
    await deleteIngredient(id)
    list.value = list.value.filter(i => i.id !== id)
  }

  return {
    list, loading, currentFilter, currentZone, searchKeyword,
    CATEGORIES, ZONES, UNITS,
    notConsumed, expiringItems, expiredItems, byZone, byCategory, categorySummary, filteredList,
    fetchAll, fetchOne, addOne, editOne, markConsumed, removeOne,
  }
})