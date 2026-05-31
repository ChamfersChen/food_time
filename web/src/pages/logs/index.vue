<template>
  <view class="page-logs">
    <scroll-view class="page-logs__list" scroll-y enable-back-to-top>
      <view class="page-logs__list-inner">
        <view v-if="loading && logs.length === 0" class="page-logs__loading">
          <text>加载中...</text>
        </view>

        <EmptyState
          v-else-if="logs.length === 0"
          type="logs"
          title="还没有烹饪记录"
          description="记录你的第一餐吧"
          button-text="添加记录"
          @action="goAdd"
        />

        <view v-else>
          <view
            v-for="group in groupedLogs"
            :key="group.date"
            class="page-logs__group"
          >
            <view class="page-logs__group-header">
              <text class="page-logs__group-date">{{ getRelativeDateLabel(group.date) }}</text>
              <text class="page-logs__group-weekday">{{ getWeekDay(group.date) }}</text>
              <text class="page-logs__group-count">{{ group.items.length }} 餐</text>
            </view>

            <view
              v-for="log in group.items"
              :key="log.id"
              class="page-logs__card"
              @tap="goDetail(log)"
              @longpress="onLongPress(log)"
            >
              <view class="page-logs__card-left">
                <image
                  v-if="log.photo_urls?.[0]"
                  class="page-logs__card-avatar"
                  :src="log.photo_urls[0]"
                  mode="aspectFill"
                />
                <text v-else class="page-logs__card-emoji">{{ getMealEmoji(log.meal_type) }}</text>
              </view>
              <view class="page-logs__card-center">
                <text class="page-logs__card-name">{{ log.recipe_name || '未命名' }}</text>
                <text class="page-logs__card-time">{{ formatDate(log.cooked_at, 'HH:mm') }}</text>
              </view>
              <view class="page-logs__card-right">
                <text v-if="log.rating" class="page-logs__card-rating">
                  {{ '★'.repeat(log.rating) }}{{ '☆'.repeat(5 - log.rating) }}
                </text>
              </view>
            </view>
          </view>
        </view>

        <view class="page-logs__bottom-spacer" />
      </view>
    </scroll-view>

    <FabButton icon="＋" @tap="goAdd" />
  </view>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useCookingLogsStore } from '@/stores/cookingLogs'
import { formatDate, getWeekDay, getRelativeDateLabel } from '@/utils/date'

import EmptyState from '@/components/EmptyState.vue'
import FabButton from '@/components/FabButton.vue'

const store = useCookingLogsStore()

const logs = computed(() => store.logs)
const groupedLogs = computed(() => store.groupedLogs)
const totalMeals = computed(() => store.totalMeals)
const loading = computed(() => store.loading)

function getMealEmoji(mealType) {
  const map = {
    breakfast: '🌅',
    lunch: '☀️',
    dinner: '🌙',
    snack: '🍪',
  }
  return map[mealType] || '🍽️'
}

function goAdd() {
  uni.navigateTo({ url: '/pages/logs/add' })
}

function goDetail(log) {
  uni.navigateTo({ url: `/pages/logs/add?id=${log.id}` })
}

function onLongPress(log) {
  uni.showActionSheet({
    itemList: ['删除'],
    success: (res) => {
      if (res.tapIndex === 0) {
        uni.showModal({
          title: '确认删除',
          content: '确定要删除这条烹饪记录吗？',
          success: async (confirm) => {
            if (confirm.confirm) {
              try {
                await store.removeLog(log.id)
                uni.showToast({ title: '删除成功', icon: 'success' })
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

onMounted(() => {
  store.fetchLogs()
})

onShow(() => {
  store.fetchLogs()
})
</script>

<style lang="scss" scoped>
.page-logs {
  min-height: 100vh;
  background-color: $color-bg;
  display: flex;
  flex-direction: column;

  &__list {
    flex: 1;
  }

  &__list-inner {
    padding: $page-padding $page-padding 0;
  }

  &__loading {
    text-align: center;
    padding: 80rpx 0;
    color: $color-text-3;
    font-size: $font-sub;
  }

  &__group {
    margin-bottom: 32rpx;
  }

  &__group-header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 16rpx;
    padding: 0 4rpx;
  }

  &__group-date {
    font-size: $font-body;
    font-weight: $fw-semibold;
    color: $color-text-1;
  }

  &__group-weekday {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__group-count {
    font-size: $font-sub;
    color: $color-text-3;
    margin-left: auto;
  }

  &__card {
    display: flex;
    align-items: center;
    padding: 24rpx;
    margin-bottom: 16rpx;
    background-color: $color-bg-card;
    border-radius: $card-radius;
    box-shadow: $card-shadow;

    &:active {
      transform: scale(0.98);
    }
  }

  &__card-left {
    margin-right: 20rpx;
    flex-shrink: 0;
  }

  &__card-avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 12rpx;
    background-color: $color-bg;
  }

  &__card-emoji {
    font-size: 48rpx;
  }

  &__card-center {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6rpx;
  }

  &__card-name {
    font-size: $font-body;
    font-weight: $fw-medium;
    color: $color-text-1;
  }

  &__card-time {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__card-right {
    margin-left: 16rpx;
  }

  &__card-rating {
    font-size: 24rpx;
    color: #F5A623;
  }

  &__bottom-spacer {
    height: 240rpx;
  }
}
</style>
