<template>
  <view class="page-add">
    <view class="page-add__form">
      <view class="page-add__field">
        <text class="page-add__label">食材名称</text>
        <view class="page-add__input-wrap">
          <input
            class="page-add__input"
            v-model="form.name"
            placeholder="输入食材名称"
            focus
          />
        </view>
      </view>

      <view class="page-add__field">
        <text class="page-add__label">分类</text>
        <view class="page-add__category-grid">
          <view
            v-for="cat in CATEGORIES"
            :key="cat.value"
            class="page-add__category-item"
            :class="{ 'page-add__category-item--active': form.category === cat.value }"
            @tap="form.category = cat.value"
          >
            <text class="page-add__category-icon">{{ cat.icon }}</text>
            <text class="page-add__category-label">{{ cat.label }}</text>
          </view>
        </view>
      </view>

      <view class="page-add__field">
        <text class="page-add__label">存放区域</text>
        <view class="page-add__zone-group">
          <view
            v-for="zone in ZONES"
            :key="zone.value"
            class="page-add__zone-item"
            :class="{ 'page-add__zone-item--active': form.zone === zone.value }"
            @tap="form.zone = zone.value"
          >
            <text>{{ zone.label }}</text>
          </view>
        </view>
      </view>

      <view class="page-add__row">
        <view class="page-add__field page-add__field--flex">
          <text class="page-add__label">数量</text>
          <view class="page-add__stepper">
            <view class="page-add__stepper-btn" @tap="changeQuantity(-1)">－</view>
            <input
              class="page-add__stepper-input"
              type="digit"
              v-model="form.quantity"
            />
            <view class="page-add__stepper-btn" @tap="changeQuantity(1)">＋</view>
          </view>
        </view>

        <view class="page-add__field page-add__field--flex">
          <text class="page-add__label">单位</text>
          <view class="page-add__unit-selector" @tap="showUnitPicker = true">
            <text>{{ form.unit || '请选择' }}</text>
            <text class="page-add__unit-arrow">▸</text>
          </view>
        </view>
      </view>

      <view class="page-add__field">
        <text class="page-add__label">过期日期</text>
        <picker
          mode="date"
          :value="form.expire_date"
          @change="onDateChange"
        >
          <view class="page-add__date-picker">
            <text v-if="form.expire_date" class="page-add__date-text">
              {{ form.expire_date }}
            </text>
            <text v-else class="page-add__date-placeholder">选择过期日期</text>
          </view>
        </picker>
      </view>

      <view class="page-add__field">
        <text class="page-add__label">备注（选填）</text>
        <textarea
          class="page-add__textarea"
          v-model="form.note"
          placeholder="如：已开封、解冻中..."
          :maxlength="100"
        />
      </view>
    </view>

    <view class="page-add__footer">
      <button v-if="isEdit" class="page-add__delete" @tap="onDeleteIngredient">删除</button>
      <button class="page-add__submit btn-primary" @tap="onSubmit" :disabled="submitting">
        {{ isEdit ? '保存修改' : '保存食材' }}
      </button>
    </view>

    <view v-if="showUnitPicker" class="page-add__picker-mask" @tap="showUnitPicker = false">
      <view class="page-add__picker" @tap.stop>
        <text class="page-add__picker-title">选择单位</text>
        <view class="page-add__picker-grid">
          <view
            v-for="unit in UNITS"
            :key="unit"
            class="page-add__picker-item"
            :class="{ 'page-add__picker-item--active': form.unit === unit }"
            @tap="selectUnit(unit)"
          >
            {{ unit }}
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useIngredientsStore } from '@/stores/ingredients'

const store = useIngredientsStore()
const CATEGORIES = store.CATEGORIES
const ZONES = store.ZONES
const UNITS = store.UNITS

const isEdit = ref(false)
const editId = ref('')
const submitting = ref(false)
const showUnitPicker = ref(false)

const form = ref({
  name: '',
  category: 'vegetables',
  zone: 'refrigeration',
  quantity: 1,
  unit: '个',
  expire_date: '',
  note: '',
})

onLoad((options) => {
  if (options.id) {
    isEdit.value = true
    editId.value = options.id
    loadIngredient(options.id)
  }
})

