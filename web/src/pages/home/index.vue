<template>
  <view class="page-home">
    <view class="page-home__header">
      <view class="page-home__greeting">
        <text class="page-home__greeting-text">{{ greeting }}，{{ nickname }}</text>
      </view>
      <view class="page-home__avatar-wrap" @tap="goProfile">
        <image
          class="page-home__avatar"
          :src="avatarUrl || 'https://picsum.photos/200/200?random=user'"
          mode="aspectFill"
        />
      </view>
    </view>

    <view class="page-home__section">
      <view class="page-home__section-header">
        <text class="page-home__section-title">✨ AI 今日推荐</text>
      </view>
      <TodayRecommend
        :recipe="recommendRecipe"
        :match-count="matchCount"
        :loading="recommendLoading"
        @tap="goRecipeDetail"
      />
    </view>

    <view v-if="expiringItems.length > 0" class="page-home__section">
      <view class="page-home__section-header">
        <text class="page-home__section-title">⚠️ 即将过期</text>
        <text class="page-home__section-more" @tap="goFridge">查看全部</text>
      </view>
      <view class="page-home__expiring-list">
        <view
          v-for="item in expiringItems"
          :key="item.id"
          class="page-home__expiring-row"
        >
          <view class="page-home__expiring-img-wrap">
            <text class="page-home__expiring-icon">{{ getCategoryIcon(item.category) }}</text>
          </view>
          <view class="page-home__expiring-body">
            <text class="page-home__expiring-name">{{ item.name }}</text>
            <text class="page-home__expiring-days">{{ calcFreshnessLabel(item.expire_date) }}</text>
          </view>
          <ExpiryBadge :expire-date="item.expire_date" />
        </view>
      </view>
    </view>

    <view class="page-home__section">
      <text class="page-home__section-title">📦 冰箱库存概览</text>
      <view class="page-home__grid">
        <view
          v-for="cat in categoryList"
          :key="cat.value"
          class="page-home__grid-item"
          @tap="goFridgeCategory(cat.value)"
        >
          <view class="page-home__grid-icon-wrap" :style="{ backgroundColor: cat.bgColor }">
            <text class="page-home__grid-icon">{{ cat.icon }}</text>
          </view>
          <text class="page-home__grid-name">{{ cat.label }}</text>
          <text class="page-home__grid-count">{{ categorySummary[cat.value] || 0 }}</text>
        </view>
      </view>
    </view>

  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { useIngredientsStore } from '@/stores/ingredients'
import { useRecipesStore } from '@/stores/recipes'
import { calcFreshness } from '@/utils/freshness'
import { getGreeting } from '@/utils/date'

import TodayRecommend from '@/components/TodayRecommend.vue'
import ExpiryBadge from '@/components/ExpiryBadge.vue'

const CATEGORY_LIST = [
  { value: 'vegetables', label: '蔬菜', icon: '🥬', bgColor: '#E8F5F1' },
  { value: 'meat', label: '肉类', icon: '🥩', bgColor: '#FDE8E6' },
  { value: 'seafood', label: '海鲜', icon: '🦐', bgColor: '#E0F0FF' },
  { value: 'dairy', label: '乳制品', icon: '🥛', bgColor: '#FFF5E0' },
  { value: 'fruit', label: '水果', icon: '🍎', bgColor: '#FFF0E8' },
  { value: 'egg', label: '蛋类', icon: '🥚', bgColor: '#F5E8D0' },
  { value: 'beverage', label: '饮料', icon: '🧃', bgColor: '#E8F5F9' },
  { value: 'other', label: '其他', icon: '📦', bgColor: '#F0F0F0' },
]

const userStore = useUserStore()
const ingredientsStore = useIngredientsStore()
const recipesStore = useRecipesStore()

const recommendLoading = ref(true)

const greeting = computed(() => getGreeting())
const nickname = computed(() => userStore.nickname)
const avatarUrl = computed(() => userStore.avatarUrl)
const expiringItems = computed(() => ingredientsStore.expiringItems.slice(0, 5))
const categorySummary = computed(() => ingredientsStore.categorySummary)
const categoryList = CATEGORY_LIST

