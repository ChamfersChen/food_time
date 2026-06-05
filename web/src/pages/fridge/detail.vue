<template>
  <view class="page-detail">
    <view v-if="loading" class="page-detail__loading">
      <text>加载中...</text>
    </view>

    <view v-else-if="!item" class="page-detail__missing">
      <text>食材不存在或已被删除</text>
    </view>

    <view v-else>
      <view
        ref="heroCard"
        class="page-detail__hero"
        :class="{
          'page-detail__hero--bounce': bouncing,
        }"
      >
        <view class="page-detail__icon-wrap">
          <text class="page-detail__icon">{{ icon }}</text>
          <view v-if="isLowStock" class="page-detail__warn-badge">⚠️</view>
        </view>
        <text class="page-detail__name">{{ item.name }}</text>
        <text class="page-detail__qty">{{ item.quantity }} {{ item.unit }}</text>
        <view v-if="freshnessInfo" class="page-detail__status" :class="`page-detail__status--${freshnessInfo.status}`">
          {{ freshnessLabel }}
        </view>
      </view>

      <view class="page-detail__info card">
        <view class="page-detail__info-row">
          <text class="page-detail__info-label">数量</text>
          <text class="page-detail__info-value">{{ item.quantity }} {{ item.unit }}</text>
        </view>
        <view class="page-detail__info-row">
          <text class="page-detail__info-label">区域</text>
          <text class="page-detail__info-value">{{ zoneLabel }}</text>
        </view>
        <view class="page-detail__info-row">
          <text class="page-detail__info-label">入库</text>
          <text class="page-detail__info-value">{{ formatDate(item.purchase_date || item.created_at) }}</text>
        </view>
        <view class="page-detail__info-row">
          <text class="page-detail__info-label">过期</text>
          <text class="page-detail__info-value">
            {{ formatDate(item.expire_date) }}
            <text v-if="freshnessInfo && freshnessInfo.days >= 0" class="page-detail__info-days">剩 {{ freshnessInfo.days }} 天</text>
            <text v-else-if="freshnessInfo && freshnessInfo.days < 0" class="page-detail__info-days page-detail__info-days--over">已过期 {{ -freshnessInfo.days }} 天</text>
          </text>
        </view>
        <view v-if="item.note" class="page-detail__info-row">
          <text class="page-detail__info-label">备注</text>
          <text class="page-detail__info-value">{{ item.note }}</text>
        </view>
      </view>
    </view>

    <view v-if="item" class="page-detail__actions">
      <view class="page-detail__action" @tap="openConsume">
        <text class="page-detail__action-icon">🍳</text>
        <text class="page-detail__action-label">消耗</text>
      </view>
      <view class="page-detail__action" @tap="openAdd">
        <text class="page-detail__action-icon">➕</text>
        <text class="page-detail__action-label">添加</text>
      </view>
      <view class="page-detail__action" @tap="openZone">
        <text class="page-detail__action-icon">🗄️</text>
        <text class="page-detail__action-label">区域</text>
      </view>
      <view class="page-detail__action" @tap="openDate">
        <text class="page-detail__action-icon">📅</text>
        <text class="page-detail__action-label">日期</text>
      </view>
      <view class="page-detail__action page-detail__action--more" @tap="openMore">
        <text class="page-detail__action-icon">⋯</text>
        <text class="page-detail__action-label">更多</text>
      </view>
    </view>

    <QuantitySheet
      :visible="sheetVisible"
      :mode="sheetMode"
      :name="item ? item.name : ''"
      :icon="icon"
      :unit="item ? item.unit : '个'"
      :current-quantity="item ? Number(item.quantity) : 0"
      @cancel="closeSheet"
      @confirm="onSheetConfirm"
    />

    <view v-if="zoneSheetVisible" class="zone-sheet">
      <view class="zone-sheet__mask" @tap="zoneSheetVisible = false" />
      <view class="zone-sheet__panel">
        <view class="zone-sheet__drag" />
        <text class="zone-sheet__title">修改区域</text>
        <view class="zone-sheet__list">
          <view
            v-for="z in ZONES"
            :key="z.value"
            class="zone-sheet__item"
            :class="{ 'zone-sheet__item--active': item && item.zone === z.value }"
            @tap="changeZone(z.value)"
          >
            <text class="zone-sheet__item-icon">{{ z.icon }}</text>
            <text class="zone-sheet__item-label">{{ z.label }}</text>
            <text v-if="item && item.zone === z.value" class="zone-sheet__item-check">✓</text>
          </view>
        </view>
      </view>
    </view>

    <view v-if="dateSheetVisible" class="date-sheet">
      <view class="date-sheet__mask" @tap="closeDateSheet" />
      <view class="date-sheet__panel">
        <view class="date-sheet__drag" />
        <text class="date-sheet__title">修改过期日期</text>

        <view class="date-sheet__current">
          <text class="date-sheet__current-label">当前</text>
          <text class="date-sheet__current-date">{{ formatDate(datePickerValue) }}</text>
        </view>

        <picker
          mode="date"
          :value="datePickerValue"
          :start="datePickerStart"
          :end="datePickerEnd"
          @change="onDatePicked"
        >
          <view class="date-sheet__trigger">
            <text class="date-sheet__trigger-icon">📅</text>
            <view class="date-sheet__trigger-body">
              <text class="date-sheet__trigger-label">新过期日期</text>
              <text class="date-sheet__trigger-value">{{ formatDate(previewDate) }}</text>
            </view>
            <text class="date-sheet__trigger-arrow">›</text>
          </view>
        </picker>

        <view class="date-sheet__footer">
          <button class="date-sheet__btn date-sheet__btn--cancel" @tap="closeDateSheet">取消</button>
        </view>
      </view>
    </view>

    <view v-if="undoVisible" class="undo-snackbar">
      <text class="undo-snackbar__text">已消耗 {{ undoMessage }}</text>
      <view class="undo-snackbar__btn" @tap="onUndo">
        <text class="undo-snackbar__btn-text">撤销 ({{ undoCountdown }}s)</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { useIngredientsStore } from '@/stores/ingredients'
