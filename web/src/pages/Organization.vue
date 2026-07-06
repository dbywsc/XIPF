<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrganization, getPlayersRatings, getSchoolsRatings, getPlayerRatingDetail, getContest, getContestTeamRatings, getOrganizations, type PlayerRating, type SchoolRating } from '@/lib/api'
import { ratingColor } from '@/lib/colors'

const route = useRoute(); const router = useRouter()
const data = ref<any>(null); const members = ref<PlayerRating[]>([]); const loading = ref(true)
const sr = ref<number|null>(null); const sn = ref(0)
const activeTab = ref<'players'|'records'>('players')
const records = ref<any[]>([]); const recordsLoading = ref(false)
const playerSearch = ref('')

const fd = (d: number|null) => d===null||d===undefined?'-':(d>0?'+':'')+d.toFixed(0)

const filteredMembers = computed(() => {
  if (!playerSearch.value.trim()) return members.value
  const q = playerSearch.value.trim().toLowerCase()
  return members.value.filter(m => m.name.toLowerCase().includes(q))
})

onMounted(async () => {
  try {
    let orgId = route.params.id as string
    // Check English-to-Chinese name mapping
    if (/^[a-zA-Z]/.test(orgId)) {
      try {
        const resp = await fetch(import.meta.env.BASE_URL + 'data/org_name_map.json')
        const nameMap: Record<string, string> = await resp.json()
        // Get the org data first to check its name
        const od = await getOrganization(orgId)
        const mappedName = nameMap[od.name.trim()]
        if (mappedName) {
          const allOrgs = await getOrganizations()
          const zhOrg = allOrgs.find((o: any) => o.name.trim() === mappedName)
          if (zhOrg) {
            router.replace(`/org/${zhOrg.id}`)
            return
          }
        }
      } catch {}
    }
    const [od, pr, rt] = await Promise.all([
      getOrganization(orgId),
      getPlayersRatings().catch(() => [] as PlayerRating[]),
      getSchoolsRatings().catch(() => [] as SchoolRating[]),
    ])
    data.value = od
    const s = rt.find((x: SchoolRating) => x.name === od.name)
    sr.value = s?.rating ?? null
    sn.value = s?.contests ?? 0
    members.value = pr.filter(p => p.org === od.name).sort((a, b) => (b.rating ?? -Infinity) - (a.rating ?? -Infinity))
  } catch { data.value = null }
  loading.value = false
})

