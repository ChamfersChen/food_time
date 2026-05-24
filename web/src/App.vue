<script setup>
import { onLaunch, onShow } from '@dcloudio/uni-app'
import { requestSubscribeMsg } from '@/api/auth'
import { post } from '@/api/request'
import { useUserStore } from '@/stores/user'

onLaunch(async () => {
  console.log('食光机 App Launch')
  const userStore = useUserStore()

  if (!userStore.isLoggedIn) {
    try {
      // #ifdef MP-WEIXIN
      const loginRes = await new Promise((resolve, reject) => {
        uni.login({
          success: resolve,
          fail: reject,
        })
      })
      if (loginRes.code) {
        const res = await post('/auth/login', { code: loginRes.code })
        userStore.login(res.access_token, res.user)
      }
      // #endif

      // #ifndef MP-WEIXIN
      const res = await post('/auth/dev-login')
      userStore.login(res.access_token, res.user)
      // #endif
    } catch (e) {
      console.error('自动登录失败，尝试开发模式登录', e)
      // #ifdef MP-WEIXIN
      try {
        const res = await post('/auth/dev-login')
        userStore.login(res.access_token, res.user)
      } catch (e2) {
        console.error('开发模式登录也失败', e2)
      }
      // #endif
    }
  }
})

onShow(() => {
  // #ifdef MP-WEIXIN
  requestSubscribeMsg()
  // #endif
})
</script>

<style lang="scss">
@import '@/styles/global.scss';
</style>