<template>
  <view class="freshness-bar">
    <view class="freshness-bar__track">
      <view
        class="freshness-bar__fill"
        :style="{
          width: barWidth,
          backgroundColor: color,
        }"
      />
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { calcFreshness } from '@/utils/freshness'

const props = defineProps({
  expireDate: { type: [String, Date], required: true },
  width: { type: String, default: '120rpx' },
})

const info = computed(() => calcFreshness(props.expireDate))

const barWidth = computed(() => {
  const pct = Math.max(info.value.barWidth * 100, info.value.status === 'expired' ? 2 : 5)
  return `${pct}%`
})

const color = computed(() => info.value.color)
</script>

<style lang="scss" scoped>
.freshness-bar {
  width: v-bind(width);

  &__track {
    width: 100%;
    height: 8rpx;
    background-color: $color-border;
    border-radius: 4rpx;
    overflow: hidden;
  }

  &__fill {
    height: 100%;
    border-radius: 4rpx;
    transition: width 0.3s ease;
  }
}
</style>