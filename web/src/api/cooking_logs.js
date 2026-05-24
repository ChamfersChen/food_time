import { get, post } from './request'

export function getCookingLogs(params) {
  return get('/cooking-logs', params)
}

export function getCookingLog(id) {
  return get(`/cooking-logs/${id}`)
}

export function createCookingLog(data) {
  return post('/cooking-logs', data)
}

export function getLogsByDate(date) {
  return get('/cooking-logs/by-date', { date })
}