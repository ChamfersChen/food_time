<template>
  <view v-if="visible" class="random-modal">
    <view class="random-modal__mask" @tap="onClose" />
    <view class="random-modal__panel">
      <view class="random-modal__drag" />
      <text class="random-modal__title">🎲 随机推荐</text>

      <view v-if="recipe" class="random-modal__card">
        <image
          class="random-modal__cover"
          :src="recipe.cover_url || '/static/icons/recipe-placeholder.png'"
          mode="aspectFill"
        />
        <text class="random-modal__name">{{ recipe.name }}</text>

        <view v-if="tags.length || cookTime" class="random-modal__meta">
          <text v-for="t in tags" :key="t" class="random-modal__tag">{{ t }}</text>
          <text v-if="cookTime" class="random-modal__time">⏱ {{ cookTime }} 分钟</text>
        </view>

        <text v-if="recipe.description" class="random-modal__desc">
          {{ recipe.description }}
        </text>
      </view>

      <view v-else class="random-modal__empty">
        <text class="random-modal__empty-text">{{ loading ? '摇一摇…' : '暂无菜谱' }}</text>
      </view>

      <view class="random-modal__actions">
        <button
          class="random-modal__btn random-modal__btn--ghost"
          @tap="onReshuffle"
          :disabled="loading"
        >
          🔄 换一个
        </button>
        <button
          class="random-modal__btn random-modal__btn--primary"
          @tap="onView"
          :disabled="!recipe || loading"
        >
          去看看
        </button>
        <button
          class="random-modal__btn random-modal__btn--text"
          @tap="onClose"
        >
          算了
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  recipe: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:visible', 'reshuffle', 'view'])

const tags = computed(() => {
  if (!props.recipe?.tags) return []
  const t = props.recipe.tags
  return Array.isArray(t) ? t.filter(Boolean) : []
})

const cookTime = computed(() => {
  if (!props.recipe) return null
  return props.recipe.cook_time || props.recipe.cook_time_minutes || null
})

function onClose() {
  emit('update:visible', false)
}

function onReshuffle() {
  emit('reshuffle')
}

function onView() {
  if (!props.recipe) return
  emit('view', props.recipe)
}
</script>

<style lang="scss" scoped>
.random-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: flex-end;

  &__mask {
    position: absolute;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    animation: fadeIn 0.2s ease;
  }

  &__panel {
    position: relative;
    width: 100%;
    background-color: $color-bg-card;
    border-radius: 32rpx 32rpx 0 0;
    padding: 24rpx $page-padding 32rpx;
    padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
    z-index: 1;
    max-height: 85vh;
    overflow-y: auto;
    animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  &__drag {
    width: 60rpx;
    height: 8rpx;
    background-color: $color-border;
    border-radius: 4rpx;
    margin: 0 auto 24rpx;
  }

  &__title {
    display: block;
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
    text-align: center;
    margin-bottom: 28rpx;
  }

  &__card {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__cover {
    width: 100%;
    height: 360rpx;
    border-radius: 20rpx;
    background-color: $color-cream;
    margin-bottom: 24rpx;
  }

  &__name {
    font-size: 40rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
    text-align: center;
    margin-bottom: 16rpx;
  }

  &__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 12rpx;
    justify-content: center;
    margin-bottom: 20rpx;
  }

  &__tag {
    padding: 6rpx 20rpx;
    border-radius: 999rpx;
    background-color: $color-primary-light;
    color: $color-primary;
    font-size: $font-label;
    font-weight: $fw-medium;
  }

  &__time {
    padding: 6rpx 20rpx;
    border-radius: 999rpx;
    background-color: $color-bg-section;
    color: $color-text-2;
    font-size: $font-label;
    font-weight: $fw-medium;
  }

  &__desc {
    display: block;
    font-size: $font-sub;
    color: $color-text-2;
    line-height: 1.6;
    text-align: center;
    margin-bottom: 28rpx;
    padding: 0 16rpx;
  }

  &__empty {
    height: 360rpx;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__empty-text {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__actions {
    display: flex;
    gap: 16rpx;
    margin-top: 12rpx;
  }

  &__btn {
    flex: 1;
    height: 88rpx;
    line-height: 88rpx;
    border-radius: 999rpx;
    font-size: $font-body;
    font-weight: $fw-medium;
    border: none;
    padding: 0;

    &:active {
      opacity: 0.85;
    }

    &[disabled] {
      opacity: 0.5;
    }

    &--ghost {
      background-color: $color-bg;
      color: $color-text-1;
    }

    &--primary {
      background: linear-gradient(135deg, $color-primary, $color-sage);
      color: #FFFFFF;
      flex: 1.4;
    }

    &--text {
      background-color: transparent;
      color: $color-text-3;
      flex: 0 0 120rpx;
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
</style>
