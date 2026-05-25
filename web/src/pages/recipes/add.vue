<template>
  <view class="page-add-recipe">
    <scroll-view class="page-add-recipe__scroll" scroll-y>
      <view class="page-add-recipe__form">
        <view v-if="isImport" class="page-add-recipe__field">
          <text class="page-add-recipe__label">导入来源</text>
          <view class="page-add-recipe__platform-grid">
            <view
              v-for="p in PLATFORMS"
              :key="p.value"
              class="page-add-recipe__platform-item"
              :class="{ 'page-add-recipe__platform-item--active': form.import_source === p.value }"
              @tap="form.import_source = p.value"
            >
              <text class="page-add-recipe__platform-icon">{{ p.icon }}</text>
              <text class="page-add-recipe__platform-label">{{ p.label }}</text>
            </view>
          </view>
        </view>

        <view v-if="isImport" class="page-add-recipe__field">
          <text class="page-add-recipe__label">链接地址</text>
          <view class="page-add-recipe__input-wrap">
            <input
              class="page-add-recipe__input"
              v-model="form.import_url"
              placeholder="粘贴小红书/抖音等链接"
            />
          </view>
        </view>

        <view class="page-add-recipe__field">
          <text class="page-add-recipe__label">菜谱名称 <text class="page-add-recipe__required">*</text></text>
          <view class="page-add-recipe__input-wrap">
            <input
              class="page-add-recipe__input"
              v-model="form.name"
              placeholder="输入菜谱名称"
              :focus="!isImport"
            />
          </view>
        </view>

        <view class="page-add-recipe__field">
          <text class="page-add-recipe__label">封面图片</text>
          <view class="page-add-recipe__cover" @tap="chooseCover">
            <image
              v-if="form.cover_url"
              class="page-add-recipe__cover-img"
              :src="form.cover_url"
              mode="aspectFill"
            />
            <view v-else class="page-add-recipe__cover-placeholder">
              <text class="page-add-recipe__cover-icon">📷</text>
              <text class="page-add-recipe__cover-text">点击上传</text>
            </view>
          </view>
        </view>

        <view class="page-add-recipe__field">
          <text class="page-add-recipe__label">菜系</text>
          <view class="page-add-recipe__cuisine-grid">
            <view
              v-for="c in CUISINES"
              :key="c.value"
              class="page-add-recipe__cuisine-item"
              :class="{ 'page-add-recipe__cuisine-item--active': form.cuisine === c.value }"
              @tap="form.cuisine = c.value"
            >
              <text class="page-add-recipe__cuisine-icon">{{ c.icon }}</text>
              <text class="page-add-recipe__cuisine-label">{{ c.label }}</text>
            </view>
          </view>
        </view>

        <view class="page-add-recipe__row">
          <view class="page-add-recipe__field page-add-recipe__field--half">
            <text class="page-add-recipe__label">烹饪时间(分钟)</text>
            <view class="page-add-recipe__input-wrap">
              <input
                class="page-add-recipe__input"
                type="digit"
                v-model="form.cook_time"
                placeholder="如30"
              />
            </view>
          </view>

          <view class="page-add-recipe__field page-add-recipe__field--half">
            <text class="page-add-recipe__label">难度</text>
            <view class="page-add-recipe__difficulty-group">
              <view
                v-for="d in DIFFICULTIES"
                :key="d.value"
                class="page-add-recipe__difficulty-item"
                :class="{ 'page-add-recipe__difficulty-item--active': form.difficulty === d.value }"
                @tap="form.difficulty = d.value"
              >
                {{ d.label }}
              </view>
            </view>
          </view>
        </view>

        <view class="page-add-recipe__field">
          <text class="page-add-recipe__label">简介</text>
          <textarea
            class="page-add-recipe__textarea"
            v-model="form.description"
            placeholder="简单描述这道菜..."
            :maxlength="200"
          />
        </view>

        <view class="page-add-recipe__field">
          <view class="page-add-recipe__section-header">
            <text class="page-add-recipe__label">食材清单</text>
            <text class="page-add-recipe__add-link" @tap="addIngredient">＋ 添加</text>
          </view>
          <view
            v-for="(ing, idx) in form.ingredients"
            :key="idx"
            class="page-add-recipe__ingredient-row"
          >
            <view class="page-add-recipe__input-wrap page-add-recipe__input-wrap--ing-name">
              <input
                class="page-add-recipe__input"
                v-model="ing.name"
                placeholder="食材名称"
              />
            </view>
            <view class="page-add-recipe__input-wrap page-add-recipe__input-wrap--ing-amount">
              <input
                class="page-add-recipe__input"
                v-model="ing.amount"
                placeholder="用量"
              />
            </view>
            <view
              v-if="form.ingredients.length > 1"
              class="page-add-recipe__remove-btn"
              @tap="removeIngredient(idx)"
            >
              <text class="page-add-recipe__remove-icon">✕</text>
            </view>
          </view>
        </view>

        <view class="page-add-recipe__field">
          <view class="page-add-recipe__section-header">
            <text class="page-add-recipe__label">步骤</text>
            <text class="page-add-recipe__add-link" @tap="addStep">＋ 添加</text>
          </view>
          <view
            v-for="(step, idx) in form.steps"
            :key="idx"
            class="page-add-recipe__step-row"
          >
            <view class="page-add-recipe__step-num-wrap">
              <text class="page-add-recipe__step-num">{{ idx + 1 }}</text>
            </view>
            <view class="page-add-recipe__step-content">
              <textarea
                class="page-add-recipe__textarea page-add-recipe__textarea--step"
                v-model="form.steps[idx]"
                :placeholder="`描述第${idx + 1}步...`"
              />
            </view>
            <view
              v-if="form.steps.length > 1"
              class="page-add-recipe__remove-btn"
              @tap="removeStep(idx)"
            >
              <text class="page-add-recipe__remove-icon">✕</text>
            </view>
          </view>
        </view>
      </view>

      <view class="page-add-recipe__bottom-spacer" />
    </scroll-view>

    <view class="page-add-recipe__footer">
      <button class="page-add-recipe__submit btn-primary" :disabled="submitting" @tap="onSubmit">
        {{ submitting ? '保存中...' : '保存菜谱' }}
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useRecipesStore } from '@/stores/recipes'

