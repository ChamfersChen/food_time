import { get, post, put, del } from './request'

export function getCookingLogs(params) {
  return get('/cooking-logs', params)
}

export function getCookingLog(id) {
  return get(`/cooking-logs/${id}`)
}

export function createCookingLog(data) {
  return post('/cooking-logs', data)
}

export function updateCookingLog(id, data) {
  return put(`/cooking-logs/${id}`, data)
}

export function deleteCookingLog(id) {
  return del(`/cooking-logs/${id}`)
}

export function getLogsByDate(date) {
  return get('/cooking-logs/by-date', { date })
}

export function getCalendarDates(year, month) {
  return get('/cooking-logs/calendar', { year, month })
}