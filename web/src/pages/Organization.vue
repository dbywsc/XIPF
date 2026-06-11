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
    members.value = s.contestants.filter((c:any)=>c.org===od.name).sort((a:any,b:any)=>((b.medals?.champion||0)-(a.medals?.champion||0))||((b.medals?.runner_up||0)-(a.medals?.runner_up||0))||((b.medals?.third||0)-(a.medals?.third||0))||((b.medals?.gold||0)-(a.medals?.gold||0))||((b.medals?.silver||0)-(a.medals?.silver||0))||((b.medals?.bronze||0)-(a.medals?.bronze||0)))
  } catch { data.value = null }
  loading.value = false
})
</script>

<template>
  <div v-if="loading" class="empty-state"><p>加载中...</p></div>
  <div v-else-if="!data" class="empty-state"><p>学校不存在</p></div>
  <div v-else class="page">
    <button class="back-link" @click="router.back()">&larr; 返回</button>
    <div class="card profile"><h1>{{ data.name }}</h1></div>

    <div class="card stats">
      <h2>获奖统计</h2>
      <div class="grid">
        <div class="stat"><div class="n" style="color:#cf222e">{{ data.stats?.champion_冠军||0 }}</div><div class="l">冠军</div></div>
        <div class="stat"><div class="n" style="color:#bf8700">{{ data.stats?.champion_亚军||0 }}</div><div class="l">亚军</div></div>
        <div class="stat"><div class="n" style="color:#9a4e00">{{ data.stats?.champion_季军||0 }}</div><div class="l">季军</div></div>
        <div class="stat"><div class="n" style="color:#bf8700">{{ data.stats?.gold||0 }}</div><div class="l">金牌</div></div>
        <div class="stat"><div class="n" style="color:#656d76">{{ data.stats?.silver||0 }}</div><div class="l">银牌</div></div>
        <div class="stat"><div class="n" style="color:#9a4e00">{{ data.stats?.bronze||0 }}</div><div class="l">铜牌</div></div>
        <div class="stat"><div class="n">{{ data.stats?.count||0 }}</div><div class="l">总参赛</div></div>
      </div>
    </div>

    <div class="card" v-if="members.length">
      <h2 style="padding:20px 24px 0;font-size:15px;font-weight:600;margin-bottom:8px">选手</h2>
      <table class="table">
        <thead><tr><th>姓名</th><th class="text-right">参赛</th><th class="text-right">冠</th><th class="text-right">亚</th><th class="text-right">季</th><th class="text-right">金</th><th class="text-right">银</th><th class="text-right">铜</th></tr></thead>
        <tbody><tr v-for="m in members" :key="m.id"><td><router-link :to="`/contestant/${m.id}`">{{ m.name }}</router-link></td><td class="num text-right">{{ m.record_count }}</td><td class="num text-right">{{ m.medals?.champion||0 }}</td><td class="num text-right">{{ m.medals?.runner_up||0 }}</td><td class="num text-right">{{ m.medals?.third||0 }}</td><td class="num text-right">{{ m.medals?.gold }}</td><td class="num text-right">{{ m.medals?.silver }}</td><td class="num text-right">{{ m.medals?.bronze }}</td></tr></tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; }
.profile { padding: 28px; margin-bottom: 24px; }
.profile h1 { font-size: 24px; font-weight: 700; }
.stats { padding: 20px 24px; margin-bottom: 24px; }
.stats h2 { font-size: 15px; font-weight: 600; margin-bottom: 16px; }
.grid { display: flex; gap: 32px; flex-wrap: wrap; }
.stat { text-align: center; }
.n { font-size: 32px; font-weight: 700; line-height: 1.2; }
.l { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-sm); margin-bottom: 24px; overflow: hidden; }
</style>
