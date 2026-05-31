import { get, post } from './request'

export function getLogComments(logId) {
  return get(`/comments/log/${logId}`)
}

export function createComment(data) {
  return post('/comments', data)
}
