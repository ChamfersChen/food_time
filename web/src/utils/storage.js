/**
 * 本地存储封装
 */

const TOKEN_KEY = 'jwt_token'
const USER_KEY = 'user_info'
const PREFERENCES_KEY = 'user_preferences'

export function getToken() {
  return uni.getStorageSync(TOKEN_KEY) || ''
}

export function setToken(token) {
  uni.setStorageSync(TOKEN_KEY, token)
}

export function removeToken() {
  uni.removeStorageSync(TOKEN_KEY)
}

export function getUserInfo() {
  try {
    return uni.getStorageSync(USER_KEY) ? JSON.parse(uni.getStorageSync(USER_KEY)) : null
  } catch {
    return null
  }
}

export function setUserInfo(user) {
  uni.setStorageSync(USER_KEY, JSON.stringify(user))
}

export function removeUserInfo() {
  uni.removeStorageSync(USER_KEY)
}

export function getPreferences() {
  try {
    return uni.getStorageSync(PREFERENCES_KEY) ? JSON.parse(uni.getStorageSync(PREFERENCES_KEY)) : null
  } catch {
    return null
  }
}

export function setPreferences(prefs) {
  uni.setStorageSync(PREFERENCES_KEY, JSON.stringify(prefs))
}

export function clearAll() {
  uni.removeStorageSync(TOKEN_KEY)
  uni.removeStorageSync(USER_KEY)
  uni.removeStorageSync(PREFERENCES_KEY)
}