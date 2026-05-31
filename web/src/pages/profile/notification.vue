<template>
  <view class="page-notify">
    <view class="page-notify__section card">
      <view class="page-notify__row">
        <view class="page-notify__row-info">
          <text class="page-notify__row-title">全局通知开关</text>
          <text class="page-notify__row-desc">开启后才会推送以下提醒</text>
        </view>
        <switch
          class="page-notify__switch"
          :checked="form.notification_open"
          @change="form.notification_open = $event.detail.value"
          color="#7BBF8E"
        />
      </view>
    </view>

    <view class="page-notify__section card">
      <text class="page-notify__section-title">提醒类型</text>

      <view class="page-notify__row">
        <view class="page-notify__row-info">
          <text class="page-notify__row-title">🕐 食材临期提醒</text>
          <text class="page-notify__row-desc">食材即将过期时通知你</text>
        </view>
        <switch
          class="page-notify__switch"
          :checked="form.notify_expiry"
          @change="form.notify_expiry = $event.detail.value"
          color="#7BBF8E"
        />
      </view>

      <view class="page-notify__row page-notify__row--indent">
        <text class="page-notify__row-title">提前</text>
        <view class="page-notify__slider-wrap">
          <slider
            class="page-notify__slider"
            :value="form.notify_days_before"
            min="1"
            max="14"
            step="1"
            @change="form.notify_days_before = $event.detail.value"
            block-size="20"
            active-color="#7BBF8E"
            backgroundColor="#EAE8E3"
          />
          <text class="page-notify__slider-label">{{ form.notify_days_before }} 天</text>
        </view>
      </view>

      <view class="page-notify__divider" />

      <view class="page-notify__row">
        <view class="page-notify__row-info">
          <text class="page-notify__row-title">📦 冰箱库存不足提醒</text>
          <text class="page-notify__row-desc">食材用完后提醒补货</text>
        </view>
        <switch
          class="page-notify__switch"
          :checked="form.notify_stock"
          @change="form.notify_stock = $event.detail.value"
          color="#7BBF8E"
        />
      </view>

      <view class="page-notify__divider" />

      <view class="page-notify__row">
        <view class="page-notify__row-info">
          <text class="page-notify__row-title">🔥 久未烹饪提醒</text>
          <text class="page-notify__row-desc">超过设置天数未记录时提醒</text>
        </view>
        <switch
          class="page-notify__switch"
          :checked="form.notify_inactive"
          @change="form.notify_inactive = $event.detail.value"
          color="#7BBF8E"
        />
      </view>

      <view class="page-notify__row page-notify__row--indent">
        <text class="page-notify__row-title">超过</text>
        <view class="page-notify__slider-wrap">
          <slider
            class="page-notify__slider"
            :value="form.inactive_days"
            min="3"
            max="30"
            step="1"
            @change="form.inactive_days = $event.detail.value"
            block-size="20"
            active-color="#7BBF8E"
            backgroundColor="#EAE8E3"
          />
          <text class="page-notify__slider-label">{{ form.inactive_days }} 天</text>
        </view>
      </view>
    </view>

    <view class="page-notify__section card">
      <text class="page-notify__section-title">推送时段</text>
      <view class="page-notify__row">
        <text class="page-notify__row-title">通知时间</text>
        <picker
          mode="time"
          :value="notifyTimeStr"
          @change="onTimeChange"
        >
          <view class="page-notify__time-picker">
            <text class="page-notify__time-text">{{ notifyTimeStr }}</text>
            <text class="page-notify__time-arrow">›</text>
          </view>
        </picker>
      </view>
    </view>

    <view class="page-notify__section card">
      <text class="page-notify__section-title">微信订阅管理</text>
      <text class="page-notify__subscribe-hint">
        订阅后通知将通过微信「服务通知」推送给你。每次模板授权仅能推送一条消息，用完需重新订阅。
      </text>
      <button
        class="page-notify__subscribe-btn"
        :disabled="subscribing"
        @tap="onSubscribe"
      >
        {{ subscribing ? '请求中...' : '订阅通知' }}
      </button>
      <view v-if="subscribedList.length" class="page-notify__subscribed">
        <text class="page-notify__subscribed-label">已订阅：</text>
        <text class="page-notify__subscribed-item" v-for="(name, i) in subscribedList" :key="i">{{ name }}</text>
      </view>
    </view>

    <view class="page-notify__footer">
      <button class="page-notify__save btn-primary" @tap="onSubmit" :disabled="saving">
        {{ saving ? '保存中...' : '保存设置' }}
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { subscribeTemplates } from '@/api/users'
import { requestSubscribeMsg } from '@/api/auth'
import { WX_TEMPLATES, TEMPLATE_NAMES, ALL_TMPL_IDS } from '@/config/wechat'

const userStore = useUserStore()

const form = reactive({
  notification_open: true,
  notify_days_before: 3,
  notify_hour: 9,
  notify_expiry: true,
  notify_stock: true,
  notify_inactive: false,
  inactive_days: 7,
})

