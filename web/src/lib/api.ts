/** Static data fetcher. Uses Vite's BASE_URL for production. */
const DATA_BASE = import.meta.env.BASE_URL + 'data'

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
  tier: 'final' | 'regional' | 'invitational' | 'provincial' | 'preliminary'
  no_awards?: boolean
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
  champion_冠军: number
  champion_亚军: number
  champion_季军: number
}

export interface ContestantSummary {
  id: string
  name: string
  org: string
  medals: { gold: number; silver: number; bronze: number }
  record_count: number
}

export interface PlayerRating {
  id: string
  name: string
  org: string
  org_id: string
  rating: number
  contests: number
}

export interface PlayerRatingDetail {
  id: string
  history: {
    contest_id: string
    contest_title: string
    date: string
    rating: number
    perf: number | null
    contests: number
  }[]
}

export interface SchoolRating {
  id: string
  name: string
  rating: number
  contests: number
}

export interface SearchEntry {
  name: string
  type: 'contestant' | 'organization'
  id: string
}

let contestsCache: ContestSummary[] | null = null
let orgsCache: OrgSummary[] | null = null
let contestantsCache: ContestantSummary[] | null = null
let searchIndexCache: SearchEntry[] | null = null

export async function getContests(): Promise<ContestSummary[]> {
  if (contestsCache) return contestsCache
  const resp = await fetch(`${DATA_BASE}/contests.json`)
  contestsCache = await resp.json()
  return contestsCache!
}

export async function getOrganizations(): Promise<OrgSummary[]> {
  if (orgsCache) return orgsCache
  const resp = await fetch(`${DATA_BASE}/organizations.json`)
  orgsCache = await resp.json()
  return orgsCache!
}

export async function getContestants(): Promise<ContestantSummary[]> {
  if (contestantsCache) return contestantsCache
  const resp = await fetch(`${DATA_BASE}/contestants.json`)
  contestantsCache = await resp.json()
  return contestantsCache!
}

export async function getSearchIndex(): Promise<SearchEntry[]> {
  if (searchIndexCache) return searchIndexCache
  const resp = await fetch(`${DATA_BASE}/search_index.json`)
  searchIndexCache = await resp.json()
  return searchIndexCache!
}

let summaryCache: SummaryData | null = null

export async function getSummary(): Promise<SummaryData> {
  if (summaryCache) return summaryCache
  const [contests, organizations, contestants, search_index] = await Promise.all([
    getContests(), getOrganizations(), getContestants(), getSearchIndex()
  ])
  summaryCache = { contests, organizations, contestants, search_index }
  return summaryCache
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

let playersRatingsCache: PlayerRating[] | null = null

export async function getPlayersRatings(): Promise<PlayerRating[]> {
  if (playersRatingsCache) return playersRatingsCache
  const resp = await fetch(`${DATA_BASE}/players_ratings.json`)
  const raw = await resp.json()
  // Array-compressed format: [id, name, org, org_id, rating, contests][]
  if (Array.isArray(raw[0])) {
    playersRatingsCache = raw.map((r: any[]) => ({
      id: r[0], name: r[1], org: r[2], org_id: r[3], rating: r[4], contests: r[5],
    }))
  } else {
    playersRatingsCache = raw
  }
  return playersRatingsCache!
}

export async function getPlayerRatingDetail(id: string): Promise<PlayerRatingDetail> {
  const resp = await fetch(`${DATA_BASE}/players_ratings/${id}.json`)
  return resp.json()
}

let schoolsRatingsCache: SchoolRating[] | null = null

export async function getSchoolsRatings(): Promise<SchoolRating[]> {
  if (schoolsRatingsCache) return schoolsRatingsCache
  const resp = await fetch(`${DATA_BASE}/schools_ratings.json`)
  schoolsRatingsCache = await resp.json()
  return schoolsRatingsCache!
}

export async function getContestTeamRatings(id: string): Promise<{ teams: (null | {
  preTeamRating: number | null
  postTeamRating: number | null
  avgDelta: number
  perf: number | null
})[] }> {
  const resp = await fetch(`${DATA_BASE}/contest_ratings/${id}.json`)
  return resp.json()
}
