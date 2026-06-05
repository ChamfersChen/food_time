<template>
  <view class="page-log-add">
    <scroll-view class="page-log-add__scroll" :scroll-y="true">
      <view class="page-log-add__inner">
        <view class="photo-block">
          <view
            v-if="form.photo_urls.length"
            class="photo-block__swiper"
            @touchstart="onSwipeStart"
            @touchend="onSwipeEnd"
          >
            <view
              class="photo-block__track"
              :style="{ transform: `translateX(-${photoIndex * 100}%)` }"
            >
              <view
                v-for="(url, idx) in form.photo_urls"
                :key="idx"
                class="photo-block__slide"
              >
                <image
                  class="photo-block__img"
                  :src="url"
                  mode="aspectFill"
                  @longpress="onPhotoLongPress(idx)"
                />
              </view>
            </view>
            <view v-if="form.photo_urls.length > 1" class="photo-block__dots">
              <view
                v-for="(_, idx) in form.photo_urls"
                :key="idx"
                class="photo-block__dot"
                :class="{ 'photo-block__dot--active': idx === photoIndex }"
                @tap="photoIndex = idx"
              />
            </view>
            <view class="photo-block__counter">
              <text>{{ photoIndex + 1 }} / {{ form.photo_urls.length }}</text>
            </view>
          </view>
          <view v-else class="photo-block__empty" @tap="onAddPhoto">
            <text class="photo-block__empty-emoji">📸</text>
            <text class="photo-block__empty-text">添加成品照</text>
            <text class="photo-block__empty-hint">长按图片可删除</text>
          </view>

          <view v-if="form.photo_urls.length" class="photo-block__add" @tap="onAddPhoto">
            <text>＋</text>
          </view>
        </view>

        <view class="field-card">
          <text class="field-card__label">🍳 菜谱名称</text>
          <input
            class="field-card__input field-card__input--big"
            v-model="form.recipe_name"
            placeholder="今天做了什么呀～"
            :maxlength="40"
          />
        </view>

        <view class="field-card">
          <text class="field-card__label">🍱 餐次</text>
          <view class="meal-row">
            <view
              v-for="meal in MEALS"
              :key="meal.value"
              class="meal-pill"
              :class="{ 'meal-pill--active': form.meal_type === meal.value }"
              :style="form.meal_type === meal.value ? { backgroundColor: meal.color } : {}"
              @tap="form.meal_type = meal.value"
            >
              <text class="meal-pill__emoji">{{ meal.emoji }}</text>
              <text class="meal-pill__label">{{ meal.label }}</text>
            </view>
          </view>
        </view>

        <view class="field-card">
          <text class="field-card__label">🕒 烹饪时间</text>
          <view class="time-row">
            <picker
              mode="date"
              :value="form.cooked_date"
              :start="datePickerStart"
              :end="datePickerEnd"
              @change="onDateChange"
            >
              <view class="time-pill">
                <text class="time-pill__emoji">📅</text>
                <text class="time-pill__text">{{ form.cooked_date }}</text>
              </view>
            </picker>
            <picker
              mode="time"
              :value="form.cooked_time"
              @change="onTimeChange"
            >
              <view class="time-pill">
                <text class="time-pill__emoji">⏰</text>
                <text class="time-pill__text">{{ form.cooked_time }}</text>
              </view>
            </picker>
          </view>
        </view>

        <view class="field-card">
          <text class="field-card__label">⭐ 评分</text>
          <view class="star-row">
            <text
              v-for="i in 5"
              :key="i"
              class="star-row__star"
              :class="{ 'star-row__star--active': i <= form.rating }"
              @tap="form.rating = i"
            >★</text>
            <text class="star-row__label">{{ RATING_LABELS[form.rating - 1] || '' }}</text>
          </view>
        </view>

        <view class="field-card">
          <view class="field-card__header">
            <text class="field-card__label">🥕 消耗食材</text>
            <text class="field-card__count" v-if="form.consumed_ingredients.length">
              {{ form.consumed_ingredients.length }} 项
            </text>
          </view>
          <view
            v-if="form.consumed_ingredients.length"
            class="ing-chips"
          >
            <view
              v-for="(ing, idx) in form.consumed_ingredients"
              :key="ing.ingredient_id || ing.name"
              class="ing-chip"
            >
              <text class="ing-chip__text">{{ ing.name }} {{ ing.quantity }}{{ ing.unit }}</text>
              <text class="ing-chip__close" @tap.stop="removeIngredient(idx)">×</text>
            </view>
            <view class="ing-chip ing-chip--add" @tap="openIngredientPicker">
              <text>＋</text>
            </view>
          </view>
          <view v-else class="ing-empty" @tap="openIngredientPicker">
            <text class="ing-empty__emoji">🥬</text>
            <text class="ing-empty__text">选择用掉了哪些食材</text>
          </view>
        </view>

        <view v-if="isEdit" class="field-card field-card--comments">
          <view class="field-card__header">
            <text class="field-card__label">💬 评论 ({{ comments.length }})</text>
          </view>
          <view v-if="comments.length" class="comments">
            <view v-for="c in comments" :key="c.id" class="comment">
              <image
                class="comment__avatar"
                :src="c.avatar_url || 'https://picsum.photos/100/100'"
                mode="aspectFill"
              />
              <view class="comment__body">
                <view class="comment__header">
                  <text class="comment__name">{{ c.nickname || '匿名' }}</text>
                  <text class="comment__time">{{ formatDate(c.created_at, 'MM-dd HH:mm') }}</text>
                </view>
                <text class="comment__content">{{ c.content }}</text>
              </view>
            </view>
          </view>
          <view v-else class="comments__empty">
            <text>还没有评论，做第一个吧～ 💭</text>
          </view>
          <view class="comment-input">
            <input
              class="comment-input__field"
              v-model="newComment"
              placeholder="说点什么..."
              :maxlength="200"
              confirm-type="send"
              @confirm="onSendComment"
            />
            <view
              class="comment-input__send"
              :class="{ 'comment-input__send--disabled': !newComment.trim() }"
              @tap="onSendComment"
            >
              <text>发送</text>
            </view>
          </view>
        </view>

        <view class="bottom-spacer" />
      </view>
    </scroll-view>

    <view class="page-log-add__footer">
      <view v-if="isEdit" class="footer-btn footer-btn--danger" @tap="onDeleteLog">
        <text>🗑</text>
      </view>
      <view class="footer-btn footer-btn--primary" @tap="onSubmit" :class="{ 'footer-btn--loading': submitting }">
        <text v-if="!submitting">{{ isEdit ? '保存修改 ✨' : '记下来 ✨' }}</text>
        <text v-else>保存中…</text>
      </view>
    </view>

    <IngredientPickerSheet
      v-if="pickerVisible"
      :selected="form.consumed_ingredients"
      @close="pickerVisible = false"
      @confirm="onPickerConfirm"
    />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useCookingLogsStore } from '@/stores/cookingLogs'
