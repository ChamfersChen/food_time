/**
 * 日期格式化工具
 */

const WEEK_DAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

export const MEAL_LABELS = {
  breakfast: { label: '早餐', emoji: '🌅', color: '#FFD89B' },
  lunch: { label: '午餐', emoji: '☀️', color: '#FFE5A0' },
  afternoon_tea: { label: '下午茶', emoji: '🧁', color: '#FFB7C5' },
  dinner: { label: '晚餐', emoji: '🌙', color: '#B8A4E3' },
  supper: { label: '夜宵', emoji: '🌟', color: '#A8D8EA' },
}

const MEAL_TYPES = Object.keys(MEAL_LABELS)

export function formatDate(date, format = 'YYYY-MM-DD') {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
}

export function formatTime(date) {
  return formatDate(date, 'HH:mm')
}

export function getMealTypeFromHour(hour) {
  if (hour < 10) return 'breakfast'
  if (hour < 14) return 'lunch'
  if (hour < 17) return 'afternoon_tea'
  if (hour < 21) return 'dinner'
  return 'supper'
}

export function getMealTypeFromDate(date) {
  return getMealTypeFromHour(new Date(date).getHours())
}

export function getMealMeta(type) {
  if (!type) return { label: '加餐', emoji: '🍴', color: '#E0E0E0' }
  return MEAL_LABELS[type] || { label: type, emoji: '🍴', color: '#E0E0E0' }
}

export function getWeekDay(date) {
  return WEEK_DAYS[new Date(date).getDay()]
}

export function getRelativeDateLabel(date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  const diff = Math.floor((d.getTime() - now.getTime()) / 86400000)
  if (diff === 0) return '今天'
  if (diff === 1) return '明天'
  if (diff === -1) return '昨天'
  if (diff > 1 && diff <= 7) return `${diff}天后`
  if (diff < -1 && diff >= -7) return `${Math.abs(diff)}天前`
  return formatDate(date)
}

export function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 11) return '早安'
  if (hour < 14) return '午安'
  if (hour < 18) return '下午好'
  return '晚上好'
}

export function isSameDay(date1, date2) {
  const d1 = new Date(date1)
  const d2 = new Date(date2)
  return d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
}

export function groupLogsByDate(logs) {
  const groups = {}
  logs.forEach((log) => {
    const key = formatDate(log.cooked_at)
    if (!groups[key]) {
      groups[key] = []
    }
    groups[key].push(log)
  })
  return Object.entries(groups)
    .sort((a, b) => new Date(b[0]) - new Date(a[0]))
    .map(([date, items]) => ({ date, items }))
}

export { MEAL_TYPES }