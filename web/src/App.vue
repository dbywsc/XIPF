<script setup lang="ts">
import { ref, onMounted } from 'vue'

const theme = ref<'light' | 'dark'>('light')

function applyTheme(t: 'light' | 'dark') {
  theme.value = t
  document.documentElement.setAttribute('data-theme', t)
  try { localStorage.setItem('xipf-theme', t) } catch {}
}

function toggleTheme() {
  applyTheme(theme.value === 'light' ? 'dark' : 'light')
}

onMounted(() => {
  let t: 'light' | 'dark' = 'light'
  try {
    const saved = localStorage.getItem('xipf-theme')
    if (saved === 'dark' || saved === 'light') t = saved
    else if (window.matchMedia('(prefers-color-scheme: dark)').matches) t = 'dark'
  } catch {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) t = 'dark'
  }
  applyTheme(t)
})
</script>

<template>
  <div class="app" :class="theme">
    <header class="header">
      <div class="header-inner">
        <router-link to="/" class="logo">XIPF</router-link>
        <nav class="nav">
          <router-link to="/contests">比赛</router-link>
          <router-link to="/orgs">学校</router-link>
          <router-link to="/contestants">选手</router-link>
          <router-link to="/import">导入</router-link>
        </nav>
        <button class="theme-toggle" @click="toggleTheme" :title="theme === 'light' ? '暗色模式' : '亮色模式'">
          <svg v-if="theme === 'light'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        </button>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
    <footer class="footer">
      <span><a href="https://github.com/dbywsc/XIPF" target="_blank">XIPF</a> &copy; 2026 &middot; dbywsc</span>
    </footer>
  </div>
</template>

<style>
/* ── Design Tokens ── */
:root {
  --bg: #F8F7F4;
  --bg-warm: #F2F0EC;
  --card: #FFFFFF;
  --card-hover: #FAFAF8;
  --text: #1A1A1A;
  --text-secondary: #6B6B6B;
  --text-muted: #A0A0A0;
  --border: #E8E6E1;
  --border-light: #F0EFEC;
  --primary: #4F5BD5;
  --primary-hover: #3F4AB8;
  --primary-bg: rgba(79, 91, 213, 0.06);
  --primary-border: rgba(79, 91, 213, 0.18);

  /* Medal colors */
  --gold: #9B7A2A;
  --gold-bg: #FDF6E8;
  --silver: #6B7280;
  --silver-bg: #F3F4F6;
  --bronze: #A0522D;
  --bronze-bg: #FEF3EC;
  --champion: #C0392B;
  --champion-bg: #FEF0EF;

  /* Radii */
  --radius-sm: 6px;
  --radius: 10px;
  --radius-lg: 14px;

  /* Shadows */
  --shadow-xs: 0 1px 2px rgba(0,0,0,0.03);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
  --shadow-card: 0 0 0 1px rgba(0,0,0,0.03), 0 1px 3px rgba(0,0,0,0.04);

  --transition: 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ── Dark Mode ── */
[data-theme="dark"] {
  --bg: #111111;
  --bg-warm: #181818;
  --card: #1C1C1C;
  --card-hover: #222222;
  --text: #ECECEC;
  --text-secondary: #9B9B9B;
  --text-muted: #6B6B6B;
  --border: #2A2A2A;
  --border-light: #222222;
  --primary: #7B85F0;
  --primary-hover: #939BFF;
  --primary-bg: rgba(123, 133, 240, 0.08);
  --primary-border: rgba(123, 133, 240, 0.2);

  --gold: #D4A843;
  --gold-bg: #2A2418;
  --silver: #9CA3AF;
  --silver-bg: #1F2022;
  --bronze: #C48660;
  --bronze-bg: #2A2018;
  --champion: #E74C3C;
  --champion-bg: #2A1818;

  --shadow-xs: none;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.12);
  --shadow-card: 0 0 0 1px rgba(255,255,255,0.04), 0 1px 3px rgba(0,0,0,0.16);
}

