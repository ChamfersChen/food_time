<template>
  <view class="page-profile">
    <view class="page-profile__header">
      <view class="page-profile__avatar-wrap" @tap="goEditProfile">
        <image
          class="page-profile__avatar"
          :src="avatarUrl || 'https://picsum.photos/200/200?random=profile'"
          mode="aspectFill"
        />
        <view class="page-profile__avatar-edit">
          <text class="page-profile__avatar-edit-icon">✎</text>
        </view>
      </view>
      <text class="page-profile__nickname">{{ nickname }}</text>
      <text class="page-profile__bio">{{ userInfo.bio || '享受轻盈生活，记录每一餐的治愈时刻。' }}</text>
      <view class="page-profile__tags">
        <view v-for="tag in preferenceTags" :key="tag" class="page-profile__tag">
          {{ tag }}
        </view>
      </view>
    </view>

    <view class="page-profile__stats">
      <view class="page-profile__stat card">
        <text class="page-profile__stat-num">{{ stats.totalMeals }}</text>
        <text class="page-profile__stat-label">已记录餐食</text>
      </view>
      <view class="page-profile__stat card">
        <text class="page-profile__stat-num">{{ stats.streakDays }}</text>
        <text class="page-profile__stat-label">连续打卡(天)</text>
      </view>
    </view>

    <view class="page-profile__list card">
      <view class="page-profile__item" @tap="goNotificationSettings">
        <view class="page-profile__item-left">
          <view class="page-profile__item-icon">
            <text>🔔</text>
          </view>
          <text class="page-profile__item-text">提醒设置</text>
        </view>
        <text class="page-profile__item-arrow">›</text>
      </view>

      <view class="page-profile__divider" />

      <view class="page-profile__item" @tap="goDataSync">
        <view class="page-profile__item-left">
          <view class="page-profile__item-icon">
            <text>🔄</text>
          </view>
          <text class="page-profile__item-text">数据同步</text>
        </view>
        <view class="page-profile__item-right">
          <text class="page-profile__item-status">已连接</text>
          <text class="page-profile__item-arrow">›</text>
        </view>
      </view>

      <view class="page-profile__divider" />

      <view class="page-profile__item" @tap="goFamilyShare">
        <view class="page-profile__item-left">
          <view class="page-profile__item-icon">
            <text>👨‍👩‍👧</text>
          </view>
          <text class="page-profile__item-text">家庭共享</text>
        </view>
        <text class="page-profile__item-arrow">›</text>
      </view>

      <view class="page-profile__divider" />

      <view class="page-profile__item" @tap="goAIPreferences">
        <view class="page-profile__item-left">
          <view class="page-profile__item-icon page-profile__item-icon--ai">
            <text>✨</text>
          </view>
          <text class="page-profile__item-text">AI 偏好设置</text>
        </view>
        <text class="page-profile__item-arrow">›</text>
      </view>
    </view>

    <view class="page-profile__footer">
      <text class="page-profile__version">食光机 v1.0.0</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'


const userStore = useUserStore()
const stats = ref({ totalMeals: 0, streakDays: 0 })

const nickname = computed(() => userStore.nickname)
const avatarUrl = computed(() => userStore.avatarUrl)
const userInfo = computed(() => userStore.userInfo)

const preferenceTags = computed(() => {
  const prefs = userStore.preferences
  const tags = []
  if (prefs.diet_type === 'vegetarian') tags.push('🌿 素食倾向')
  else if (prefs.diet_type === 'vegan') tags.push('🌱 纯素')
  else if (prefs.diet_type === 'halal') tags.push('🕌 清真')
  if (prefs.skill_level === 'beginner') tags.push('📖 厨房新手')
  else if (prefs.skill_level === 'intermediate') tags.push('👨‍🍳 进阶厨师')
  prefs.flavor_pref?.forEach(f => {
    if (f === '清淡') tags.push('🍵 清淡')
    else if (f === '微辣') tags.push('🌶 微辣')
  })
  return tags.length ? tags : ['🍽 美食爱好者']
})

function goEditProfile() {
  // TODO: navigate to edit profile page
}

function goNotificationSettings() {
  // TODO: navigate to notification settings
}

function goDataSync() {
  // TODO: navigate to data sync
}

function goFamilyShare() {
  // TODO: navigate to family share
}

function goAIPreferences() {
  // TODO: navigate to AI preferences
}

onShow(async () => {
  await Promise.all([
    userStore.fetchProfile(),
    userStore.fetchStatistics(),
  ])
  stats.value = userStore.stats
})
</script>

<style lang="scss" scoped>
.page-profile {
  min-height: 100vh;
  background-color: $color-bg;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));

  &__header {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: $page-padding;
    padding-top: calc(env(safe-area-inset-top) + 40rpx);
    margin-bottom: 32rpx;
  }

  &__avatar-wrap {
    position: relative;
    width: 160rpx;
    height: 160rpx;
    border-radius: 50%;
    overflow: visible;
    margin-bottom: 24rpx;
  }

  &__avatar {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 6rpx solid #FFFFFF;
    box-shadow: $card-shadow;
  }

  &__avatar-edit {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 44rpx;
    height: 44rpx;
    border-radius: 50%;
    background-color: $color-primary;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
  }

  &__avatar-edit-icon {
    color: #FFFFFF;
    font-size: 20rpx;
  }

  &__nickname {
    font-size: 36rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
    margin-bottom: 8rpx;
  }

  &__bio {
    font-size: $font-sub;
    color: $color-text-3;
    text-align: center;
    margin-bottom: 24rpx;
    max-width: 500rpx;
  }

  &__tags {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 16rpx;
  }

  &__tag {
    padding: 8rpx 24rpx;
    border-radius: 999rpx;
    background-color: $color-bg-section;
    font-size: $font-label;
    color: $color-text-2;
  }

  &__stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20rpx;
    padding: 0 $page-padding;
    margin-bottom: 32rpx;
  }

  &__stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 32rpx;
  }

  &__stat-num {
    font-size: 48rpx;
    font-weight: $fw-semibold;
    color: $color-primary;
    margin-bottom: 8rpx;
  }

  &__stat-label {
    font-size: $font-label;
    color: $color-text-3;
  }

  &__list {
    margin: 0 $page-padding;
    overflow: hidden;
  }

  &__item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 28rpx 0;

    &:active {
      background-color: $color-bg-section;
    }
  }

  &__item-left {
    display: flex;
    align-items: center;
    gap: 20rpx;
  }

  &__item-icon {
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
    background-color: $color-bg-section;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28rpx;

    &--ai {
      background-color: rgba($color-primary, 0.15);
    }
  }

  &__item-text {
    font-size: $font-body;
    color: $color-text-1;
  }

  &__item-right {
    display: flex;
    align-items: center;
    gap: 8rpx;
  }

  &__item-status {
    font-size: $font-sub;
    color: $color-primary;
  }

  &__item-arrow {
    font-size: 28rpx;
    color: $color-text-3;
  }

  &__divider {
    height: 1rpx;
    background-color: rgba($color-border, 0.3);
    margin-left: 84rpx;
  }

  &__footer {
    text-align: center;
    padding: 48rpx 0;
  }

  &__version {
    font-size: $font-label;
    color: $color-text-3;
  }
}
</style>