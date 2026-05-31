<template>
  <view class="page-family">
    <view v-if="loading" class="page-family__loading">
      <text>加载中...</text>
    </view>

    <template v-else>
      <view v-if="!household" class="page-family__empty">
        <view class="page-family__empty-icon">👨‍👩‍👧</view>
        <text class="page-family__empty-title">家庭冰箱</text>
        <text class="page-family__empty-desc">与家人共享冰箱食材和菜谱，一起享受烹饪乐趣</text>
        <view class="page-family__empty-actions">
          <button class="btn-primary page-family__create-btn" @tap="onCreate">创建家庭冰箱</button>
          <text class="page-family__join-hint">已有家庭？</text>
          <view class="page-family__join-row">
            <input class="page-family__join-input" v-model="joinCode" placeholder="输入6位邀请码" maxlength="6" />
            <button class="page-family__join-btn" @tap="onJoin">加入</button>
          </view>
        </view>
      </view>

      <view v-else class="page-family__info">
        <view class="page-family__header card">
          <view class="page-family__header-top">
            <text class="page-family__name">{{ household.name }}</text>
            <text class="page-family__role">{{ isOwner ? '房主' : '成员' }}</text>
          </view>

          <view class="page-family__invite">
            <text class="page-family__invite-label">邀请码</text>
            <view class="page-family__invite-code-wrap">
              <text class="page-family__invite-code">{{ household.invite_code }}</text>
              <button class="page-family__copy-btn" @tap="onCopyCode">复制</button>
            </view>
            <button v-if="isOwner" class="page-family__regenerate-btn" @tap="onRegenerate">重新生成</button>
          </view>
        </view>

        <view class="page-family__members card">
          <text class="page-family__section-title">家庭成员（{{ household.members?.length }}）</text>
          <view
            v-for="m in household.members"
            :key="m.id"
            class="page-family__member"
          >
            <image
              class="page-family__member-avatar"
              :src="m.avatar_url || 'https://picsum.photos/100/100'"
              mode="aspectFill"
            />
            <text class="page-family__member-name">{{ m.nickname || '未命名' }}</text>
            <text v-if="m.id === household.owner_id" class="page-family__member-role">房主</text>
            <button
              v-if="isOwner && m.id !== household.owner_id"
              class="page-family__remove-btn"
              @tap="onRemoveMember(m.id, m.nickname)"
            >移除</button>
          </view>
        </view>

        <view class="page-family__actions">
          <button class="page-family__leave-btn" @tap="onLeave">退出家庭冰箱</button>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import {
  getCurrentHousehold, createHousehold, joinHousehold,
  regenerateInvite, removeMember, leaveHousehold,
} from '@/api/households'

const userStore = useUserStore()

const household = ref(null)
const loading = ref(true)
const joinCode = ref('')

const isOwner = computed(() => {
  return household.value && household.value.owner_id === userStore.userInfo.id
})

onShow(async () => {
  await loadHousehold()
})

async function loadHousehold() {
  loading.value = true
  try {
    household.value = await getCurrentHousehold()
  } catch {
    household.value = null
  } finally {
    loading.value = false
  }
}

async function onCreate() {
  try {
    await createHousehold()
    await userStore.fetchProfile()
    uni.showToast({ title: '创建成功', icon: 'success' })
    await loadHousehold()
  } catch (e) {
    uni.showToast({ title: e.message || '创建失败', icon: 'none' })
  }
}

async function onJoin() {
  if (!joinCode.value || joinCode.value.length !== 6) {
    return uni.showToast({ title: '请输入6位邀请码', icon: 'none' })
  }
  try {
    await joinHousehold(joinCode.value)
    await userStore.fetchProfile()
    uni.showToast({ title: '加入成功', icon: 'success' })
    await loadHousehold()
  } catch (e) {
    uni.showToast({ title: e.message || '加入失败', icon: 'none' })
  }
}

function onCopyCode() {
  uni.setClipboardData({
    data: household.value.invite_code,
    success: () => uni.showToast({ title: '已复制', icon: 'success' }),
  })
}

async function onRegenerate() {
  try {
    const res = await regenerateInvite()
    household.value.invite_code = res.invite_code
    uni.showToast({ title: '已重新生成', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.message || '操作失败', icon: 'none' })
  }
}