async function loadRecords() {
  if (records.value.length > 0) return
  recordsLoading.value = true
  try {
    const memberIds = members.value.map(m => m.id)
    const details = await Promise.all(memberIds.map(id => getPlayerRatingDetail(id).catch(() => null)))
    const contestMap = new Map<string, {
      contest_id: string
      contest_title: string
      date: string
      players: { name: string; id: string; rating_after: number; delta: number | null }[]
      total_delta: number
    }>()
    for (let di = 0; di < details.length; di++) {
      const detail = details[di]
      if (!detail?.history) continue
      const member = members.value[di]
      for (let hi = 0; hi < detail.history.length; hi++) {
        const cur = detail.history[hi]
        const prev = hi > 0 ? detail.history[hi - 1] : null
        const delta = prev ? cur.rating - prev.rating : null
        if (!contestMap.has(cur.contest_id)) {
          contestMap.set(cur.contest_id, {
            contest_id: cur.contest_id,
            contest_title: cur.contest_title,
            date: cur.date,
            players: [],
            total_delta: 0,
          })
        }
        const entry = contestMap.get(cur.contest_id)!
        entry.players.push({
          name: member.name,
          id: member.id,
          rating_after: cur.rating,
          delta,
        })
        if (delta !== null) entry.total_delta += delta
      }
    }
    const rawRecords = [...contestMap.values()].sort((a, b) => b.date.localeCompare(a.date))
    const contestIds = rawRecords.map(r => r.contest_id)
    const [contestDetails, contestRatings] = await Promise.all([
      Promise.all(contestIds.map(id => getContest(id).catch(() => null))),
      Promise.all(contestIds.map(id => getContestTeamRatings(id).catch(() => ({ teams: [] })))),
    ])
    const withRanks = rawRecords.map((rec, idx) => {
      const cd = contestDetails[idx]
      const cr = contestRatings[idx]
      let rank: number | null = null
      let totalOrgs: number | null = null
      let bestTeam: string | null = null
      let bestTeamIdx: number = -1
      let ratingDelta: number | null = null
      if (cd?.teams) {
        const officialTeams = cd.teams.filter((t: any) => t.official)
        const orgNames = new Set(officialTeams.map((t: any) => t.organization))
        totalOrgs = orgNames.size
        const schoolTeams = officialTeams.filter((t: any) => t.organization === data.value.name)
        if (schoolTeams.length > 0) {
          const best = schoolTeams.reduce((a: any, b: any) => (a.official_rank || a.rank) < (b.official_rank || b.rank) ? a : b)
          rank = best.official_rank || best.rank
          bestTeam = best.name
          // Find the original index of this team in the contest for rating lookup
          bestTeamIdx = cd.teams.findIndex((t: any) => t.id === best.id)
        }
      }
      // Get school rating delta from contest ratings (best team's avgDelta)
      if (bestTeamIdx >= 0 && cr?.teams?.[bestTeamIdx]) {
        ratingDelta = cr.teams[bestTeamIdx].avgDelta ?? null
      }
      return { ...rec, rank, totalOrgs, bestTeam, ratingDelta }
    })
    records.value = withRanks
  } catch {}
  recordsLoading.value = false
}

function switchTab(t: 'players'|'records') {
  activeTab.value = t
  if (t === 'records') loadRecords()
}
</script>

