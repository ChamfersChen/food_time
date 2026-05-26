<template>
  <view class="cook-done-modal">
    <view class="cook-done-modal__mask" @tap="$emit('close')" />
    <view class="cook-done-modal__content">
      <text class="cook-done-modal__title">烹饪完成 🎉</text>

      <view class="cook-done-modal__section">
        <text class="cook-done-modal__label">给这道菜打个分</text>
        <view class="cook-done-modal__rate">
          <view
            v-for="star in 5"
            :key="star"
            class="cook-done-modal__star"
            :class="{ 'cook-done-modal__star--active': rating >= star }"
            @tap="rating = star"
          >
            ★
          </view>
        </view>
      </view>

      <view class="cook-done-modal__section">
        <text class="cook-done-modal__label">此刻的心情</text>
        <view class="cook-done-modal__moods">
          <view
            v-for="mood in moods"
            :key="mood.value"
            class="cook-done-modal__mood"
            :class="{ 'cook-done-modal__mood--active': selectedMood === mood.value }"
            @tap="selectedMood = mood.value"
          >
            <text class="cook-done-modal__mood-emoji">{{ mood.emoji }}</text>
            <text class="cook-done-modal__mood-label">{{ mood.label }}</text>
          </view>
        </view>
      </view>

      <view class="cook-done-modal__section">
        <text class="cook-done-modal__label">烹饪感悟</text>
        <textarea
          class="cook-done-modal__textarea"
          v-model="note"
          placeholder="今天在厨房里发现了什么有趣的小事？"
          :maxlength="200"
        />
      </view>

      <view class="cook-done-modal__section">
        <text class="cook-done-modal__label">上传成品照片</text>
        <view class="cook-done-modal__photos">
          <view
            v-for="(url, idx) in photoUrls"
            :key="idx"
            class="cook-done-modal__photo-item"
          >
            <image class="cook-done-modal__photo-img" :src="url" mode="aspectFill" />
            <view class="cook-done-modal__photo-del" @tap="removePhoto(idx)">
              <text class="cook-done-modal__photo-del-icon">×</text>
            </view>
          </view>
          <view v-if="photoUrls.length < 6" class="cook-done-modal__upload" @tap="choosePhotos">
            <text class="cook-done-modal__upload-icon">＋</text>
          </view>
        </view>
      </view>

      <button class="cook-done-modal__btn btn-primary" @tap="onSubmit">
        确认完成
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { upload } from '@/api/request'

const MOODS = [
  { value: 'satisfied', emoji: '😊', label: '满足' },
  { value: 'normal', emoji: '😐', label: '一般' },
  { value: 'failed', emoji: '😅', label: '翻车' },
]

const emit = defineEmits(['close', 'submit'])

const rating = ref(0)
const selectedMood = ref('')
const note = ref('')
const photoUrls = ref([])
const moods = MOODS
const uploading = ref(false)

async function choosePhotos() {
  const res = await new Promise((resolve, reject) => {
    uni.chooseImage({ count: 6 - photoUrls.value.length, sizeType: ['compressed'], success: resolve, fail: reject })
  })
  if (!res?.tempFilePaths?.length) return
  uploading.value = true
  uni.showLoading({ title: '上传中...' })
  try {
    for (const tempFile of res.tempFilePaths) {
      const result = await upload('/upload', tempFile, 'file')
      photoUrls.value.push(result.url)
    }
  } catch {
    uni.showToast({ title: '图片上传失败', icon: 'none' })
  } finally {
    uni.hideLoading()
    uploading.value = false
  }
}

function removePhoto(idx) {
  photoUrls.value.splice(idx, 1)
}

function onSubmit() {
  if (!rating.value) return uni.showToast({ title: '请给这道菜打个分', icon: 'none' })
  emit('submit', {
    rating: rating.value,
    mood: selectedMood.value,
    note: note.value,
    photo_urls: photoUrls.value,
  })
}
</script>

<style lang="scss" scoped>
.cook-done-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: flex-end;

  &__mask {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
  }

  &__content {
    position: relative;
    width: 100%;
    background-color: $color-bg-card;
    border-radius: 32rpx 32rpx 0 0;
    padding: 40rpx $page-padding;
    padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
    z-index: 1;
    max-height: 80vh;
    overflow-y: auto;
  }

  &__title {
    display: block;
    font-size: 40rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
    text-align: center;
    margin-bottom: 40rpx;
  }

  &__section {
    margin-bottom: 32rpx;
  }

  &__label {
    display: block;
    font-size: $font-sub;
    color: $color-text-3;
    margin-bottom: 16rpx;
  }

  &__rate {
    display: flex;
    gap: 16rpx;
  }

  &__star {
    font-size: 48rpx;
    color: $color-border;
    transition: color 0.2s;
    cursor: pointer;

    &--active {
      color: #FFB800;
    }
  }

  &__moods {
    display: flex;
    gap: 20rpx;
  }

  &__mood {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 12rpx 24rpx;
    border-radius: 999rpx;
    border: 2rpx solid $color-border;
    background-color: $color-bg;
    transition: all 0.2s;

    &:active,
    &--active {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.1);
    }
  }

  &__mood-emoji {
    font-size: 32rpx;
  }

  &__mood-label {
    font-size: $font-sub;
    color: $color-text-2;
  }

  &__textarea {
    width: 100%;
    height: 160rpx;
    padding: 20rpx;
    background-color: $color-bg;
    border-radius: 16rpx;
    font-size: $font-body;
    color: $color-text-1;
    border: 1rpx solid $color-border;
  }

  &__photos {
    display: flex;
    flex-wrap: wrap;
    gap: 16rpx;
  }

  &__photo-item {
    position: relative;
    width: 160rpx;
    height: 160rpx;
    border-radius: 16rpx;
    overflow: hidden;
  }

  &__photo-img {
    width: 100%;
    height: 100%;
  }

  &__photo-del {
    position: absolute;
    top: 4rpx;
    right: 4rpx;
    width: 36rpx;
    height: 36rpx;
    border-radius: 50%;
    background-color: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__photo-del-icon {
    font-size: 24rpx;
    color: #fff;
    line-height: 1;
  }

  &__upload {
    width: 160rpx;
    height: 160rpx;
    border-radius: 16rpx;
    border: 2rpx dashed $color-border;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: $color-bg;
    overflow: hidden;
    flex-shrink: 0;
  }

  &__upload-icon {
    font-size: 48rpx;
    color: $color-text-3;
  }

  &__btn {
    width: 100%;
    margin-top: 16rpx;
  }
}
</style>