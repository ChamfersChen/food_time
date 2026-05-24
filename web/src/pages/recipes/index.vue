<template>
  <view class="page-recipes">
    <view class="page-recipes__header">
      <text class="page-recipes__title">{{ warmMessage }}</text>
      <text class="page-recipes__subtitle">发现冰箱里的宝藏食材，让每一顿饭都充满惊喜。</text>
    </view>

    <view class="page-recipes__actions">
      <button
        class="page-recipes__random-btn"
        :class="{ 'shake': isShaking }"
        @tap="onRandomRecipe"
      >
        <text class="page-recipes__random-icon">🎲</text>
        今晚吃什么
      </button>
    </view>

    <view class="page-recipes__tags">
      <scroll-view scroll-x enable-flex class="page-recipes__tags-scroll">
        <view
          v-for="tag in RECIPE_TAGS"
          :key="tag.value"
          class="page-recipes__tag"
          :class="{ 'page-recipes__tag--active': currentTag === tag.value }"
          @tap="switchTag(tag.value)"
        >
          {{ tag.label }}
        </view>
      </scroll-view>
    </view>

    <scroll-view class="page-recipes__list" scroll-y @scrolltolower="onLoadMore">
      <view class="page-recipes__list-inner">
        <view v-if="loading && recipeList.length === 0" class="page-recipes__loading">
          <text>加载中...</text>
        </view>

        <EmptyState
          v-else-if="recipeList.length === 0"
          type="recipe"
          description="暂无匹配的菜谱"
        />

        <view v-else>
          <RecipeCard
            v-for="recipe in recipeList"
            :key="recipe.id"
            :recipe="recipe"
            :match-percent="recipe.match_percent || 0"
            @tap="goDetail"
          />
        </view>
      </view>
    </scroll-view>

    <view class="page-recipes__fab" @tap="onRandomRecipe">
      <text class="page-recipes__fab-icon">✨</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useRecipesStore } from '@/stores/recipes'

import RecipeCard from '@/components/RecipeCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const store = useRecipesStore()

const currentTag = ref('')
const isShaking = ref(false)
const loading = ref(false)

const RECIPE_TAGS = store.RECIPE_TAGS
const warmMessage = computed(() => store.warmMessage)
const recipeList = computed(() => store.filteredList)

function switchTag(tag) {
  currentTag.value = tag
  store.currentTag = tag
}

async function onRandomRecipe() {
  isShaking.value = true
  setTimeout(() => { isShaking.value = false }, 200)
  try {
    const recipe = await store.fetchRandom()
    if (recipe && recipe.id) {
      uni.navigateTo({ url: `/pages/recipe-detail/index?id=${recipe.id}` })
    }
  } catch {
    uni.showToast({ title: '随机失败，请重试', icon: 'none' })
  }
}

function goDetail(recipe) {
  if (recipe.id) {
    uni.navigateTo({ url: `/pages/recipe-detail/index?id=${recipe.id}` })
  }
}

function onLoadMore() {
  // TODO: load more recipes
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      store.fetchList(),
      store.fetchRecommended(),
    ])
  } finally {
    loading.value = false
  }
})

onShow(() => {
  store.refreshWarmMessage()
})
</script>

<style lang="scss" scoped>
.page-recipes {
  min-height: 100vh;
  background-color: $color-bg;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));

  &__header {
    padding: $page-padding;
    padding-top: calc(env(safe-area-inset-top) + 20rpx);
    margin-bottom: 16rpx;
  }

  &__title {
    display: block;
    font-size: 36rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
    margin-bottom: 8rpx;
  }

  &__subtitle {
    display: block;
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__actions {
    padding: 0 $page-padding;
    margin-bottom: 24rpx;
  }

  &__random-btn {
    width: 100%;
    height: 96rpx;
    border-radius: 20rpx;
    background: linear-gradient(135deg, $color-primary, $color-sage);
    color: #FFFFFF;
    font-size: $font-body;
    font-weight: $fw-medium;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    border: none;

    &:active {
      opacity: 0.9;
    }
  }

  &__random-icon {
    font-size: 32rpx;
  }

  &__tags {
    padding: 0 $page-padding;
    margin-bottom: 24rpx;
  }

  &__tags-scroll {
    white-space: nowrap;
  }

  &__tag {
    display: inline-flex;
    padding: 14rpx 32rpx;
    border-radius: 999rpx;
    font-size: $font-sub;
    font-weight: $fw-medium;
    color: $color-text-3;
    background-color: $color-bg-card;
    border: 2rpx solid $color-border;
    margin-right: 16rpx;
    transition: all 0.2s;

    &--active {
      background-color: $color-primary;
      color: #FFFFFF;
      border-color: $color-primary;
      box-shadow: 0 4rpx 12rpx rgba($color-primary, 0.3);
    }
  }

  &__list-inner {
    padding: 0 $page-padding;
  }

  &__loading {
    text-align: center;
    padding: 80rpx 0;
    color: $color-text-3;
    font-size: $font-sub;
  }

  &__fab {
    position: fixed;
    right: 40rpx;
    bottom: calc(170rpx + env(safe-area-inset-bottom));
    width: 96rpx;
    height: 96rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, $color-primary, $color-sage);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 20rpx rgba($color-primary, 0.4);
    z-index: 100;

    &:active {
      transform: scale(0.95);
    }
  }

  &__fab-icon {
    font-size: 40rpx;
  }
}
</style>