/* ── Reset ── */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'SF Pro Display', 'Helvetica Neue', 'Segoe UI', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: 15px;
}

a { color: var(--primary); text-decoration: none; transition: opacity var(--transition); }
a:hover { opacity: 0.75; }

.app { min-height: 100vh; display: flex; flex-direction: column; }

/* ── Header ── */
.header {
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}
[data-theme="dark"] .header {
  background: rgba(17,17,17,0.82);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
  height: 54px;
  display: flex;
  align-items: center;
  gap: 32px;
}
.logo {
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
}
.logo:hover { opacity: 0.7; }

.nav { display: flex; gap: 2px; }
.nav a {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  transition: all var(--transition);
}
.nav a:hover,
.nav a.router-link-active {
  color: var(--text);
  background: var(--primary-bg);
  opacity: 1;
}

.theme-toggle {
  margin-left: auto;
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 6px 8px;
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}
.theme-toggle:hover { color: var(--text); border-color: var(--text-muted); }

/* ── Main ── */
.main { flex: 1; max-width: 1280px; width: 100%; margin: 40px auto; padding: 0 24px; }

/* ── Footer ── */
.footer {
  text-align: center;
  padding: 32px 24px;
  color: var(--text-muted);
  font-size: 13px;
  border-top: 1px solid var(--border);
  margin-top: 64px;
}
.footer a { color: var(--text-secondary); font-weight: 500; }
.footer a:hover { color: var(--primary); opacity: 1; }

/* ── Shared: Card ── */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-xs);
}
.card-hover { transition: box-shadow var(--transition), border-color var(--transition); }
.card-hover:hover {
  border-color: var(--text-muted);
  box-shadow: var(--shadow-sm);
}

/* ── Shared: Table ── */
.table { width: 100%; border-collapse: collapse; font-size: 14px; }
.table thead th {
  text-align: left;
  padding: 12px 20px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  border-bottom: 1px solid var(--border);
  background: var(--bg);
  white-space: nowrap;
  position: sticky;
  top: 0;
}
.table thead th.text-right { text-align: right; }
.table tbody td {
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-light);
  color: var(--text);
  vertical-align: middle;
}
.table tbody tr { transition: background var(--transition); }
.table tbody tr:hover td { background: var(--card-hover); }
.table tbody tr:last-child td { border-bottom: none; }

/* ── Shared: Badge ── */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 99px;
  font-weight: 600;
  letter-spacing: 0.3px;
}
.badge-gold { background: var(--gold-bg); color: var(--gold); }
.badge-silver { background: var(--silver-bg); color: var(--silver); }
.badge-bronze { background: var(--bronze-bg); color: var(--bronze); }
.badge-champion { background: var(--champion-bg); color: var(--champion); }

/* ── Shared: Utilities ── */
.num { font-variant-numeric: tabular-nums; font-feature-settings: "tnum"; }
.text-right { text-align: right; }

/* ── Shared: Search ── */
.search-input {
  width: 100%;
  padding: 13px 18px;
  font-size: 15px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
  font-family: inherit;
  background: var(--card);
  color: var(--text);
}
.search-input::placeholder { color: var(--text-muted); }
.search-input:focus {
  border-color: var(--primary-border);
  box-shadow: 0 0 0 3px var(--primary-bg);
}

/* ── Shared: Back Link ── */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 24px;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  font-family: inherit;
  transition: color var(--transition);
}
.back-link:hover { color: var(--text); }

/* ── Shared: Page Title ── */
.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 32px;
  color: var(--text);
  letter-spacing: -0.4px;
}

/* ── Shared: Empty State ── */
.empty-state {
  text-align: center;
  padding: 80px 24px;
  color: var(--text-muted);
}
.empty-state p { margin-top: 8px; font-size: 15px; }

/* ── Skeleton ── */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg, var(--bg) 25%, var(--bg-warm) 50%, var(--bg) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.8s infinite;
  border-radius: var(--radius-sm);
}

/* ── Fade-in ── */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-in {
  animation: fade-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── Selection ── */
::selection { background: var(--primary-bg); }
</style>
