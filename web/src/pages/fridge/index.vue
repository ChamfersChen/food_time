<template>
  <view class="page-fridge">
    <view class="page-fridge__header">
      <text class="page-fridge__title">食材管理</text>
      <text class="page-fridge__count">共 {{ notConsumed.length }} 项</text>
    </view>

    <view class="page-fridge__search">
      <view class="page-fridge__search-inner">
        <text class="page-fridge__search-icon">🔍</text>
        <input
          class="page-fridge__search-input"
          v-model="searchKeyword"
          placeholder="搜索食材名称或标签..."
          placeholder-class="page-fridge__search-placeholder"
          confirm-type="search"
          @confirm="onSearch"
        />
      </view>
    </view>

    <view class="page-fridge__zones">
      <view
        v-for="zone in ZONES"
        :key="zone.value"
        class="page-fridge__zone-tab"
        :class="{ 'page-fridge__zone-tab--active': currentZone === zone.value }"
        @tap="switchZone(zone.value)"
      >
        <text class="page-fridge__zone-label">{{ zone.label }}</text>
      </view>
    </view>

    <scroll-view class="page-fridge__list" scroll-y enable-back-to-top>
      <view class="page-fridge__list-inner">
        <view v-if="loading && filteredList.length === 0" class="page-fridge__loading">
          <text>加载中...</text>
        </view>

        <EmptyState
          v-else-if="filteredList.length === 0"
          type="fridge"
          title="冰箱空空如也"
          description="快去添加一些食材吧"
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
const searchKeyword = ref('')
const loading = ref(false)

const notConsumed = computed(() => store.notConsumed)
const filteredList = computed(() => store.filteredList)

function switchZone(zone) {
  currentZone.value = zone
  store.currentZone = zone
}

function onSearch() {
  store.searchKeyword = searchKeyword.value
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
  loading.value = true
  store.fetchAll().finally(() => { loading.value = false })
})

onShow(() => {
  store.fetchAll()
})
</script>

<style lang="scss" scoped>
.page-fridge {
  min-height: 100vh;
  background-color: $color-cream;
  display: flex;
  flex-direction: column;

  &__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding: $page-padding;
    padding-top: calc(env(safe-area-inset-top) + 20rpx);
  }

  &__title {
    font-size: 44rpx;
    font-weight: $fw-semibold;
    color: $color-text-1;
  }

  &__count {
    font-size: $font-sub;
    color: $color-text-3;
    margin-bottom: 4rpx;
  }

  &__search {
    padding: 16rpx $page-padding;
  }

  &__search-inner {
    display: flex;
    align-items: center;
    height: 80rpx;
    background-color: $color-bg-card;
    border-radius: 999rpx;
    padding: 0 28rpx;
    box-shadow: $card-shadow;
  }

  &__search-icon {
    font-size: 28rpx;
    margin-right: 16rpx;
  }

  &__search-input {
    flex: 1;
    font-size: $font-body;
    color: $color-text-1;
    background: transparent;
  }

  &__search-placeholder {
    color: $color-text-3;
    font-size: $font-body;
  }

  &__zones {
    display: flex;
    gap: 16rpx;
    padding: 0 $page-padding;
    margin-bottom: 24rpx;
    overflow-x: auto;
    white-space: nowrap;

    &::-webkit-scrollbar {
      display: none;
    }
  }

  &__zone-tab {
    flex-shrink: 0;
    padding: 14rpx 32rpx;
    border-radius: 999rpx;
    font-size: $font-sub;
    font-weight: $fw-medium;
    color: $color-text-3;
    background-color: $color-bg-card;
    border: 2rpx solid $color-border;
    transition: all 0.2s;

    &:active {
      transform: scale(0.95);
    }

    &--active {
      background-color: $color-primary;
      color: #FFFFFF;
      border-color: $color-primary;
      box-shadow: 0 4rpx 12rpx rgba($color-primary, 0.3);
    }
  }

  &__zone-label {
    line-height: 1;
  }

  &__list {
    flex: 1;
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