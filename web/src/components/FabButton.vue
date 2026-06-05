<template>
  <view
    class="fab-btn"
    :class="{ 'fab-btn--dragging': isDragging, 'fab-btn--longpress': isLongPressing }"
    :style="fabStyle"
    @touchstart="onTouchStart"
    @touchmove.stop.prevent="onTouchMove"
    @touchend="onTouchEnd"
    @touchcancel="onTouchEnd"
    @tap="onClick"
  >
    <text class="fab-btn__icon">{{ icon }}</text>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  icon: { type: String, default: '＋' },
  longPressDuration: { type: Number, default: 600 },
})

const emit = defineEmits(['tap', 'longpress'])

const margin = 10
const fabRight = margin

let fabSize = 48
let maxTop = 0
let maxBottom = 0

function getScreenInfo() {
  const info = uni.getSystemInfoSync()
  const windowHeight = info.windowHeight
  const windowWidth = info.windowWidth
  const safeBottom = info.safeAreaInsets ? info.safeAreaInsets.bottom : 0
  const safeTop = info.safeAreaInsets ? info.safeAreaInsets.top : (info.statusBarHeight || 0)

  fabSize = Math.round(windowWidth / 750 * 96)

  const tabBarHeight = 50
  maxTop = safeTop + margin
  maxBottom = windowHeight - tabBarHeight - safeBottom - margin - fabSize

  return { windowHeight }
}

function getInitialTop() {
  getScreenInfo()
  return maxBottom
}

const topPos = ref(getInitialTop())
const isDragging = ref(false)
const isMoved = ref(false)
const isLongPressing = ref(false)

let startY = 0
let startTop = 0
let longPressTimer = null

const fabStyle = computed(() => ({
  top: topPos.value + 'px',
  right: fabRight + 'px',
}))

function clampPos(val) {
  if (val < maxTop) return maxTop
  if (val > maxBottom) return maxBottom
  return val
}

function onTouchStart(e) {
  isMoved.value = false
  startY = e.touches[0].clientY
  startTop = topPos.value
  getScreenInfo()
  if (longPressTimer) clearTimeout(longPressTimer)
  if (props.longPressDuration > 0) {
    isLongPressing.value = true
    longPressTimer = setTimeout(() => {
      longPressTimer = null
      if (isLongPressing.value && !isMoved.value) {
        isLongPressing.value = false
        isMoved.value = true
        uni.vibrateShort && uni.vibrateShort({ type: 'medium' })
        emit('longpress')
      }
    }, props.longPressDuration)
  }
}

function onTouchMove(e) {
  const dy = e.touches[0].clientY - startY
  if (Math.abs(dy) > 4) {
    isDragging.value = true
    isMoved.value = true
    isLongPressing.value = false
    if (longPressTimer) {
      clearTimeout(longPressTimer)
      longPressTimer = null
    }
  }
  topPos.value = clampPos(startTop + dy)
}

function onTouchEnd() {
  isDragging.value = false
  isLongPressing.value = false
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
}

function onClick() {
  if (!isMoved.value) {
    emit('tap')
  }
}
</script>

<style lang="scss" scoped>
.fab-btn {
  position: fixed;
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, $color-primary, $color-sage);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba($color-primary, 0.3);
  z-index: 100;
  transition: box-shadow 0.2s, transform 0.1s;

  &--dragging {
    transform: scale(1.08);
    box-shadow: 0 12rpx 36rpx rgba($color-primary, 0.4);
  }

  &--longpress {
    transform: scale(0.92);
    box-shadow: 0 4rpx 12rpx rgba($color-primary, 0.3);
  }
}

.fab-btn__icon {
  color: #FFFFFF;
  font-size: 44rpx;
  font-weight: $fw-medium;
}
</style>

