import Fuse from 'fuse.js'
import { getSearchIndex, type SearchEntry } from './api'

let fuseContestants: Fuse<SearchEntry> | null = null
let fuseOrganizations: Fuse<SearchEntry> | null = null

export async function initSearch() {
  if (fuseContestants) return
  const data = await getSearchIndex()
  const ci = data.filter(e => e.type === 'contestant')
  const oi = data.filter(e => e.type === 'organization')
  fuseContestants = new Fuse(ci, { keys: ['name'], threshold: 0.2, minMatchCharLength: 2 })
  fuseOrganizations = new Fuse(oi, { keys: ['name'], threshold: 0.2, minMatchCharLength: 2 })
}

export function searchContestant(query: string): SearchEntry[] {
  if (!fuseContestants || !query.trim()) return []
  return fuseContestants.search(query.trim()).map(r => r.item).slice(0, 15)
}

export function searchOrg(query: string): SearchEntry[] {
  if (!fuseOrganizations || !query.trim()) return []
  return fuseOrganizations.search(query.trim()).map(r => r.item).slice(0, 15)
}
