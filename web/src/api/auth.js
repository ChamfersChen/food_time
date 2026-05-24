/**
 * 微信能力集成（条件编译）
 */

export function scanBarcode() {
  return new Promise((resolve, reject) => {
    // #ifdef MP-WEIXIN
    wx.scanCode({
      onlyFromCamera: false,
      scanType: ['barCode'],
      success: (res) => resolve(res.result),
      fail: reject
    })
    // #endif
    // #ifndef MP-WEIXIN
    uni.showToast({ title: '扫码仅支持微信小程序', icon: 'none' })
    reject(new Error('不支持扫码'))
    // #endif
  })
}

export function requestSubscribeMsg(tmplIds) {
  // #ifdef MP-WEIXIN
  return new Promise((resolve) => {
    wx.requestSubscribeMessage({
      tmplIds: tmplIds || ['YOUR_EXPIRY_TEMPLATE_ID'],
      success: (res) => {
        console.log('订阅成功', res)
        resolve(res)
      },
      fail: (err) => {
        console.log('订阅失败或取消', err)
        resolve(null)
      }
    })
  })
  // #endif
  // #ifndef MP-WEIXIN
  return Promise.resolve(null)
  // #endif
}