<template>
  <view class="page-logs">
    <scroll-view
      class="page-logs__scroll"
      :scroll-y="true"
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @refresherrestore="onRestore"
      @scrolltolower="onLoadMore"
    >
      <view class="page-logs__inner">
        <view v-if="loading && logs.length === 0" class="page-logs__loading">
          <text class="page-logs__loading-emoji">🍳</text>
          <text class="page-logs__loading-text">正在翻开小本本…</text>
        </view>

        <EmptyState
          v-else-if="logs.length === 0"
          type="log"
          title="还没有烹饪记录呀"
          description="记下第一餐，开始你的美食之旅 ✨"
          button-text="记下第一餐"
          @action="goAdd"
        />

        <view v-else class="page-logs__timeline">
          <view
            v-for="(group, gIdx) in groupedLogs"
            :key="group.date"
            class="timeline-group"
          >
            <view class="timeline-group__header">
              <view class="timeline-group__dot" />
              <view class="timeline-group__date-block">
                <text class="timeline-group__date">{{ getRelativeDateLabel(group.date) }}</text>
                <text class="timeline-group__weekday">{{ getWeekDay(group.date) }} · {{ group.date.slice(5) }}</text>
              </view>
              <view class="timeline-group__pill">
                <text class="timeline-group__pill-emoji">🍱</text>
                <text class="timeline-group__pill-text">{{ group.items.length }} 餐</text>
              </view>
            </view>

            <view class="timeline-group__cards">
              <view
                v-for="(log, idx) in group.items"
                :key="log.id"
                class="log-card"
                :style="{ animationDelay: (gIdx * 80 + idx * 60) + 'ms' }"
                @tap="goDetail(log)"
                @longpress="onLongPress(log)"
              >
                <view
                  v-if="log.photo_urls && log.photo_urls.length"
                  class="log-card__photo"
                >
                  <image
                    class="log-card__photo-img"
                    :src="log.photo_urls[0]"
                    mode="aspectFill"
                  />
                  <view v-if="log.photo_urls.length > 1" class="log-card__photo-count">
                    <text>+{{ log.photo_urls.length }}</text>
                  </view>
                  <view
                    class="log-card__meal-tag"
                    :style="{ backgroundColor: getMealMeta(log.meal_type).color }"
                  >
                    <text class="log-card__meal-emoji">{{ getMealMeta(log.meal_type).emoji }}</text>
                    <text class="log-card__meal-label">{{ getMealMeta(log.meal_type).label }}</text>
                  </view>
                </view>
                <view
                  v-else
                  class="log-card__photo log-card__photo--placeholder"
                  :style="{ backgroundColor: getMealMeta(log.meal_type).color }"
                >
                  <text class="log-card__photo-emoji">{{ getMealMeta(log.meal_type).emoji }}</text>
                  <view class="log-card__meal-tag log-card__meal-tag--floating">
                    <text class="log-card__meal-emoji">{{ getMealMeta(log.meal_type).emoji }}</text>
                    <text class="log-card__meal-label">{{ getMealMeta(log.meal_type).label }}</text>
                  </view>
                </view>

                <view class="log-card__body">
                  <view class="log-card__row">
                    <text class="log-card__name">{{ log.recipe_name || '未命名' }}</text>
                    <text v-if="log.rating" class="log-card__rating">
                      {{ '★'.repeat(log.rating) }}<text class="log-card__rating--dim">{{ '★'.repeat(5 - log.rating) }}</text>
                    </text>
                  </view>

                  <view class="log-card__meta">
                    <text class="log-card__time">🕒 {{ formatTime(log.cooked_at) }}</text>
                    <text v-if="log.duration" class="log-card__duration">⏱ {{ log.duration }} 分钟</text>
                  </view>

                  <view
                    v-if="log.consumed_ingredients && log.consumed_ingredients.length"
                    class="log-card__chips"
                  >
                    <view
                      v-for="ing in log.consumed_ingredients.slice(0, 3)"
                      :key="ing.name"
                      class="log-card__chip"
                    >
                      <text class="log-card__chip-text">🥕 {{ ing.name }}</text>
                    </view>
                    <view
                      v-if="log.consumed_ingredients.length > 3"
                      class="log-card__chip log-card__chip--more"
                    >
                      <text class="log-card__chip-text">+{{ log.consumed_ingredients.length - 3 }}</text>
                    </view>
                  </view>
                </view>
              </view>
            </view>
          </view>

          <view v-if="!hasMore && logs.length > 0" class="page-logs__end">
            <text class="page-logs__end-text">已经到底啦 🐾</text>
          </view>

          <view class="page-logs__bottom-spacer" />
        </view>
      </view>
    </scroll-view>

    <FabButton icon="＋" @tap="goAdd" @longpress="onFabLongPress" />

    <QuickRecordSheet
      v-if="quickSheetVisible"
      @close="quickSheetVisible = false"
      @saved="onQuickSaved"
    />
  </view>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useCookingLogsStore } from '@/stores/cookingLogs'
