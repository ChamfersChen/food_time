<template>
  <view v-if="visible" class="smoke-effect" :style="positionStyle">
    <text
      v-for="(p, idx) in particles"
      :key="idx"
      class="smoke-effect__puff"
      :style="p.style"
    >
      {{ p.char }}
    </text>
  </view>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  top: { type: Number, default: 0 },
  left: { type: Number, default: 0 },
  width: { type: Number, default: 200 },
  height: { type: Number, default: 80 },
  intensity: { type: Number, default: 6 },
})

const emit = defineEmits(['done'])

const particles = ref([])

const positionStyle = ref({})

const CHARS = ['💨', '✨', '☁️']

watch(() => props.visible, (v) => {
  if (v) {
    positionStyle.value = {
      top: props.top + 'px',
      left: props.left + 'px',
      width: props.width + 'px',
      height: props.height + 'px',
    }
    spawn()
    setTimeout(() => emit('done'), 1100)
  } else {
    particles.value = []
  }
})

function spawn() {
  const arr = []
  for (let i = 0; i < props.intensity; i++) {
    const drift = (Math.random() - 0.5) * props.width * 0.7
    const delay = Math.random() * 250
    const duration = 700 + Math.random() * 400
    const size = 28 + Math.random() * 18
    const char = CHARS[Math.floor(Math.random() * CHARS.length)]
    arr.push({
      char,
      style: {
        left: `calc(50% + ${drift}rpx)`,
        fontSize: size + 'rpx',
        animationDelay: delay + 'ms',
        animationDuration: duration + 'ms',
      },
    })
  }
  particles.value = arr
}
</script>

<style lang="scss" scoped>
.smoke-effect {
  position: fixed;
  z-index: 800;
  pointer-events: none;
  overflow: visible;

  &__puff {
    position: absolute;
    bottom: 30%;
    transform: translateX(-50%);
    opacity: 0;
    animation-name: puffRise;
    animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
    animation-fill-mode: forwards;
  }
}

@keyframes puffRise {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(0) scale(0.5) rotate(0deg);
  }
  20% {
    opacity: 0.9;
    transform: translateX(-50%) translateY(-20rpx) scale(1) rotate(10deg);
  }
  100% {
    opacity: 0;
    transform: translateX(-50%) translateY(-160rpx) scale(1.4) rotate(20deg);
  }
}
</style>
