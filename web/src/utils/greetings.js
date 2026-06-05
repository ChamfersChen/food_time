export const COUNTABLE_UNITS = ['个', '根', '只', '袋', '盒', '瓶', '罐', '片', '把']

export function isCountableUnit(unit) {
  return COUNTABLE_UNITS.includes(unit)
}

export function getTimeBasedGreeting() {
  const hour = new Date().getHours()
  if (hour >= 6 && hour < 10) return '早餐加菜 🌅'
  if (hour >= 11 && hour < 14) return '午餐吃好 ☀️'
  if (hour >= 17 && hour < 21) return '晚餐愉快 🌙'
  return '深夜食堂 🌃'
}

export function getConsumeSuccessText(name, quantity, unit) {
  const greeting = getTimeBasedGreeting()
  if (isCountableUnit(unit)) {
    return {
      main: `吃掉 ${quantity} 个${name}`,
      sub: greeting,
    }
  }
  return {
    main: `消耗 ${quantity}${unit}${name}`,
    sub: greeting,
  }
}

export function getAddSuccessText(name, quantity, unit) {
  if (isCountableUnit(unit)) {
    return `已添加 ${quantity} 个${name} ✨`
  }
  return `已添加 ${quantity}${unit}${name} ✨`
}

export function getZoneChangeText(zone) {
  const zoneNames = { refrigeration: '冷藏', freezing: '冷冻', room_temp: '常温' }
  return `已搬到 ${zoneNames[zone] || zone} ❄️`
}

export function getQuickChipPresets(quantity, unit) {
  if (isCountableUnit(unit)) {
    const presets = []
    if (quantity >= 1) presets.push(1)
    if (quantity >= 2) presets.push(2)
    if (quantity >= 5) presets.push(5)
    return presets
  }
  if (quantity <= 0) return []
  const q25 = Math.floor(quantity * 0.25)
  const q50 = Math.floor(quantity * 0.5)
  const q75 = Math.floor(quantity * 0.75)
  const presets = []
  if (q25 > 0) presets.push(q25)
  if (q50 > 0) presets.push(q50)
  if (q75 > 0) presets.push(q75)
  return presets
}

export function getAddChipPresets(unit) {
  if (isCountableUnit(unit)) {
    return [1, 2, 5, 10]
  }
  return [50, 100, 200, 500]
}

export function getStepperStep(unit) {
  if (isCountableUnit(unit)) return 1
  return 100
}
