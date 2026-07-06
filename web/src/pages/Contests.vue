<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getContests, type ContestSummary } from '@/lib/api'

const contests = ref<ContestSummary[]>([]); const loading = ref(true)
const activeTier = ref('regional')

const T: Record<string, { label: string; color: string }> = {
  final: { label: '决赛', color: '#ef4444' },
  regional: { label: '区域赛', color: '#3b82f6' },
  invitational: { label: '邀请赛', color: '#fbbf24' },
  provincial: { label: '省赛', color: 'var(--fg3)' },
  preliminary: { label: '网络赛', color: '#8b5cf6' },
}
const TIERS = ['final', 'regional', 'invitational', 'provincial', 'preliminary']

onMounted(async () => { contests.value = await getContests(); loading.value = false })

const filtered = computed(() => contests.value.filter(c => c.tier === activeTier.value && !c.no_awards))

const grouped = computed(() => {
  const map = new Map<string, ContestSummary[]>()
  for (const c of filtered.value) {
    const y = c.date.slice(0, 4)
    if (!map.has(y)) map.set(y, [])
    map.get(y)!.push(c)
  }
  return [...map.entries()].sort((a, b) => b[0].localeCompare(a[0]))
})
</script>

<template>
<div class="fade-in contests-page">
  <h1 class="page-title" style="text-align:left">比赛列表</h1>

  <div class="tabs">
    <button v-for="t in TIERS" :key="t" :class="{tab:true, active:activeTier===t}" @click="activeTier = t">
      {{ T[t].label }}
      <span class="tb-count">{{ contests.filter(c => c.tier === t && !c.no_awards).length }}</span>
    </button>
  </div>

  <div v-if="loading" class="empty">加载中...</div>

  <div v-else>
    <template v-for="[year, list] in grouped" :key="year">
      <div class="year-label">{{ year }}</div>
      <div class="card">
        <div v-for="c in list" :key="c.id" class="crow clickable" @click="$router.push(`/contest/${c.id}`)">
          <span class="cr-date">{{ c.date?.slice(5) }}</span>
          <span class="cr-title">{{ c.title }}</span>
          <span class="cr-teams muted tnum">{{ c.team_count }} 队</span>
        </div>
      </div>
    </template>
  </div>
</div>
</template>

<style scoped>
.contests-page{max-width:1040px;margin:0 auto}
.crow{display:flex;align-items:center;gap:14px;padding:11px 18px;border-bottom:1px solid var(--line2);transition:background .1s}
.crow:last-child{border-bottom:none}
.crow:hover{background:var(--bg5)}
.cr-date{font-size:12px;color:var(--fg4);flex-shrink:0;width:48px;font-variant-numeric:tabular-nums}
.cr-title{font-size:13.5px;font-weight:500;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cr-teams{font-size:12px;flex-shrink:0}
.year-label{font-size:12px;font-weight:600;color:var(--fg3);margin:20px 0 8px 4px;text-transform:uppercase;letter-spacing:.5px}

/* Mobile */
@media(max-width:768px){
  .tabs{flex-wrap:wrap;width:100%;overflow-x:auto}
  .tab{padding:8px 14px;font-size:12.5px;white-space:nowrap}
  .crow{padding:10px 14px;gap:10px}
  .cr-date{width:40px;font-size:11px}
  .cr-title{font-size:13px}
  .cr-teams{font-size:11px}
}
@media(max-width:480px){
  .tab{padding:7px 11px;font-size:11.5px;gap:4px}
  .tb-count{font-size:10px}
  .crow{padding:9px 12px;gap:8px}
  .cr-date{width:36px;font-size:10.5px}
  .cr-title{font-size:12.5px}
}
</style>
