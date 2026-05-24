import { get, put } from './request'

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