const recommendRecipe = computed(() =>
  recipesStore.recommendedList[0] || {}
)
const matchCount = computed(() =>
  recommendRecipe.value.match_count || 0
)

function getCategoryIcon(category) {
  const map = { vegetables: '🥬', meat: '🥩', seafood: '🦐', dairy: '🥛', fruit: '🍎', egg: '🥚', beverage: '🧃', other: '📦' }
  return map[category] || '📦'
}

function calcFreshnessLabel(date) {
  const info = calcFreshness(date)
  return info.label
}

function goRecipeDetail() {
  if (recommendRecipe.value.id) {
    uni.navigateTo({ url: `/pages/recipe-detail/index?id=${recommendRecipe.value.id}` })
  }
}

function goFridge() {
  uni.switchTab({ url: '/pages/fridge/index' })
}

function goFridgeCategory(cat) {
  ingredientsStore.pendingCategoryFilter = cat || null
  ingredientsStore.currentZone = 'all'
  ingredientsStore.searchKeyword = ''
  uni.switchTab({ url: '/pages/fridge/index' })
}

function goProfile() {
  uni.switchTab({ url: '/pages/profile/index' })
}

onMounted(async () => {
  recommendLoading.value = true
  try {
    await Promise.all([
      ingredientsStore.fetchAll(),
      recipesStore.fetchRecommended(),
    ])
  } finally {
    recommendLoading.value = false
  }
})

onShow(() => {
  ingredientsStore.fetchAll()
})
</script>

<style lang="scss" scoped>
.page-home {
  min-height: 100vh;
  background-color: $color-bg;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));

  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $page-padding;
    padding-top: $page-padding;
  }

  &__greeting {
    flex: 1;
  }

  &__greeting-text {
    font-size: 40rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
    line-height: 1.4;
    white-space: pre-line;
  }

  &__avatar-wrap {
    width: 88rpx;
    height: 88rpx;
    border-radius: 50%;
    overflow: hidden;
    box-shadow: $card-shadow;
  }

  &__avatar {
    width: 100%;
    height: 100%;
  }

  &__section {
    padding: 0 $page-padding;
    margin-bottom: 48rpx;
  }

  &__section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
  }

  &__section-title {
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
  }

  &__section-more {
    font-size: $font-sub;
    color: $color-primary;
  }

  &__expiring-list {
    display: flex;
    flex-direction: column;
  }

  &__expiring-row {
    display: flex;
    align-items: center;
    padding: 24rpx;
    background-color: $color-bg-card;
    border-radius: $card-radius;
    box-shadow: $card-shadow;
    margin-bottom: 16rpx;

    &:last-child {
      margin-bottom: 0;
    }
  }

  &__expiring-img-wrap {
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
    background-color: $color-cream;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-right: 20rpx;
  }

  &__expiring-icon {
    font-size: 36rpx;
  }

  &__expiring-body {
    flex: 1;
    min-width: 0;
  }

  &__expiring-name {
    display: block;
    font-size: $font-body;
    font-weight: $fw-medium;
    color: $color-text-1;
    margin-bottom: 4rpx;
  }

  &__expiring-days {
    display: block;
    font-size: $font-label;
    color: $color-text-3;
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16rpx;
  }

  &__grid-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20rpx 8rpx;
    background-color: $color-bg-card;
    border-radius: $card-radius;
    box-shadow: $card-shadow;
    gap: 8rpx;

    &:active {
      transform: scale(0.95);
    }
  }

  &__grid-icon-wrap {
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__grid-icon {
    font-size: 36rpx;
  }

  &__grid-name {
    font-size: $font-label;
    color: $color-text-2;
  }

  &__grid-count {
    font-size: $font-sub;
    font-weight: $fw-semibold;
    color: $color-text-1;
  }

  &__grid-item {
    display: flex;
    align-items: center;
    gap: 20rpx;
  }

  &__grid-icon-wrap {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__grid-icon {
    font-size: 40rpx;
  }

  &__grid-info {
    flex: 1;
  }

  &__grid-name {
    display: block;
    font-size: $font-body;
    font-weight: $fw-medium;
    color: $color-text-1;
  }

  &__grid-count {
    display: block;
    font-size: $font-label;
    color: $color-text-3;
    margin-top: 4rpx;
  }
}
</style>