import { getIngredientIcon } from '@/utils/ingredientIcons'
import { calcFreshness } from '@/utils/freshness'
import { getConsumeSuccessText, getAddSuccessText, getZoneChangeText } from '@/utils/greetings'

import QuantitySheet from '@/components/QuantitySheet.vue'

const store = useIngredientsStore()
const ZONES = [
  { value: 'refrigeration', label: '冷藏', icon: '❄️' },
  { value: 'freezing', label: '冷冻', icon: '🧊' },
  { value: 'room_temp', label: '常温', icon: '🌡️' },
]

const item = ref(null)
const loading = ref(true)
const bouncing = ref(false)

const sheetVisible = ref(false)
const sheetMode = ref('consume')
const zoneSheetVisible = ref(false)
const dateSheetVisible = ref(false)
const datePickerValue = ref('')
const previewDate = ref('')

const undoVisible = ref(false)
const undoCountdown = ref(3)
const undoSnapshot = ref(null)
const undoMessage = ref('')
let undoTimer = null
let undoCountdownTimer = null

const heroCard = ref(null)

const today = new Date()
const currentYear = today.getFullYear()
const datePickerStart = `${currentYear - 5}-01-01`
const datePickerEnd = `${currentYear + 5}-12-31`

const icon = computed(() => item.value ? getIngredientIcon(item.value.name, item.value.category) : '📦')

const freshnessInfo = computed(() => item.value ? calcFreshness(item.value.expire_date) : null)

const freshnessLabel = computed(() => {
  if (!freshnessInfo.value) return ''
  if (freshnessInfo.value.days < 0) return '已过期'
  if (freshnessInfo.value.days === 0) return '今天过期'
  if (freshnessInfo.value.days <= 3) return `剩 ${freshnessInfo.value.days} 天`
  return '新鲜'
})

const isLowStock = computed(() => {
  if (!item.value) return false
  const countable = ['个', '根', '只', '袋', '盒', '瓶', '罐', '片', '把'].includes(item.value.unit)
  return countable && Number(item.value.quantity) <= 2
})

