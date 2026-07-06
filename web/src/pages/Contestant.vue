<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContestant, getPlayerRatingDetail, getContests, type ContestSummary } from '@/lib/api'
import { ratingColor } from '@/lib/colors'

const route = useRoute(); const router = useRouter(); const data = ref<any>(null); const rdata = ref<any>(null)
const loading = ref(true); const err = ref(false); const tiers = ref<Record<string,string>>({})
const TL: Record<string,string> = {final:'决赛',regional:'区域赛',invitational:'邀请赛',provincial:'省赛',preliminary:'网络赛'}
const TC: Record<string,string> = {final:'#ef4444',regional:'#3b82f6',invitational:'#fbbf24',provincial:'var(--fg3)',preliminary:'#8b5cf6'}
const TO = ['final','regional','invitational','provincial','preliminary']

onMounted(async () => { try { const [d,r,cs] = await Promise.all([getContestant(route.params.id as string), getPlayerRatingDetail(route.params.id as string).catch(()=>null), getContests().catch(()=>[] as ContestSummary[])]); data.value=d; rdata.value=r; for(const c of cs) tiers.value[c.id]=c.tier||'provincial' } catch { err.value=true }; loading.value=false })

const rmap = computed(() => { const m: Record<string,any> = {}; const h = rdata.value?.history||[]; for(let i=0;i<h.length;i++){const cur=h[i];const prev=i>0?h[i-1]:null;m[cur.contest_id]={after:cur.rating,perf:cur.perf,delta:prev?cur.rating-prev.rating:null}};return m })
const cr = computed(() => { const h = rdata.value?.history; return h?.length ? h[h.length-1].rating : null })
const fd = (d:number|null) => d===null||d===undefined?'-':(d>0?'+':'')+d.toFixed(0)
const ml: Record<string,string> = {gold:'金奖',silver:'银奖',bronze:'铜奖'}

function getTierRecords(tier: string) {
  if (!data.value?.records) return []
  const tmap: Record<string,string> = tiers.value || {}
  return data.value.records.filter((r: any) => tmap[r.contest_id] === tier).sort((a: any, b: any) => b.date.localeCompare(a.date))
}

