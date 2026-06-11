/** Static data fetcher. In dev, reads from ../../dist/; in production, from /data/. */

const DATA_BASE = import.meta.env.DEV ? '/data' : '/data'

interface SummaryData {
  contests: ContestSummary[]
  organizations: OrgSummary[]
  contestants: ContestantSummary[]
  search_index: SearchEntry[]
}

export interface ContestSummary {
  id: string
  title: string
  date: string
  team_count: number
  official_count: number
  problem_count: number
}

export interface OrgSummary {
  id: string
  name: string
  gold: number
  silver: number
  bronze: number
  count: number
}

export interface ContestantSummary {
  id: string
  name: string
  org: string
  medals: { gold: number; silver: number; bronze: number }
  record_count: number
}

export interface SearchEntry {
  name: string
  type: 'contestant' | 'organization'
  id: string
}

let summaryCache: SummaryData | null = null

export async function getSummary(): Promise<SummaryData> {
  if (summaryCache) return summaryCache
  const resp = await fetch(`${DATA_BASE}/summary.json`)
  summaryCache = await resp.json()
  return summaryCache!
}

export async function getContest(id: string) {
  const resp = await fetch(`${DATA_BASE}/contests/${id}.json`)
  return resp.json()
}

export async function getContestant(id: string) {
  const resp = await fetch(`${DATA_BASE}/contestants/${id}.json`)
  return resp.json()
}

export async function getOrganization(id: string) {
  const resp = await fetch(`${DATA_BASE}/organizations/${id}.json`)
  return resp.json()
}