import { useIngredientsStore } from '@/stores/ingredients'
import { formatDate } from '@/utils/date'
import { getLogComments, createComment } from '@/api/comments'
import { uploadImage } from '@/api/upload'
import IngredientPickerSheet from '@/components/IngredientPickerSheet.vue'

const store = useCookingLogsStore()
const ingStore = useIngredientsStore()

const MEALS = [
  { value: 'breakfast', emoji: '🌅', label: '早餐', color: '#FFE9C2' },
  { value: 'lunch', emoji: '☀️', label: '午餐', color: '#FFF1B8' },
  { value: 'afternoon_tea', emoji: '🧁', label: '下午茶', color: '#FFD6E0' },
  { value: 'dinner', emoji: '🌙', label: '晚餐', color: '#DCD0F4' },
  { value: 'supper', emoji: '🌟', label: '夜宵', color: '#C7E9F1' },
]

const RATING_LABELS = ['一般', '还行', '不错', '好吃', '超棒']

const isEdit = ref(false)
const editId = ref('')
const submitting = ref(false)

const currentYear = new Date().getFullYear()
const datePickerStart = `${currentYear - 5}-01-01`
const datePickerEnd = `${currentYear + 5}-12-31`

const form = ref({
  recipe_name: '',
  meal_type: getMealTypeByHour(new Date().getHours()),
  cooked_date: formatDate(new Date()),
  cooked_time: formatDate(new Date(), 'HH:mm'),
  rating: 5,
  photo_urls: [],
  consumed_ingredients: [],
})

