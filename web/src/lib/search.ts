import Fuse from 'fuse.js'
import { getSummary, type SearchEntry } from './api'

let contestants: Fuse<SearchEntry> | null = null
let organizations: Fuse<SearchEntry> | null = null

export async function initSearch() {
  if (contestants) return
  const data = await getSummary()
  const ci = data.search_index.filter(e => e.type === 'contestant')
  const oi = data.search_index.filter(e => e.type === 'organization')
  contestants = new Fuse(ci, { keys: ['name'], threshold: 0.2, minMatchCharLength: 2 })
  organizations = new Fuse(oi, { keys: ['name'], threshold: 0.2, minMatchCharLength: 2 })
}

export function searchContestant(query: string): SearchEntry[] {
  if (!contestants || !query.trim()) return []
  return contestants.search(query.trim()).map(r => r.item).slice(0, 15)
}

export function searchOrg(query: string): SearchEntry[] {
  if (!organizations || !query.trim()) return []
  return organizations.search(query.trim()).map(r => r.item).slice(0, 15)
}
