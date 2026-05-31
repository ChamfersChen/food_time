<template>
  <view class="page-log-add">
    <view class="page-log-add__form">
      <view class="page-log-add__field">
        <text class="page-log-add__label">菜谱名称</text>
        <view class="page-log-add__input-wrap">
          <input
            class="page-log-add__input"
            v-model="form.recipe_name"
            placeholder="输入菜谱名称"
            focus
          />
        </view>
      </view>

      <view class="page-log-add__field">
        <text class="page-log-add__label">餐次</text>
        <view class="page-log-add__meal-group">
          <view
            v-for="meal in MEALS"
            :key="meal.value"
            class="page-log-add__meal-item"
            :class="{ 'page-log-add__meal-item--active': form.meal_type === meal.value }"
            @tap="form.meal_type = meal.value"
          >
            <text class="page-log-add__meal-emoji">{{ meal.emoji }}</text>
            <text class="page-log-add__meal-label">{{ meal.label }}</text>
          </view>
        </view>
      </view>

      <view class="page-log-add__field">
        <text class="page-log-add__label">烹饪时间</text>
        <picker
          mode="date"
          :value="form.cooked_date"
          @change="onDateChange"
        >
          <view class="page-log-add__date-picker">
            <text v-if="form.cooked_date" class="page-log-add__date-text">
              {{ form.cooked_date }}
            </text>
            <text v-else class="page-log-add__date-placeholder">选择日期</text>
          </view>
        </picker>
      </view>

      <view class="page-log-add__field">
        <text class="page-log-add__label">评分</text>
        <view class="page-log-add__rating">
          <text
            v-for="i in 5"
            :key="i"
            class="page-log-add__star"
            :class="{ 'page-log-add__star--active': i <= form.rating }"
            @tap="form.rating = i"
          >★</text>
        </view>
      </view>

      <view class="page-log-add__field">
        <text class="page-log-add__label">备注（选填）</text>
        <textarea
          class="page-log-add__textarea"
          v-model="form.note"
          placeholder="记录烹饪心得..."
          :maxlength="200"
        />
      </view>

      <view v-if="form.photo_urls?.length" class="page-log-add__field">
        <text class="page-log-add__label">成品照片</text>
        <scroll-view class="page-log-add__photos" scroll-x enable-flex>
          <image
            v-for="(url, idx) in form.photo_urls"
            :key="idx"
            class="page-log-add__photo"
            :src="url"
            mode="aspectFill"
          />
        </scroll-view>
      </view>

      <view v-if="isEdit" class="page-log-add__field">
        <text class="page-log-add__label">评论（{{ comments.length }}）</text>
        <view v-if="comments.length" class="page-log-add__comments">
          <view v-for="c in comments" :key="c.id" class="page-log-add__comment">
            <image
              class="page-log-add__comment-avatar"
              :src="c.avatar_url || 'https://picsum.photos/100/100'"
              mode="aspectFill"
            />
            <view class="page-log-add__comment-body">
              <view class="page-log-add__comment-header">
                <text class="page-log-add__comment-name">{{ c.nickname || '匿名' }}</text>
                <text class="page-log-add__comment-time">{{ formatDate(c.created_at, 'MM-dd HH:mm') }}</text>
              </view>
              <text class="page-log-add__comment-content">{{ c.content }}</text>
            </view>
          </view>
        </view>
        <view v-else class="page-log-add__no-comments">
          <text class="page-log-add__no-comments-text">暂无评论</text>
        </view>
        <view class="page-log-add__comment-input-wrap">
          <input
            class="page-log-add__comment-input"
            v-model="newComment"
            placeholder="写一条评论..."
            :maxlength="200"
            confirm-type="send"
            @confirm="onSendComment"
          />
          <button class="page-log-add__comment-send" @tap="onSendComment" :disabled="!newComment.trim()">发送</button>
        </view>
      </view>
    </view>

    <view class="page-log-add__footer">
      <button v-if="isEdit" class="page-log-add__delete btn-outline" @tap="onDeleteLog">
        删除
      </button>
      <button class="page-log-add__submit btn-primary" @tap="onSubmit" :disabled="submitting">
        {{ isEdit ? '保存修改' : '保存记录' }}
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useCookingLogsStore } from '@/stores/cookingLogs'
import { formatDate } from '@/utils/date'
import { getLogComments, createComment } from '@/api/comments'

const store = useCookingLogsStore()

const MEALS = [
  { value: 'breakfast', emoji: '🌅', label: '早餐' },
  { value: 'lunch', emoji: '☀️', label: '午餐' },
  { value: 'dinner', emoji: '🌙', label: '晚餐' },
  { value: 'snack', emoji: '🍪', label: '加餐' },
]

const isEdit = ref(false)
const editId = ref('')
const submitting = ref(false)

const form = ref({
  recipe_name: '',
  meal_type: 'dinner',
  cooked_date: formatDate(new Date()),
  rating: 5,
  note: '',
  photo_urls: [],
})

const comments = ref([])
const newComment = ref('')

onLoad((options) => {
  if (options.id) {
    isEdit.value = true
    editId.value = options.id
    loadLog(options.id)
    uni.setNavigationBarTitle({ title: '编辑记录' })
  } else {
    uni.setNavigationBarTitle({ title: '添加烹饪记录' })
  }
})

