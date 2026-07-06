<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getPlayersRatings, type PlayerRating } from '@/lib/api'
import { initSearch, searchContestant } from '@/lib/search'
import { ratingColor } from '@/lib/colors'

const PAGE = 100
const list = ref<PlayerRating[]>([]); const loading = ref(true)
const q = ref(''); const all = ref<PlayerRating[]>([])
const shown = ref(PAGE)
const searching = ref(false)

onMounted(async () => { await initSearch(); all.value = await getPlayersRatings().catch(() => []); list.value = all.value.slice(0, PAGE); loading.value = false })

watch(q, v => {
  if (!v.trim()) { searching.value = false; list.value = all.value.slice(0, PAGE); shown.value = PAGE; return }
  searching.value = true
  const ids = new Set(searchContestant(v).map(r => r.id))
  list.value = all.value.filter(p => ids.has(p.id))
})

function loadMore() { shown.value += PAGE; list.value = all.value.slice(0, shown.value) }
</script>

<template>
<div style="max-width:1040px;margin:0 auto"><h1 class="page-title">选手排行</h1>
  <div class="srch" style="margin-bottom:18px;max-width:320px"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg><input v-model="q" placeholder="搜索选手..."/></div>
  <div v-if="loading" class="empty">加载中...</div>
  <div v-else class="card">
    <table class="tbl"><thead><tr><th style="width:52px">#</th><th>姓名</th><th>学校</th><th class="rt" style="width:92px">Rating</th><th class="rt" style="width:54px">场次</th></tr></thead>
      <tbody><tr v-for="(c,i) in list" :key="c.id" class="clickable row-anim" :style="{animationDelay:`${(i%PAGE)*10}ms`}" @click="$router.push(`/contestant/${c.id}`)">
        <td class="tnum muted">{{ i+1 }}</td><td style="font-weight:600;font-size:14px">{{ c.name }}</td><td class="muted" style="font-size:13px"><router-link :to="`/org/${c.org_id}`" @click.stop style="color:var(--fg3)">{{ c.org }}</router-link></td>
        <td class="tnum rt">
          <template v-if="c.rating >= 3000">
            <span style="font-weight:650;color:var(--fg)">{{ c.rating.toFixed(0)[0] }}</span><span :style="{color:ratingColor(c.rating),fontWeight:650}">{{ c.rating.toFixed(0).slice(1) }}</span>
          </template>
          <span v-else :style="{color:ratingColor(c.rating),fontWeight:650}">{{ c.rating.toFixed(0) }}</span>
        </td><td class="tnum rt muted">{{ c.contests }}</td>
      </tr></tbody>
    </table>
  </div>
  <div v-if="!searching && list.length < all.length" style="text-align:center;padding:24px">
    <button @click="loadMore" class="lm">加载更多（{{ list.length }} / {{ all.length }}）</button>
  </div>
</div>
</template>

<style scoped>
.lm{font-size:13.5px;font-weight:500;color:var(--fg2);padding:8px 24px;border:1px solid var(--line2);border-radius:var(--r);background:var(--bg4);cursor:pointer;font-family:inherit;transition:all .2s}
.lm:hover{color:var(--fg);border-color:var(--accent);background:var(--accent-glow)}

@media(max-width:480px){
  .tbl thead th:nth-child(3),.tbl tbody td:nth-child(3){display:none}
}
</style>
