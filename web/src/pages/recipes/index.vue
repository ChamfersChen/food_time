<template>
  <view class="page-recipes">
    <scroll-view
      class="page-recipes__scroll"
      :style="{ height: scrollHeight }"
      scroll-y
      refresher-enabled
      :refresher-triggered="refreshing"
      :refresher-threshold="80"
      refresher-default-style="none"
      refresher-background="transparent"
      @refresherrefresh="onPullRandom"
      @scrolltolower="onLoadMore"
    >
      <view slot="refresher" class="page-recipes__refresher">
        <view class="page-recipes__refresher-inner">
          <text
            class="page-recipes__dice"
            :class="{ 'page-recipes__dice--rolling': refreshing }"
          >🎲</text>
          <text class="page-recipes__refresher-text">
            {{ refreshing ? '摇一摇…' : '下拉随机一道菜' }}
          </text>
        </view>
      </view>

      <view class="page-recipes__tags">
        <scroll-view scroll-x enable-flex class="page-recipes__tags-scroll" :show-scrollbar="false">
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

        <view class="page-recipes__bottom-spacer" />
      </view>
    </scroll-view>

    <FabButton icon="＋" @tap="onTapAdd" />

    <RandomRecipeModal
      v-model:visible="randomModalVisible"
      :recipe="randomRecipe"
      :loading="refreshing"
      @reshuffle="onPullRandom"
      @view="goRandomDetail"
    />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useRecipesStore } from '@/stores/recipes'

import RecipeCard from '@/components/RecipeCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import FabButton from '@/components/FabButton.vue'
import RandomRecipeModal from '@/components/RandomRecipeModal.vue'

const store = useRecipesStore()

const currentTag = ref('')
const loading = ref(false)
const refreshing = ref(false)

const randomModalVisible = ref(false)
const randomRecipe = ref(null)

const scrollHeight = ref('100vh')

const RECIPE_TAGS = store.RECIPE_TAGS
const recipeList = computed(() => store.filteredList)

function switchTag(tag) {
  currentTag.value = tag
  store.currentTag = tag
}

function goDetail(recipe) {
  if (recipe.id) {
    uni.navigateTo({ url: `/pages/recipe-detail/index?id=${recipe.id}` })
  }
}

function goRandomDetail(recipe) {
  if (recipe?.id) {
    randomModalVisible.value = false
    uni.navigateTo({ url: `/pages/recipe-detail/index?id=${recipe.id}` })
  }
}

function onLoadMore() {
  // TODO: load more recipes
}

function onTapAdd() {
  uni.showActionSheet({
    itemList: ['自己创建菜谱', '外部导入'],
    success: (res) => {
      if (res.tapIndex === 0) {
        uni.navigateTo({ url: '/pages/recipes/add' })
      } else if (res.tapIndex === 1) {
        uni.showToast({ title: '导入功能开发中', icon: 'none' })
      }
    },
  })
}

async function onPullRandom() {
  refreshing.value = true
  try {
    const r = await store.fetchRandom()
    if (r && r.id) {
      randomRecipe.value = r
      randomModalVisible.value = true
    } else {
      uni.showToast({ title: '菜谱库空空如也', icon: 'none' })
    }
  } catch (e) {
    uni.showToast({ title: '随机失败，请重试', icon: 'none' })
  } finally {
    refreshing.value = false
  }
}

onMounted(async () => {
  try {
    const info = uni.getSystemInfoSync()
    if (info && info.windowHeight) {
      scrollHeight.value = `${info.windowHeight}px`
    }
  } catch (e) {
    // fallback to 100vh
  }
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
  // no-op: warm message moved out per redesign
})
</script>

<style lang="scss" scoped>
.page-recipes {
  min-height: 100vh;
  background-color: $color-bg;
  display: flex;
  flex-direction: column;

  &__scroll {
    flex: 1;
  }

  &__refresher {
    width: 100%;
    height: 160rpx;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__refresher-inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8rpx;
  }

  &__dice {
    font-size: 56rpx;
    line-height: 1;
    transition: transform 0.2s ease;

    &--rolling {
      animation: diceRoll 0.6s linear infinite;
    }
  }

  &__refresher-text {
    font-size: $font-label;
    color: $color-text-3;
  }

  &__tags {
    padding: 20rpx $page-padding 0;
    background-color: $color-bg;
  }

  &__tags-scroll {
    white-space: nowrap;

    &::-webkit-scrollbar {
      display: none;
    }
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
    padding: 16rpx $page-padding 0;
  }

  &__loading {
    text-align: center;
    padding: 80rpx 0;
    color: $color-text-3;
    font-size: $font-sub;
  }

  &__bottom-spacer {
    height: 200rpx;
  }
}

@keyframes diceRoll {
  0% {
    transform: rotate(0deg) scale(1);
  }
  50% {
    transform: rotate(180deg) scale(1.15);
  }
  100% {
    transform: rotate(360deg) scale(1);
  }
}
</style>
