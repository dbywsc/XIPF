<script setup lang="ts">
import { ref, onMounted } from 'vue'

const m = ref<'dark'|'light'>('dark')
function set(t:'dark'|'light'){m.value=t;document.documentElement.className=t;try{localStorage.setItem('xipf-theme',t)}catch{}}
onMounted(()=>{const s=localStorage.getItem('xipf-theme');set(s==='light'?'light':'dark')})
</script>

<template>
<div class="app">
  <header class="top">
    <div class="top-in">
      <router-link to="/" class="logo">XIPF</router-link>
      <nav class="nav">
        <router-link to="/contests">比赛</router-link>
        <router-link to="/orgs">学校</router-link>
        <router-link to="/contestants">选手</router-link>
        <router-link to="/rules">规则</router-link>
      </nav>
      <button class="theme" @click="set(m==='dark'?'light':'dark')" :title="m==='dark'?'亮色模式':'暗色模式'">
        <svg v-if="m==='dark'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </header>
  <main class="main">
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
  <footer class="foot">
    <span><a href="https://github.com/dbywsc/XIPF">XIPF</a> &middot; ICPC / CCPC 竞赛数据平台</span>
  </footer>
</div>
</template>

<style>
/* ── Reset ── */
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{font-size:15px;-webkit-text-size-adjust:100%}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','PingFang SC','Noto Sans SC',sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
a{text-decoration:none;color:inherit}

/* ── Dark Mode (default) ── */
html.dark{
  --bg:#08080a;--bg2:#0d0d10;--bg3:#141418;--bg4:#18181c;--bg5:#1e1e23;
  --fg:#f4f4f5;--fg2:#a1a1aa;--fg3:#5c5c66;--fg4:#33333a;
  --line:#222228;--line2:#2a2a30;--line3:#36363e;
  --accent:#4f8cff;--accent-dim:#3b6fdb;--accent-glow:rgba(79,140,255,0.14);
  --gold:#fbbf24;--gold-bg:rgba(251,191,36,0.10);
  --silver:#a1a1aa;--silver-bg:rgba(161,161,170,0.08);
  --bronze:#fb923c;--bronze-bg:rgba(251,146,60,0.10);
  --up:#22c55e;--up-bg:rgba(34,197,94,0.08);
  --down:#ef4444;--down-bg:rgba(239,68,68,0.08);
  --r:10px;--r-sm:6px;
  --sh:0 0 0 1px rgba(255,255,255,0.04);
  --sh-md:0 8px 32px rgba(0,0,0,0.40);
  --sh-glow:0 0 40px rgba(79,140,255,0.08);
}

/* ── Light Mode ── */
html.light{
  --bg:#f8f8fa;--bg2:#f1f1f4;--bg3:#e8e8ec;--bg4:#ffffff;--bg5:#f4f4f6;
  --fg:#18181b;--fg2:#52525b;--fg3:#a1a1aa;--fg4:#d4d4d8;
  --line:#e4e4e7;--line2:#eeeef0;--line3:#d4d4d8;
  --accent:#2563eb;--accent-dim:#1d4ed8;--accent-glow:rgba(37,99,235,0.08);
  --gold:#b45309;--gold-bg:rgba(180,83,9,0.06);
  --silver:#52525b;--silver-bg:rgba(82,82,91,0.05);
  --bronze:#c2410c;--bronze-bg:rgba(194,65,12,0.06);
  --up:#16a34a;--up-bg:rgba(22,163,74,0.06);
  --down:#dc2626;--down-bg:rgba(220,38,38,0.06);
  --r:10px;--r-sm:6px;
  --sh:0 0 0 1px rgba(0,0,0,0.04);
  --sh-md:0 8px 32px rgba(0,0,0,0.08);
  --sh-glow:0 0 40px rgba(37,99,235,0.06);
}

/* ── Layout ── */
.app{min-height:100vh;display:flex;flex-direction:column;background:var(--bg);color:var(--fg)}

/* ── Page Transitions ── */
.page-enter-active{animation:pageIn .35s cubic-bezier(.16,1,.3,1)}
.page-leave-active{animation:pageOut .2s ease}
@keyframes pageIn{from{opacity:0;transform:translateY(12px);filter:blur(2px)}to{opacity:1;transform:translateY(0);filter:blur(0)}}
@keyframes pageOut{from{opacity:1}to{opacity:0;transform:translateY(-8px)}}