async function loadIngredient(id) {
  try {
    const data = await store.fetchOne(id)
    form.value = {
      name: data.name,
      category: data.category,
      zone: data.zone,
      quantity: data.quantity,
      unit: data.unit,
      expire_date: data.expire_date ? data.expire_date.split('T')[0] : '',
      note: data.note || '',
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

function changeQuantity(delta) {
  const val = Number(form.value.quantity) + delta
  if (val >= 0.1) {
    form.value.quantity = Math.round(val * 100) / 100
  }
}

function selectUnit(unit) {
  form.value.unit = unit
  showUnitPicker.value = false
}

function onDateChange(e) {
  form.value.expire_date = e.detail.value
}

async function onDeleteIngredient() {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除「' + form.value.name + '」吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await store.removeOne(editId.value)
          uni.showToast({ title: '删除成功', icon: 'success' })
          setTimeout(() => uni.navigateBack(), 500)
        } catch {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    },
  })
}

async function onSubmit() {
  if (!form.value.name.trim()) {
    return uni.showToast({ title: '请输入食材名称', icon: 'none' })
  }
  if (!form.value.expire_date) {
    return uni.showToast({ title: '请选择过期日期', icon: 'none' })
  }

  submitting.value = true
  try {
    const data = { ...form.value, quantity: Number(form.value.quantity) }
    if (isEdit.value) {
      await store.editOne(editId.value, data)
      uni.showToast({ title: '修改成功', icon: 'success' })
    } else {
      await store.addOne(data)
      uni.showToast({ title: '添加成功', icon: 'success' })
    }
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.page-add {
  min-height: 100vh;
  background-color: $color-bg;
  padding: $page-padding;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));

  &__form {
    display: flex;
    flex-direction: column;
    gap: 32rpx;
  }

  &__field {
    &--flex {
      flex: 1;
    }
  }

  &__label {
    display: block;
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

  &__category-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16rpx;
  }

  &__category-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6rpx;
    padding: 16rpx 8rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    border: 2rpx solid transparent;
    transition: all 0.2s;

    &--active {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.08);
    }
  }

  &__category-icon {
    font-size: 36rpx;
  }

  &__category-label {
    font-size: $font-label;
    color: $color-text-2;
  }

  &__zone-group {
    display: flex;
    gap: 16rpx;
  }

  &__zone-item {
    flex: 1;
    text-align: center;
    padding: 20rpx 0;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    font-size: $font-sub;
    color: $color-text-2;
    border: 2rpx solid transparent;
    transition: all 0.2s;

    &--active {
      border-color: $color-primary;
      background-color: rgba($color-primary, 0.08);
      color: $color-primary;
      font-weight: $fw-medium;
    }
  }

  &__row {
    display: flex;
    gap: 24rpx;
  }

  &__stepper {
    display: flex;
    align-items: center;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    overflow: hidden;
    box-shadow: $card-shadow;
    flex: 1;
  }

  &__stepper-btn {
    width: 80rpx;
    height: 80rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34rpx;
    color: $color-text-2;
    background-color: $color-bg-card;

    &:active {
      background-color: $color-cream;
    }
  }

  &__stepper-input {
    flex: 1;
    height: 80rpx;
    text-align: center;
    font-size: $font-body;
    color: $color-text-1;
    border-left: 2rpx solid $color-border;
    border-right: 2rpx solid $color-border;
    min-width: 0;
  }

  &__unit-selector {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 80rpx;
    padding: 0 24rpx;
    background-color: $color-bg-card;
    border-radius: 16rpx;
    box-shadow: $card-shadow;
    font-size: $font-body;
    color: $color-text-1;
    flex: 1;
  }

  &__unit-arrow {
    color: $color-text-3;
    margin-left: 8rpx;
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

  &__picker-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    display: flex;
    align-items: flex-end;
  }

  &__picker {
    width: 100%;
    background-color: $color-bg-card;
    border-radius: 32rpx 32rpx 0 0;
    padding: 40rpx $page-padding;
    padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
  }

  &__picker-title {
    display: block;
    font-size: $font-title;
    font-weight: $fw-semibold;
    color: $color-text-1;
    margin-bottom: 32rpx;
  }

  &__picker-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16rpx;
  }

  &__picker-item {
    text-align: center;
    padding: 16rpx 0;
    border-radius: 16rpx;
    background-color: $color-bg;
    font-size: $font-sub;
    color: $color-text-2;
    border: 2rpx solid transparent;

    &--active {
      border-color: $color-primary;
      color: $color-primary;
      background-color: rgba($color-primary, 0.08);
    }
  }
}
</style>