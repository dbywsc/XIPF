<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContest } from '@/lib/api'

const route = useRoute(); const router = useRouter()
const data = ref<any>(null); const loading = ref(true)
const expanded = ref<Set<string>>(new Set())

onMounted(async () => {
  try { data.value = await getContest(route.params.id as string) } catch { data.value = null }
  loading.value = false
})

function toggle(id: string) { const s = new Set(expanded.value); s.has(id) ? s.delete(id) : s.add(id); expanded.value = s }
const ml: Record<string,string> = { gold:'金奖', silver:'银奖', bronze:'铜奖' }
</script>

<template>
  <div v-if="loading" class="empty-state"><p>加载中...</p></div>
  <div v-else-if="!data" class="empty-state"><p>比赛不存在</p></div>
  <div v-else class="page">
    <button class="back-link" @click="router.back()">&larr; 返回</button>
    <div class="card header-card">
      <h1>{{ data.title }}</h1>
      <p class="meta">{{ data.date||'日期待补充' }} &middot; {{ data.teams.length }} 支队伍（{{ data.teams.filter((t:any)=>t.official).length }} 正式）</p>
    </div>

    <div class="card" style="overflow-x:auto">
      <table class="table">
        <thead><tr><th>排名</th><th>学校</th><th>队伍</th><th>奖项</th></tr></thead>
        <tbody v-for="team in data.teams" :key="team.id">
          <tr :class="{ row: true, unofficial: !team.official }" @click="toggle(team.id)" style="cursor:pointer">
            <td class="num">
              <span v-if="team.official">{{ team.rank }} / {{ team.official_rank }}</span>
              <span v-else class="unoff-rank">{{ team.rank }}</span>
            </td>
            <td>{{ team.organization }}</td>
            <td><span class="tname">{{ team.name }}</span><span v-if="team.girl_team" class="gtag">女队</span><span v-if="team.members.length" class="arrow">{{ expanded.has(team.id)?'▾':'▸' }}</span></td>
            <td>
              <template v-if="team.division_medals && Object.keys(team.division_medals).length">
                <span v-for="(m, div) in team.division_medals" :key="div" class="badge" :class="`badge-${m}`" style="margin-right:4px">{{ div }}{{ ml[m] || m }}</span>
              </template>
              <span v-else-if="team.medal" class="badge" :class="`badge-${team.medal}`">{{ ml[team.medal] }}</span>
              <span v-else class="no">-</span>
            </td>
          </tr>
          <tr v-if="expanded.has(team.id) && team.members.length" class="exp">
            <td colspan="4"><div class="mems"><template v-for="m in team.members" :key="m.name"><router-link v-if="m.contestant_id" :to="`/contestant/${m.contestant_id}`" class="mlink">{{ m.name }}</router-link><span v-else class="mlink dim">{{ m.name }}</span></template></div></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; }
.header-card { padding: 24px; margin-bottom: 24px; }
.header-card h1 { font-size: 20px; font-weight: 700; }
.meta { color: var(--text-secondary); font-size: 14px; margin-top: 6px; }
.row { transition: background var(--transition); }
.unofficial { opacity: .55; }
.unoff-rank { color: var(--text-muted); }
.tname { font-weight: 500; }
.gtag { margin-left: 6px; font-size: 10px; padding: 1px 6px; border-radius: 4px; background: #fce7f3; color: #be185d; font-weight: 500; }
.arrow { margin-left: 6px; color: var(--text-muted); font-size: 12px; }
.exp td { padding: 0; border-bottom: 2px solid var(--border); }
.mems { display: flex; gap: 8px; padding: 10px 16px; flex-wrap: wrap; }
.mlink { display: inline-block; padding: 4px 12px; background: var(--primary-light); color: var(--primary-hover); border-radius: 6px; font-size: 13px; text-decoration: none; }
.mlink:hover { background: #b6e3ff; text-decoration: none; }
.mlink.dim { background: #f0f0f0; color: #999; }
.no { color: var(--text-muted); }
.card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-sm); }
</style>