/* ── Top Nav ── */
.top{position:sticky;top:0;z-index:100;background:rgba(8,8,10,0.84);backdrop-filter:saturate(180%) blur(24px);-webkit-backdrop-filter:saturate(180%) blur(24px);border-bottom:1px solid var(--line)}
html.light .top{background:rgba(248,248,250,0.84)}
.top-in{max-width:1240px;margin:0 auto;padding:0 32px;height:54px;display:flex;align-items:center;gap:36px}
.logo{font-size:18px;font-weight:700;letter-spacing:-.3px;color:var(--fg);position:relative}
.logo::after{content:'';position:absolute;bottom:-2px;left:0;right:0;height:2px;background:var(--accent);border-radius:1px;opacity:0;transform:scaleX(0);transition:all .25s cubic-bezier(.16,1,.3,1)}
.logo:hover::after{opacity:1;transform:scaleX(1)}
.nav{display:flex;gap:2px}
.nav a{font-size:13.5px;font-weight:500;color:var(--fg3);padding:6px 14px;border-radius:var(--r-sm);transition:all .2s;position:relative}
.nav a::after{content:'';position:absolute;bottom:2px;left:50%;right:50%;height:2px;background:var(--accent);border-radius:1px;transition:all .25s cubic-bezier(.16,1,.3,1)}
.nav a:hover{color:var(--fg2);background:var(--bg3)}
.nav a:hover::after{left:14px;right:14px}
.nav a.router-link-active{color:var(--fg);background:var(--bg3)}
.nav a.router-link-active::after{left:14px;right:14px;background:var(--accent)}
.theme{margin-left:auto;background:none;border:1px solid var(--line2);border-radius:var(--r-sm);padding:6px 9px;cursor:pointer;color:var(--fg3);display:flex;align-items:center;transition:all .2s}
.theme:hover{color:var(--fg);border-color:var(--fg4);transform:scale(1.05)}

/* ── Main / Footer ── */
.main{flex:1;max-width:1240px;width:100%;margin:0 auto;padding:48px 32px 100px}
.foot{text-align:center;padding:32px;color:var(--fg3);font-size:12.5px;border-top:1px solid var(--line)}
.foot a{font-weight:600;color:var(--fg2);transition:color .15s}.foot a:hover{color:var(--accent)}

/* ── Card / Table ── */
.card{background:var(--bg4);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;transition:box-shadow .3s,transform .3s}
.card:hover{box-shadow:var(--sh-md)}
.tbl{width:100%;border-collapse:collapse;font-size:14px}
.tbl thead th{padding:10px 16px;font-size:10.5px;font-weight:600;color:var(--fg3);text-transform:uppercase;letter-spacing:.5px;border-bottom:2px solid var(--line3);background:var(--bg3);white-space:nowrap;text-align:left}
.tbl thead th.rt{text-align:right}
.tbl tbody td{padding:10px 16px;border-bottom:1px solid var(--line2);color:var(--fg);vertical-align:middle}
.tbl tbody tr{transition:background .12s,transform .15s}
.tbl tbody tr:hover td{background:var(--bg5)}
.tbl tbody tr:hover{transform:translateX(2px)}
.tbl tbody tr:last-child td{border-bottom:none}
.tbl a{color:var(--accent);font-weight:500}.tbl a:hover{color:var(--accent-dim)}

/* ── Row Animation ── */
@keyframes rowIn{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:translateX(0)}}
.row-anim{animation:rowIn .4s cubic-bezier(.16,1,.3,1) both}

/* ── Badge ── */
.badge{display:inline-flex;align-items:center;font-size:10.5px;padding:2px 10px;border-radius:99px;font-weight:600;letter-spacing:.2px;transition:transform .15s}
.badge:hover{transform:scale(1.08)}
.badge-gold{background:var(--gold-bg);color:var(--gold);box-shadow:0 0 12px rgba(251,191,36,0.12)}.badge-silver{background:var(--silver-bg);color:var(--silver)}.badge-bronze{background:var(--bronze-bg);color:var(--bronze);box-shadow:0 0 12px rgba(251,146,60,0.10)}

/* ── Utilities ── */
.tnum{font-variant-numeric:tabular-nums;font-feature-settings:'tnum'1}
.rt{text-align:right}.muted{color:var(--fg3)}.faint{color:var(--fg4)}
.clickable{cursor:pointer;transition:transform .2s}
.clickable:active{transform:scale(.995)}

