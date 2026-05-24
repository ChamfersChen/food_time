<template>
  <view class="recipe-row" @tap="onTap">
    <image
      class="recipe-row__image"
      :src="recipe.cover_url || '/static/icons/recipe-placeholder.png'"
      mode="aspectFill"
    />
    <view class="recipe-row__body">
      <view class="recipe-row__header">
        <text class="recipe-row__name">{{ recipe.name }}</text>
        <text v-if="hasExpiringTag" class="recipe-row__expire-tag">消耗临期</text>
      </view>
      <view class="recipe-row__meta">
        <text class="recipe-row__meta-item">⏱ {{ recipe.cook_time }}分钟</text>
        <text class="recipe-row__meta-item">{{ difficultyLabel }}</text>
        <text v-if="matchPercent > 0" class="recipe-row__match">匹配 {{ matchPercent }}%</text>
      </view>
    </view>
    <text class="recipe-row__arrow">›</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const DIFFICULTY_MAP = { easy: '简单', medium: '中等', hard: '困难' }

const props = defineProps({
  recipe: { type: Object, required: true },
  matchPercent: { type: Number, default: 0 },
})

const emit = defineEmits(['tap'])

const difficultyLabel = computed(() => DIFFICULTY_MAP[props.recipe.difficulty] || '简单')
const hasExpiringTag = computed(() => props.recipe.has_expiring_ingredient || false)

function onTap() {
  emit('tap', props.recipe)
}
</script>

<style lang="scss" scoped>
.recipe-row {
  display: flex;
  align-items: center;
  padding: 24rpx 20rpx;
  background-color: $color-bg-card;
  border-radius: 16rpx;
  margin-bottom: 16rpx;

  &__image {
    width: 120rpx;
    height: 120rpx;
    border-radius: 12rpx;
    flex-shrink: 0;
    background-color: $color-bg-section;
  }

  &__body {
    flex: 1;
    padding-left: 20rpx;
    overflow: hidden;
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
  }

  &__name {
    font-size: $font-body;
    font-weight: $fw-medium;
    color: $color-text-1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 300rpx;
  }

  &__expire-tag {
    font-size: 18rpx;
    color: #FFFFFF;
    background-color: $color-warn;
    padding: 4rpx 12rpx;
    border-radius: 6rpx;
    flex-shrink: 0;
  }

  &__meta {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-top: 8rpx;
    flex-wrap: wrap;
  }

  &__meta-item {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__match {
    font-size: $font-sub;
    color: $color-primary;
    font-weight: $fw-medium;
  }

  &__arrow {
    font-size: 36rpx;
    color: $color-text-3;
    padding-left: 12rpx;
    flex-shrink: 0;
  }
}
</style>