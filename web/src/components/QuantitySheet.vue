<template>
  <view v-if="visible" class="quantity-sheet">
    <view class="quantity-sheet__mask" @tap="onCancel" />
    <view class="quantity-sheet__panel">
      <view class="quantity-sheet__drag" />
      <view class="quantity-sheet__header">
        <text class="quantity-sheet__title">
          <text class="quantity-sheet__icon">{{ icon }}</text>
          {{ mode === 'consume' ? '消耗' : '添加' }} {{ name }}
        </text>
        <text class="quantity-sheet__close" @tap="onCancel">✕</text>
      </view>

      <view class="quantity-sheet__amount">
        <view class="quantity-sheet__stepper" @tap.stop>
          <view class="quantity-sheet__step-btn" @tap="change(-step)">－</view>
          <view class="quantity-sheet__step-display">
            <text class="quantity-sheet__step-num" :class="{ 'quantity-sheet__step-num--bump': bumping }">
              {{ amount }}
            </text>
            <text v-if="mode === 'consume'" class="quantity-sheet__step-unit">/ {{ currentQuantity }} {{ unit }}</text>
          </view>
          <view class="quantity-sheet__step-btn" @tap="change(step)">＋</view>
        </view>
        <text v-if="!isCountable" class="quantity-sheet__amount-tip">步长 {{ step }}{{ unit }}</text>
      </view>

      <view v-if="chips.length" class="quantity-sheet__chips">
        <view
          v-for="(chip, idx) in chips"
          :key="idx"
          class="quantity-sheet__chip"
          :class="{
            'quantity-sheet__chip--active': amount === chip.value,
            'quantity-sheet__chip--all': chip.all,
          }"
          @tap="pickChip(chip)"
        >
          {{ chip.label }}
        </view>
      </view>

      <view class="quantity-sheet__footer">
        <button class="quantity-sheet__btn quantity-sheet__btn--cancel" @tap="onCancel">取消</button>
        <button
          class="quantity-sheet__btn quantity-sheet__btn--confirm"
          :class="{ 'quantity-sheet__btn--all': isAll }"
          :disabled="amount <= 0"
          @tap="onConfirm"
        >
          {{ confirmLabel }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { isCountableUnit, getStepperStep, getQuickChipPresets, getAddChipPresets } from '@/utils/greetings'

const props = defineProps({
  visible: { type: Boolean, default: false },
  mode: { type: String, default: 'consume' },
    name: { type: String, default: '' },
  icon: { type: String, default: '🍴' },
  unit: { type: String, default: '个' },
  currentQuantity: { type: Number, default: 0 },
})

const emit = defineEmits(['cancel', 'confirm'])

const amount = ref(0)
const bumping = ref(false)

const isCountable = computed(() => isCountableUnit(props.unit))
const step = computed(() => getStepperStep(props.unit))

const chips = computed(() => {
  if (props.mode === 'consume') {
    const presets = getQuickChipPresets(props.currentQuantity, props.unit)
    const list = presets.map(v => ({ value: v, label: v + (isCountable.value ? '' : props.unit), all: false }))
    if (props.currentQuantity > 0) {
      list.push({ value: props.currentQuantity, label: '全部', all: true })
    }
    return list
  }
  return getAddChipPresets(props.unit).map(v => ({ value: v, label: '+' + v + (isCountable.value ? '' : props.unit), all: false }))
})

const isAll = computed(() => props.mode === 'consume' && amount.value === props.currentQuantity && props.currentQuantity > 0)

const confirmLabel = computed(() => {
  if (props.mode === 'consume') {
    if (isAll.value) return '🍳 全部消耗'
    return '确认消耗'
  }
  return '确认添加'
})

watch(() => props.visible, (v) => {
  if (v) {
    amount.value = props.mode === 'consume'
      ? Math.min(step.value, props.currentQuantity)
      : step.value
    bumping.value = false
  }
})

function change(delta) {
  let next = amount.value + delta
  if (props.mode === 'consume') {
    if (next < 0) next = 0
    if (next > props.currentQuantity) next = props.currentQuantity
  } else {
    if (next < 1) next = 1
  }
  amount.value = next
  triggerBump()
}

function pickChip(chip) {
  amount.value = chip.value
  triggerBump()
}

function triggerBump() {
  bumping.value = false
  setTimeout(() => { bumping.value = true }, 10)
  setTimeout(() => { bumping.value = false }, 350)
}

function onCancel() {
  emit('cancel')
}

function onConfirm() {
  if (amount.value <= 0) return
  emit('confirm', amount.value)
}
</script>

<style lang="scss" scoped>
.quantity-sheet {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 900;

  &__mask {
    position: absolute;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    animation: fadeIn 0.2s ease;
  }

  &__panel {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: $color-bg-card;
    border-radius: 32rpx 32rpx 0 0;
    padding: 24rpx $page-padding;
    padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
    animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  }

  &__drag {
    width: 60rpx;
    height: 8rpx;
    background-color: $color-border;
    border-radius: 4rpx;
    margin: 0 auto 24rpx;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32rpx;
  }

  &__title {
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
  }

  &__icon {
    margin-right: 8rpx;
  }

  &__close {
    width: 56rpx;
    height: 56rpx;
    line-height: 56rpx;
    text-align: center;
    color: $color-text-3;
    font-size: 32rpx;
    background-color: $color-bg;
    border-radius: 50%;
  }

  &__amount {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12rpx;
    padding: 24rpx 0;
  }

  &__stepper {
    display: flex;
    align-items: center;
    background-color: $color-bg;
    border-radius: 999rpx;
    padding: 12rpx;
    gap: 16rpx;
  }

  &__step-btn {
    width: 88rpx;
    height: 88rpx;
    line-height: 88rpx;
    text-align: center;
    background-color: $color-bg-card;
    border-radius: 50%;
    font-size: 44rpx;
    color: $color-text-1;
    font-weight: $fw-medium;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);

    &:active {
      transform: scale(0.92);
      background-color: $color-cream;
    }
  }

  &__step-display {
    min-width: 240rpx;
    text-align: center;
  }

  &__step-num {
    font-size: 80rpx;
    font-weight: $fw-semibold;
    color: $color-primary;
    line-height: 1;
    display: inline-block;
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);

    &--bump {
      animation: bump 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
  }

  &__step-unit {
    font-size: $font-sub;
    color: $color-text-3;
    margin-left: 8rpx;
  }

  &__amount-tip {
    font-size: $font-label;
    color: $color-text-3;
  }

  &__chips {
    display: flex;
    gap: 16rpx;
    padding: 16rpx 0 24rpx;
    flex-wrap: wrap;
    justify-content: center;
  }

  &__chip {
    padding: 14rpx 28rpx;
    border-radius: 999rpx;
    font-size: $font-sub;
    color: $color-text-2;
    background-color: $color-bg;
    border: 2rpx solid transparent;
    transition: all 0.2s;

    &:active {
      transform: scale(0.95);
    }

    &--active {
      background-color: $color-primary-light;
      color: $color-primary;
      border-color: $color-primary;
      font-weight: $fw-medium;
    }

    &--all {
      color: $color-danger;

      &.quantity-sheet__chip--active {
        background-color: rgba($color-danger, 0.1);
        border-color: $color-danger;
        color: $color-danger;
      }
    }
  }

  &__footer {
    display: flex;
    gap: 16rpx;
    margin-top: 16rpx;
  }

  &__btn {
    flex: 1;
    height: 96rpx;
    line-height: 96rpx;
    border-radius: 999rpx;
    font-size: $font-body;
    font-weight: $fw-medium;
    border: none;

    &--cancel {
      background-color: $color-bg;
      color: $color-text-2;
    }

    &--confirm {
      background-color: $color-primary;
      color: #FFFFFF;

      &:disabled {
        background-color: $color-border;
        color: $color-text-3;
      }
    }

    &--all {
      background-color: $color-danger;

      &:disabled {
        background-color: $color-border;
      }
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

@keyframes bump {
  0% { transform: scale(1); }
  35% { transform: scale(0.8); }
  70% { transform: scale(1.2); }
  100% { transform: scale(1); }
}
</style>
