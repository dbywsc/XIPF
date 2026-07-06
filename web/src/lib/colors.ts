/** Codeforces-style rating colors. Only the color is used — band names are hidden. */
export function ratingColor(rating: number | null | undefined): string {
  if (rating == null) return 'var(--ink-3)'
  if (rating >= 3000) return '#CC0000'
  if (rating >= 2400) return '#CC0000'
  if (rating >= 2100) return '#FF8C00'
  if (rating >= 1900) return '#AA00AA'
  if (rating >= 1600) return '#0000FF'
  if (rating >= 1400) return '#03A89E'
  if (rating >= 1200) return '#008000'
  return '#808080'
}

export function ratingColorDark(rating: number | null | undefined): string {
  if (rating == null) return 'var(--ink-3)'
  if (rating >= 3000) return '#FF3333'
  if (rating >= 2400) return '#FF6666'
  if (rating >= 2100) return '#FFAA33'
  if (rating >= 1900) return '#CC66CC'
  if (rating >= 1600) return '#6666FF'
  if (rating >= 1400) return '#33CCBB'
  if (rating >= 1200) return '#44CC44'
  return '#AAAAAA'
}

/** For 3000+ ratings: first character black (or near-black), rest red */
export function ratingColorSplit(rating: number): { first: string; rest: string } | null {
  if (rating < 3000) return null
  const s = rating.toFixed(0)
  return { first: s[0], rest: s.slice(1) }
}
