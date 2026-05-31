<template>
  <view class="page-profile-edit">
    <view class="page-profile-edit__avatar-section" @tap="onChangeAvatar">
      <image
        class="page-profile-edit__avatar"
        :src="form.avatar_url || 'https://picsum.photos/200/200?random=profile'"
        mode="aspectFill"
      />
      <view class="page-profile-edit__avatar-overlay">
        <text class="page-profile-edit__avatar-camera">📷</text>
        <text class="page-profile-edit__avatar-hint">更换头像</text>
      </view>
    </view>

    <view class="page-profile-edit__form">
      <view class="page-profile-edit__field">
        <text class="page-profile-edit__label">昵称</text>
        <input
          class="page-profile-edit__input"
          v-model="form.nickname"
          placeholder="输入你的昵称"
          :maxlength="20"
        />
      </view>

      <view class="page-profile-edit__field">
        <text class="page-profile-edit__label">个性签名</text>
        <textarea
          class="page-profile-edit__textarea"
          v-model="form.bio"
          placeholder="写一句话介绍自己吧"
          :maxlength="120"
        />
      </view>

      <view class="page-profile-edit__field">
        <text class="page-profile-edit__label">饮食习惯</text>
        <view class="page-profile-edit__options">
          <view
            v-for="opt in DIET_OPTIONS"
            :key="opt.value"
            class="page-profile-edit__option"
            :class="{ 'page-profile-edit__option--active': form.diet_type === opt.value }"
            @tap="form.diet_type = opt.value"
          >
            <text class="page-profile-edit__option-emoji">{{ opt.emoji }}</text>
            <text class="page-profile-edit__option-label">{{ opt.label }}</text>
          </view>
        </view>
      </view>

      <view class="page-profile-edit__field">
        <text class="page-profile-edit__label">烹饪水平</text>
        <view class="page-profile-edit__options">
          <view
            v-for="opt in SKILL_OPTIONS"
            :key="opt.value"
            class="page-profile-edit__option"
            :class="{ 'page-profile-edit__option--active': form.skill_level === opt.value }"
            @tap="form.skill_level = opt.value"
          >
            <text class="page-profile-edit__option-emoji">{{ opt.emoji }}</text>
            <text class="page-profile-edit__option-label">{{ opt.label }}</text>
          </view>
        </view>
      </view>

      <view class="page-profile-edit__field">
        <text class="page-profile-edit__label">口味偏好（可多选）</text>
        <view class="page-profile-edit__chips">
          <view
            v-for="opt in FLAVOR_OPTIONS"
            :key="opt.value"
            class="page-profile-edit__chip"
            :class="{ 'page-profile-edit__chip--active': form.flavor_pref.includes(opt.value) }"
            @tap="toggleFlavor(opt.value)"
          >
            {{ opt.label }}
          </view>
        </view>
      </view>
    </view>

    <view class="page-profile-edit__footer">
      <button class="page-profile-edit__save btn-primary" @tap="onSubmit" :disabled="saving">
        {{ saving ? '保存中...' : '保存' }}
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { upload } from '@/api/request'

const userStore = useUserStore()

const DIET_OPTIONS = [
  { value: 'omnivore', emoji: '🍖', label: '不忌口' },
  { value: 'vegetarian', emoji: '🥦', label: '素食' },
  { value: 'vegan', emoji: '🌱', label: '纯素' },
  { value: 'halal', emoji: '🕌', label: '清真' },
]

const SKILL_OPTIONS = [
  { value: 'beginner', emoji: '📖', label: '厨房新手' },
  { value: 'intermediate', emoji: '👨‍🍳', label: '进阶厨师' },
  { value: 'advanced', emoji: '👩‍🍳', label: '烹饪达人' },
]

const FLAVOR_OPTIONS = [
  { value: '清淡', label: '🥗 清淡' },
  { value: '微辣', label: '🌶 微辣' },
  { value: '麻辣', label: '🔥 麻辣' },
  { value: '酸甜', label: '🍋 酸甜' },
  { value: '咸鲜', label: '🧂 咸鲜' },
  { value: '甜', label: '🍬 偏甜' },
]

