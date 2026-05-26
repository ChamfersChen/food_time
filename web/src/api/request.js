/**
 * 统一请求封装
 * 自动注入 JWT，处理 401 跳登录，统一 toast 报错
 */
const BASE_URL = 'http://localhost:17890/api/v1'

function request(options) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('jwt_token')
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.header,
      },
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync('jwt_token')
          uni.reLaunch({ url: '/pages/login/index' })
          return reject(new Error('未授权'))
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const msg = res.data?.message || '请求失败'
          uni.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络错误，请重试', icon: 'none' })
        reject(err)
      }
    })
  })
}

export function get(url, data) {
  return request({ url, method: 'GET', data })
}

export function post(url, data) {
  return request({ url, method: 'POST', data })
}

export function put(url, data) {
  return request({ url, method: 'PUT', data })
}

export function del(url, data) {
  return request({ url, method: 'DELETE', data })
}

export function upload(url, filePath, name = 'file') {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('jwt_token')
    uni.uploadFile({
      url: BASE_URL + url,
      filePath,
      name,
      header: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(res.data))
          } catch {
            resolve(res.data)
          }
        } else {
          const msg = (() => { try { return JSON.parse(res.data).message } catch { return '上传失败' } })()
          uni.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络错误，请重试', icon: 'none' })
        reject(err)
      },
    })
  })
}

export default request