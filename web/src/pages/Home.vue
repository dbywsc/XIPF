<script setup lang="ts">
import { ref, onMounted } from 'vue'

const mounted = ref(false)
const announcement = ref<{ title: string; items: { text: string }[] } | null>(null)

onMounted(async () => {
  mounted.value = true
  try {
    const resp = await fetch(import.meta.env.BASE_URL + 'data/announcement.json')
    announcement.value = await resp.json()
  } catch {}
})
</script>

<template>
<div class="home" :class="{ loaded: mounted }">
  <!-- Announcement -->
  <div v-if="announcement?.items?.length" class="announce">
    <div class="announce-inner">
      <svg class="announce-icon" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>
      <span class="announce-text">{{ announcement.items[0].text }}</span>
    </div>
  </div>

  <!-- Hero -->
  <div class="hero">
    <div class="hero-label"><span class="hero-line"></span><span>XIPF Platform</span></div>
    <h1>大学生程序设计竞赛<br>数据平台</h1>
    <p class="hero-sub">追踪 ICPC / CCPC 选手与学校的竞技实力</p>
  </div>

  <!-- Quick Links -->
  <div class="quick">
    <router-link to="/contests" class="qc">
      <div class="qc-icon">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
      </div>
      <span class="qc-title">比赛列表</span>
      <span class="qc-desc">浏览所有比赛</span>
    </router-link>
    <router-link to="/orgs" class="qc">
      <div class="qc-icon">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      </div>
      <span class="qc-title">学校排行</span>
      <span class="qc-desc">各高校实力排名</span>
    </router-link>
    <router-link to="/contestants" class="qc">
      <div class="qc-icon">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
      </div>
      <span class="qc-title">选手排行</span>
      <span class="qc-desc">Rating 排名总览</span>
    </router-link>
    <router-link to="/rules" class="qc">
      <div class="qc-icon">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
      </div>
      <span class="qc-title">积分规则</span>
      <span class="qc-desc">算法详解</span>
    </router-link>
  </div>
</div>
</template>

<style scoped>
.home{display:flex;flex-direction:column;padding:60px 0 60px;max-width:1040px;margin:0 auto}

/* ── Announcement ── */
.announce{margin-bottom:24px;opacity:0;animation:heroIn .6s cubic-bezier(.16,1,.3,1) forwards}
.announce-inner{display:flex;align-items:center;gap:10px;padding:11px 18px;background:var(--bg2);border:1px solid var(--line);border-radius:var(--r)}
.announce-icon{color:var(--fg3);flex-shrink:0}
.announce-text{font-size:13.5px;color:var(--fg2);line-height:1.5}

/* ── Hero ── */
.hero{margin-bottom:48px}
.hero-label{display:flex;align-items:center;gap:12px;margin-bottom:18px;opacity:0;animation:heroIn .6s .05s cubic-bezier(.16,1,.3,1) forwards}
.hero-line{display:block;width:28px;height:1px;background:var(--fg4)}
.hero-label span{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:2px;color:var(--fg3)}
.hero h1{font-size:48px;font-weight:750;letter-spacing:-.8px;line-height:1.1;margin-bottom:14px;color:var(--fg);opacity:0;animation:heroIn .7s .1s cubic-bezier(.16,1,.3,1) forwards}
.hero-sub{font-size:15.5px;color:var(--fg2);max-width:500px;line-height:1.65;opacity:0;animation:heroIn .7s .2s cubic-bezier(.16,1,.3,1) forwards}
@keyframes heroIn{from{opacity:0;transform:translateY(20px);filter:blur(4px)}to{opacity:1;transform:translateY(0);filter:blur(0)}}

/* ── Quick Cards ── */
.quick{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;opacity:0;animation:heroIn .7s .3s cubic-bezier(.16,1,.3,1) forwards}
.qc{display:flex;flex-direction:column;gap:8px;padding:20px;border:1px solid var(--line);border-radius:12px;background:var(--bg4);transition:all .3s cubic-bezier(.16,1,.3,1);position:relative;overflow:hidden}
.qc::before{content:'';position:absolute;inset:0;background:var(--accent-glow);opacity:0;transition:opacity .35s}
.qc:hover{border-color:var(--line2);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,0.08)}
.qc:hover::before{opacity:1}
.qc-icon{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:var(--fg2);background:var(--bg3);transition:all .3s;position:relative}
.qc:hover .qc-icon{color:var(--accent);background:var(--accent-glow)}
.qc-title{font-size:15px;font-weight:600;color:var(--fg);position:relative;letter-spacing:-.2px}
.qc-desc{font-size:12.5px;color:var(--fg3);line-height:1.4;position:relative}

@media(max-width:768px){.home{padding:40px 0 40px}.hero h1{font-size:32px}.quick{grid-template-columns:repeat(2,1fr)}.qc{padding:16px}.qc-desc{display:none}}
@media(max-width:480px){.hero h1{font-size:26px}.quick{gap:8px}.qc{padding:14px}}
</style>