async function onRemoveMember(userId, nickname) {
  uni.showModal({
    title: '移除成员',
    content: `确定移除「${nickname || '该成员'}」吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await removeMember(userId)
          uni.showToast({ title: '已移除', icon: 'success' })
          await loadHousehold()
        } catch (e) {
          uni.showToast({ title: e.message || '操作失败', icon: 'none' })
        }
      }
    },
  })
}

async function onLeave() {
  uni.showModal({
    title: '退出家庭',
    content: '确定退出当前家庭冰箱吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await leaveHousehold()
          await userStore.fetchProfile()
          uni.showToast({ title: '已退出', icon: 'success' })
          household.value = null
        } catch (e) {
          uni.showToast({ title: e.message || '操作失败', icon: 'none' })
        }
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.page-family {
  min-height: 100vh;
  background-color: $color-bg;
  padding: $page-padding;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));

  &__loading {
    text-align: center;
    padding: 80rpx 0;
    color: $color-text-3;
  }

  &__empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 100rpx;
  }

  &__empty-icon {
    font-size: 120rpx;
    margin-bottom: 32rpx;
  }

  &__empty-title {
    font-size: 40rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
    margin-bottom: 16rpx;
  }

  &__empty-desc {
    font-size: $font-sub;
    color: $color-text-3;
    text-align: center;
    margin-bottom: 48rpx;
    line-height: 1.6;
    max-width: 500rpx;
  }

  &__empty-actions {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 24rpx;
  }

  &__create-btn {
    width: 100%;
    height: 96rpx;
    line-height: 96rpx;
    border-radius: 999rpx;
    font-size: $font-body;
  }

  &__join-hint {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__join-row {
    display: flex;
    gap: 16rpx;
    width: 100%;
  }

  &__join-input {
    flex: 1;
    height: 88rpx;
    padding: 0 24rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    font-size: 32rpx;
    letter-spacing: 8rpx;
    text-align: center;
    color: $color-text-1;
    box-shadow: $card-shadow;
  }

  &__join-btn {
    width: 160rpx;
    height: 88rpx;
    line-height: 88rpx;
    border-radius: 16rpx;
    background-color: $color-primary;
    color: #fff;
    font-size: $font-body;
    border: none;
  }

  &__header {
    padding: 32rpx;
    margin-bottom: 24rpx;
  }

  &__header-top {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 24rpx;
  }

  &__name {
    font-size: 36rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
  }

  &__role {
    font-size: $font-label;
    color: $color-primary;
    background-color: rgba($color-primary, 0.1);
    padding: 4rpx 16rpx;
    border-radius: 8rpx;
  }

  &__invite {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
  }

  &__invite-label {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__invite-code-wrap {
    display: flex;
    align-items: center;
    gap: 16rpx;
  }

  &__invite-code {
    font-size: 48rpx;
    font-weight: $fw-semibold;
    color: $color-primary;
    letter-spacing: 8rpx;
    font-family: monospace;
  }

  &__copy-btn {
    min-width: 96rpx;
    height: 56rpx;
    line-height: 56rpx;
    border-radius: 12rpx;
    background-color: rgba($color-primary, 0.1);
    color: $color-primary;
    font-size: $font-label;
    border: none;
    padding: 0 16rpx;
  }

  &__regenerate-btn {
    align-self: flex-start;
    height: 56rpx;
    line-height: 56rpx;
    border-radius: 12rpx;
    background-color: transparent;
    color: $color-text-3;
    font-size: $font-label;
    border: 2rpx solid $color-border;
    padding: 0 24rpx;
  }

  &__members {
    padding: 32rpx;
    margin-bottom: 24rpx;
  }

  &__section-title {
    display: block;
    font-size: $font-sub;
    color: $color-text-3;
    margin-bottom: 24rpx;
  }

  &__member {
    display: flex;
    align-items: center;
    gap: 20rpx;
    padding: 16rpx 0;

    &:not(:last-child) {
      border-bottom: 1rpx solid rgba($color-border, 0.3);
    }
  }

  &__member-avatar {
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
    background-color: $color-bg;
  }

  &__member-name {
    flex: 1;
    font-size: $font-body;
    color: $color-text-1;
  }

  &__member-role {
    font-size: $font-label;
    color: $color-text-3;
    background-color: $color-bg-section;
    padding: 4rpx 16rpx;
    border-radius: 8rpx;
  }

  &__remove-btn {
    min-width: 96rpx;
    height: 56rpx;
    line-height: 56rpx;
    border-radius: 12rpx;
    background-color: rgba($color-warn, 0.1);
    color: $color-warn;
    font-size: $font-label;
    border: none;
    padding: 0 16rpx;
  }

  &__actions {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
  }

  &__leave-btn {
    height: 88rpx;
    line-height: 88rpx;
    border-radius: 16rpx;
    background-color: transparent;
    color: $color-warn;
    font-size: $font-body;
    border: 2rpx solid rgba($color-warn, 0.3);
  }
}
</style>
