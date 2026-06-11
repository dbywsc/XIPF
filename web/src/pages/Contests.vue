<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSummary, type ContestSummary } from '@/lib/api'
const contests = ref<ContestSummary[]>([]); const loading = ref(true)
onMounted(async () => { const d = await getSummary(); contests.value = d.contests; loading.value = false })
</script>

<template>
  <div class="page">
    <h1 class="page-title">全部比赛</h1>
    <div v-if="loading" class="empty-state"><p>加载中...</p></div>
    <table v-else class="table card">
      <thead><tr><th>日期</th><th>名称</th><th class="text-right">队伍</th><th class="text-right">正式</th></tr></thead>
      <tbody><tr v-for="c in contests" :key="c.id"><td class="num">{{ c.date||'-' }}</td><td><router-link :to="`/contest/${c.id}`">{{ c.title }}</router-link></td><td class="num text-right">{{ c.team_count }}</td><td class="num text-right">{{ c.official_count }}</td></tr></tbody>
    </table>
  </div>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-sm); }
</style>