<template>
<div v-if="loading" class="empty">加载中...</div>
<div v-else-if="!data" class="empty">学校不存在</div>
<div v-else style="max-width:900px;margin:0 auto">
  <button class="back" @click="router.back()">← 返回</button>

  <!-- Header Card -->
  <div class="card" style="padding:24px 28px;margin-bottom:28px">
    <h1 style="font-size:24px;font-weight:700;letter-spacing:-.3px">{{ data.name }}</h1>
    <div v-if="sr!==null" style="display:flex;align-items:baseline;gap:8px;margin-top:10px">
      <span style="font-size:10px;font-weight:600;color:var(--fg3);text-transform:uppercase;letter-spacing:.5px">Rating</span>
      <span style="font-size:34px;font-weight:700;line-height:1">
        <template v-if="sr >= 3000"><span style="color:var(--fg)">{{ sr.toFixed(0)[0] }}</span><span :style="{color:ratingColor(sr)}">{{ sr.toFixed(0).slice(1) }}</span></template>
        <span v-else :style="{color:ratingColor(sr)}">{{ sr.toFixed(0) }}</span>
      </span>
      <span class="muted" style="font-size:13.5px">{{ sn }} 场</span>
    </div>
  </div>

  <!-- Stats Card -->
  <div class="card" style="padding:0;margin-bottom:24px">
    <div class="sec-head"><h2>获奖统计</h2></div>
    <div style="display:flex;gap:32px;padding:2px 20px 20px;flex-wrap:wrap">
      <div v-for="it in [{l:'冠军',k:'champion_冠军',c:'#ef4444'},{l:'亚军',k:'champion_亚军',c:'#3b82f6'},{l:'季军',k:'champion_季军',c:'#fb923c'},{l:'金奖',k:'gold',c:'var(--gold)'},{l:'银奖',k:'silver',c:'var(--silver)'},{l:'铜奖',k:'bronze',c:'var(--bronze)'},{l:'总参赛',k:'count',c:'var(--fg)'}]" :key="it.k" style="text-align:center">
        <div style="font-size:26px;font-weight:700;line-height:1.1" :style="{color:it.c}">{{ data.stats?.[it.k]||0 }}</div>
        <div style="font-size:11.5px;color:var(--fg3);margin-top:3px">{{ it.l }}</div>
      </div>
    </div>
  </div>

  <!-- Tabs -->
  <div class="tabs" style="margin-bottom:18px">
    <button :class="{tab:true, active:activeTab==='players'}" @click="switchTab('players')">选手列表</button>
    <button :class="{tab:true, active:activeTab==='records'}" @click="switchTab('records')">比赛记录</button>
  </div>

  <!-- Players Tab -->
  <div v-if="activeTab==='players' && members.length" class="card">
    <div class="sec-head"><h2>选手 ({{ members.length }})</h2></div>
    <div style="padding:0 18px 8px">
      <div class="srch" style="max-width:260px">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input v-model="playerSearch" placeholder="搜索选手姓名..." />
      </div>
    </div>
    <table class="tbl">
      <thead><tr><th>姓名</th><th class="rt" style="width:92px">Rating</th><th class="rt" style="width:54px">场次</th></tr></thead>
      <tbody><tr v-for="m in filteredMembers" :key="m.id" class="clickable row-anim" :style="{animationDelay:`${filteredMembers.indexOf(m)*25}ms`}" @click="router.push(`/contestant/${m.id}`)">
        <td style="font-weight:600;font-size:14px">{{ m.name }}</td>
        <td class="tnum rt">
          <template v-if="m.rating >= 3000">
            <span style="font-weight:650;color:var(--fg)">{{ m.rating.toFixed(0)[0] }}</span><span :style="{color:ratingColor(m.rating),fontWeight:650}">{{ m.rating.toFixed(0).slice(1) }}</span>
          </template>
          <span v-else :style="{color:ratingColor(m.rating),fontWeight:650}">{{ m.rating.toFixed(0) }}</span>
        </td>
        <td class="tnum rt muted">{{ m.contests }}</td>
      </tr></tbody>
    </table>
  </div>

  <!-- Records Tab -->
  <div v-if="activeTab==='records'">
    <div v-if="recordsLoading" class="empty">加载中...</div>
    <div v-else-if="!records.length" class="empty">暂无比赛记录</div>
    <div v-else class="card">
      <table class="tbl" style="table-layout:fixed">
        <thead><tr><th style="width:90px">日期</th><th>比赛</th><th style="width:120px">队伍</th><th class="rt" style="width:80px">排名</th><th class="rt" style="width:90px">Rating</th></tr></thead>
        <tbody><tr v-for="rec in records" :key="rec.contest_id">
          <td class="tnum muted" style="font-size:13px;width:90px;white-space:nowrap">{{ rec.date }}</td>
          <td><router-link :to="`/contest/${rec.contest_id}`" style="color:var(--accent);font-size:13.5px;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ rec.contest_title }}</router-link></td>
          <td style="width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px;color:var(--fg3)">{{ rec.bestTeam || '-' }}</td>
          <td class="tnum rt" style="font-size:13px;width:80px">
            <span v-if="rec.rank !== null && rec.totalOrgs !== null">{{ rec.rank }}/{{ rec.totalOrgs }}</span>
            <span v-else class="faint">-</span>
          </td>
          <td class="tnum rt" style="width:90px">
            <span v-if="rec.ratingDelta !== null" class="delta" :class="rec.ratingDelta>0?'d-up':rec.ratingDelta<0?'d-down':''" style="font-size:13px">{{ fd(rec.ratingDelta) }}</span>
            <span v-else class="faint">-</span>
          </td>
        </tr></tbody>
      </table>
    </div>
  </div>
</div>
</template>

<style scoped>
@media(max-width:480px){
  .tbl thead th:nth-child(3),.tbl tbody td:nth-child(3),
  .tbl thead th:nth-child(4),.tbl tbody td:nth-child(4),
  .tbl thead th:nth-child(5),.tbl tbody td:nth-child(5){display:none}
}
</style>
