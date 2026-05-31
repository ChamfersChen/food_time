<script setup>
import { onLaunch, onShow } from '@dcloudio/uni-app'
import { requestSubscribeMsg } from '@/api/auth'
import { post } from '@/api/request'
import { useUserStore } from '@/stores/user'

function getDeviceId() {
  const key = 'device_id'
  let id = uni.getStorageSync(key)
  if (!id) {
    id = 'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16)
    })
    uni.setStorageSync(key, id)
  }
  return id
}

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
      if (loginRes.errMsg !== 'login:ok') throw new Error(loginRes.errMsg)
      const res = await post('/auth/login', { code: loginRes.code })
      userStore.login(res.access_token, res.user)
      // #endif

      // #ifndef MP-WEIXIN
      const deviceId = getDeviceId()
      const res = await post('/auth/guest-login', { code: deviceId })
      userStore.login(res.access_token, res.user)
      // #endif
    } catch (e) {
      console.error('自动登录失败', e)
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