<template>
  <view class="page-detail">
    <view class="page-detail__hero">
      <image
        class="page-detail__hero-img"
        :src="recipe.cover_url || 'https://picsum.photos/800/600'"
        mode="aspectFill"
      />
      <view class="page-detail__hero-overlay" />
      <view class="page-detail__change-cover" @tap="onChangeCover">
        <text class="page-detail__change-cover-icon">📷</text>
        <text class="page-detail__change-cover-text">更换封面</text>
      </view>
      <view class="page-detail__fav" @tap="onToggleFav">
        <text class="page-detail__fav-icon" :class="{ 'page-detail__fav-icon--active': recipe.is_favorited }">
          {{ recipe.is_favorited ? '♥' : '♡' }}
        </text>
      </view>
    </view>

    <view class="page-detail__main">
      <view class="page-detail__tags">
        <text class="tag tag--primary">{{ recipe.difficulty === 'easy' ? '简单' : recipe.difficulty === 'medium' ? '中等' : '困难' }}</text>
        <text v-if="recipe.cuisine" class="tag tag--sage">{{ recipe.cuisine }}</text>
      </view>

      <text class="page-detail__name">{{ recipe.name }}</text>
      <text class="page-detail__desc">{{ recipe.description }}</text>

      <view class="page-detail__meta">
        <view class="page-detail__meta-item">
          <text class="page-detail__meta-icon">⏱</text>
          <view class="page-detail__meta-info">
            <text class="page-detail__meta-label">耗时</text>
            <text class="page-detail__meta-value">{{ recipe.cook_time || 0 }} 分钟</text>
          </view>
        </view>
        <view class="page-detail__meta-item">
          <text class="page-detail__meta-icon">📊</text>
          <view class="page-detail__meta-info">
            <text class="page-detail__meta-label">难度</text>
            <text class="page-detail__meta-value">{{ difficultyLabel }}</text>
          </view>
        </view>
        <view class="page-detail__meta-item">
          <text class="page-detail__meta-icon">🔥</text>
          <view class="page-detail__meta-info">
            <text class="page-detail__meta-label">热量</text>
            <text class="page-detail__meta-value">{{ recipe.calories || '-' }} kcal</text>
          </view>
        </view>
      </view>
    </view>

    <view class="page-detail__section card">
      <text class="page-detail__section-title">🧺 准备食材</text>
      <view
        v-for="(ing, idx) in recipe.ingredients"
        :key="idx"
        class="page-detail__ingredient"
      >
        <view class="page-detail__ingredient-info">
          <text class="page-detail__ingredient-icon" :class="ing.inFridge ? 'page-detail__ingredient-icon--yes' : 'page-detail__ingredient-icon--no'">
            {{ ing.inFridge ? '✓' : '✗' }}
          </text>
          <text class="page-detail__ingredient-name" :class="{ 'page-detail__ingredient-name--dim': !ing.inFridge }">
            {{ ing.name }}
          </text>
        </view>
        <text class="page-detail__ingredient-qty">{{ ing.quantity }} {{ ing.unit }}</text>
      </view>

      <view v-if="aiSuggestion" class="page-detail__ai-tip">
        <text class="page-detail__ai-icon">✨</text>
        <text class="page-detail__ai-text">{{ aiSuggestion }}</text>
      </view>
    </view>

    <view class="page-detail__section card">
      <text class="page-detail__section-title">👨‍🍳 烹饪步骤</text>
      <view
        v-for="(step, idx) in recipe.steps"
        :key="idx"
        class="page-detail__step"
      >
        <view class="page-detail__step-num">{{ step.step || idx + 1 }}</view>
        <view class="page-detail__step-content">
          <text class="page-detail__step-desc">{{ step.desc }}</text>
          <image
            v-if="step.image_url"
            class="page-detail__step-img"
            :src="step.image_url"
            mode="aspectFill"
          />
        </view>
      </view>
    </view>

    <view class="page-detail__bottom-spacer" />

    <view class="page-detail__footer">
      <view class="page-detail__footer-fav" @tap="onToggleFav">
        <text :class="recipe.is_favorited ? 'page-detail__fav-heart--active' : ''">
          {{ recipe.is_favorited ? '♥' : '♡' }}
        </text>
      </view>
      <button class="page-detail__footer-btn btn-primary" @tap="onStartCook">
        {{ isCooking ? '已完成 ✓' : '开始烹饪' }}
      </button>
    </view>

    <CookDoneModal
      v-if="showDoneModal"
      @close="showDoneModal = false"
      @submit="onCookDone"
    />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useRecipesStore } from '@/stores/recipes'
