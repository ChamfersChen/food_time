<template>
  <view class="ingredient-card card" @longpress="onLongPress" @tap="onTap">
    <view class="ingredient-card__left">
      <text class="ingredient-card__icon">{{ categoryIcon }}</text>
    </view>

    <view class="ingredient-card__center">
      <view class="ingredient-card__top">
        <text class="ingredient-card__name">{{ item.name }}</text>
        <ExpiryBadge :expire-date="item.expire_date" />
      </view>
      <text class="ingredient-card__quantity">{{ item.quantity }} {{ item.unit }}</text>
    </view>

    <view class="ingredient-card__right">
      <text class="ingredient-card__date">🛒 {{ formatDate(item.purchase_date || item.created_at) }}</text>
      <text class="ingredient-card__date-divider">|</text>
      <text class="ingredient-card__date">⌛ {{ formatDate(item.expire_date) }}</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import ExpiryBadge from './ExpiryBadge.vue'
import { useIngredientsStore } from '@/stores/ingredients'

const CATEGORY_ICONS = {
  vegetables: '🥬', meat: '🥩', seafood: '🦐', dairy: '🥛',
  fruit: '🍎', egg: '🥚', beverage: '🧃', other: '📦',
}

const props = defineProps({
  item: { type: Object, required: true },
})

const emit = defineEmits(['edit', 'consume', 'delete'])

const store = useIngredientsStore()

const categoryIcon = computed(() => CATEGORY_ICONS[props.item.category] || '📦')

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

function onTap() {
  emit('edit', props.item)
}

function onLongPress() {
  uni.showActionSheet({
    itemList: ['编辑', '标记已消耗', '删除'],
    success: (res) => {
      if (res.tapIndex === 0) {
        emit('edit', props.item)
      } else if (res.tapIndex === 1) {
        emit('consume', props.item)
      } else if (res.tapIndex === 2) {
        emit('delete', props.item)
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.ingredient-card {
  display: flex;
  align-items: center;
  padding: $card-padding;
  margin-bottom: 16rpx;
  transition: transform 0.15s ease;

  &:active {
    transform: scale(0.98);
  }

  &__left {
    width: 80rpx;
    height: 80rpx;
    border-radius: 16rpx;
    background-color: $color-cream;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-right: 20rpx;
  }

  &__icon {
    font-size: 40rpx;
  }

  &__center {
    flex: 1;
    min-width: 0;
  }

  &__top {
    display: flex;
    align-items: center;
    gap: 12rpx;
  }

  &__name {
    font-size: $font-body;
    font-weight: $fw-semibold;
    color: $color-text-1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__quantity {
    display: block;
    font-size: $font-sub;
    color: $color-text-2;
    margin-top: 4rpx;
  }

  &__right {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-left: 16rpx;
    flex-shrink: 0;
    gap: 8rpx;
  }

  &__date {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__date-divider {
    font-size: $font-label;
    color: $color-border;
  }
}
</style>