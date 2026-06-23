<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSummary, type ContestSummary } from '@/lib/api'

const contests = ref<ContestSummary[]>([]); const loading = ref(true)

onMounted(async () => {
  const d = await getSummary()
  contests.value = d.contests
  loading.value = false
})
</script>

<template>
  <div class="page animate-in">
    <h1 class="page-title">全部比赛</h1>
    <div v-if="loading" class="empty-state"><p>加载中...</p></div>
    <div v-else class="card" style="overflow:hidden">
      <table class="table">
        <thead>
          <tr>
            <th>日期</th>
            <th>名称</th>
            <th class="text-right">队伍</th>
            <th class="text-right">正式</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in contests" :key="c.id">
            <td class="num date-cell">{{ c.date || '-' }}</td>
            <td><router-link :to="`/contest/${c.id}`" class="contest-link">{{ c.title }}</router-link></td>
            <td class="num text-right">{{ c.team_count }}</td>
            <td class="num text-right">{{ c.official_count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; }
.date-cell { color: var(--text-secondary); }
.contest-link { color: var(--text); font-weight: 500; }
.contest-link:hover { color: var(--primary); opacity: 1; }
</style>
