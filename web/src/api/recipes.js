import { get, post } from './request'

export function getRecipes(params) {
  return get('/recipes', params)
}

export function getRecipe(id) {
  return get(`/recipes/${id}`)
}

export function getRecommendedRecipes(params) {
  return get('/recipes/recommended', params)
}

export function getRandomRecipe() {
  return get('/recipes/random')
}

export function searchRecipes(keyword) {
  return get('/recipes/search', { keyword })
}

export function toggleFavorite(recipeId) {
  return post(`/recipes/${recipeId}/favorite`)
}