const cd = computed(() => {
  const h = rdata.value?.history||[]; if(h.length<2)return null
  const ratings = h.map((r:any)=>r.rating); const lo=Math.floor(Math.min(...ratings)/50)*50-25; const hi=Math.ceil(Math.max(...ratings)/50)*50+25; const rng=hi-lo||1
  const W=720,H=230,pl=54,pr=16,pt=24,pb=36; const pw=W-pl-pr,ph=H-pt-pb
  const pts = h.map((r:any,i:number)=>({x:pl+(i/Math.max(h.length-1,1))*pw, y:pt+ph-((r.rating-lo)/rng)*ph, r:r.rating, d:(r.date||'').slice(2).replace(/-/g,'/')}))
  const line = pts.map((p,i)=>`${i===0?'M':'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
  const fill = line+` L${pts[pts.length-1].x.toFixed(1)},${pt+ph} L${pts[0].x.toFixed(1)},${pt+ph} Z`
  const grid: {y:number,l:string}[] = []; for(let i=0;i<=4;i++){const v=lo+(rng*i/4);grid.push({y:pt+ph-((v-lo)/rng)*ph,l:v.toFixed(0)})}
  return {W,H,pl,pt,pb,pr,pts,line,fill,grid}
})
const li = computed(() => { const h=rdata.value?.history||[]; if(h.length<=6)return h.map((_:any,i:number)=>i); const step=Math.max(1,Math.floor(h.length/5)); const idx:number[]=[];for(let i=0;i<h.length;i+=step)idx.push(i);if(idx[idx.length-1]!==h.length-1)idx.push(h.length-1);return idx })
</script>

<template>
<div v-if="loading" class="empty">加载中...</div>
<div v-else-if="err||!data" class="empty">选手不存在</div>
<div v-else style="max-width:900px;margin:0 auto">
  <button class="back" @click="router.back()">← 返回</button>

  <div class="card profile-card" style="padding:24px 28px;margin-bottom:28px;display:flex;align-items:center;justify-content:space-between;gap:24px">
    <div>
        <h1 style="font-size:24px;font-weight:700;letter-spacing:-.3px;line-height:1.2">{{ data.name }}</h1>
        <p style="font-size:14.5px;margin-top:3px"><router-link :to="`/org/${data.org_id||data.organization}`" style="color:var(--accent)">{{ data.organization }}</router-link></p>
        <div style="display:flex;align-items:center;gap:8px;margin-top:5px;font-size:13px;color:var(--fg3)">
          <span v-if="data.gender" style="font-size:10.5px;padding:2px 8px;border-radius:99px;background:var(--accent-glow);color:var(--accent);font-weight:500">{{ data.gender==='male'?'男':'女' }}</span>
          <span>{{ data.records.length }} 场比赛</span>
        </div>
    </div>
    <div v-if="cr" style="text-align:center;flex-shrink:0;padding:16px 26px;border-radius:var(--r);background:var(--bg3);border:1px solid var(--line2);animation:pulse 2s ease-in-out infinite">
      <div style="font-size:9.5px;font-weight:600;color:var(--fg3);text-transform:uppercase;letter-spacing:.6px">Rating</div>
      <div style="font-size:34px;font-weight:700;line-height:1.1;margin-top:4px">
        <template v-if="cr >= 3000">
          <span style="color:var(--fg)">{{ cr.toFixed(0)[0] }}</span><span :style="{color:ratingColor(cr)}">{{ cr.toFixed(0).slice(1) }}</span>
        </template>
        <span v-else :style="{color:ratingColor(cr)}">{{ cr.toFixed(0) }}</span>
      </div>
    </div>
  </div>

  <div v-if="cd" class="card" style="margin-bottom:24px;overflow:hidden">
    <div class="sec-head"><h2>Rating 变化曲线</h2></div>
    <div style="padding:0 0 8px">
      <svg :viewBox="`0 0 ${cd.W} ${cd.H}`" style="width:100%;display:block" preserveAspectRatio="xMidYMid meet">
        <g v-for="gl in cd.grid" :key="gl.l"><line :x1="cd.pl" :y1="gl.y" :x2="cd.W-cd.pr" :y2="gl.y" style="stroke:var(--line2);stroke-width:.5"/><text :x="cd.pl-8" :y="gl.y+4" style="fill:var(--fg4);font-size:10px;text-anchor:end">{{ gl.l }}</text></g>
        <path :d="cd.fill" class="ca"/><path :d="cd.line" class="cl"/>
        <circle v-for="(pt,i) in cd.pts" :key="i" :cx="pt.x.toFixed(1)" :cy="pt.y.toFixed(1)" r="3" class="cd"/>
        <text v-for="i in li" :key="i" :x="cd.pts[i].x.toFixed(1)" :y="cd.H-8" style="fill:var(--fg4);font-size:9px;text-anchor:middle">{{ cd.pts[i].d }}</text>
      </svg>
    </div>
  </div>

  <div v-for="t in TO" :key="t" style="margin-bottom:28px">
    <div class="card">
      <div class="tier-header" style="display:flex;align-items:center;gap:12px;padding:14px 18px 10px;border-bottom:1px solid var(--line2);flex-wrap:wrap">
        <span style="font-size:16px;font-weight:700" :style="{color:TC[t]}">{{ TL[t] }}</span>
        <template v-if="data.medal_summary_by_tier?.[t]">
          <span class="mc" :class="{z:!data.medal_summary_by_tier[t].champion}" style="color:#ef4444">冠 {{ data.medal_summary_by_tier[t].champion }}</span>
          <span class="mc" :class="{z:!data.medal_summary_by_tier[t].runner_up}" style="color:#3b82f6">亚 {{ data.medal_summary_by_tier[t].runner_up }}</span>
          <span class="mc" :class="{z:!data.medal_summary_by_tier[t].third}" style="color:#fb923c">季 {{ data.medal_summary_by_tier[t].third }}</span>
          <span class="mc" :class="{z:!data.medal_summary_by_tier[t].gold}" style="color:var(--gold)">金 {{ data.medal_summary_by_tier[t].gold }}</span>
          <span class="mc" :class="{z:!data.medal_summary_by_tier[t].silver}" style="color:var(--silver)">银 {{ data.medal_summary_by_tier[t].silver }}</span>
          <span class="mc" :class="{z:!data.medal_summary_by_tier[t].bronze}" style="color:var(--bronze)">铜 {{ data.medal_summary_by_tier[t].bronze }}</span>
        </template>
      </div>
      <table class="tbl" v-if="getTierRecords(t).length" style="table-layout:fixed">
        <thead><tr><th style="width:90px">日期</th><th style="width:auto">比赛</th><th style="width:110px">队伍</th><th class="rt" style="width:76px">排名</th><th class="rt" style="width:76px">Rating</th><th style="width:60px">奖项</th></tr></thead>
        <tbody><tr v-for="(r,ri) in getTierRecords(t)" :key="`${r.contest_id}-${r.team_name}`">
          <td class="tnum muted" style="font-size:13px;width:90px;white-space:nowrap">{{ r.date }}</td>
          <td><router-link :to="`/contest/${r.contest_id}`" style="color:var(--accent);font-size:13.5px;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ r.contest_title }}</router-link></td>
          <td style="width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px;color:var(--fg3)">{{ r.team_name }}</td>
          <td class="tnum rt" style="font-size:13px;width:76px"><span v-if="r.official">{{ r.rank }}<span class="faint" style="font-weight:400;margin:0 1px">/</span>{{ r.official_rank }}</span><span v-else class="faint" style="font-style:italic">{{ r.rank }}</span></td>
          <td class="tnum rt" style="width:76px"><template v-if="rmap[r.contest_id]"><template v-if="rmap[r.contest_id].after >= 3000"><span style="font-weight:650;color:var(--fg)">{{ rmap[r.contest_id].after.toFixed(0)[0] }}</span><span :style="{color:ratingColor(rmap[r.contest_id].after),fontWeight:650}">{{ rmap[r.contest_id].after.toFixed(0).slice(1) }}</span></template><span v-else :style="{color:ratingColor(rmap[r.contest_id].after),fontWeight:650}">{{ rmap[r.contest_id].after?.toFixed(0)??'-' }}</span><span v-if="rmap[r.contest_id].delta!==null" class="delta" style="font-size:10.5px;margin-left:3px;white-space:nowrap" :class="rmap[r.contest_id].delta>0?'d-up':rmap[r.contest_id].delta<0?'d-down':''">{{ fd(rmap[r.contest_id].delta) }}</span></template><span v-else class="faint">-</span></td>
          <td style="width:60px"><span v-if="r.medal" class="badge" :class="`badge-${r.medal}`">{{ ml[r.medal] }}</span><span v-else class="faint">-</span></td>
        </tr></tbody>
      </table>
      <div v-else class="faint" style="padding:14px 18px;font-size:13px">暂无参赛记录</div>
    </div>
  </div>
</div>
</template>

<style scoped>
@keyframes slideIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.profile-card{animation:slideIn .5s cubic-bezier(.16,1,.3,1) both}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 var(--accent-glow)}50%{box-shadow:0 0 20px 4px var(--accent-glow)}}
.mc{font-size:11.5px;font-weight:600;margin-right:10px;white-space:nowrap}.mc.z{opacity:.18}
.ca{fill:var(--accent-glow)}.cl{fill:none;stroke:var(--accent);stroke-width:2;stroke-linejoin:round;stroke-linecap:round;stroke-dasharray:2000;stroke-dashoffset:2000;animation:drawLine 2s .5s cubic-bezier(.16,1,.3,1) forwards}
@keyframes drawLine{to{stroke-dashoffset:0}}
.cd{fill:var(--accent);opacity:0;animation:dotIn .3s .8s ease forwards}
.cd:nth-child(odd){animation-delay:.85s}.cd:nth-child(even){animation-delay:.9s}
@keyframes dotIn{to{opacity:1}}

@media(max-width:768px){
  .profile-card{flex-direction:column;align-items:flex-start!important;gap:16px;padding:18px 20px!important}
  .mc{font-size:10.5px;margin-right:6px}
  .tbl thead th{font-size:10px;padding:8px 4px}
  .tbl tbody td{padding:8px 4px;font-size:12.5px}
}
@media(max-width:480px){
  .profile-card{gap:12px;padding:14px 16px!important}
  .tier-header{gap:6px!important;padding:10px 12px 8px!important}
  .tier-header span:first-child{font-size:14px!important}
  .mc{font-size:9.5px;margin-right:3px}
  .tbl thead th{font-size:9.5px;padding:6px 3px}
  .tbl tbody td{padding:6px 3px;font-size:11.5px}
  .tbl thead th:nth-child(3){display:none}
  .tbl tbody td:nth-child(3){display:none}
  .tbl thead th:nth-child(4){display:none}
  .tbl tbody td:nth-child(4){display:none}
  .tbl thead th:nth-child(1){width:55px!important}
  .tbl thead th:nth-child(5){width:52px!important;font-size:9px}
  .tbl thead th:nth-child(6){width:36px!important}
  .delta{font-size:9px!important;margin-left:1px!important}
  .badge{font-size:9px!important;padding:1px 6px!important}
}
</style>
