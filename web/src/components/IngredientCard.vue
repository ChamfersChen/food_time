<template>
  <view
    class="ingredient-card-slot"
    :class="slotClass"
  >
    <view
      class="ingredient-card-slot__bg ingredient-card-slot__bg--add"
      :style="addHintStyle"
    >
      <text class="ingredient-card-slot__bg-icon">➕</text>
      <text class="ingredient-card-slot__bg-text">添加 {{ stepSize }} {{ item.unit }}</text>
    </view>
    <view
      class="ingredient-card-slot__bg ingredient-card-slot__bg--consume"
      :style="consumeHintStyle"
    >
      <text class="ingredient-card-slot__bg-icon">🍳</text>
      <text class="ingredient-card-slot__bg-text">消耗 {{ stepSize }} {{ item.unit }}</text>
    </view>

    <view
      class="ingredient-card card"
      :class="{
        'ingredient-card--just-added': justAdded,
        'ingredient-card--removing': removing,
        'ingredient-card--swiping': swiping,
      }"
      :style="cardStyle"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
      @touchcancel="onTouchEnd"
      @longpress="onLongPress"
      @tap="onTap"
    >
      <view class="ingredient-card__left">
        <text class="ingredient-card__icon">{{ icon }}</text>
        <view v-if="isLowStock" class="ingredient-card__warn">⚠️</view>
      </view>

      <view class="ingredient-card__center">
        <view class="ingredient-card__top">
          <text class="ingredient-card__name">{{ item.name }}</text>
          <ExpiryBadge :expire-date="item.expire_date" />
        </view>
        <text class="ingredient-card__quantity">{{ formatQuantity }} {{ item.unit }}</text>
      </view>

      <view class="ingredient-card__right">
        <text class="ingredient-card__date">🛒 {{ formatDate(item.purchase_date || item.created_at) }}</text>
        <text class="ingredient-card__date-divider">|</text>
        <text class="ingredient-card__date">⌛ {{ formatDate(item.expire_date) }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import ExpiryBadge from './ExpiryBadge.vue'
import { getIngredientIcon } from '@/utils/ingredientIcons'
import { getStepSize } from '@/utils/ingredientUtils'

const props = defineProps({
  item: { type: Object, required: true },
  justAdded: { type: Boolean, default: false },
  removing: { type: Boolean, default: false },
})

const emit = defineEmits(['select', 'edit', 'consume', 'delete', 'swipe-add', 'swipe-consume'])

const icon = computed(() => getIngredientIcon(props.item.name, props.item.category))

const formatQuantity = computed(() => {
  const q = Number(props.item.quantity)
  return Number.isInteger(q) ? q : Math.round(q * 100) / 100
})

const isLowStock = computed(() => {
  const countable = ['个', '根', '只', '袋', '盒', '瓶', '罐', '片', '把'].includes(props.item.unit)
  return countable && Number(props.item.quantity) <= 2
})

const stepSize = computed(() => getStepSize(props.item.unit))

const SWIPE_MAX = 280
const SWIPE_THRESHOLD = 240

const swiping = ref(false)
const swipeDir = ref(null)
const offsetX = ref(0)
const startX = ref(0)
const startY = ref(0)
const startTime = ref(0)
const activated = ref(false)
const committing = ref(false)

const slotClass = computed(() => ({
  'ingredient-card-slot--swiping': activated.value,
}))

const hintProgress = computed(() => {
  if (!activated.value) return 0
  return Math.min(1, Math.abs(offsetX.value) / SWIPE_THRESHOLD)
})

const addHintStyle = computed(() => {
  if (swipeDir.value !== 'right') return 'opacity: 0;'
  return `opacity: ${hintProgress.value};`
})

const consumeHintStyle = computed(() => {
  if (swipeDir.value !== 'left') return 'opacity: 0;'
  return `opacity: ${hintProgress.value};`
})

const cardStyle = computed(() => {
  if (props.removing) return ''
  if (offsetX.value === 0 && !committing.value) return ''
  const baseTransform = `translate3d(${offsetX.value}rpx, 0, 0)`
  if (committing.value) {
    return `transform: ${baseTransform} scale(0.95); opacity: 0.55;`
  }
  return `transform: ${baseTransform};`
})

function onTouchStart(e) {
  if (props.removing) return
  const t = e.touches?.[0]
  if (!t) return
  startX.value = t.clientX
  startY.value = t.clientY
  startTime.value = Date.now()
  swiping.value = false
  swipeDir.value = null
  offsetX.value = 0
  activated.value = false
  committing.value = false
}

function onTouchMove(e) {
  if (props.removing) return
  const t = e.touches?.[0]
  if (!t) return
  const deltaX = t.clientX - startX.value
  const deltaY = t.clientY - startY.value

  if (!activated.value) {
    if (Math.abs(deltaX) < 12 && Math.abs(deltaY) < 12) return
    if (Math.abs(deltaY) > Math.abs(deltaX) * 1.3) return
    activated.value = true
    swiping.value = true
    swipeDir.value = deltaX > 0 ? 'right' : 'left'
  }

  const resistance = 0.35
  let dx = deltaX
  if (Math.abs(dx) > SWIPE_MAX) {
    const sign = Math.sign(dx)
    dx = sign * (SWIPE_MAX + (Math.abs(dx) - SWIPE_MAX) * resistance)
  }
  offsetX.value = Math.round(dx)
}

function onTouchEnd(e) {
  if (!activated.value) {
    swiping.value = false
    return
  }
  const t = e.changedTouches?.[0]
  const finalX = t?.clientX ?? startX.value
  const deltaX = finalX - startX.value

  swiping.value = false

  if (Math.abs(deltaX) > SWIPE_THRESHOLD) {
    const dir = deltaX > 0 ? 'right' : 'left'
    committing.value = true
    setTimeout(() => {
      if (dir === 'right') {
        emit('swipe-add', props.item)
      } else {
        emit('swipe-consume', props.item)
      }
    }, 80)
    setTimeout(() => {
      offsetX.value = 0
      committing.value = false
      swipeDir.value = null
      activated.value = false
    }, 280)
  } else {
    offsetX.value = 0
    swipeDir.value = null
    activated.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

function onTap() {
  if (activated.value || committing.value) return
  emit('select', props.item)
}

function onLongPress() {
  if (activated.value || committing.value) return
  uni.showActionSheet({
    itemList: ['查看详情', '编辑信息', '消耗', '删除'],
    success: (res) => {
      if (res.tapIndex === 0) emit('select', props.item)
      else if (res.tapIndex === 1) emit('edit', props.item)
      else if (res.tapIndex === 2) emit('consume', props.item)
      else if (res.tapIndex === 3) emit('delete', props.item)
    },
  })
}
</script>

<style lang="scss" scoped>
.ingredient-card-slot {
  position: relative;
  margin-bottom: 16rpx;
  border-radius: $card-radius;
  overflow: hidden;
  box-shadow: $card-shadow;
  touch-action: pan-y;

  &__bg {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    gap: 12rpx;
    font-weight: $fw-semibold;
    color: #FFFFFF;
    opacity: 0;
    transition: opacity 0.12s linear;
    pointer-events: none;
    z-index: 0;
  }

  &__bg--add {
    background: linear-gradient(90deg, $color-primary 0%, $color-primary-light 80%, $color-bg-card 100%);
    justify-content: flex-start;
    padding-left: 48rpx;
  }

  &__bg--consume {
    background: linear-gradient(270deg, $color-warn 0%, $color-cream 80%, $color-bg-card 100%);
    justify-content: flex-end;
    padding-right: 48rpx;
    color: $color-text-1;
  }

  &__bg-icon {
    font-size: 40rpx;
  }

  &__bg-text {
    font-size: $font-sub;
  }
}

.ingredient-card {
  display: flex;
  align-items: center;
  padding: $card-padding;
  position: relative;
  z-index: 1;
  background-color: $color-bg-card;
  transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;

  &:active:not(.ingredient-card--swiping):not(.ingredient-card--removing) {
    background-color: $color-cream;
  }

  &--swiping {
    transition: none;
  }

  &--just-added {
    animation: flyIn 0.7s cubic-bezier(0.16, 1, 0.3, 1);
  }

  &--removing {
    transition: transform 0.4s ease, opacity 0.4s ease;
    transform: translateX(-100%);
    opacity: 0;
  }

  &__left {
    position: relative;
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

  &__warn {
    position: absolute;
    top: -8rpx;
    right: -8rpx;
    width: 32rpx;
    height: 32rpx;
    line-height: 32rpx;
    text-align: center;
    background-color: $color-warn;
    color: #FFFFFF;
    font-size: 20rpx;
    border-radius: 50%;
    border: 2rpx solid #FFFFFF;
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

@keyframes flyIn {
  0% {
    transform: translateY(-60rpx) scale(0.7);
    opacity: 0;
  }
  60% {
    transform: translateY(8rpx) scale(1.04);
    opacity: 1;
  }
  80% {
    transform: translateY(0) scale(0.98);
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}
</style>
