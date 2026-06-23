<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { getSummary } from '@/lib/api'
import { initSearch, searchOrg } from '@/lib/search'

const all = ref<any[]>([]); const loading = ref(true)
const query = ref(''); const results = ref<any[]>([])

const sf = (a: any, b: any) =>
  ((b.champion_冠军 || 0) - (a.champion_冠军 || 0)) ||
  ((b.champion_亚军 || 0) - (a.champion_亚军 || 0)) ||
  ((b.champion_季军 || 0) - (a.champion_季军 || 0)) ||
  ((b.gold || 0) - (a.gold || 0)) ||
  ((b.silver || 0) - (a.silver || 0)) ||
  ((b.bronze || 0) - (a.bronze || 0))

onMounted(async () => {
  await initSearch()
  const d = await getSummary()
  all.value = d.organizations.sort(sf)
  loading.value = false
})

const byId = computed(() => {
  const m: Record<string, any> = {}
  for (const o of all.value) m[o.id] = o
  return m
})

watch(query, (q) => {
  if (!q.trim()) { results.value = []; return }
  results.value = searchOrg(q).map(r => byId.value[r.id] || r)
})

const list = computed(() => query.value.trim() ? results.value : all.value)
</script>

<template>
  <div class="page animate-in">
    <h1 class="page-title">学校列表</h1>
    <div class="search-bar">
      <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input v-model="query" class="search-input" type="text" placeholder="搜索学校..." />
    </div>
    <div v-if="loading" class="empty-state"><p>加载中...</p></div>
    <div v-else class="card" style="overflow:hidden">
      <table class="table">
        <thead>
          <tr>
            <th>#</th>
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
          <tr v-for="(o, i) in list" :key="o.id">
            <td class="num rank-cell">{{ i + 1 }}</td>
            <td><router-link :to="`/org/${o.id}`" class="org-link">{{ o.name }}</router-link></td>
            <td class="num text-right">{{ o.count }}</td>
            <td class="num text-right">{{ o.champion_冠军 || 0 }}</td>
            <td class="num text-right">{{ o.champion_亚军 || 0 }}</td>
            <td class="num text-right">{{ o.champion_季军 || 0 }}</td>
            <td class="num text-right">{{ o.gold }}</td>
            <td class="num text-right">{{ o.silver }}</td>
            <td class="num text-right">{{ o.bronze }}</td>
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
.org-link { color: var(--text); font-weight: 500; }
.org-link:hover { color: var(--primary); opacity: 1; }
.rank-cell { color: var(--text-muted); font-weight: 500; }
</style>
