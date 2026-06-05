<template>
  <view class="picker-mask" @tap="$emit('close')">
    <view class="picker-sheet" @tap.stop>
      <view class="picker-sheet__handle" />
      <view class="picker-sheet__header">
        <text class="picker-sheet__title">🥕 选择消耗的食材</text>
        <text class="picker-sheet__hint">长按可多选</text>
      </view>

      <view class="picker-sheet__search">
        <text class="picker-sheet__search-emoji">🔍</text>
        <input
          class="picker-sheet__search-input"
          v-model="keyword"
          placeholder="搜索食材"
          placeholder-style="color: #888780"
        />
      </view>

      <scroll-view class="picker-sheet__list" :scroll-y="true">
        <view
          v-for="group in filteredGroups"
          :key="group.zone"
          class="picker-group"
        >
          <text class="picker-group__label">{{ group.zoneLabel }}</text>
          <view class="picker-group__items">
            <view
              v-for="ing in group.items"
              :key="ing.id"
              class="pick-item"
              :class="{ 'pick-item--checked': isSelected(ing.id) }"
              @tap="toggle(ing)"
            >
              <view class="pick-item__check">
                <text v-if="isSelected(ing.id)">✓</text>
              </view>
              <text class="pick-item__emoji">{{ getCategoryEmoji(ing.category) }}</text>
              <view class="pick-item__body">
                <text class="pick-item__name">{{ ing.name }}</text>
                <text class="pick-item__qty">剩余 {{ ing.quantity }}{{ ing.unit }}</text>
              </view>
            </view>
          </view>
        </view>

        <view v-if="!filteredGroups.length" class="picker-empty">
          <text class="picker-empty__emoji">🍃</text>
          <text class="picker-empty__text">没有找到食材</text>
        </view>
      </scroll-view>

      <view class="picker-sheet__footer">
        <view class="picker-sheet__count">
          <text>已选 </text>
          <text class="picker-sheet__count-num">{{ selectedItems.length }}</text>
          <text> 项</text>
        </view>
        <view class="picker-btn picker-btn--primary" @tap="confirm">
          <text>确定 ✨</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useIngredientsStore } from '@/stores/ingredients'

const props = defineProps({
  selected: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'confirm'])

const ingStore = useIngredientsStore()
const keyword = ref('')

const ZONE_LABELS = {
  refrigeration: '🧊 冷藏',
  freezing: '❄️ 冷冻',
  room_temp: '🌡️ 常温',
}

const CATEGORY_EMOJI = {
  vegetables: '🥬',
  meat: '🥩',
  seafood: '🦐',
  dairy: '🥛',
  fruit: '🍎',
  egg: '🥚',
  beverage: '🧃',
  other: '📦',
}

const selectedItems = ref([...props.selected])

watch(() => props.selected, (v) => {
  selectedItems.value = [...v]
}, { deep: true })

const filteredGroups = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  const filtered = ingStore.notConsumed.filter(i =>
    !kw || i.name.toLowerCase().includes(kw)
  )
  const byZone = {}
  filtered.forEach(item => {
    if (!byZone[item.zone]) byZone[item.zone] = []
    byZone[item.zone].push(item)
  })
  return Object.entries(byZone).map(([zone, items]) => ({
    zone,
    zoneLabel: ZONE_LABELS[zone] || zone,
    items,
  }))
})

function isSelected(id) {
  return selectedItems.value.some(s => s.ingredient_id === id)
}

function toggle(ing) {
  const idx = selectedItems.value.findIndex(s => s.ingredient_id === ing.id)
  if (idx > -1) {
    selectedItems.value.splice(idx, 1)
  } else {
    selectedItems.value.push({
      ingredient_id: ing.id,
      name: ing.name,
      quantity: ing.quantity,
      unit: ing.unit,
    })
  }
}

function getCategoryEmoji(category) {
  return CATEGORY_EMOJI[category] || '🥗'
}

function confirm() {
  emit('confirm', selectedItems.value)
}
</script>

<style lang="scss" scoped>
.picker-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 200;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.2s ease;
}

.picker-sheet {
  width: 100%;
  max-height: 80vh;
  background: $color-bg;
  border-radius: 32rpx 32rpx 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);

  &__handle {
    width: 80rpx;
    height: 8rpx;
    border-radius: 4rpx;
    background: $color-border;
    margin: 16rpx auto 8rpx;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8rpx $page-padding 16rpx;
  }

  &__title {
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
  }

  &__hint {
    font-size: $font-label;
    color: $color-text-3;
  }

  &__search {
    margin: 0 $page-padding 16rpx;
    display: flex;
    align-items: center;
    gap: 12rpx;
    padding: 0 24rpx;
    height: 72rpx;
    background: $color-bg-card;
    border-radius: 999rpx;
  }

  &__search-emoji {
    font-size: 28rpx;
  }

  &__search-input {
    flex: 1;
    font-size: $font-body;
    color: $color-text-1;
  }

  &__list {
    flex: 1;
    padding: 0 $page-padding;
    max-height: 60vh;
  }

  &__footer {
    display: flex;
    align-items: center;
    gap: 16rpx;
    padding: 20rpx $page-padding;
    padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
    background: $color-bg-card;
    border-top: 2rpx solid $color-bg;
  }

  &__count {
    font-size: $font-sub;
    color: $color-text-2;
  }

  &__count-num {
    color: $color-primary;
    font-weight: $fw-semibold;
    font-size: $font-body;
  }
}

.picker-group {
  margin-bottom: 24rpx;

  &__label {
    display: block;
    font-size: $font-label;
    color: $color-text-3;
    margin-bottom: 12rpx;
    font-weight: $fw-medium;
  }

  &__items {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
  }
}

.pick-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 20rpx;
  background: $color-bg-card;
  border-radius: 20rpx;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  border: 2rpx solid transparent;

  &--checked {
    background: $color-primary-light;
    border-color: $color-primary;
    transform: translateX(4rpx);
  }

  &__check {
    width: 36rpx;
    height: 36rpx;
    border-radius: 50%;
    border: 2rpx solid $color-border;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 24rpx;
    font-weight: $fw-semibold;
    transition: all 0.2s;
  }

  &--checked &__check {
    background: $color-primary;
    border-color: $color-primary;
  }

  &__emoji {
    font-size: 36rpx;
  }

  &__body {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  &__name {
    font-size: $font-body;
    color: $color-text-1;
    font-weight: $fw-medium;
  }

  &__qty {
    font-size: $font-label;
    color: $color-text-3;
    margin-top: 2rpx;
  }
}

.picker-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
  gap: 12rpx;

  &__emoji {
    font-size: 80rpx;
  }

  &__text {
    font-size: $font-sub;
    color: $color-text-3;
  }
}

.picker-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-body;
  font-weight: $fw-semibold;
  transition: transform 0.2s;

  &--primary {
    background: linear-gradient(135deg, $color-primary, $color-sage);
    color: #fff;
  }

  &:active {
    transform: scale(0.97);
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
