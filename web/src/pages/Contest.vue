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

function toggle(id: string) {
  const s = new Set(expanded.value)
  s.has(id) ? s.delete(id) : s.add(id)
  expanded.value = s
}
const ml: Record<string, string> = { gold: '金奖', silver: '银奖', bronze: '铜奖' }
</script>

<template>
  <div v-if="loading" class="empty-state"><p>加载中...</p></div>
  <div v-else-if="!data" class="empty-state"><p>比赛不存在</p></div>
  <div v-else class="page animate-in">
    <button class="back-link" @click="router.back()">&larr; 返回</button>

    <div class="card header-card">
      <h1>{{ data.title }}</h1>
      <p class="meta">{{ data.date || '日期待补充' }} &middot; {{ data.teams.length }} 支队伍（{{ data.teams.filter((t: any) => t.official).length }} 正式）</p>
    </div>

    <div class="card" style="overflow-x:auto">
      <table class="table">
        <thead>
          <tr>
            <th>排名</th>
            <th>学校</th>
            <th>队伍</th>
            <th>奖项</th>
          </tr>
        </thead>
        <tbody v-for="team in data.teams" :key="team.id">
          <tr
            :class="{ row: true, unofficial: !team.official }"
            class="clickable"
            @click="toggle(team.id)"
          >
            <td class="num">
              <span v-if="team.official" class="rank-both">{{ team.rank }} <span class="sep">/</span> {{ team.official_rank }}</span>
              <span v-else class="unoff-rank">{{ team.rank }}</span>
            </td>
            <td>{{ team.organization }}</td>
            <td>
              <span class="tname">{{ team.name }}</span>
              <span v-if="team.girl_team" class="gtag">女队</span>
              <span v-if="team.members.length" class="arrow">{{ expanded.has(team.id) ? '▾' : '▸' }}</span>
            </td>
            <td>
              <template v-if="team.division_medals && Object.keys(team.division_medals).length">
                <span v-for="(m, div) in team.division_medals" :key="div" class="badge" :class="`badge-${m}`" style="margin-right:4px">{{ div }}{{ ml[m] || m }}</span>
              </template>
              <span v-else-if="team.medal" class="badge" :class="`badge-${team.medal}`">{{ ml[team.medal] }}</span>
              <span v-else class="no-award">-</span>
            </td>
          </tr>
          <tr v-if="expanded.has(team.id) && team.members.length" class="exp">
            <td colspan="4">
              <div class="mems">
                <template v-for="m in team.members" :key="m.name">
                  <router-link v-if="m.contestant_id" :to="`/contestant/${m.contestant_id}`" class="mlink">{{ m.name }}</router-link>
                  <span v-else class="mlink dim">{{ m.name }}</span>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; }

.header-card { padding: 28px; margin-bottom: 24px; }
.header-card h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.3px; }
.meta { color: var(--text-secondary); font-size: 14px; margin-top: 8px; }

.clickable { cursor: pointer; }
.row { transition: background var(--transition); }
.unofficial { opacity: 0.5; }
.unoff-rank { color: var(--text-muted); font-style: italic; }
.rank-both { font-weight: 600; }
.rank-both .sep { font-weight: 400; color: var(--text-muted); margin: 0 2px; }
.tname { font-weight: 500; }
.gtag {
  margin-left: 6px;
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 99px;
  background: #FCE7F3;
  color: #BE185D;
  font-weight: 500;
}
[data-theme="dark"] .gtag {
  background: rgba(190, 24, 93, 0.15);
  color: #F472B6;
}
.arrow { margin-left: 6px; color: var(--text-muted); font-size: 12px; }

.exp td { padding: 0; border-bottom: 2px solid var(--border); }
.mems { display: flex; gap: 8px; padding: 10px 20px; flex-wrap: wrap; }
.mlink {
  display: inline-block;
  padding: 5px 14px;
  background: var(--primary-bg);
  color: var(--primary);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: background var(--transition);
}
.mlink:hover { background: var(--primary-border); opacity: 1; }
.mlink.dim { background: var(--bg); color: var(--text-muted); }
.no-award { color: var(--text-muted); }
</style>
