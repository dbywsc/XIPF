<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContestant } from '@/lib/api'

const route = useRoute(); const router = useRouter()
const data = ref<any>(null); const loading = ref(true)

onMounted(async () => {
  try { data.value = await getContestant(route.params.id as string) } catch { data.value = null }
  loading.value = false
})

const ml: Record<string,string> = { gold:'金奖', silver:'银奖', bronze:'铜奖' }
</script>

<template>
  <div v-if="loading" class="empty-state"><p>加载中...</p></div>
  <div v-else-if="!data" class="empty-state"><p>选手不存在</p></div>
  <div v-else class="page">
    <button class="back-link" @click="router.back()">&larr; 返回</button>
    <div class="card profile">
      <div class="avatar">{{ data.name[0] }}</div>
      <div class="info">
        <h1>{{ data.name }}</h1>
        <p class="org"><router-link :to="`/org/${data.org_id||data.organization}`">{{ data.organization }}</router-link></p>
        <p class="meta">{{ data.gender ? (data.gender==='male'?'男':'女')+' &middot; ' : '' }}共 {{ data.records.length }} 场比赛</p>
      </div>
    </div>

    <div class="card stats">
      <h2>获奖统计</h2>
      <div class="grid">
        <div class="stat"><div class="n" style="color:#cf222e">{{ data.medal_summary?.champion||0 }}</div><div class="l">冠军</div></div>
        <div class="stat"><div class="n" style="color:#bf8700">{{ data.medal_summary?.runner_up||0 }}</div><div class="l">亚军</div></div>
        <div class="stat"><div class="n" style="color:#9a4e00">{{ data.medal_summary?.third||0 }}</div><div class="l">季军</div></div>
        <div class="stat"><div class="n" style="color:#bf8700">{{ data.medal_summary?.gold||0 }}</div><div class="l">金牌</div></div>
        <div class="stat"><div class="n" style="color:#656d76">{{ data.medal_summary?.silver||0 }}</div><div class="l">银牌</div></div>
        <div class="stat"><div class="n" style="color:#9a4e00">{{ data.medal_summary?.bronze||0 }}</div><div class="l">铜牌</div></div>
      </div>
    </div>

    <div class="card">
      <h2 style="padding:20px 24px 0;font-size:16px;font-weight:600;margin-bottom:8px">参赛记录</h2>
      <table class="table">
        <thead><tr><th>日期</th><th>比赛</th><th>队伍</th><th class="text-right">排名</th><th>奖牌</th></tr></thead>
        <tbody>
          <tr v-for="r in data.records" :key="`${r.contest_id}-${r.team_name}`">
            <td class="num">{{ r.date }}</td>
            <td><router-link :to="`/contest/${r.contest_id}`">{{ r.contest_title }}</router-link></td>
            <td>{{ r.team_name }}</td>
            <td class="num text-right">{{ r.rank }}</td>
            <td><span v-if="r.medal" class="badge" :class="`badge-${r.medal}`">{{ ml[r.medal] }}</span><span v-else class="no">-</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 800px; margin: 0 auto; }
.profile { display: flex; align-items: center; gap: 24px; padding: 28px; margin-bottom: 24px; }
.avatar { width: 68px; height: 68px; border-radius: 50%; background: linear-gradient(135deg, #0969da, #0550ae); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 700; flex-shrink: 0; box-shadow: 0 4px 12px rgba(9,105,218,.3); }
.info h1 { font-size: 24px; font-weight: 700; }
.org { font-size: 15px; margin-top: 2px; }
.meta { color: var(--text-muted); font-size: 14px; margin-top: 4px; }
.stats { padding: 20px 24px; margin-bottom: 24px; }
.stats h2 { font-size: 15px; font-weight: 600; margin-bottom: 16px; }
.grid { display: flex; gap: 36px; }
.stat { text-align: center; }
.n { font-size: 34px; font-weight: 700; line-height: 1.2; }
.l { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }
.no { color: var(--text-muted); }
.card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-sm); margin-bottom: 24px; overflow: hidden; }
</style>
