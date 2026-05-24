<template>
  <view class="empty-state">
    <image
      v-if="image"
      class="empty-state__image"
      :src="image"
      mode="aspectFit"
    />
    <view v-else class="empty-state__icon-wrap">
      <text class="empty-state__icon">{{ defaultIcon }}</text>
    </view>
    <text class="empty-state__title">{{ title }}</text>
    <text v-if="description" class="empty-state__desc">{{ description }}</text>
    <button
      v-if="buttonText"
      class="empty-state__btn btn-primary"
      @tap="$emit('action')"
    >
      {{ buttonText }}
    </button>
  </view>
</template>

<script setup>
const TYPES = {
  fridge: { icon: '🧊', title: '冰箱空空如也' },
  recipe: { icon: '🍳', title: '暂无推荐菜谱' },
  log: { icon: '📖', title: '还没有烹饪记录' },
  search: { icon: '🔍', title: '未找到结果' },
  network: { icon: '📡', title: '网络似乎有点问题' },
}

const props = defineProps({
  type: { type: String, default: 'fridge' },
  image: { type: String, default: '' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  buttonText: { type: String, default: '' },
})

defineEmits(['action'])

const defaultIcon = TYPES[props.type]?.icon || '📭'
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx $page-padding;

  &__icon-wrap {
    width: 160rpx;
    height: 160rpx;
    border-radius: 50%;
    background-color: $color-cream;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 32rpx;
  }

  &__icon {
    font-size: 72rpx;
  }

  &__image {
    width: 320rpx;
    height: 320rpx;
    margin-bottom: 32rpx;
  }

  &__title {
    font-size: $font-title;
    font-weight: $fw-medium;
    color: $color-text-2;
    text-align: center;
    margin-bottom: 12rpx;
  }

  &__desc {
    font-size: $font-sub;
    color: $color-text-3;
    text-align: center;
    margin-bottom: 40rpx;
    line-height: 1.6;
  }

  &__btn {
    width: 320rpx;
    height: 80rpx;
    line-height: 80rpx;
    font-size: $font-body;
  }
}
</style>