import { get, put, post } from './request'
import { upload } from './request'

export function getUserProfile() {
  return get('/users/profile')
}

export function updateUserProfile(data) {
  return put('/users/profile', data)
}

export function updatePreferences(data) {
  return put('/users/preferences', data)
}

export function getStatistics() {
  return get('/users/statistics')
}

export function uploadAvatar(filePath) {
  return upload('/users/avatar', filePath, 'file')
}

export function subscribeTemplates(templates) {
  return post('/users/subscribe', { templates })
}