const MEASURABLE_UNITS = ['克', '毫升', '升', '千克']

export function getStepSize(unit) {
  return MEASURABLE_UNITS.includes(unit) ? 10 : 1
}

export function isMeasurableUnit(unit) {
  return MEASURABLE_UNITS.includes(unit)
}

export function isCountableUnit(unit) {
  return !MEASURABLE_UNITS.includes(unit)
}