const photoIndex = ref(0)
const comments = ref([])
const newComment = ref('')
const pickerVisible = ref(false)

function getMealTypeByHour(hour) {
  if (hour < 10) return 'breakfast'
  if (hour < 14) return 'lunch'
  if (hour < 17) return 'afternoon_tea'
  if (hour < 21) return 'dinner'
  return 'supper'
}

let touchStartX = 0
function onSwipeStart(e) {
  touchStartX = e.touches[0].clientX
}
function onSwipeEnd(e) {
  const dx = e.changedTouches[0].clientX - touchStartX
  if (Math.abs(dx) < 50) return
  if (dx < 0 && photoIndex.value < form.value.photo_urls.length - 1) {
    photoIndex.value += 1
  } else if (dx > 0 && photoIndex.value > 0) {
    photoIndex.value -= 1
  }
}

async function onAddPhoto() {
  try {
    const choose = await uni.chooseImage({ count: 9 - form.value.photo_urls.length })
    const paths = choose[1].tempFilePaths
    uni.showLoading({ title: '上传中...' })
    const urls = []
    for (const p of paths) {
      const res = await uploadImage(p)
      urls.push(res.url)
    }
    form.value.photo_urls = [...form.value.photo_urls, ...urls]
    photoIndex.value = form.value.photo_urls.length - 1
  } catch (e) {
    uni.showToast({ title: '上传失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

function onPhotoLongPress(idx) {
  uni.vibrateShort && uni.vibrateShort({ type: 'medium' })
  uni.showModal({
    title: '删除照片',
    content: '要删除这张照片吗？',
    confirmColor: '#E05A50',
    success: (res) => {
      if (res.confirm) {
        form.value.photo_urls.splice(idx, 1)
        if (photoIndex.value >= form.value.photo_urls.length) {
          photoIndex.value = Math.max(0, form.value.photo_urls.length - 1)
        }
      }
    },
  })
}

function onDateChange(e) {
  form.value.cooked_date = e.detail.value
}
function onTimeChange(e) {
  form.value.cooked_time = e.detail.value
}

function openIngredientPicker() {
  pickerVisible.value = true
}

function onPickerConfirm(selected) {
  form.value.consumed_ingredients = selected
  pickerVisible.value = false
}

function removeIngredient(idx) {
  form.value.consumed_ingredients.splice(idx, 1)
}

async function onSendComment() {
  const text = newComment.value.trim()
  if (!text || !editId.value) return
  try {
    const res = await createComment({ log_id: editId.value, content: text })
    comments.value.push(res)
    newComment.value = ''
  } catch {
    uni.showToast({ title: '评论失败', icon: 'none' })
  }
}

onLoad(async (options) => {
  await ingStore.fetchAll()
  if (options.id) {
    isEdit.value = true
    editId.value = options.id
    uni.setNavigationBarTitle({ title: '记录详情' })
    await loadLog(options.id)
  } else {
    uni.setNavigationBarTitle({ title: '记一餐 ✨' })
  }
})

async function loadLog(id) {
  try {
    const data = await store.fetchLog(id)
    const cookedAt = data.cooked_at ? new Date(data.cooked_at) : new Date()
    form.value = {
      recipe_name: data.recipe_name || '',
      meal_type: data.meal_type || getMealTypeByHour(cookedAt.getHours()),
      cooked_date: formatDate(cookedAt),
      cooked_time: formatDate(cookedAt, 'HH:mm'),
      rating: data.rating || 5,
      photo_urls: data.photo_urls || [],
      consumed_ingredients: data.consumed_ingredients || [],
    }
    photoIndex.value = 0
    try {
      comments.value = await getLogComments(id)
    } catch {
      comments.value = []
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

async function onSubmit() {
  if (!form.value.recipe_name.trim()) {
    uni.showToast({ title: '记得填一下菜名呀 🍽', icon: 'none' })
    return
  }
  submitting.value = true
  try {
    const cookedAt = new Date(`${form.value.cooked_date} ${form.value.cooked_time}:00`)
    const data = {
      recipe_name: form.value.recipe_name,
      meal_type: form.value.meal_type,
      cooked_at: cookedAt.toISOString(),
      rating: form.value.rating,
      photo_urls: form.value.photo_urls,
      consumed_ingredients: form.value.consumed_ingredients,
    }
    if (isEdit.value) {
      await store.updateLog(editId.value, data)
    } else {
      await store.createLog(data)
    }
    uni.showToast({ title: '已记录 ✨', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 600)
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

function onDeleteLog() {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这条记录吗？',
    confirmColor: '#E05A50',
    success: async (res) => {
      if (res.confirm) {
        try {
          await store.removeLog(editId.value)
          uni.showToast({ title: '已删除', icon: 'success' })
          setTimeout(() => uni.navigateBack(), 500)
        } catch {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.page-log-add {
  min-height: 100vh;
  background: linear-gradient(180deg, $color-bg 0%, #FFF8F0 100%);

  &__scroll {
    height: 100vh;
  }

  &__inner {
    padding: $page-padding;
    padding-bottom: 200rpx;
    box-sizing: border-box;
  }

  &__footer {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 100;
    display: flex;
    gap: 16rpx;
    padding: 20rpx $page-padding;
    padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20rpx);
  }
}

.photo-block {
  position: relative;
  width: 100%;
  height: 480rpx;
  border-radius: 32rpx;
  overflow: hidden;
  margin-bottom: 24rpx;
  background: $color-cream;
  box-shadow: 0 6rpx 24rpx rgba(0, 0, 0, 0.05);

  &__swiper {
    width: 100%;
    height: 100%;
    overflow: hidden;
    position: relative;
  }

  &__track {
    display: flex;
    height: 100%;
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }

  &__slide {
    width: 100%;
    flex-shrink: 0;
    height: 100%;
  }

  &__img {
    width: 100%;
    height: 100%;
  }

  &__dots {
    position: absolute;
    bottom: 24rpx;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 8rpx;
  }

  &__dot {
    width: 12rpx;
    height: 12rpx;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transition: all 0.2s;

    &--active {
      background: #fff;
      width: 32rpx;
      border-radius: 6rpx;
    }
  }

  &__counter {
    position: absolute;
    top: 24rpx;
    right: 24rpx;
    background: rgba(0, 0, 0, 0.45);
    color: #fff;
    font-size: $font-label;
    padding: 6rpx 14rpx;
    border-radius: 999rpx;
    backdrop-filter: blur(8rpx);
  }

  &__empty {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
  }

  &__empty-emoji {
    font-size: 96rpx;
  }

  &__empty-text {
    font-size: $font-body;
    color: $color-text-2;
    font-weight: $fw-medium;
  }

  &__empty-hint {
    font-size: $font-label;
    color: $color-text-3;
  }

  &__add {
    position: absolute;
    right: 20rpx;
    bottom: 20rpx;
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 44rpx;
    color: $color-primary;
    box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.1);
    font-weight: $fw-medium;
  }
}

.field-card {
  background: $color-bg-card;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16rpx;
  }

  &__label {
    display: block;
    font-size: $font-sub;
    color: $color-text-3;
    margin-bottom: 12rpx;
    font-weight: $fw-medium;
  }

  &__count {
    font-size: $font-label;
    color: $color-primary;
    background: $color-primary-light;
    padding: 4rpx 12rpx;
    border-radius: 999rpx;
  }

  &__input {
    width: 100%;
    font-size: $font-body;
    color: $color-text-1;
    background: transparent;
    box-sizing: border-box;
  }

  &__input--big {
    font-size: 36rpx;
    font-weight: $fw-semibold;
    padding: 8rpx 0;
  }
}

.meal-row {
  display: flex;
  gap: 12rpx;
}

.meal-pill {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  padding: 16rpx 0;
  background: $color-bg;
  border-radius: 20rpx;
  border: 2rpx solid transparent;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);

  &--active {
    border-color: $color-primary;
    transform: translateY(-2rpx);
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  }

  &__emoji {
    font-size: 36rpx;
  }

  &__label {
    font-size: $font-label;
    color: $color-text-2;
  }
}

.time-row {
  display: flex;
  gap: 16rpx;
}

.time-pill {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 24rpx;
  background: $color-bg;
  border-radius: 20rpx;

  &__emoji {
    font-size: 32rpx;
  }

  &__text {
    font-size: $font-body;
    color: $color-text-1;
    font-weight: $fw-medium;
  }
}

.star-row {
  display: flex;
  align-items: center;
  gap: 12rpx;

  &__star {
    font-size: 56rpx;
    color: $color-border;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);

    &--active {
      color: #F5A623;
      text-shadow: 0 2rpx 8rpx rgba(245, 166, 35, 0.4);
    }
  }

  &__label {
    font-size: $font-sub;
    color: $color-primary;
    font-weight: $fw-medium;
    margin-left: 12rpx;
  }
}

.ing-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.ing-chip {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 20rpx;
  background: $color-cream;
  border-radius: 999rpx;
  font-size: $font-sub;
  color: $color-text-2;
  transition: transform 0.2s;

  &:active {
    transform: scale(0.95);
  }

  &__text {
    font-size: $font-sub;
  }

  &__close {
    font-size: 32rpx;
    color: $color-text-3;
    line-height: 1;
    margin-left: 4rpx;
  }

  &--add {
    background: $color-primary-light;
    color: $color-primary;
    font-size: 36rpx;
    width: 56rpx;
    height: 56rpx;
    padding: 0;
    justify-content: center;
    border-radius: 50%;
  }
}

.ing-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 32rpx 0;

  &__emoji {
    font-size: 64rpx;
  }

  &__text {
    font-size: $font-sub;
    color: $color-text-3;
  }
}

.comments {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 20rpx;

  &__empty {
    text-align: center;
    padding: 24rpx 0;
    font-size: $font-sub;
    color: $color-text-3;
  }
}

.comment {
  display: flex;
  gap: 16rpx;
  padding: 16rpx;
  background: $color-bg;
  border-radius: 20rpx;

  &__avatar {
    width: 56rpx;
    height: 56rpx;
    border-radius: 50%;
    background: $color-bg-card;
    flex-shrink: 0;
  }

  &__body {
    flex: 1;
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 6rpx;
  }

  &__name {
    font-size: $font-sub;
    font-weight: $fw-medium;
    color: $color-text-1;
  }

  &__time {
    font-size: 20rpx;
    color: $color-text-3;
  }

  &__content {
    font-size: $font-body;
    color: $color-text-2;
    line-height: 1.6;
  }
}

.comment-input {
  display: flex;
  gap: 12rpx;
  margin-top: 8rpx;

  &__field {
    flex: 1;
    height: 72rpx;
    padding: 0 24rpx;
    background: $color-bg;
    border-radius: 999rpx;
    font-size: $font-body;
    color: $color-text-1;
    box-sizing: border-box;
  }

  &__send {
    height: 72rpx;
    padding: 0 28rpx;
    border-radius: 999rpx;
    background: $color-primary;
    color: #fff;
    font-size: $font-sub;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: $fw-medium;
    transition: all 0.2s;

    &--disabled {
      background: $color-border;
      color: $color-text-3;
    }
  }
}

.footer-btn {
  height: 96rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-body;
  font-weight: $fw-semibold;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.08);

  &--primary {
    flex: 1;
    background: linear-gradient(135deg, $color-primary, $color-sage);
    color: #fff;
  }

  &--danger {
    width: 96rpx;
    background: $color-bg-card;
    color: $color-danger;
    border: 2rpx solid $color-border;
    font-size: 36rpx;
  }

  &--loading {
    opacity: 0.6;
  }

  &:active {
    transform: scale(0.97);
  }
}

.bottom-spacer {
  height: 40rpx;
}
</style>