const form = reactive({
  avatar_url: '',
  nickname: '',
  bio: '',
  diet_type: 'omnivore',
  skill_level: 'beginner',
  flavor_pref: [],
})

const saving = ref(false)

onLoad(() => {
  const info = userStore.userInfo
  form.avatar_url = info.avatar_url || ''
  form.nickname = info.nickname || ''
  form.bio = info.bio || ''
  form.diet_type = info.diet_type || 'omnivore'
  form.skill_level = info.skill_level || 'beginner'
  form.flavor_pref = info.flavor_pref || []
})

async function onChangeAvatar() {
  try {
    const res = await new Promise((resolve, reject) => {
      uni.chooseImage({ count: 1, sizeType: ['compressed'], success: resolve, fail: reject })
    })
    if (!res?.tempFilePaths?.[0]) return
    uni.showLoading({ title: '上传中...' })
    const result = await upload('/upload', res.tempFilePaths[0], 'file')
    form.avatar_url = result.url
    uni.hideLoading()
    uni.showToast({ title: '头像已更新', icon: 'success' })
  } catch {
    uni.hideLoading()
  }
}

function toggleFlavor(val) {
  const idx = form.flavor_pref.indexOf(val)
  if (idx === -1) {
    form.flavor_pref.push(val)
  } else {
    form.flavor_pref.splice(idx, 1)
  }
}

async function onSubmit() {
  if (!form.nickname.trim()) return uni.showToast({ title: '请输入昵称', icon: 'none' })
  saving.value = true
  try {
    await userStore.updateProfile({
      nickname: form.nickname.trim(),
      avatar_url: form.avatar_url,
      bio: form.bio.trim(),
    })
    await userStore.savePreferences({
      diet_type: form.diet_type,
      skill_level: form.skill_level,
      flavor_pref: form.flavor_pref,
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
.page-profile-edit {
  min-height: 100vh;
  background-color: $color-bg;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));

  &__avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 48rpx 0 40rpx;
    position: relative;
  }

  &__avatar {
    width: 160rpx;
    height: 160rpx;
    border-radius: 50%;
    border: 6rpx solid #FFFFFF;
    box-shadow: $card-shadow;
  }

  &__avatar-overlay {
    position: absolute;
    top: 48rpx;
    width: 160rpx;
    height: 160rpx;
    border-radius: 50%;
    background-color: rgba(0,0,0,0.4);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.2s;
  }

  &__avatar-section:active &__avatar-overlay {
    opacity: 1;
  }

  &__avatar-camera {
    font-size: 36rpx;
  }

  &__avatar-hint {
    font-size: 20rpx;
    color: #fff;
    margin-top: 4rpx;
  }

  &__form {
    padding: 0 $page-padding;
    display: flex;
    flex-direction: column;
    gap: 36rpx;
  }

  &__field {
    display: flex;
    flex-direction: column;
  }

  &__label {
    font-size: $font-sub;
    color: $color-text-3;
    margin-bottom: 16rpx;
  }

  &__input {
    height: 88rpx;
    padding: 0 24rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    font-size: $font-body;
    color: $color-text-1;
    box-shadow: $card-shadow;
  }

  &__textarea {
    width: 100%;
    height: 140rpx;
    padding: 20rpx 24rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    font-size: $font-body;
    color: $color-text-1;
    border: 2rpx solid transparent;
    box-sizing: border-box;
    box-shadow: $card-shadow;
  }

  &__options {
    display: flex;
    gap: 16rpx;
  }

  &__option {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8rpx;
    padding: 20rpx 8rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    border: 2rpx solid transparent;
    transition: all 0.2s;

    &--active {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.08);
    }
  }

  &__option-emoji {
    font-size: 32rpx;
  }

  &__option-label {
    font-size: $font-label;
    color: $color-text-2;
  }

  &__chips {
    display: flex;
    flex-wrap: wrap;
    gap: 16rpx;
  }

  &__chip {
    padding: 14rpx 28rpx;
    border-radius: 999rpx;
    background-color: $color-bg-card;
    border: 2rpx solid $color-border;
    font-size: $font-sub;
    color: $color-text-2;
    transition: all 0.2s;

    &--active {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.1);
      color: $color-primary;
    }
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
