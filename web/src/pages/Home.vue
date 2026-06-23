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
const bulletin = ref<{ title: string; items: { text: string }[] } | null>(null)

onMounted(async () => {
  await initSearch()
  const d = await getSummary()
  contests.value = d.contests
  orgs.value = d.organizations.sort((a: any, b: any) =>
    ((b.champion_冠军 || 0) - (a.champion_冠军 || 0)) ||
    ((b.champion_亚军 || 0) - (a.champion_亚军 || 0)) ||
    ((b.champion_季军 || 0) - (a.champion_季军 || 0)) ||
    ((b.gold || 0) - (a.gold || 0)) ||
    ((b.silver || 0) - (a.silver || 0)) ||
    ((b.bronze || 0) - (a.bronze || 0))
  ).slice(0, 50)
  loading.value = false
  try {
    const resp = await fetch(import.meta.env.BASE_URL + 'data/announcement.json')
    if (resp.ok) {
      const data = await resp.json()
      if (data.title && data.items?.length) {
        bulletin.value = data
      }
    }
  } catch { }
})

watch(cq, (q) => { cr.value = searchContestant(q) })
watch(sq, (q) => { sr.value = searchOrg(q) })
</script>

<template>
  <div class="home">
    <!-- Hero Search -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">大学生程序设计竞赛数据平台</h1>
        <p class="hero-sub">追踪 ICPC / CCPC 参赛数据，探索学校与选手表现</p>
        <div class="search-row">
          <div class="search-wrap">
            <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <input v-model="cq" type="text" placeholder="搜索选手..." />
            <div v-if="cr.length" class="dd">
              <div v-for="r in cr" :key="r.id" @click="router.push(`/contestant/${r.id}`); cq = ''">
                {{ r.name }}
                <span class="tag">选手</span>
              </div>
            </div>
          </div>
          <div class="search-wrap">
            <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <input v-model="sq" type="text" placeholder="搜索学校..." />
            <div v-if="sr.length" class="dd">
              <div v-for="r in sr" :key="r.id" @click="router.push(`/org/${r.id}`); sq = ''">
                {{ r.name }}
                <span class="tag">学校</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Bulletin Board -->
    <section v-if="bulletin" class="card bulletin">
      <div class="bulletin-head">
        <svg class="bulletin-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        <h2>{{ bulletin.title }}</h2>
      </div>
      <ul class="bulletin-list">
        <li v-for="(item, i) in bulletin.items" :key="i">
          <span class="bulletin-dot"></span>
          {{ item.text }}
        </li>
      </ul>
    </section>

    <!-- Main Grid -->
    <div class="cols">
      <!-- Contests -->
      <section class="card panel">
        <div class="panel-head">
          <h2>近期比赛</h2>
          <router-link to="/contests" class="see-all">全部 &rarr;</router-link>
        </div>
        <div v-if="loading" class="skel-wrap">
          <div class="skeleton" v-for="i in 5" :key="i" style="height:18px;margin-bottom:10px;width:100%"></div>
        </div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>日期</th>
              <th>名称</th>
              <th class="text-right">队伍</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in contests" :key="c.id" class="animate-in" :style="{ animationDelay: `${contests.indexOf(c) * 30}ms` }">
              <td class="num date-cell">{{ c.date || '-' }}</td>
              <td class="title-cell"><router-link :to="`/contest/${c.id}`">{{ c.title }}</router-link></td>
              <td class="num text-right">{{ c.team_count }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Orgs -->
      <section class="card panel">
        <div class="panel-head">
          <h2>学校排行</h2>
          <router-link to="/orgs" class="see-all">全部 &rarr;</router-link>
        </div>
        <div v-if="loading" class="skel-wrap">
          <div class="skeleton" v-for="i in 5" :key="i" style="height:18px;margin-bottom:10px;width:100%"></div>
        </div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>学校</th>
              <th class="text-right">冠</th>
              <th class="text-right">亚</th>
              <th class="text-right">季</th>
              <th class="text-right">金</th>
              <th class="text-right">银</th>
              <th class="text-right">铜</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(o, i) in orgs" :key="o.id" class="animate-in" :style="{ animationDelay: `${i * 30}ms` }">
              <td class="num rank-cell">{{ i + 1 }}</td>
              <td><router-link :to="`/org/${o.id}`">{{ o.name }}</router-link></td>
              <td class="num text-right">{{ o.champion_冠军 || 0 }}</td>
              <td class="num text-right">{{ o.champion_亚军 || 0 }}</td>
              <td class="num text-right">{{ o.champion_季军 || 0 }}</td>
              <td class="num text-right">{{ o.gold }}</td>
              <td class="num text-right">{{ o.silver }}</td>
              <td class="num text-right">{{ o.bronze }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<style scoped>
.home { display: flex; flex-direction: column; gap: 32px; }

/* Hero */
.hero {
  padding: 16px 0 8px;
  text-align: center;
}
.hero-title {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--text);
  margin-bottom: 8px;
}
.hero-sub {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

/* Search */
.search-row {
  display: flex;
  gap: 12px;
  max-width: 560px;
  margin: 0 auto;
}
.search-wrap {
  position: relative;
  flex: 1;
}
.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}
.search-wrap input {
  width: 100%;
  padding: 12px 18px 12px 40px;
  font-size: 15px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  outline: none;
  background: var(--card);
  color: var(--text);
  font-family: inherit;
  transition: all var(--transition);
}
.search-wrap input::placeholder { color: var(--text-muted); }
.search-wrap input:focus {
  border-color: var(--primary-border);
  box-shadow: 0 0 0 3px var(--primary-bg);
}

/* Dropdown */
.dd {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  z-index: 100;
  overflow: hidden;
}
[data-theme="dark"] .dd {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}
.dd div {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 18px;
  cursor: pointer;
  color: var(--text);
  font-size: 14px;
  border-bottom: 1px solid var(--border-light);
  transition: background var(--transition);
}
.dd div:last-child { border-bottom: none; }
.dd div:hover { background: var(--card-hover); }
.tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 99px;
  background: var(--primary-bg);
  color: var(--primary);
  font-weight: 500;
}

/* Bulletin */
.bulletin {
  overflow: hidden;
  border-left: 3px solid var(--primary);
}
.bulletin-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 24px 0;
}
.bulletin-head h2 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}
.bulletin-icon {
  flex-shrink: 0;
  color: var(--primary);
}
.bulletin-list {
  list-style: none;
  padding: 14px 24px 20px;
}
.bulletin-list li {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 7px 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}
.bulletin-dot {
  flex-shrink: 0;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--primary);
  margin-top: 7px;
  opacity: 0.6;
}

/* Panels */
.panel { overflow: hidden; }
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-light);
}
.panel-head h2 { font-size: 16px; font-weight: 600; color: var(--text); }
.see-all { font-size: 13px; color: var(--text-muted); font-weight: 500; }
.see-all:hover { color: var(--primary); opacity: 1; }
.skel-wrap { padding: 16px 24px; }
.date-cell { color: var(--text-secondary); }
.title-cell a { color: var(--text); font-weight: 500; }
.title-cell a:hover { color: var(--primary); opacity: 1; }
.rank-cell { color: var(--text-muted); font-weight: 500; }

/* Grid */
.cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
@media (max-width: 768px) {
  .cols { grid-template-columns: 1fr; }
  .hero-title { font-size: 22px; }
}
</style>
