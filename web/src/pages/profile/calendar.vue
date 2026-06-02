<template>
  <view class="page-calendar">
    <view class="page-calendar__header">
      <view class="page-calendar__nav" @tap="prevMonth">‹</view>
      <text class="page-calendar__title">{{ currentYear }} 年 {{ currentMonth }} 月</text>
      <view class="page-calendar__nav" @tap="nextMonth">›</view>
    </view>

    <view class="page-calendar__weekdays">
      <text v-for="d in weekdays" :key="d" class="page-calendar__weekday">{{ d }}</text>
    </view>

    <view class="page-calendar__grid">
      <view
        v-for="(day, idx) in days"
        :key="idx"
        class="page-calendar__day"
        :class="{
          'page-calendar__day--empty': !day,
          'page-calendar__day--checked': day && checkedDates.has(day),
        }"
      >
        <text v-if="day" class="page-calendar__day-text">{{ day }}</text>
        <text v-if="day && isToday(day)" class="page-calendar__day-dot">●</text>
      </view>
    </view>

    <view class="page-calendar__streak">
      <text class="page-calendar__streak-label">当前连续打卡</text>
      <text class="page-calendar__streak-num">{{ streakDays }} 天</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getCalendarDates } from '@/api/cooking_logs'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const weekdays = ['日', '一', '二', '三', '四', '五', '六']
const checkedDates = ref(new Set())
const streakDays = ref(0)
const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth() + 1)

const days = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDay = new Date(year, month - 1, 1).getDay()
  const totalDays = new Date(year, month, 0).getDate()
  const result = []
  for (let i = 0; i < firstDay; i++) result.push(null)
  for (let d = 1; d <= totalDays; d++) result.push(d)
  return result
})

function isToday(day) {
  const d = new Date()
  return d.getFullYear() === currentYear.value &&
    d.getMonth() + 1 === currentMonth.value &&
    d.getDate() === day
}

function prevMonth() {
  if (currentMonth.value === 1) {
    currentYear.value--
    currentMonth.value = 12
  } else {
    currentMonth.value--
  }
  fetchData()
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentYear.value++
    currentMonth.value = 1
  } else {
    currentMonth.value++
  }
  fetchData()
}

async function fetchData() {
  try {
    const res = await getCalendarDates(currentYear.value, currentMonth.value)
    checkedDates.value = new Set((res.dates || []).map(d => new Date(d).getDate()))
  } catch {
    checkedDates.value = new Set()
  }
}

onLoad(async () => {
  await Promise.all([
    userStore.fetchStatistics(),
    fetchData(),
  ])
  streakDays.value = userStore.stats.streakDays || 0
})
</script>

<style lang="scss" scoped>
.page-calendar {
  min-height: 100vh;
  background-color: $color-bg;

  &__header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 40rpx;
    padding: 40rpx $page-padding 20rpx;
  }

  &__nav {
    font-size: 48rpx;
    color: $color-text-2;
    width: 80rpx;
    height: 80rpx;
    display: flex;
    align-items: center;
    justify-content: center;

    &:active {
      color: $color-primary;
    }
  }

  &__title {
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
    min-width: 200rpx;
    text-align: center;
  }

  &__weekdays {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    padding: 0 $page-padding;
    margin-bottom: 16rpx;
  }

  &__weekday {
    text-align: center;
    font-size: $font-sub;
    color: $color-text-3;
    padding: 12rpx 0;
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    padding: 0 $page-padding;
    gap: 4rpx;
  }

  &__day {
    aspect-ratio: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-radius: 16rpx;
    position: relative;

    &--empty {
      visibility: hidden;
    }

    &--checked {
      background-color: rgba($color-primary, 0.1);
      border-radius: 16rpx;

      .page-calendar__day-text {
        color: $color-primary;
        font-weight: $fw-semibold;
      }
    }
  }

  &__day-text {
    font-size: $font-body;
    color: $color-text-1;
    line-height: 1;
  }

  &__day-dot {
    font-size: 16rpx;
    color: $color-primary;
    line-height: 1;
    position: absolute;
    bottom: 6rpx;
  }

  &__streak {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16rpx;
    margin: 60rpx $page-padding;
    padding: 32rpx;
    background-color: $color-bg-card;
    border-radius: $card-radius;
    box-shadow: $card-shadow;
  }

  &__streak-label {
    font-size: $font-body;
    color: $color-text-3;
  }

  &__streak-num {
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-primary;
  }
}
</style>
