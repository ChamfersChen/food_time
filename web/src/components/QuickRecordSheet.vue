<template>
  <view class="quick-mask" @tap="onCancel">
    <view class="quick-sheet" @tap.stop>
      <view class="quick-sheet__handle" />
      <view class="quick-sheet__header">
        <view class="quick-sheet__title-block">
          <text class="quick-sheet__title">⚡ 快速记录</text>
          <text class="quick-sheet__sub">{{ getMealMeta(form.meal_type).label }} · {{ form.cooked_time }}</text>
        </view>
        <view class="quick-sheet__close" @tap="onCancel">
          <text>×</text>
        </view>
      </view>

      <view class="quick-sheet__photo" @tap="onPickPhoto">
        <image
          v-if="form.photo_url"
          class="quick-sheet__photo-img"
          :src="form.photo_url"
          mode="aspectFill"
        />
        <view v-else class="quick-sheet__photo-empty">
          <text class="quick-sheet__photo-emoji">📷</text>
          <text class="quick-sheet__photo-text">拍一张</text>
        </view>
      </view>

      <view class="quick-sheet__name-wrap">
        <text class="quick-sheet__name-emoji">🍳</text>
        <input
          class="quick-sheet__name"
          v-model="form.recipe_name"
          placeholder="今天吃了什么？"
          :maxlength="20"
          focus
        />
      </view>

      <view class="quick-sheet__meals">
        <view
          v-for="meal in MEALS"
          :key="meal.value"
          class="quick-meal"
          :class="{ 'quick-meal--active': form.meal_type === meal.value }"
          :style="form.meal_type === meal.value ? { backgroundColor: meal.color } : {}"
          @tap="form.meal_type = meal.value"
        >
          <text class="quick-meal__emoji">{{ meal.emoji }}</text>
          <text class="quick-meal__label">{{ meal.label }}</text>
        </view>
      </view>

      <view class="quick-sheet__rating">
        <text class="quick-sheet__rating-label">评分</text>
        <view class="quick-stars">
          <text
            v-for="i in 5"
            :key="i"
            class="quick-stars__star"
            :class="{ 'quick-stars__star--active': i <= form.rating }"
            @tap="form.rating = i"
          >★</text>
        </view>
      </view>

      <view class="quick-sheet__footer">
        <view class="quick-btn quick-btn--ghost" @tap="onCancel">取消</view>
        <view
          class="quick-btn quick-btn--primary"
          :class="{ 'quick-btn--loading': saving }"
          @tap="onSave"
        >
          <text v-if="!saving">记下来 ✨</text>
          <text v-else>保存中…</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useCookingLogsStore } from '@/stores/cookingLogs'
import { formatDate, getMealMeta, getMealTypeFromHour } from '@/utils/date'
import { uploadImage } from '@/api/upload'

const emit = defineEmits(['close', 'saved'])

const store = useCookingLogsStore()

const MEALS = [
  { value: 'breakfast', emoji: '🌅', label: '早餐', color: '#FFE9C2' },
  { value: 'lunch', emoji: '☀️', label: '午餐', color: '#FFF1B8' },
  { value: 'afternoon_tea', emoji: '🧁', label: '下午茶', color: '#FFD6E0' },
  { value: 'dinner', emoji: '🌙', label: '晚餐', color: '#DCD0F4' },
  { value: 'supper', emoji: '🌟', label: '夜宵', color: '#C7E9F1' },
]

const form = ref({
  recipe_name: '',
  meal_type: getMealTypeFromHour(new Date().getHours()),
  cooked_time: formatDate(new Date(), 'HH:mm'),
  rating: 5,
  photo_url: '',
})

const saving = ref(false)
const uploading = ref(false)

async function onPickPhoto() {
  try {
    const choose = await uni.chooseImage({ count: 1, sourceType: ['camera', 'album'] })
    const path = choose[1].tempFilePaths[0]
    uploading.value = true
    const res = await uploadImage(path)
    form.value.photo_url = res.url
  } catch (e) {
    uni.showToast({ title: '上传失败', icon: 'none' })
  } finally {
    uploading.value = false
  }
}