import { formatTime, getRelativeDateLabel, getWeekDay, getMealMeta } from '@/utils/date'

import EmptyState from '@/components/EmptyState.vue'
import FabButton from '@/components/FabButton.vue'
import QuickRecordSheet from '@/components/QuickRecordSheet.vue'

const store = useCookingLogsStore()

const logs = computed(() => store.logs)
const groupedLogs = computed(() => store.groupedLogs)
const loading = computed(() => store.loading)
const refreshing = ref(false)
const page = ref(1)
const pageSize = 20
const hasMore = ref(true)
const quickSheetVisible = ref(false)

function goAdd() {
  uni.navigateTo({ url: '/pages/logs/add' })
}

function onFabLongPress() {
  quickSheetVisible.value = true
}

function onQuickSaved() {
  hasMore.value = true
  page.value = 1
  store.fetchLogs({ page: 1, page_size: pageSize })
}

function goDetail(log) {
  uni.navigateTo({ url: `/pages/logs/add?id=${log.id}` })
}

function onLongPress(log) {
  uni.vibrateShort && uni.vibrateShort({ type: 'medium' })
  uni.showActionSheet({
    itemList: ['🗑 删除这条'],
    success: (res) => {
      if (res.tapIndex === 0) {
        uni.showModal({
          title: '确认删除',
          content: '确定要删除这条烹饪记录吗？',
          confirmColor: '#E05A50',
          success: async (confirm) => {
            if (confirm.confirm) {
              try {
                await store.removeLog(log.id)
                uni.showToast({ title: '已删除', icon: 'success' })
              } catch {
                uni.showToast({ title: '删除失败', icon: 'none' })
              }
            }
          },
        })
      }
    },
  })
}

async function onRefresh() {
  refreshing.value = true
  page.value = 1
  hasMore.value = true
  try {
    await store.fetchLogs({ page: 1, page_size: pageSize })
  } finally {
    refreshing.value = false
  }
}

function onRestore() {
  refreshing.value = false
}

async function onLoadMore() {
  if (!hasMore.value || loading.value) return
  page.value += 1
  const { list } = await store.appendLogs({ page: page.value, page_size: pageSize })
  if (list.length < pageSize) hasMore.value = false
}

onMounted(() => {
  store.fetchLogs({ page: 1, page_size: pageSize })
})

onShow(() => {
  store.fetchLogs({ page: 1, page_size: pageSize })
})
</script>

