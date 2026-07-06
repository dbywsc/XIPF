<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContest, getContestTeamRatings } from '@/lib/api'

const route = useRoute(); const router = useRouter()
const data = ref<any>(null); const tr = ref<any[]>([]); const loading = ref(true)
const exp = ref<Set<string>>(new Set())
const sq = ref('')

onMounted(async () => {
  try {
    const [d, t] = await Promise.all([
      getContest(route.params.id as string),
      getContestTeamRatings(route.params.id as string).catch(() => ({ teams: [] })),
    ])
    data.value = d; tr.value = t.teams || []
  } catch { data.value = null }
  loading.value = false
})

function tg(id: string) { const s = new Set(exp.value); s.has(id) ? s.delete(id) : s.add(id); exp.value = s }
const fd = (d: number) => (d > 0 ? '+' : '') + d.toFixed(0)
const ml: Record<string, string> = { gold: '金奖', silver: '银奖', bronze: '铜奖' }

// Filtered and searched teams (with original index for rating lookup)
const filteredTeams = computed(() => {
  if (!data.value?.teams) return []
  let teams = (data.value.teams as any[]).map((t: any, i: number) => ({ ...t, _origIdx: i }))
  if (sq.value.trim()) {
    const q = sq.value.trim().toLowerCase()
    teams = teams.filter((t: any) => {
      if (t.name.toLowerCase().includes(q)) return true
      if (t.organization.toLowerCase().includes(q)) return true
      if (t.members?.some((m: any) => m.name.toLowerCase().includes(q))) return true
      return false
    })
  }
  return teams
})

function clearSearch() { sq.value = '' }
</script>

