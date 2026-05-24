<template>
  <view class="recommend card" :class="{ 'breathe': !loading }" @tap="$emit('tap', recipe)">
    <view v-if="loading" class="recommend__skeleton">
      <view class="recommend__skeleton-img skeleton-bg" />
      <view class="recommend__skeleton-content">
        <view class="recommend__skeleton-title skeleton-bg" />
        <view class="recommend__skeleton-text skeleton-bg" />
      </view>
    </view>

    <view v-else class="recommend__inner">
      <image
        class="recommend__image"
        :src="recipe.cover_url || 'https://picsum.photos/800/400'"
        mode="aspectFill"
      />
      <view class="recommend__overlay">
        <view class="recommend__tags">
          <text class="recommend__tag tag tag--primary">
            {{ recipe.cook_time || 15 }} 分钟
          </text>
          <text class="recommend__tag tag tag--sage">
            匹配 {{ matchCount }} 种库存
          </text>
        </view>
      </view>

      <view class="recommend__content">
        <view class="recommend__info">
          <text class="recommend__name">{{ recipe.name || '今日推荐菜谱' }}</text>
          <text class="recommend__desc">{{ recipe.description || '发现冰箱里的宝藏食材，让每一顿饭都充满惊喜' }}</text>
        </view>
        <view class="recommend__btn">
          <text class="recommend__btn-icon">▶</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
defineProps({
  recipe: { type: Object, default: () => ({}) },
  matchCount: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },
})

defineEmits(['tap'])
</script>

<style lang="scss" scoped>
.recommend {
  overflow: hidden;
  margin-bottom: 32rpx;

  &__skeleton {
    padding: 0;
  }

  &__skeleton-img {
    width: 100%;
    height: 320rpx;
    border-radius: $card-radius $card-radius 0 0;
  }

  &__skeleton-content {
    padding: 24rpx;
  }

  &__skeleton-title {
    width: 60%;
    height: 36rpx;
    border-radius: 8rpx;
    margin-bottom: 16rpx;
  }

  &__skeleton-text {
    width: 90%;
    height: 24rpx;
    border-radius: 8rpx;
  }

  &__inner {
    position: relative;
  }

  &__image {
    width: 100%;
    height: 320rpx;
    display: block;
  }

  &__overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 320rpx;
    background: linear-gradient(to top, rgba(0,0,0,0.4), transparent);
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    padding: 20rpx;
  }

  &__tags {
    display: flex;
    gap: 12rpx;
  }

  &__tag {
    background-color: rgba(#FAF9F6, 0.9);
    backdrop-filter: blur(8rpx);
  }

  &__content {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 24rpx;
  }

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__name {
    display: block;
    font-size: 36rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
    margin-bottom: 8rpx;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__desc {
    display: block;
    font-size: $font-sub;
    color: $color-text-3;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__btn {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, $color-primary, $color-sage);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-left: 20rpx;
    box-shadow: inset 0 2rpx 0 rgba(255,255,255,0.2), inset 0 -2rpx 0 rgba(0,0,0,0.1);

    &:active {
      opacity: 0.9;
      transform: scale(0.95);
    }
  }

  &__btn-icon {
    color: #FFFFFF;
    font-size: 28rpx;
  }
}

.skeleton-bg {
  background-color: $color-border;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>