import { get, post, del } from './request'

export function getCurrentHousehold() {
  return get('/households/current')
}

export function createHousehold() {
  return post('/households')
}

export function joinHousehold(inviteCode) {
  return post('/households/join', { invite_code: inviteCode })
}

export function regenerateInvite() {
  return post('/households/regenerate-invite')
}

export function removeMember(userId) {
  return del(`/households/members/${userId}`)
}

export function leaveHousehold() {
  return del('/households/leave')
}
