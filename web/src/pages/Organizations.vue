<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getOrganizations, getSchoolsRatings, type SchoolRating } from '@/lib/api'
import { initSearch, searchOrg } from '@/lib/search'
import { ratingColor } from '@/lib/colors'

const list = ref<any[]>([]); const loading = ref(true); const q = ref(''); const all = ref<any[]>([])

onMounted(async () => {
  await initSearch()
  const [o, r] = await Promise.all([
    getOrganizations(),
    getSchoolsRatings().catch(() => [] as SchoolRating[]),
  ])
  // Build a map from school name to rating data (try trimmed name matching)
  const rm = new Map<string, SchoolRating>()
  for (const s of r) {
    rm.set(s.name.trim(), s)
    // Also add without trimming for fallback
    if (s.name !== s.name.trim()) rm.set(s.name, s)
  }
  // Merge org stats with school ratings by name
  all.value = o
    .map((org: any) => {
      const rt = rm.get(org.name.trim()) || rm.get(org.name) || null
      return {
        ...org,
        rating: rt?.rating ?? null,
        rc: rt?.contests ?? 0,
        org_rating_id: rt?.id ?? null,
      }
    })
    .sort((a: any, b: any) => (b.rating ?? -Infinity) - (a.rating ?? -Infinity))
  list.value = all.value
  loading.value = false
})

// Build lookup after data loads
function lookup(r: any) {
  for (const o of all.value) {
    if (o.name.trim() === r.name.trim()) return o
    if (o.org_rating_id && o.org_rating_id === r.id) return o
  }
  return null
}

watch(q, v => {
  if (!v.trim()) {
    list.value = all.value
    return
  }
  const results = searchOrg(v)
  const matched = results
    .map(r => lookup(r) || r)
    .filter((item: any) => item.rating !== undefined || item.name)
  matched.sort((a: any, b: any) => (b.rating ?? -Infinity) - (a.rating ?? -Infinity))
  list.value = matched
})
</script>

<template>
<div style="max-width:960px;margin:0 auto"><h1 class="page-title">学校排行</h1>
  <div class="srch" style="margin-bottom:18px;max-width:320px"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg><input v-model="q" placeholder="搜索学校..."/></div>
  <div v-if="loading" class="empty">加载中...</div>
  <div v-else class="card">
    <table class="tbl"><thead><tr><th style="width:52px">#</th><th>学校</th><th class="rt" style="width:92px">Rating</th><th class="rt" style="width:54px">场次</th></tr></thead>
      <tbody><tr v-for="(o,i) in list" :key="o.id" class="clickable row-anim" :style="{animationDelay:`${i*20}ms`}" @click="$router.push(`/org/${o.id}`)">
        <td class="tnum muted">{{ i+1 }}</td><td style="font-weight:600;font-size:14px">{{ o.name }}</td>
        <td class="tnum rt">
          <template v-if="o.rating !== null && o.rating >= 3000">
            <span style="font-weight:650;color:var(--fg)">{{ o.rating.toFixed(0)[0] }}</span><span :style="{color:ratingColor(o.rating),fontWeight:650}">{{ o.rating.toFixed(0).slice(1) }}</span>
          </template>
          <span v-else-if="o.rating !== null" :style="{color:ratingColor(o.rating),fontWeight:650}">{{ o.rating.toFixed(0) }}</span>
          <span v-else class="faint">-</span>
        </td><td class="tnum rt muted">{{ o.rc||o.count }}</td>
      </tr></tbody>
    </table>
  </div>
</div>
</template>

<style scoped>
@media(max-width:480px){
  .tbl thead th:nth-child(3),.tbl tbody td:nth-child(3),
  .tbl thead th:nth-child(4),.tbl tbody td:nth-child(4){display:none}
}
</style>