/* ── Search ── */
.srch{position:relative}.srch svg{position:absolute;left:13px;top:50%;transform:translateY(-50%);color:var(--fg3);transition:color .2s}
.srch:focus-within svg{color:var(--accent)}
.srch input{width:100%;padding:10px 16px 10px 38px;font-size:14px;border:1px solid var(--line2);border-radius:var(--r);outline:none;font-family:inherit;background:var(--bg4);color:var(--fg);transition:all .25s}
.srch input::placeholder{color:var(--fg4)}.srch input:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow)}

/* ── Back ── */
.back{display:inline-flex;align-items:center;gap:5px;font-size:12.5px;font-weight:500;color:var(--fg3);margin-bottom:18px;cursor:pointer;background:none;border:none;padding:0;font-family:inherit;transition:all .2s}
.back:hover{color:var(--fg);gap:8px}

/* ── Empty ── */
.empty{text-align:center;padding:80px 24px;color:var(--fg3);font-size:14.5px}

/* ── Section Head ── */
.sec-head{display:flex;align-items:center;justify-content:space-between;padding:16px 18px 0;margin-bottom:6px}.sec-head h2{font-size:13.5px;font-weight:600;color:var(--fg2)}

/* ── Page Title ── */
.page-title{font-size:30px;font-weight:700;letter-spacing:-.5px;margin-bottom:28px;text-align:center}

/* ── Delta ── */
.delta{font-weight:650;font-variant-numeric:tabular-nums;font-feature-settings:'tnum'1;transition:transform .15s}
.d-up{color:var(--up)}.d-down{color:var(--down)}

/* ── Skeleton ── */
@keyframes shim{0%{background-position:-200% 0}100%{background-position:200% 0}}
.skel{background:linear-gradient(90deg,var(--bg3) 25%,var(--bg2) 50%,var(--bg3) 75%);background-size:200% 100%;animation:shim 1.8s infinite;border-radius:var(--r-sm)}

/* ── Tabs ── */
.tabs{display:flex;gap:4px;margin-bottom:24px;padding:4px;background:var(--bg3);border-radius:var(--r);width:fit-content}
.tab{font-size:13.5px;font-weight:500;color:var(--fg3);padding:8px 20px;border-radius:7px;border:none;background:none;cursor:pointer;font-family:inherit;transition:all .25s;display:flex;align-items:center;gap:7px}
.tab:hover{color:var(--fg)}
.tab.active{background:var(--bg4);color:var(--fg);box-shadow:var(--sh)}
.tb-count{font-size:11px;color:var(--fg4);font-weight:500}

/* ── Spinner ── */
@keyframes spin{to{transform:rotate(360deg)}}
.spinner{width:20px;height:20px;border:2px solid var(--line2);border-top-color:var(--accent);border-radius:50%;animation:spin .6s linear infinite}

/* ── Fade In ── */
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.fade-in{animation:fadeIn .5s cubic-bezier(.16,1,.3,1) both}

/* ── scrollbar ── */
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--fg4);border-radius:3px}
::selection{background:var(--accent-glow)}

/* ── Responsive ── */
@media(max-width:768px){
  .top-in{gap:16px;padding:0 18px}
  .nav a{padding:5px 9px;font-size:12.5px}
  .main{padding:32px 18px 80px}
  .page-title{font-size:22px}
  .tbl{font-size:13px}
  .tbl thead th{padding:8px 10px;font-size:10px}
  .tbl tbody td{padding:8px 10px}
  .card{overflow-x:auto}
  .tabs{width:100%;overflow-x:auto;flex-wrap:nowrap}
  .tab{white-space:nowrap}
}
@media(max-width:480px){
  .top{height:auto}
  .top-in{height:46px;gap:10px;padding:0 12px}
  .logo{font-size:15px}
  .nav a{padding:5px 7px;font-size:11.5px}
  .theme{padding:5px 7px}
  .main{padding:24px 12px 64px}
  .page-title{font-size:19px;margin-bottom:20px}
  .foot{padding:20px;font-size:11.5px}
  .back{font-size:12px;margin-bottom:14px}
  .sec-head{padding:12px 14px 0}
  .sec-head h2{font-size:12.5px}
}
</style>
