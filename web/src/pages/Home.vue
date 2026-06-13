<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSummary, type ContestSummary, type OrgSummary } from '@/lib/api'
import { initSearch, searchContestant, searchOrg } from '@/lib/search'

const router = useRouter()
const contests = ref<ContestSummary[]>([])
const orgs = ref<OrgSummary[]>([])
const loading = ref(true)
const cq = ref(''), sq = ref('')
const cr = ref<any[]>([]), sr = ref<any[]>([])
const notice = ref('')

onMounted(async () => {
  await initSearch()
  const d = await getSummary()
  contests.value = d.contests
  orgs.value = d.organizations.sort((a:any,b:any)=>((b.champion_冠军||0)-(a.champion_冠军||0))||((b.champion_亚军||0)-(a.champion_亚军||0))||((b.champion_季军||0)-(a.champion_季军||0))||((b.gold||0)-(a.gold||0))||((b.silver||0)-(a.silver||0))||((b.bronze||0)-(a.bronze||0))).slice(0,50)
  loading.value = false
  try {
    const resp = await fetch(import.meta.env.BASE_URL + 'data/announcement.json')
    if (resp.ok) {
      const data = await resp.json()
      notice.value = data.text || ''
    }
  } catch {}
})

watch(cq, (q) => { cr.value = searchContestant(q) })
watch(sq, (q) => { sr.value = searchOrg(q) })
</script>

<template>
  <div class="home">
    <section class="search-hero">
      <div class="search-row">
        <div class="search-wrap">
          <input v-model="cq" type="text" placeholder="搜索选手..." />
          <div v-if="cr.length" class="dd">
            <div v-for="r in cr" :key="r.id" @click="router.push(`/contestant/${r.id}`);cq=''">{{ r.name }}<span class="tag">选手</span></div>
          </div>
        </div>
        <div class="search-wrap">
          <input v-model="sq" type="text" placeholder="搜索学校..." />
          <div v-if="sr.length" class="dd">
            <div v-for="r in sr" :key="r.id" @click="router.push(`/org/${r.id}`);sq=''">{{ r.name }}<span class="tag">学校</span></div>
          </div>
        </div>
      </div>
    </section>

    <section v-if="notice" class="card notice-card">
      <div class="notice-inner">
        <svg class="notice-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        <span class="notice-text">{{ notice }}</span>
      </div>
    </section>

    <div class="cols">
      <section class="card">
        <div class="card-head"><h2>比赛</h2><router-link to="/contests">全部 &rarr;</router-link></div>
        <table class="table" v-if="!loading">
          <thead><tr><th>日期</th><th>名称</th><th class="text-right">队伍</th></tr></thead>
          <tbody><tr v-for="c in contests" :key="c.id"><td class="num">{{ c.date||'-' }}</td><td><router-link :to="`/contest/${c.id}`">{{ c.title }}</router-link></td><td class="num text-right">{{ c.team_count }}</td></tr></tbody>
        </table>
      </section>

      <section class="card">
        <div class="card-head"><h2>学校排行</h2><router-link to="/orgs">全部 &rarr;</router-link></div>
        <table class="table" v-if="!loading">
          <thead><tr><th>#</th><th>学校</th><th class="text-right">冠</th><th class="text-right">亚</th><th class="text-right">季</th><th class="text-right">金</th><th class="text-right">银</th><th class="text-right">铜</th></tr></thead>
          <tbody><tr v-for="(o,i) in orgs" :key="o.id"><td class="num">{{ i+1 }}</td><td><router-link :to="`/org/${o.id}`">{{ o.name }}</router-link></td><td class="num text-right">{{ o.champion_冠军||0 }}</td><td class="num text-right">{{ o.champion_亚军||0 }}</td><td class="num text-right">{{ o.champion_季军||0 }}</td><td class="num text-right">{{ o.gold }}</td><td class="num text-right">{{ o.silver }}</td><td class="num text-right">{{ o.bronze }}</td></tr></tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<style scoped>
.home { display: flex; flex-direction: column; gap: 28px; }
.search-hero { padding: 24px 0 8px; }
.search-row { display: flex; gap: 12px; max-width: 560px; margin: 0 auto; }
.search-wrap { position: relative; flex: 1; }
.search-wrap input { width: 100%; padding: 11px 18px; font-size: 15px; border: 1px solid var(--border); border-radius: 10px; outline: none; background: var(--card); color: var(--text); font-family: inherit; box-shadow: var(--shadow-sm); transition: all var(--transition); }
.search-wrap input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(9,105,218,.1); }
.dd { position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: #fff; border-radius: 8px; box-shadow: 0 12px 40px rgba(0,0,0,.2); z-index: 100; overflow: hidden; }
.dd div { display: flex; justify-content: space-between; padding: 10px 18px; cursor: pointer; color: var(--text); font-size: 14px; border-bottom: 1px solid #f0f0f0; }
.dd div:hover { background: #f6f8fa; }
.tag { font-size: 10px; padding: 2px 8px; border-radius: 10px; background: #f0f0f0; color: #666; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 768px) { .cols { grid-template-columns: 1fr; } }
.notice-card { border-left: 3px solid var(--primary); background: var(--primary-light); }
.notice-inner { display: flex; align-items: flex-start; gap: 12px; padding: 16px 20px; }
.notice-icon { flex-shrink: 0; color: var(--primary); margin-top: 1px; }
.notice-text { font-size: 14px; line-height: 1.6; color: var(--text); }

.card-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 24px; border-bottom: 1px solid var(--border-light); }
.card-head h2 { font-size: 16px; font-weight: 600; }
.card-head a { font-size: 13px; color: var(--text-muted); }
</style>
