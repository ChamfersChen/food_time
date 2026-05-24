<template>
  <view
    class="expiry-badge"
    :class="`expiry-badge--${status}`"
  >
    <text class="expiry-badge__text">{{ label }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { calcFreshness } from '@/utils/freshness'

const props = defineProps({
  expireDate: { type: [String, Date], required: true },
})

const info = computed(() => calcFreshness(props.expireDate))
const status = computed(() => info.value.status)
const label = computed(() => {
  if (info.value.days < 0) return '已过期'
  if (info.value.days === 0) return '今天过期'
  if (info.value.days <= 3) return `剩${info.value.days}天`
  return ''
})
</script>

<style lang="scss" scoped>
.expiry-badge {
  display: inline-flex;
  align-items: center;
  padding: 2rpx 12rpx;
  border-radius: 999rpx;
  font-size: $font-label;
  font-weight: $fw-medium;
  letter-spacing: 0.02em;

  &--fresh {
    display: none;
  }

  &--expiring {
    background-color: rgba($color-warn, 0.15);
    color: $color-warn;
  }

  &--expired {
    background-color: rgba($color-danger, 0.15);
    color: $color-danger;
  }

  &__text {
    line-height: 1.4;
  }
}
</style>