import { createCookingLog } from '@/api/cooking_logs'
import { upload } from '@/api/request'
import CookDoneModal from '@/components/CookDoneModal.vue'

const store = useRecipesStore()
const recipe = ref({})
const isCooking = ref(false)
const showDoneModal = ref(false)
const aiSuggestion = ref('')

const DIFFICULTY_MAP = { easy: '简单', medium: '中等', hard: '困难' }
const difficultyLabel = computed(() => DIFFICULTY_MAP[recipe.value.difficulty] || '简单')

onLoad(async (options) => {
  if (options.id) {
    try {
      const data = await store.fetchDetail(options.id)
      recipe.value = data
      uni.setNavigationBarTitle({ title: data.name || '菜谱详情' })
      if (data.ingredients) {
        const missingIngredients = data.ingredients.filter(i => !i.inFridge && i.is_essential)
        if (missingIngredients.length > 0) {
          const names = missingIngredients.map(i => i.name).join('、')
          aiSuggestion.value = `冰箱缺少 ${names}，去超市补充一下吧 🛒`
        }
      }
    } catch {
      uni.showToast({ title: '加载失败', icon: 'none' })
    }
  }
})

async function onChangeCover() {
  if (!recipe.value.id) return
  try {
    const res = await new Promise((resolve, reject) => {
      uni.chooseImage({ count: 1, success: resolve, fail: reject })
    })
    if (!res?.tempFilePaths?.[0]) return
    uni.showLoading({ title: '上传中...' })
    const tempFile = res.tempFilePaths[0]
    const result = await upload('/upload', tempFile, 'file')
    await store.editRecipe(recipe.value.id, { cover_url: result.url })
    recipe.value.cover_url = result.url
    uni.hideLoading()
    uni.showToast({ title: '封面已更换', icon: 'none' })
  } catch {
    uni.hideLoading()
    uni.showToast({ title: '更换失败', icon: 'none' })
  }
}

