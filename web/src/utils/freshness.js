/**
 * 根据 expire_date 计算食材新鲜度信息
 * @param {string|Date} expireDate
 * @returns {{ days: number, status: string, label: string, color: string, barWidth: number }}
 */
export function calcFreshness(expireDate) {
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  const expire = new Date(expireDate)
  expire.setHours(0, 0, 0, 0)
  const diff = expire.getTime() - now.getTime()
  const days = Math.ceil(diff / 86400000)
  const status = days > 3 ? 'fresh' : days >= 0 ? 'expiring' : 'expired'

  return {
    days,
    status,
    label: days > 3 ? `${days}天` : days > 0 ? `还剩 ${days} 天` : days === 0 ? '今天过期' : '已过期',
    color: status === 'fresh' ? '#7BBF8E' : status === 'expiring' ? '#F0A050' : '#E05A50',
    barWidth: status === 'fresh' ? Math.min(days / 30, 1) : status === 'expiring' ? Math.max(days / 3, 0.1) : 0,
  }
}

export function getFreshnessColor(status) {
  const map = {
    fresh: '#7BBF8E',
    expiring: '#F0A050',
    expired: '#E05A50',
  }
  return map[status] || '#888780'
}

export function getFreshnessLabel(status) {
  const map = {
    fresh: '新鲜',
    expiring: '临期',
    expired: '已过期',
  }
  return map[status] || '未知'
}