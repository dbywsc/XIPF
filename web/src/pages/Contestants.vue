<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { getSummary } from '@/lib/api'
import { initSearch, searchContestant } from '@/lib/search'

const all = ref<any[]>([]); const loading = ref(true)
const query = ref(''); const results = ref<any[]>([])

const sf = (a: any, b: any) =>
  ((b.medals?.champion || 0) - (a.medals?.champion || 0)) ||
  ((b.medals?.runner_up || 0) - (a.medals?.runner_up || 0)) ||
  ((b.medals?.third || 0) - (a.medals?.third || 0)) ||
  ((b.medals?.gold || 0) - (a.medals?.gold || 0)) ||
  ((b.medals?.silver || 0) - (a.medals?.silver || 0)) ||
  ((b.medals?.bronze || 0) - (a.medals?.bronze || 0))

onMounted(async () => {
  await initSearch()
  const d = await getSummary()
  all.value = d.contestants.sort(sf)
  loading.value = false
})

const byId = computed(() => {
  const m: Record<string, any> = {}
  for (const c of all.value) m[c.id] = c
  return m
})

watch(query, (q) => {
  if (!q.trim()) { results.value = []; return }
  results.value = searchContestant(q).map(r => byId.value[r.id] || r)
})

const list = computed(() => query.value.trim() ? results.value : all.value)
</script>

<template>
  <div class="page animate-in">
    <h1 class="page-title">选手列表</h1>
    <div class="search-bar">
      <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input v-model="query" class="search-input" type="text" placeholder="搜索选手..." />
    </div>
    <div v-if="loading" class="empty-state"><p>加载中...</p></div>
    <div v-else class="card" style="overflow:hidden">
      <table class="table">
        <thead>
          <tr>
            <th>#</th>
            <th>姓名</th>
            <th>学校</th>
            <th class="text-right">参赛</th>
            <th class="text-right">冠</th>
            <th class="text-right">亚</th>
            <th class="text-right">季</th>
            <th class="text-right">金</th>
            <th class="text-right">银</th>
            <th class="text-right">铜</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(c, i) in list" :key="c.id">
            <td class="num rank-cell">{{ i + 1 }}</td>
            <td><router-link :to="`/contestant/${c.id}`" class="name-link">{{ c.name }}</router-link></td>
            <td><router-link :to="`/org/${c.org_id}`" class="org-link">{{ c.org }}</router-link></td>
            <td class="num text-right">{{ c.record_count }}</td>
            <td class="num text-right">{{ c.medals?.champion || 0 }}</td>
            <td class="num text-right">{{ c.medals?.runner_up || 0 }}</td>
            <td class="num text-right">{{ c.medals?.third || 0 }}</td>
            <td class="num text-right">{{ c.medals?.gold }}</td>
            <td class="num text-right">{{ c.medals?.silver }}</td>
            <td class="num text-right">{{ c.medals?.bronze }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 1200px; margin: 0 auto; }
.search-bar { position: relative; margin-bottom: 24px; }
.search-bar .search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}
.search-bar .search-input { max-width: 400px; padding-left: 42px; }
.name-link { color: var(--text); font-weight: 500; }
.name-link:hover { color: var(--primary); opacity: 1; }
.org-link { color: var(--text-secondary); font-size: 13px; }
.org-link:hover { color: var(--primary); opacity: 1; }
.rank-cell { color: var(--text-muted); font-weight: 500; }
</style>