function onCancel() {
  if (saving.value) return
  emit('close')
}

async function onSave() {
  if (!form.value.recipe_name.trim()) {
    uni.showToast({ title: '说一道菜名吧 🍽', icon: 'none' })
    return
  }
  saving.value = true
  try {
    const now = new Date()
    const data = {
      recipe_name: form.value.recipe_name,
      meal_type: form.value.meal_type,
      cooked_at: now.toISOString(),
      rating: form.value.rating,
      photo_urls: form.value.photo_url ? [form.value.photo_url] : [],
      consumed_ingredients: [],
    }
    const created = await store.createLog(data)
    uni.showToast({ title: '已记录 ✨', icon: 'success' })
    emit('saved', created)
    setTimeout(() => emit('close'), 400)
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.quick-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 200;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.2s ease;
}

.quick-sheet {
  width: 100%;
  background: $color-bg;
  border-radius: 36rpx 36rpx 0 0;
  padding: 8rpx $page-padding 0;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);

  &__handle {
    width: 80rpx;
    height: 8rpx;
    border-radius: 4rpx;
    background: $color-border;
    margin: 16rpx auto 20rpx;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24rpx;
  }

  &__title-block {
    display: flex;
    flex-direction: column;
  }

  &__title {
    font-size: 36rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
  }

  &__sub {
    font-size: $font-sub;
    color: $color-text-3;
    margin-top: 4rpx;
  }

  &__close {
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
    background: $color-bg-card;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40rpx;
    color: $color-text-2;
    line-height: 1;
  }

  &__photo {
    width: 100%;
    height: 360rpx;
    border-radius: 28rpx;
    background: $color-cream;
    overflow: hidden;
    margin-bottom: 20rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
  }

  &__photo-img {
    width: 100%;
    height: 100%;
  }

  &__photo-empty {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
  }

  &__photo-emoji {
    font-size: 80rpx;
  }

  &__photo-text {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__name-wrap {
    display: flex;
    align-items: center;
    gap: 12rpx;
    padding: 20rpx 24rpx;
    background: $color-bg-card;
    border-radius: 24rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
  }

  &__name-emoji {
    font-size: 32rpx;
  }

  &__name {
    flex: 1;
    font-size: 30rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
  }

  &__meals {
    display: flex;
    gap: 12rpx;
    margin-bottom: 20rpx;
  }

  &__rating {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20rpx 24rpx;
    background: $color-bg-card;
    border-radius: 24rpx;
    margin-bottom: 24rpx;
  }

  &__rating-label {
    font-size: $font-sub;
    color: $color-text-3;
    font-weight: $fw-medium;
  }

  &__footer {
    display: flex;
    gap: 16rpx;
  }
}

.quick-meal {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  padding: 16rpx 0;
  background: $color-bg-card;
  border-radius: 20rpx;
  border: 2rpx solid transparent;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);

  &--active {
    border-color: $color-primary;
    transform: translateY(-2rpx);
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  }

  &__emoji {
    font-size: 32rpx;
  }

  &__label {
    font-size: $font-label;
    color: $color-text-2;
  }
}

.quick-stars {
  display: flex;
  gap: 8rpx;

  &__star {
    font-size: 44rpx;
    color: $color-border;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);

    &--active {
      color: #F5A623;
      text-shadow: 0 2rpx 8rpx rgba(245, 166, 35, 0.4);
    }
  }
}

.quick-btn {
  flex: 1;
  height: 96rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-body;
  font-weight: $fw-semibold;
  transition: transform 0.2s;

  &--ghost {
    background: $color-bg-card;
    color: $color-text-2;
    border: 2rpx solid $color-border;
    flex: 0 0 200rpx;
  }

  &--primary {
    background: linear-gradient(135deg, $color-primary, $color-sage);
    color: #fff;
    box-shadow: 0 6rpx 20rpx rgba($color-primary, 0.3);
  }

  &--loading {
    opacity: 0.6;
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
