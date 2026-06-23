<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrganization, getSummary } from '@/lib/api'

const route = useRoute(); const router = useRouter()
const data = ref<any>(null); const members = ref<any[]>([]); const loading = ref(true)

onMounted(async () => {
  try {
    const [od, s] = await Promise.all([getOrganization(route.params.id as string), getSummary()])
    data.value = od
    members.value = s.contestants
      .filter((c: any) => c.org === od.name)
      .sort((a: any, b: any) =>
        ((b.medals?.champion || 0) - (a.medals?.champion || 0)) ||
        ((b.medals?.runner_up || 0) - (a.medals?.runner_up || 0)) ||
        ((b.medals?.third || 0) - (a.medals?.third || 0)) ||
        ((b.medals?.gold || 0) - (a.medals?.gold || 0)) ||
        ((b.medals?.silver || 0) - (a.medals?.silver || 0)) ||
        ((b.medals?.bronze || 0) - (a.medals?.bronze || 0))
      )
  } catch { data.value = null }
  loading.value = false
})
</script>

<template>
  <div v-if="loading" class="empty-state"><p>加载中...</p></div>
  <div v-else-if="!data" class="empty-state"><p>学校不存在</p></div>
  <div v-else class="page animate-in">
    <button class="back-link" @click="router.back()">&larr; 返回</button>

    <div class="card profile-card">
      <h1>{{ data.name }}</h1>
    </div>

    <!-- Stats -->
    <div class="card stats-card">
      <h2>获奖统计</h2>
      <div class="medal-grid">
        <div class="medal-item">
          <div class="medal-num" style="color: var(--champion)">{{ data.stats?.champion_冠军 || 0 }}</div>
          <div class="medal-label">冠军</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--gold)">{{ data.stats?.champion_亚军 || 0 }}</div>
          <div class="medal-label">亚军</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--bronze)">{{ data.stats?.champion_季军 || 0 }}</div>
          <div class="medal-label">季军</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--gold)">{{ data.stats?.gold || 0 }}</div>
          <div class="medal-label">金牌</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--silver)">{{ data.stats?.silver || 0 }}</div>
          <div class="medal-label">银牌</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--bronze)">{{ data.stats?.bronze || 0 }}</div>
          <div class="medal-label">铜牌</div>
        </div>
        <div class="medal-item">
          <div class="medal-num">{{ data.stats?.count || 0 }}</div>
          <div class="medal-label">总参赛</div>
        </div>
      </div>
    </div>

    <!-- Members -->
    <div class="card" v-if="members.length">
      <div class="section-head">
        <h2>选手</h2>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>姓名</th>
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
          <tr v-for="m in members" :key="m.id">
            <td><router-link :to="`/contestant/${m.id}`">{{ m.name }}</router-link></td>
            <td class="num text-right">{{ m.record_count }}</td>
            <td class="num text-right">{{ m.medals?.champion || 0 }}</td>
            <td class="num text-right">{{ m.medals?.runner_up || 0 }}</td>
            <td class="num text-right">{{ m.medals?.third || 0 }}</td>
            <td class="num text-right">{{ m.medals?.gold }}</td>
            <td class="num text-right">{{ m.medals?.silver }}</td>
            <td class="num text-right">{{ m.medals?.bronze }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; }

.profile-card { padding: 28px; margin-bottom: 24px; }
.profile-card h1 { font-size: 24px; font-weight: 700; letter-spacing: -0.3px; }

.stats-card { padding: 24px 28px; margin-bottom: 24px; }
.stats-card h2 { font-size: 15px; font-weight: 600; margin-bottom: 20px; }

.medal-grid { display: flex; gap: 40px; flex-wrap: wrap; }
.medal-item { text-align: center; }
.medal-num { font-size: 32px; font-weight: 700; line-height: 1.1; }
.medal-label { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }

.section-head {
  padding: 20px 24px 0;
  margin-bottom: 8px;
}
.section-head h2 { font-size: 15px; font-weight: 600; }
</style>