<template>
<div v-if="loading" class="empty">加载中...</div>
<div v-else-if="!data" class="empty">比赛不存在</div>
<div v-else style="max-width:1040px;margin:0 auto">
  <button class="back" @click="router.back()">← 返回</button>

  <!-- Header -->
  <section style="margin-bottom:28px">
    <h1 style="font-size:22px;font-weight:700;letter-spacing:-.3px;margin-bottom:4px">{{ data.title }}</h1>
    <p class="muted" style="font-size:13.5px">{{ data.date||'日期待补充' }} · {{ data.teams.length }} 支队伍（正式 {{ data.teams.filter((t:any)=>t.official).length }}）</p>
    <p v-if="data.no_awards" style="margin-top:10px;padding:9px 16px;background:var(--gold-bg);color:var(--gold);font-size:13.5px;font-weight:500;border-radius:var(--r);border:1px solid rgba(251,191,36,0.15)">本场比赛缺少奖项信息，未计入 Rating</p>
  </section>

  <!-- Search Bar -->
  <div style="display:flex;gap:10px;margin-bottom:16px">
    <div class="srch" style="flex:1;min-width:200px;max-width:360px">
      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input v-model="sq" placeholder="搜索队伍名/选手名/学校名..." />
    </div>
    <button v-if="sq" @click="clearSearch" style="padding:8px 14px;font-size:12.5px;border:1px solid var(--line2);border-radius:var(--r);background:var(--bg4);color:var(--fg2);cursor:pointer;font-family:inherit;transition:all .2s;white-space:nowrap">清除</button>
  </div>

  <!-- Result count -->
  <div v-if="sq" class="muted" style="font-size:12.5px;margin-bottom:10px">
    找到 {{ filteredTeams.length }} 支队伍
  </div>

  <!-- Team Table -->
  <div class="card" style="overflow-x:auto">
    <table class="tbl"><thead><tr>
      <th style="width:82px">排名</th><th>学校</th><th>队伍</th>
      <th v-if="!data.no_awards" class="rt" style="width:100px">Rating 变化</th>
      <th v-if="!data.no_awards" style="width:76px">奖项</th>
    </tr></thead>
      <tbody v-for="(team) in filteredTeams" :key="team.id">
        <tr :class="{clickable:true,uo:!team.official}" @click="tg(team.id)">
          <td class="tnum"><span v-if="team.official" style="font-weight:600">{{ team.rank }}<span class="faint" style="font-weight:400;margin:0 2px">/</span>{{ team.official_rank }}</span><span v-else class="faint" style="font-style:italic">{{ team.rank }}</span></td>
          <td>{{ team.organization }}</td>
          <td><span style="font-weight:500">{{ team.name }}</span><span v-if="team.girl_team" style="margin-left:5px;font-size:9.5px;padding:2px 6px;border-radius:99px;border:1px solid rgba(236,72,153,0.25);color:#ec4899;font-weight:500">女队</span><span v-if="team.members.length" class="faint" style="margin-left:5px;font-size:10px">{{ exp.has(team.id)?'▾':'▸' }}</span></td>
          <td v-if="!data.no_awards" class="tnum rt">
            <template v-if="tr[team._origIdx]"><span class="delta" :class="tr[team._origIdx].avgDelta>0?'d-up':tr[team._origIdx].avgDelta<0?'d-down':''">{{ fd(tr[team._origIdx].avgDelta) }}</span></template>
            <span v-else class="faint">-</span>
          </td>
          <td v-if="!data.no_awards">
            <template v-if="team.division_medals&&Object.keys(team.division_medals).length"><span v-for="(m,div) in team.division_medals" :key="div" class="badge" :class="`badge-${m}`" style="margin-right:2px">{{ div }}{{ ml[m]||m }}</span></template>
            <span v-else-if="team.medal" class="badge" :class="`badge-${team.medal}`">{{ ml[team.medal] }}</span><span v-else class="faint">-</span>
          </td>
        </tr>
        <tr v-if="exp.has(team.id)&&team.members.length" style="border-bottom:2px solid var(--line3)"><td :colspan="data.no_awards?3:5" style="padding:0">
          <div style="padding:10px 16px">
            <div style="display:flex;gap:5px;flex-wrap:wrap;margin-bottom:8px">
              <template v-for="m in team.members" :key="m.name">
                <router-link v-if="m.contestant_id" :to="`/contestant/${m.contestant_id}`" style="display:inline-block;padding:4px 11px;background:var(--accent-glow);color:var(--accent);border-radius:var(--r-sm);font-size:13px;font-weight:500;transition:all .15s">{{ m.name }}</router-link>
                <span v-else style="display:inline-block;padding:4px 11px;background:var(--bg3);color:var(--fg3);border-radius:var(--r-sm);font-size:13px">{{ m.name }}</span>
              </template>
            </div>
            <div v-if="tr[team._origIdx]" style="display:flex;gap:18px;padding-top:7px;border-top:1px solid var(--line2)">
              <span v-if="tr[team._origIdx].preTeamRating!==null" style="font-size:12px;color:var(--fg3)">赛前 <strong style="font-weight:600;color:var(--fg)">{{ tr[team._origIdx].preTeamRating?.toFixed(0)??'-' }}</strong></span>
              <span v-if="tr[team._origIdx].perf!==null" style="font-size:12px;color:var(--fg3)">表现 <strong style="font-weight:600;color:var(--fg)">{{ tr[team._origIdx].perf?.toFixed(0)??'-' }}</strong></span>
              <span v-if="tr[team._origIdx].postTeamRating!==null" style="font-size:12px;color:var(--fg3)">赛后 <strong style="font-weight:600;color:var(--fg)">{{ tr[team._origIdx].postTeamRating?.toFixed(0)??'-' }}</strong></span>
            </div>
          </div>
        </td></tr>
      </tbody>
    </table>
  </div>
</div>
</template>

<style scoped>
.uo{opacity:.32}
select:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow)}

@media(max-width:768px){
  .tbl thead th{font-size:10px;padding:8px}
  .tbl tbody td{padding:8px;font-size:13px}
}
@media(max-width:480px){
  .tbl thead th:nth-child(4),.tbl tbody td:nth-child(4){display:none}
  .tbl thead th:nth-child(1){width:60px!important}
  .tbl thead th:nth-child(5){width:56px!important}
}
</style>