const store = useRecipesStore()

const CUISINES = [
  { value: '家常', label: '家常', icon: '🍳' },
  { value: '粤菜', label: '粤菜', icon: '🥘' },
  { value: '西餐', label: '西餐', icon: '🍝' },
  { value: '川菜', label: '川菜', icon: '🌶️' },
  { value: '日料', label: '日料', icon: '🍣' },
  { value: '韩餐', label: '韩餐', icon: '🥩' },
  { value: '烘焙', label: '烘焙', icon: '🍰' },
  { value: '其他', label: '其他', icon: '🍽' },
]

const DIFFICULTIES = [
  { value: 'easy', label: '简单' },
  { value: 'medium', label: '中等' },
  { value: 'hard', label: '困难' },
]

const PLATFORMS = [
  { value: 'xiaohongshu', label: '小红书', icon: '📕' },
  { value: 'douyin', label: '抖音', icon: '🎵' },
  { value: 'other', label: '其他', icon: '🔗' },
]

const isImport = ref(false)
const submitting = ref(false)

const form = ref({
  name: '',
  cover_url: '',
  cuisine: '家常',
  cook_time: '',
  difficulty: 'easy',
  description: '',
  ingredients: [{ name: '', amount: '' }],
  steps: [''],
  import_source: 'xiaohongshu',
  import_url: '',
})

onLoad((options) => {
  if (options.mode === 'import') {
    isImport.value = true
  }
})

function chooseCover() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    success: (res) => {
      form.value.cover_url = res.tempFilePaths[0]
    },
  })
}

function addIngredient() {
  form.value.ingredients.push({ name: '', amount: '' })
}

function removeIngredient(idx) {
  form.value.ingredients.splice(idx, 1)
}

function addStep() {
  form.value.steps.push('')
}

function removeStep(idx) {
  form.value.steps.splice(idx, 1)
}