async function onToggleFav() {
  if (!recipe.value.id) return
  try {
    await store.toggleFav(recipe.value.id)
    recipe.value.is_favorited = !recipe.value.is_favorited
  } catch {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function onStartCook() {
  if (isCooking.value) {
    showDoneModal.value = true
  } else {
    isCooking.value = true
    uni.showToast({ title: '开始烹饪，加油 💪', icon: 'none' })
  }
}

async function onCookDone(data) {
  try {
    await createCookingLog({
      recipe_id: recipe.value.id,
      recipe_name: recipe.value.name,
      rating: data.rating,
      mood: data.mood,
      note: data.note,
      photo_urls: data.photo_urls || [],
      consumed_ingredients: recipe.value.ingredients
        ?.filter(i => i.inFridge)
        .map(i => ({
          ingredient_id: i.ingredient_id || '',
          name: i.name,
          quantity_used: i.quantity,
          unit: i.unit,
        })) || [],
    })
    showDoneModal.value = false
    uni.showToast({ title: '烹饪记录已保存 🎉', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 1500)
  } catch {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
.page-detail {
  min-height: 100vh;
  background-color: $color-bg;
  padding-bottom: calc(160rpx + env(safe-area-inset-bottom));

  &__hero {
    position: relative;
    width: 100%;
    height: 480rpx;
  }

  &__hero-img {
    width: 100%;
    height: 100%;
  }

  &__hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 200rpx;
    background: linear-gradient(to bottom, rgba(0,0,0,0.3), transparent);
  }

  &__change-cover {
    position: absolute;
    bottom: 24rpx;
    right: 32rpx;
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 12rpx 24rpx;
    border-radius: 32rpx;
    background-color: rgba(0,0,0,0.45);
    z-index: 10;

    &-icon {
      font-size: 28rpx;
    }

    &-text {
      font-size: 24rpx;
      color: #fff;
    }
  }

  &__fav {
    position: absolute;
    top: calc(env(safe-area-inset-top) + 20rpx);
    right: 32rpx;
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
    background-color: rgba(255,255,255,0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
  }

  &__fav-icon {
    font-size: 32rpx;
    color: $color-text-3;

    &--active {
      color: $color-danger;
    }
  }

  &__main {
    margin-top: -48rpx;
    background-color: $color-bg-card;
    border-radius: 32rpx 32rpx 0 0;
    padding: 40rpx $page-padding;
    position: relative;
    z-index: 5;
  }

  &__tags {
    display: flex;
    gap: 12rpx;
    margin-bottom: 16rpx;
  }

  &__name {
    display: block;
    font-size: 44rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
    line-height: 1.3;
    margin-bottom: 12rpx;
  }

  &__desc {
    display: block;
    font-size: $font-body;
    color: $color-text-2;
    line-height: 1.6;
    margin-bottom: 32rpx;
  }

  &__meta {
    display: flex;
    justify-content: space-around;
    padding: 28rpx 0;
    border-top: 1rpx solid $color-border;
  }

  &__meta-item {
    display: flex;
    align-items: center;
    gap: 12rpx;
  }

  &__meta-icon {
    font-size: 32rpx;
  }

  &__meta-info {
    display: flex;
    flex-direction: column;
  }

  &__meta-label {
    font-size: $font-label;
    color: $color-text-3;
  }

  &__meta-value {
    font-size: $font-body;
    font-weight: $fw-medium;
    color: $color-text-1;
  }

  &__section {
    margin: 24rpx $page-padding;
  }

  &__section-title {
    display: block;
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
    margin-bottom: 24rpx;
  }

  &__ingredient {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid rgba($color-border, 0.5);
  }

  &__ingredient-info {
    display: flex;
    align-items: center;
    gap: 12rpx;
  }

  &__ingredient-icon {
    font-size: $font-sub;
    font-weight: $fw-semibold;

    &--yes {
      color: $color-primary;
    }

    &--no {
      color: $color-text-3;
    }
  }

  &__ingredient-name {
    font-size: $font-body;
    color: $color-text-1;

    &--dim {
      color: $color-text-3;
    }
  }

  &__ingredient-qty {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__ai-tip {
    display: flex;
    align-items: flex-start;
    gap: 12rpx;
    margin-top: 20rpx;
    padding: 20rpx;
    background-color: rgba($color-primary, 0.08);
    border-radius: 16rpx;
    border: 1rpx solid rgba($color-primary, 0.15);
  }

  &__ai-icon {
    font-size: $font-body;
  }

  &__ai-text {
    flex: 1;
    font-size: $font-sub;
    color: $color-text-2;
    line-height: 1.5;
  }

  &__step {
    display: flex;
    gap: 20rpx;
    margin-bottom: 32rpx;
  }

  &__step-num {
    width: 48rpx;
    height: 48rpx;
    border-radius: 50%;
    background-color: $color-bg-section;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: $font-sub;
    font-weight: $fw-medium;
    color: $color-text-2;
    flex-shrink: 0;
  }

  &__step-content {
    flex: 1;
  }

  &__step-desc {
    display: block;
    font-size: $font-body;
    color: $color-text-1;
    line-height: 1.7;
    margin-bottom: 16rpx;
  }

  &__step-img {
    width: 100%;
    height: 240rpx;
    border-radius: 16rpx;
  }

  &__bottom-spacer {
    height: 40rpx;
  }

  &__footer {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    gap: 20rpx;
    padding: 20rpx $page-padding;
    padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
    background-color: rgba($color-bg, 0.9);
    backdrop-filter: blur(10px);
    border-top: 1rpx solid rgba($color-border, 0.5);
    z-index: 100;
  }

  &__footer-fav {
    width: 96rpx;
    height: 96rpx;
    border-radius: 50%;
    border: 2rpx solid $color-border;
    background-color: $color-bg-card;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40rpx;
    color: $color-text-3;
    flex-shrink: 0;

    &:active {
      background-color: $color-bg-section;
    }
  }

  &__fav-heart--active {
    color: $color-danger !important;
  }

  &__footer-btn {
    flex: 1;
    height: 96rpx;
    line-height: 96rpx;
    border-radius: 999rpx;
  }
}
</style>