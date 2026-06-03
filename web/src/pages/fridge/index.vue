<template>
  <view class="page-fridge">
    <view class="page-fridge__filters">
      <scroll-view scroll-x class="page-fridge__filters-scroll" show-scrollbar="false">
        <view
          v-for="zone in ZONES"
          :key="zone.value"
          class="page-fridge__pill page-fridge__pill--zone"
          :class="{ 'page-fridge__pill--zone-active': currentZone === zone.value }"
          @tap="switchZone(zone.value)"
        >
          <text class="page-fridge__pill-label">{{ zone.label }}</text>
        </view>

        <view class="page-fridge__divider" />

        <view
          v-for="cat in store.CATEGORIES"
          :key="cat.value"
          class="page-fridge__pill page-fridge__pill--cat"
          :class="{ 'page-fridge__pill--cat-active': currentCategory === cat.value }"
          @tap="switchCategory(cat.value)"
        >
          <text class="page-fridge__pill-icon">{{ cat.icon }}</text>
          <text class="page-fridge__pill-label">{{ cat.label }}</text>
        </view>
      </scroll-view>
    </view>

    <scroll-view class="page-fridge__list" scroll-y enable-back-to-top>
      <view class="page-fridge__list-inner">
        <view v-if="loading && filteredList.length === 0" class="page-fridge__loading">
          <text>加载中...</text>
        </view>

        <EmptyState
          v-else-if="filteredList.length === 0"
          type="fridge"
          :title="emptyTitle"
          :description="emptyDescription"
          button-text="添加食材"
          @action="goAdd"
        />

        <view v-else>
          <IngredientCard
            v-for="item in filteredList"
            :key="item.id"
            :item="item"
            @edit="goEdit"
            @consume="onConsume"
            @delete="onDelete"
          />
        </view>

        <view class="page-fridge__bottom-spacer" />
      </view>
    </scroll-view>

    <FabButton icon="＋" @tap="goAdd" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useIngredientsStore } from '@/stores/ingredients'

import IngredientCard from '@/components/IngredientCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import FabButton from '@/components/FabButton.vue'

const store = useIngredientsStore()

const ZONES = [
  { value: 'all', label: '全部' },
  { value: 'refrigeration', label: '冷藏' },
  { value: 'freezing', label: '冷冻' },
  { value: 'room_temp', label: '常温' },
]

const currentZone = ref('all')
const currentCategory = ref(store.currentFilter)
const loading = ref(false)

const filteredList = computed(() => store.filteredList)

const emptyTitle = computed(() => {
  if (currentCategory.value !== 'all') {
    const cat = store.CATEGORIES.find(c => c.value === currentCategory.value)
    return `冰箱没有${cat ? cat.label : '这类'}食物`
  }
  if (currentZone.value !== 'all') {
    const zone = ZONES.find(z => z.value === currentZone.value)
    return `冰箱没有${zone ? zone.label : '该区域'}的食物`
  }
  return '冰箱空空如也'
})

const emptyDescription = computed(() => {
  if (currentCategory.value !== 'all' || currentZone.value !== 'all') {
    return '换个分类看看吧'
  }
  return '快去添加一些食材吧'
})

function switchCategory(cat) {
  currentCategory.value = cat
  store.currentFilter = cat
  currentZone.value = 'all'
  store.currentZone = 'all'
}

function switchZone(zone) {
  currentZone.value = zone
  store.currentZone = zone
  currentCategory.value = 'all'
  store.currentFilter = 'all'
}

function goAdd() {
  uni.navigateTo({ url: '/pages/fridge/add' })
}

function goEdit(item) {
  uni.navigateTo({ url: `/pages/fridge/add?id=${item.id}` })
}

async function onConsume(item) {
  uni.showModal({
    title: '确认消耗',
    content: `确认将「${item.name}」标记为已消耗？`,
    success: async (res) => {
      if (res.confirm) {
        await store.markConsumed(item.id)
        uni.showToast({ title: '已消耗', icon: 'success' })
      }
    },
  })
}

function onDelete(item) {
  uni.showModal({
    title: '确认删除',
    content: `确认删除「${item.name}」？`,
    success: async (res) => {
      if (res.confirm) {
        await store.removeOne(item.id)
        uni.showToast({ title: '已删除', icon: 'success' })
      }
    },
  })
}

onMounted(() => {
  applyPendingFilter()
  loading.value = true
  store.fetchAll().finally(() => { loading.value = false })
})

onShow(() => {
  applyPendingFilter()
  store.fetchAll()
})

function applyPendingFilter() {
  if (store.pendingCategoryFilter) {
    currentCategory.value = store.pendingCategoryFilter
    store.currentFilter = store.pendingCategoryFilter
    store.pendingCategoryFilter = null
    currentZone.value = 'all'
    store.currentZone = 'all'
  }
}
</script>

<style lang="scss" scoped>
.page-fridge {
  min-height: 100vh;
  background-color: $color-bg;
  display: flex;
  flex-direction: column;

  &__filters {
    padding: 20rpx $page-padding 0;
  }

  &__filters-scroll {
    white-space: nowrap;

    &::-webkit-scrollbar {
      display: none;
    }
  }

  &__pill {
    display: inline-flex;
    align-items: center;
    gap: 8rpx;
    flex-shrink: 0;
    border-radius: 999rpx;
    font-weight: $fw-medium;
    border: 2rpx solid $color-border;
    transition: all 0.2s;
    vertical-align: middle;

    &:active {
      transform: scale(0.95);
    }

    &--zone {
      padding: 16rpx 32rpx;
      font-size: $font-sub;
      color: $color-text-3;
      background-color: $color-bg-card;
      margin-right: 12rpx;

      &-active {
        background-color: $color-primary;
        color: #FFFFFF;
        border-color: $color-primary;
        box-shadow: 0 4rpx 12rpx rgba($color-primary, 0.3);
      }
    }

    &--cat {
      padding: 14rpx 26rpx;
      font-size: $font-label;
      color: $color-text-3;
      background-color: $color-bg-card;
      margin-right: 12rpx;

      &-active {
        background-color: $color-primary-light;
        color: $color-primary;
        border-color: $color-primary;
      }
    }
  }

  &__pill-icon {
    font-size: 28rpx;
    line-height: 1;
  }

  &__pill-label {
    line-height: 1;
  }

  &__divider {
    display: inline-block;
    width: 4rpx;
    height: 32rpx;
    background-color: $color-border;
    border-radius: 2rpx;
    flex-shrink: 0;
    margin: 0 16rpx;
    vertical-align: middle;
  }

  &__list {
    flex: 1;
    margin-top: 20rpx;
  }

  &__list-inner {
    padding: 0 $page-padding;
  }

  &__loading {
    text-align: center;
    padding: 80rpx 0;
    color: $color-text-3;
    font-size: $font-sub;
  }

  &__bottom-spacer {
    height: 240rpx;
  }
}
</style>