async function loadLog(id) {
  try {
    const data = await store.fetchLog(id)
    form.value = {
      recipe_name: data.recipe_name || '',
      meal_type: data.meal_type || 'dinner',
      cooked_date: data.cooked_at ? formatDate(data.cooked_at) : formatDate(new Date()),
      rating: data.rating || 5,
      note: data.note || '',
      photo_urls: data.photo_urls || [],
    }
    try {
      comments.value = await getLogComments(id)
    } catch {
      comments.value = []
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
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

function onDateChange(e) {
  form.value.cooked_date = e.detail.value
}

async function onSubmit() {
  if (!form.value.recipe_name.trim()) {
    return uni.showToast({ title: '请输入菜谱名称', icon: 'none' })
  }

  submitting.value = true
  try {
    const data = {
      recipe_name: form.value.recipe_name,
      meal_type: form.value.meal_type,
      cooked_at: form.value.cooked_date,
      rating: form.value.rating,
      note: form.value.note,
    }
    if (isEdit.value) {
      await store.updateLog(editId.value, data)
    } else {
      await store.createLog(data)
    }
    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

async function onDeleteLog() {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这条烹饪记录吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await store.removeLog(editId.value)
          uni.showToast({ title: '删除成功', icon: 'success' })
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
  background-color: $color-bg;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));

  &__form {
    padding: 0 $page-padding;
    display: flex;
    flex-direction: column;
    gap: 32rpx;
  }

  &__field {
    display: flex;
    flex-direction: column;
  }

  &__label {
    font-size: $font-sub;
    color: $color-text-3;
    margin-bottom: 12rpx;
  }

  &__input-wrap {
    display: flex;
    align-items: center;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    padding: 0 20rpx;
    height: 88rpx;
    box-shadow: $card-shadow;
  }

  &__input {
    flex: 1;
    font-size: $font-body;
    color: $color-text-1;
    height: 88rpx;
  }

  &__meal-group {
    display: flex;
    gap: 16rpx;
  }

  &__meal-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8rpx;
    padding: 20rpx 0;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    border: 2rpx solid transparent;
    transition: all 0.2s;

    &--active {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.08);
    }
  }

  &__meal-emoji {
    font-size: 40rpx;
  }

  &__meal-label {
    font-size: $font-sub;
    color: $color-text-2;
  }

  &__date-picker {
    height: 88rpx;
    display: flex;
    align-items: center;
    padding: 0 20rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    box-shadow: $card-shadow;
  }

  &__date-text {
    font-size: $font-body;
    color: $color-text-1;
  }

  &__date-placeholder {
    font-size: $font-body;
    color: $color-text-3;
  }

  &__rating {
    display: flex;
    gap: 16rpx;
  }

  &__star {
    font-size: 48rpx;
    color: $color-border;
    transition: color 0.2s;

    &--active {
      color: #F5A623;
    }
  }

  &__textarea {
    width: 100%;
    height: 160rpx;
    padding: 20rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    font-size: $font-body;
    color: $color-text-1;
    border: 2rpx solid $color-border;
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
    background-color: $color-bg;
  }

  &__delete {
    width: 160rpx;
    height: 96rpx;
    line-height: 96rpx;
    border-radius: 999rpx;
    background-color: $color-bg-card;
    color: $color-danger;
    border: 2rpx solid $color-border;
    font-size: $font-sub;
    flex-shrink: 0;
  }

  &__submit {
    flex: 1;
    height: 96rpx;
    line-height: 96rpx;
    border-radius: 999rpx;
  }

  &__photos {
    display: flex;
    gap: 16rpx;
    white-space: nowrap;
  }

  &__photo {
    width: 200rpx;
    height: 200rpx;
    border-radius: 16rpx;
    background-color: $color-bg;
    flex-shrink: 0;
  }

  &__comments {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
  }

  &__comment {
    display: flex;
    gap: 16rpx;
  }

  &__comment-avatar {
    width: 56rpx;
    height: 56rpx;
    border-radius: 50%;
    background-color: $color-bg;
    flex-shrink: 0;
  }

  &__comment-body {
    flex: 1;
  }

  &__comment-header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 4rpx;
  }

  &__comment-name {
    font-size: $font-sub;
    font-weight: $fw-medium;
    color: $color-text-1;
  }

  &__comment-time {
    font-size: 20rpx;
    color: $color-text-3;
  }

  &__comment-content {
    font-size: $font-body;
    color: $color-text-2;
    line-height: 1.6;
  }

  &__no-comments {
    padding: 24rpx 0;
    text-align: center;
  }

  &__no-comments-text {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__comment-input-wrap {
    display: flex;
    gap: 16rpx;
    margin-top: 16rpx;
  }

  &__comment-input {
    flex: 1;
    height: 72rpx;
    padding: 0 20rpx;
    background-color: $color-bg;
    border-radius: 999rpx;
    font-size: $font-body;
    color: $color-text-1;
    border: 2rpx solid $color-border;
  }

  &__comment-send {
    height: 72rpx;
    line-height: 72rpx;
    padding: 0 28rpx;
    border-radius: 999rpx;
    background-color: $color-primary;
    color: #fff;
    font-size: $font-sub;
    border: none;
    flex-shrink: 0;
  }
}
</style>
