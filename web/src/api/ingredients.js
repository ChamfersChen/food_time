import { get, post, put, del } from './request'

export function getIngredients(params) {
  return get('/ingredients', params)
}

export function getIngredient(id) {
  return get(`/ingredients/${id}`)
}

export function addIngredient(data) {
  return post('/ingredients', data)
}

export function updateIngredient(id, data) {
  return put(`/ingredients/${id}`, data)
}

export function deleteIngredient(id) {
  return del(`/ingredients/${id}`)
}

export function markConsumed(id) {
  return put(`/ingredients/${id}/consume`)
}

export function batchDelete(ids) {
  return post('/ingredients/batch-delete', { ids })
}