const subscribing = ref(false)
const saving = ref(false)
const subscribedTemplates = ref([])

const notifyTimeStr = computed(() => {
  const h = String(form.notify_hour).padStart(2, '0')
  return `${h}:00`
})

const subscribedList = computed(() => {
  return subscribedTemplates.value
    .map(id => TEMPLATE_NAMES[id])
    .filter(Boolean)
})

onLoad(() => {
  const info = userStore.userInfo
  form.notification_open = info.notification_open !== false
  form.notify_days_before = info.notify_days_before || 3
  form.notify_hour = info.notify_hour || 9
  form.notify_expiry = info.notify_expiry !== false
  form.notify_stock = info.notify_stock !== false
  form.notify_inactive = info.notify_inactive || false
  form.inactive_days = info.inactive_days || 7
  subscribedTemplates.value = info.subscribed_templates || []
})

function onTimeChange(e) {
  const [h] = e.detail.value.split(':')
  form.notify_hour = parseInt(h, 10)
}

async function onSubscribe() {
  subscribing.value = true
  try {
    const res = await requestSubscribeMsg(ALL_TMPL_IDS)
    if (!res) return
    const accepted = ALL_TMPL_IDS.filter(id => res[id] === 'accept')
    if (!accepted.length) {
      uni.showToast({ title: '未同意任何订阅', icon: 'none' })
      return
    }
    const result = await subscribeTemplates(accepted)
    subscribedTemplates.value = result.subscribed_templates || []
    uni.showToast({ title: '订阅成功', icon: 'success' })
  } catch {
    uni.showToast({ title: '订阅失败', icon: 'none' })
  } finally {
    subscribing.value = false
  }
}

async function onSubmit() {
  saving.value = true
  try {
    await userStore.savePreferences({
      notification_open: form.notification_open,
      notify_days_before: form.notify_days_before,
      notify_hour: form.notify_hour,
      notify_expiry: form.notify_expiry,
      notify_stock: form.notify_stock,
      notify_inactive: form.notify_inactive,
      inactive_days: form.inactive_days,
    })
    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.page-notify {
  min-height: 100vh;
  background-color: $color-bg;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));

  &__section {
    margin: 0 $page-padding;
    margin-bottom: 24rpx;
    padding: 32rpx;
  }

  &__section-title {
    display: block;
    font-size: $font-sub;
    color: $color-text-3;
    margin-bottom: 24rpx;
  }

  &__row {
    display: flex;
    align-items: center;
    justify-content: space-between;

    &--indent {
      padding-left: 40rpx;
      margin-top: 16rpx;
    }
  }

  &__row-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4rpx;
  }

  &__row-title {
    font-size: $font-body;
    color: $color-text-1;
    font-weight: $fw-medium;
  }

  &__row-desc {
    font-size: $font-label;
    color: $color-text-3;
  }

  &__switch {
    transform: scale(0.8);
    transform-origin: right center;
    flex-shrink: 0;
  }

  &__divider {
    height: 1rpx;
    background-color: rgba($color-border, 0.3);
    margin: 24rpx 0;
  }

  &__slider-wrap {
    display: flex;
    align-items: center;
    gap: 16rpx;
    flex: 1;
    max-width: 320rpx;
  }

  &__slider {
    flex: 1;
  }

  &__slider-label {
    font-size: $font-body;
    color: $color-primary;
    font-weight: $fw-medium;
    min-width: 56rpx;
    text-align: right;
  }

  &__time-picker {
    display: flex;
    align-items: center;
    gap: 8rpx;
  }

  &__time-text {
    font-size: $font-body;
    color: $color-primary;
    font-weight: $fw-medium;
  }

  &__time-arrow {
    font-size: 28rpx;
    color: $color-text-3;
  }

  &__subscribe-hint {
    display: block;
    font-size: $font-label;
    color: $color-text-3;
    line-height: 1.6;
    margin-bottom: 20rpx;
  }

  &__subscribe-btn {
    width: 100%;
    height: 88rpx;
    line-height: 88rpx;
    border-radius: 999rpx;
    background-color: $color-primary;
    color: #fff;
    font-size: $font-body;
    font-weight: $fw-medium;
    border: none;

    &:active {
      opacity: 0.9;
    }
  }

  &__subscribed {
    display: flex;
    flex-wrap: wrap;
    gap: 8rpx;
    margin-top: 16rpx;
  }

  &__subscribed-label {
    font-size: $font-label;
    color: $color-text-3;
    line-height: 40rpx;
  }

  &__subscribed-item {
    font-size: $font-label;
    color: $color-primary;
    background-color: rgba($color-primary, 0.1);
    padding: 4rpx 16rpx;
    border-radius: 8rpx;
  }

  &__footer {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 20rpx $page-padding;
    padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
    background-color: rgba($color-bg, 0.9);
    backdrop-filter: blur(10px);
  }

  &__save {
    width: 100%;
    height: 96rpx;
    line-height: 96rpx;
    border-radius: 999rpx;
  }
}
</style>