<style lang="scss" scoped>
.page-logs {
  min-height: 100vh;
  background: linear-gradient(180deg, $color-bg 0%, #FFF8F0 100%);
  display: flex;
  flex-direction: column;

  &__scroll {
    flex: 1;
  }

  &__inner {
    padding: $page-padding;
    box-sizing: border-box;
  }

  &__loading {
    text-align: center;
    padding: 120rpx 0;

    &-emoji {
      display: block;
      font-size: 80rpx;
      margin-bottom: 16rpx;
      animation: bounce 1.4s ease-in-out infinite;
    }

    &-text {
      font-size: $font-sub;
      color: $color-text-3;
    }
  }

  &__end {
    text-align: center;
    padding: 48rpx 0;

    &-text {
      font-size: $font-sub;
      color: $color-text-3;
    }
  }

  &__bottom-spacer {
    height: 280rpx;
  }
}

.timeline-group {
  position: relative;
  margin-bottom: 48rpx;

  &__header {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 24rpx;
    position: relative;
    z-index: 2;
  }

  &__dot {
    width: 20rpx;
    height: 20rpx;
    border-radius: 50%;
    background: $color-primary;
    box-shadow: 0 0 0 6rpx rgba($color-primary, 0.18);
    flex-shrink: 0;
  }

  &__date-block {
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  &__date {
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
    line-height: 1.2;
  }

  &__weekday {
    font-size: $font-label;
    color: $color-text-3;
    margin-top: 2rpx;
  }

  &__pill {
    display: flex;
    align-items: center;
    gap: 6rpx;
    padding: 8rpx 18rpx;
    background: $color-primary-light;
    border-radius: 999rpx;
    flex-shrink: 0;
  }

  &__pill-emoji {
    font-size: 22rpx;
  }

  &__pill-text {
    font-size: $font-sub;
    color: $color-primary;
    font-weight: $fw-medium;
  }

  &__cards {
    position: relative;
    padding-left: 32rpx;

    &::before {
      content: '';
      position: absolute;
      left: 9rpx;
      top: 0;
      bottom: 16rpx;
      width: 4rpx;
      background: linear-gradient(180deg, rgba($color-primary, 0.4) 0%, rgba($color-primary, 0.1) 100%);
      border-radius: 2rpx;
    }
  }
}

.log-card {
  background: $color-bg-card;
  border-radius: 32rpx;
  overflow: hidden;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 1;
  animation: cardIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) backwards;
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);

  &:active {
    transform: scale(0.98);
  }

  &__photo {
    position: relative;
    width: 100%;
    height: 360rpx;
    background: $color-cream;

    &--placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }

  &__photo-img {
    width: 100%;
    height: 100%;
  }

  &__photo-emoji {
    font-size: 120rpx;
  }

  &__photo-count {
    position: absolute;
    right: 20rpx;
    bottom: 20rpx;
    background: rgba(0, 0, 0, 0.45);
    color: #fff;
    font-size: $font-sub;
    padding: 6rpx 14rpx;
    border-radius: 999rpx;
    font-weight: $fw-medium;
    backdrop-filter: blur(8rpx);
  }

  &__meal-tag {
    position: absolute;
    top: 20rpx;
    left: 20rpx;
    display: flex;
    align-items: center;
    gap: 6rpx;
    padding: 8rpx 16rpx;
    border-radius: 999rpx;
    backdrop-filter: blur(8rpx);
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);

    &--floating {
      position: absolute;
      bottom: 20rpx;
      left: 20rpx;
      top: auto;
    }
  }

  &__meal-emoji {
    font-size: 22rpx;
  }

  &__meal-label {
    font-size: $font-sub;
    color: $color-text-1;
    font-weight: $fw-medium;
  }

  &__body {
    padding: 24rpx;
  }

  &__row {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 12rpx;
  }

  &__name {
    flex: 1;
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
    line-height: 1.3;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__rating {
    font-size: 24rpx;
    color: #F5A623;
    letter-spacing: 1rpx;
    flex-shrink: 0;

    &--dim {
      color: rgba($color-text-3, 0.4);
    }
  }

  &__meta {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 16rpx;
  }

  &__time,
  &__duration {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__chips {
    display: flex;
    flex-wrap: wrap;
    gap: 12rpx;
  }

  &__chip {
    display: flex;
    align-items: center;
    padding: 8rpx 16rpx;
    background: $color-cream;
    border-radius: 999rpx;
    max-width: 280rpx;

    &--more {
      background: $color-primary-light;
    }
  }

  &__chip-text {
    font-size: $font-sub;
    color: $color-text-2;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(24rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12rpx); }
}
</style>
