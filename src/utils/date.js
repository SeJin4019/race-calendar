const DAYS = ['일', '월', '화', '수', '목', '금', '토']

export function dday(dateStr) {
  if (!dateStr) return null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const race = new Date(dateStr + 'T00:00:00')
  const diff = Math.round((race - today) / (1000 * 60 * 60 * 24))
  if (diff === 0) return 'D-day'
  if (diff > 0) return `D-${diff}`
  return null
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일 (${DAYS[d.getDay()]})`
}

export function formatDateWithTime(dateStr, timeStr) {
  if (!dateStr) return ''
  const base = formatDate(dateStr)
  return timeStr ? `${base} ${timeStr}` : base
}

export function monthStr(dateStr) {
  if (!dateStr) return ''
  return dateStr.substring(5, 7) + '월'
}

export function dayStr(dateStr) {
  if (!dateStr) return ''
  return parseInt(dateStr.substring(8, 10))
}

export function effectiveStatus(race) {
  const today = new Date().toISOString().slice(0, 10)
  if (race.status === '접수예정' && race.registration_start && race.registration_start <= today) {
    if (!race.registration_deadline || race.registration_deadline >= today) return '접수중'
    return '접수마감'
  }
  if (race.status === '접수중' && race.registration_deadline && race.registration_deadline < today) {
    return '접수마감'
  }
  return race.status
}

export function dayOfWeek(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  return DAYS[d.getDay()]
}
