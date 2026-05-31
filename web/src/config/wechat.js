// WeChat Mini Program template IDs for subscribe messages
// These must match the templates approved in WeChat Official Account backend
export const WX_TEMPLATES = {
  EXPIRY: 'YOUR_EXPIRY_TEMPLATE_ID',
  STOCK: 'YOUR_STOCK_TEMPLATE_ID',
  INACTIVE: 'YOUR_INACTIVE_TEMPLATE_ID',
}

export const TEMPLATE_NAMES = {
  [WX_TEMPLATES.EXPIRY]: '食材临期提醒',
  [WX_TEMPLATES.STOCK]: '冰箱库存不足提醒',
  [WX_TEMPLATES.INACTIVE]: '久未烹饪提醒',
}

export const ALL_TMPL_IDS = Object.values(WX_TEMPLATES)