const zoneLabel = computed(() => {
  if (!item.value) return ''
  return ZONES.find(z => z.value === item.value.zone)?.label || item.value.zone
})

onLoad((options) => {
  if (options.id) {
    loadItem(options.id)
  } else {
    loading.value = false
  }
})

onUnload(() => {
  clearUndoTimers()
})

async function loadItem(id) {
  loading.value = true
  try {
    const data = await store.fetchOne(id)
    item.value = data
    const exp = data.expire_date ? data.expire_date.split('T')[0] : ''
    datePickerValue.value = exp
    previewDate.value = exp
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

function openConsume() {
  sheetMode.value = 'consume'
  sheetVisible.value = true
}

function openAdd() {
  sheetMode.value = 'add'
  sheetVisible.value = true
}

function openZone() {
  zoneSheetVisible.value = true
}

function openDate() {
  previewDate.value = datePickerValue.value
  dateSheetVisible.value = true
}

function closeDateSheet() {
  dateSheetVisible.value = false
}

function onDatePicked(e) {
  const newDate = e.detail.value
  previewDate.value = newDate
  applyDateChange(newDate)
}

async function applyDateChange(newDate) {
  if (!item.value) return
  try {
    await store.editOne(item.value.id, { expire_date: newDate })
    const fresh = store.list.find(i => i.id === item.value.id)
    if (fresh) item.value = fresh
    datePickerValue.value = newDate
    dateSheetVisible.value = false
    uni.showToast({ title: '保质期已更新 ✨', icon: 'none' })
  } catch (e) {
    uni.showToast({ title: '更新失败', icon: 'none' })
  }
}

function openMore() {
  uni.showActionSheet({
    itemList: ['编辑完整信息', '删除食材'],
    success: (res) => {
      if (res.tapIndex === 0) {
        uni.navigateTo({ url: `/pages/fridge/add?id=${item.value.id}` })
      } else if (res.tapIndex === 1) {
        confirmDelete()
      }
    },
  })
}

function closeSheet() {
  sheetVisible.value = false
}

async function onSheetConfirm(n) {
  sheetVisible.value = false
  await new Promise(r => setTimeout(r, 220))
  if (sheetMode.value === 'consume') {
    await performConsume(n)
  } else {
    await performAdd(n)
  }
}

async function performConsume(n) {
  if (!item.value) return
  try {
    const snapshot = await store.consumeWithQuantity(item.value.id, n)
    if (!snapshot) return
    const fresh = store.list.find(i => i.id === item.value.id)
    if (fresh) item.value = fresh
    bouncing.value = true
    setTimeout(() => { bouncing.value = false }, 800)
    const txt = getConsumeSuccessText(item.value.name, n, item.value.unit)
    uni.showToast({ title: `${txt.main} · ${txt.sub}`, icon: 'none' })
    showUndo(snapshot, n)
    setTimeout(() => { uni.navigateBack() }, 1800)
  } catch (e) {
    uni.showToast({ title: '消耗失败', icon: 'none' })
  }
}

async function performAdd(n) {
  if (!item.value) return
  try {
    await store.addWithQuantity(item.value.id, n)
    const fresh = store.list.find(i => i.id === item.value.id)
    if (fresh) item.value = fresh
    bouncing.value = true
    setTimeout(() => { bouncing.value = false }, 800)
    const txt = getAddSuccessText(item.value.name, n, item.value.unit)
    uni.showToast({ title: txt, icon: 'none' })
  } catch (e) {
    uni.showToast({ title: '添加失败', icon: 'none' })
  }
}

async function changeZone(zone) {
  if (!item.value || item.value.zone === zone) {
    zoneSheetVisible.value = false
    return
  }
  const oldZone = item.value.zone
  pickedZoneSnapshot = { id: item.value.id, oldZone }
  try {
    await store.editOne(item.value.id, { zone })
    const fresh = store.list.find(i => i.id === item.value.id)
    if (fresh) item.value = fresh
    zoneSheetVisible.value = false
    uni.showToast({ title: getZoneChangeText(zone), icon: 'none' })
  } catch (e) {
    uni.showToast({ title: '更新失败', icon: 'none' })
  }
}

function confirmDelete() {
  uni.showModal({
    title: '确认删除',
    content: `确认删除「${item.value.name}」？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await store.removeOne(item.value.id)
          uni.showToast({ title: '已删除', icon: 'success' })
          setTimeout(() => uni.navigateBack(), 400)
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    },
  })
}

function showUndo(snapshot, n) {
  undoSnapshot.value = snapshot
  undoMessage.value = `${n} ${item.value.unit}`
  undoVisible.value = true
  undoCountdown.value = 3
  clearUndoTimers()
  undoCountdownTimer = setInterval(() => {
    undoCountdown.value -= 1
    if (undoCountdown.value <= 0) {
      clearInterval(undoCountdownTimer)
      undoCountdownTimer = null
    }
  }, 1000)
  undoTimer = setTimeout(() => {
    undoVisible.value = false
    undoSnapshot.value = null
    clearUndoTimers()
  }, 3000)
}

function clearUndoTimers() {
  if (undoTimer) { clearTimeout(undoTimer); undoTimer = null }
  if (undoCountdownTimer) { clearInterval(undoCountdownTimer); undoCountdownTimer = null }
}

async function onUndo() {
  if (!undoSnapshot.value) return
  const snap = undoSnapshot.value
  clearUndoTimers()
  undoVisible.value = false
  undoSnapshot.value = null
  try {
    await store.restoreConsumed(snap)
    const fresh = store.list.find(i => i.id === item.value.id)
    if (fresh) item.value = fresh
    uni.showToast({ title: '已撤销', icon: 'none' })
  } catch (e) {
    uni.showToast({ title: '撤销失败', icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
.page-detail {
  min-height: 100vh;
  background-color: $color-bg;
  padding: $page-padding;
  padding-bottom: calc(220rpx + env(safe-area-inset-bottom));

  &__loading, &__missing {
    text-align: center;
    padding: 200rpx 0;
    color: $color-text-3;
    font-size: $font-sub;
  }

  &__hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 60rpx $page-padding 48rpx;
    background: linear-gradient(180deg, $color-bg-card 0%, $color-cream 100%);
    border-radius: $card-radius;
    box-shadow: $card-shadow;
    margin-bottom: 24rpx;
    transition: transform 0.2s ease;

    &--bounce {
      animation: cardBounce 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }
  }

  &__icon-wrap {
    position: relative;
    width: 180rpx;
    height: 180rpx;
    border-radius: 50%;
    background-color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24rpx;
    box-shadow: 0 6rpx 16rpx rgba(0, 0, 0, 0.06);
  }

  &__icon {
    font-size: 96rpx;
  }

  &__warn-badge {
    position: absolute;
    top: -4rpx;
    right: -4rpx;
    width: 48rpx;
    height: 48rpx;
    line-height: 48rpx;
    text-align: center;
    background-color: $color-warn;
    color: #FFFFFF;
    font-size: 28rpx;
    border-radius: 50%;
    border: 4rpx solid #FFFFFF;
  }

  &__name {
    font-size: 44rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
    margin-bottom: 12rpx;
  }

  &__qty {
    font-size: $font-body;
    color: $color-text-2;
  }

  &__status {
    margin-top: 16rpx;
    padding: 8rpx 24rpx;
    border-radius: 999rpx;
    font-size: $font-label;
    font-weight: $fw-medium;

    &--fresh {
      background-color: $color-primary-light;
      color: $color-primary;
    }

    &--expiring {
      background-color: rgba($color-warn, 0.15);
      color: $color-warn;
    }

    &--expired {
      background-color: rgba($color-danger, 0.15);
      color: $color-danger;
    }
  }

  &__info {
    padding: 8rpx $card-padding;

    &-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 24rpx 0;
      border-bottom: 2rpx solid $color-border;

      &:last-child {
        border-bottom: none;
      }
    }

    &-label {
      font-size: $font-sub;
      color: $color-text-3;
    }

    &-value {
      font-size: $font-sub;
      color: $color-text-1;
      font-weight: $fw-medium;
    }

    &-days {
      margin-left: 12rpx;
      font-size: $font-label;
      color: $color-warn;

      &--over {
        color: $color-danger;
      }
    }
  }

  &__actions {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 100;
    display: flex;
    gap: 12rpx;
    padding: 16rpx $page-padding;
    padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
    background-color: $color-bg;
    border-top: 2rpx solid $color-border;
  }

  &__action {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4rpx;
    padding: 16rpx 0;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
    transition: all 0.2s;

    &:active {
      transform: scale(0.92);
      background-color: $color-cream;
    }

    &--more {
      flex: 0 0 100rpx;
    }
  }

  &__action-icon {
    font-size: 36rpx;
    line-height: 1;
  }

  &__action-label {
    font-size: $font-label;
    color: $color-text-2;
  }
}

.zone-sheet {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 900;

  &__mask {
    position: absolute;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    animation: fadeIn 0.2s ease;
  }

  &__panel {
    position: absolute;
    left: 0; right: 0; bottom: 0;
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

  &__title {
    display: block;
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
    text-align: center;
    margin-bottom: 24rpx;
  }

  &__list {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
  }

  &__item {
    display: flex;
    align-items: center;
    gap: 16rpx;
    padding: 24rpx;
    background-color: $color-bg;
    border-radius: 16rpx;
    border: 2rpx solid transparent;
    transition: all 0.2s;

    &:active {
      transform: scale(0.98);
    }

    &--active {
      border-color: $color-primary;
      background-color: $color-primary-light;
    }
  }

  &__item-icon {
    font-size: 36rpx;
  }

  &__item-label {
    flex: 1;
    font-size: $font-body;
    color: $color-text-1;
  }

  &__item-check {
    font-size: 32rpx;
    color: $color-primary;
    font-weight: $fw-semibold;
  }
}

.date-sheet {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 900;

  &__mask {
    position: absolute;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    animation: fadeIn 0.2s ease;
  }

  &__panel {
    position: absolute;
    left: 0; right: 0; bottom: 0;
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

  &__title {
    display: block;
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
    text-align: center;
    margin-bottom: 24rpx;
  }

  &__current {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    padding: 16rpx 0 24rpx;
  }

  &__current-label {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__current-date {
    font-size: $font-body;
    color: $color-primary;
    font-weight: $fw-semibold;
  }

  &__trigger {
    display: flex;
    align-items: center;
    gap: 16rpx;
    padding: 24rpx;
    background-color: $color-bg;
    border-radius: 16rpx;
    border: 2rpx solid $color-border;

    &:active {
      transform: scale(0.98);
      background-color: $color-cream;
    }
  }

  &__trigger-icon {
    font-size: 48rpx;
  }

  &__trigger-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4rpx;
  }

  &__trigger-label {
    font-size: $font-label;
    color: $color-text-3;
  }

  &__trigger-value {
    font-size: $font-body;
    color: $color-text-1;
    font-weight: $fw-medium;
  }

  &__trigger-arrow {
    font-size: 40rpx;
    color: $color-text-3;
  }

  &__footer {
    display: flex;
    gap: 16rpx;
    margin-top: 24rpx;
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

    &--primary {
      background-color: $color-primary;
      color: #FFFFFF;
    }
  }
}

.undo-snackbar {
  position: fixed;
  left: 32rpx;
  right: 32rpx;
  bottom: 200rpx;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 28rpx;
  background-color: $color-text-1;
  color: #FFFFFF;
  border-radius: 16rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.2);
  animation: snackbarIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);

  &__text {
    font-size: $font-sub;
    color: #FFFFFF;
    flex: 1;
  }

  &__btn {
    padding: 8rpx 20rpx;
    background-color: $color-primary;
    border-radius: 999rpx;
    flex-shrink: 0;
  }

  &__btn-text {
    font-size: $font-label;
    color: #FFFFFF;
    font-weight: $fw-semibold;
  }
}

@keyframes cardBounce {
  0%   { transform: scale(1); }
  30%  { transform: scale(1.06); }
  60%  { transform: scale(0.98); }
  100% { transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

@keyframes snackbarIn {
  from { transform: translateY(40rpx); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>
