import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getRecipes,
  getRecipe,
  getRecommendedRecipes,
  getRandomRecipe,
  searchRecipes,
  toggleFavorite,
} from '@/api/recipes'

const WARM_MESSAGES = [
  '为你精心准备的今日餐单',
  '发现冰箱里的宝藏食材',
  '让每一顿饭都充满惊喜',
  '今天想吃点什么呢？',
  '好好吃饭，是最长情的告白',
]

const RECIPE_TAGS = [
  { value: '', label: '全部' },
  { value: '家常', label: '家常' },
  { value: '快手', label: '快手' },
  { value: '低卡', label: '低卡' },
  { value: '汤类', label: '汤类' },
  { value: '早餐', label: '早餐' },
  { value: '下饭', label: '下饭' },
]

export const useRecipesStore = defineStore('recipes', () => {
  const recipeList = ref([])
  const recommendedList = ref([])
  const currentRecipe = ref(null)
  const loading = ref(false)
  const currentTag = ref('')
  const searchKeyword = ref('')
  const warmMessage = ref(WARM_MESSAGES[Math.floor(Math.random() * WARM_MESSAGES.length)])

  const filteredList = computed(() => {
    let items = recipeList.value
    if (currentTag.value) {
      items = items.filter(r => r.tags && r.tags.includes(currentTag.value))
    }
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      items = items.filter(r => r.name.toLowerCase().includes(kw))
    }
    return items
  })

  async function fetchRecommended() {
    loading.value = true
    try {
      const res = await getRecommendedRecipes({ limit: 10 })
      recommendedList.value = res.list || res || []
    } catch (e) {
      console.error('获取推荐菜谱失败', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchList(params = {}) {
    loading.value = true
    try {
      const res = await getRecipes(params)
      recipeList.value = res.list || res || []
    } catch (e) {
      console.error('获取菜谱列表失败', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchDetail(id) {
    try {
      const res = await getRecipe(id)
      currentRecipe.value = res
      return res
    } catch (e) {
      console.error('获取菜谱详情失败', e)
      throw e
    }
  }

  async function fetchRandom() {
    try {
      const res = await getRandomRecipe()
      return res
    } catch (e) {
      console.error('获取随机菜谱失败', e)
      throw e
    }
  }

  async function search(keyword) {
    searchKeyword.value = keyword
    if (!keyword) {
      return fetchList()
    }
    try {
      const res = await searchRecipes(keyword)
      recipeList.value = res.list || res || []
    } catch (e) {
      console.error('搜索菜谱失败', e)
    }
  }

  async function toggleFav(recipeId) {
    const res = await toggleFavorite(recipeId)
    if (currentRecipe.value && currentRecipe.value.id === recipeId) {
      currentRecipe.value.is_favorited = !currentRecipe.value.is_favorited
    }
    return res
  }

  function refreshWarmMessage() {
    warmMessage.value = WARM_MESSAGES[Math.floor(Math.random() * WARM_MESSAGES.length)]
  }

  return {
    recipeList, recommendedList, currentRecipe, loading, currentTag, searchKeyword,
    warmMessage, WARM_MESSAGES, RECIPE_TAGS,
    filteredList,
    fetchRecommended, fetchList, fetchDetail, fetchRandom, search, toggleFav, refreshWarmMessage,
  }
})