async function onSubmit() {
  if (!form.value.name.trim()) {
    return uni.showToast({ title: '请输入菜谱名称', icon: 'none' })
  }

  const payload = {
    name: form.value.name.trim(),
    cover_url: form.value.cover_url,
    cuisine: form.value.cuisine,
    cook_time: Number(form.value.cook_time) || 0,
    difficulty: form.value.difficulty,
    description: form.value.description.trim(),
    ingredients: form.value.ingredients.filter(i => i.name.trim()),
    steps: form.value.steps.filter(s => s.trim()),
  }

  if (isImport.value) {
    if (!form.value.import_url.trim()) {
      return uni.showToast({ title: '请输入导入链接', icon: 'none' })
    }
    payload.import_source = form.value.import_source
    payload.import_url = form.value.import_url.trim()
  }

  submitting.value = true
  try {
    if (isImport.value) {
      await store.importFromLink(payload)
    } else {
      await store.createRecipe(payload)
    }
    uni.showToast({ title: '创建成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch {
    // error toast handled by request interceptor
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.page-add-recipe {
  min-height: 100vh;
  background-color: $color-bg;
  display: flex;
  flex-direction: column;

  &__scroll {
    flex: 1;
  }

  &__form {
    padding: $page-padding;
    padding-top: calc(env(safe-area-inset-top) + 20rpx);
    display: flex;
    flex-direction: column;
    gap: 32rpx;
    padding-bottom: 40rpx;
  }

  &__field {
    &--half {
      flex: 1;
    }
  }

  &__row {
    display: flex;
    gap: 24rpx;
  }

  &__label {
    display: block;
    font-size: $font-sub;
    color: $color-text-3;
    margin-bottom: 12rpx;
  }

  &__required {
    color: $color-primary;
  }

  &__section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12rpx;

    .page-add-recipe__label {
      margin-bottom: 0;
    }
  }

  &__add-link {
    font-size: $font-sub;
    color: $color-primary;
    font-weight: $fw-medium;
  }

  &__input-wrap {
    display: flex;
    align-items: center;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    padding: 0 20rpx;
    height: 88rpx;
    box-shadow: $card-shadow;

    &--ing-name {
      flex: 1;
    }

    &--ing-amount {
      width: 200rpx;
    }
  }

  &__input {
    flex: 1;
    font-size: $font-body;
    color: $color-text-1;
    height: 88rpx;
  }

  &__cover {
    width: 100%;
    height: 320rpx;
    border-radius: 16rpx;
    overflow: hidden;
    background-color: $color-bg-card;
    box-shadow: $card-shadow;
  }

  &__cover-img {
    width: 100%;
    height: 100%;
  }

  &__cover-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    border: 2rpx dashed $color-border;
    border-radius: 16rpx;
  }

  &__cover-icon {
    font-size: 64rpx;
  }

  &__cover-text {
    font-size: $font-sub;
    color: $color-text-3;
  }

  &__platform-grid {
    display: flex;
    gap: 16rpx;
  }

  &__platform-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8rpx;
    padding: 20rpx 8rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    border: 2rpx solid transparent;
    box-shadow: $card-shadow;
    transition: all 0.2s;

    &--active {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.08);
    }
  }

  &__platform-icon {
    font-size: 36rpx;
  }

  &__platform-label {
    font-size: $font-label;
    color: $color-text-2;
  }

  &__cuisine-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16rpx;
  }

  &__cuisine-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6rpx;
    padding: 16rpx 8rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    border: 2rpx solid transparent;
    box-shadow: $card-shadow;
    transition: all 0.2s;

    &--active {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.08);
    }
  }

  &__cuisine-icon {
    font-size: 36rpx;
  }

  &__cuisine-label {
    font-size: $font-label;
    color: $color-text-2;
  }

  &__difficulty-group {
    display: flex;
    gap: 16rpx;
    height: 88rpx;
  }

  &__difficulty-item {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    border: 2rpx solid transparent;
    box-shadow: $card-shadow;
    font-size: $font-sub;
    color: $color-text-2;
    transition: all 0.2s;

    &--active {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.08);
      color: $color-primary;
      font-weight: $fw-medium;
    }
  }

  &__textarea {
    width: 100%;
    height: 140rpx;
    padding: 20rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    font-size: $font-body;
    color: $color-text-1;
    border: 2rpx solid $color-border;
    box-sizing: border-box;

    &--step {
      height: 120rpx;
    }
  }

  &__ingredient-row {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 16rpx;
  }

  &__step-row {
    display: flex;
    align-items: flex-start;
    gap: 16rpx;
    margin-bottom: 16rpx;
  }

  &__step-num-wrap {
    width: 48rpx;
    height: 48rpx;
    border-radius: 50%;
    background-color: $color-primary;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 8rpx;
  }

  &__step-num {
    font-size: $font-sub;
    font-weight: $fw-semibold;
    color: #FFFFFF;
    line-height: 1;
  }

  &__step-content {
    flex: 1;
    min-width: 0;
  }

  &__remove-btn {
    width: 48rpx;
    height: 48rpx;
    border-radius: 50%;
    background-color: $color-bg-section;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__remove-icon {
    font-size: 20rpx;
    color: $color-text-3;
  }

  &__bottom-spacer {
    height: 200rpx;
  }

  &__footer {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 20rpx $page-padding;
    padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
    background: linear-gradient(transparent, $color-bg 30%);
  }

  &__submit {
    width: 100%;
    height: 96rpx;
    line-height: 96rpx;
    border-radius: 999rpx;
  }
}
</style>
