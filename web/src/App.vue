<script setup lang="ts">
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header-inner">
        <router-link to="/" class="logo">XIPF</router-link>
        <nav class="nav">
          <router-link to="/contests">比赛</router-link>
          <router-link to="/orgs">学校</router-link>
          <router-link to="/contestants">选手</router-link>
          <router-link to="/import">导入</router-link>
        </nav>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
    <footer class="footer">
      <span>XIPF &copy; 2026 &middot; Powered by dbywsc</span>
    </footer>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #f6f8fa;
  --card: #ffffff;
  --card-hover: #f8f9fb;
  --border: #d0d7de;
  --border-light: #e8ecf0;
  --text: #1f2328;
  --text-secondary: #656d76;
  --text-muted: #8b949e;
  --primary: #0969da;
  --primary-hover: #0550ae;
  --primary-light: #ddf4ff;
  --gold: #bf8700;
  --gold-bg: #fff8e1;
  --silver: #656d76;
  --silver-bg: #f0f0f0;
  --bronze: #9a4e00;
  --bronze-bg: #fff3e0;
  --champion: #cf222e;
  --champion-bg: #ffebe9;
  --radius: 8px;
  --shadow-sm: 0 1px 2px rgba(31,35,40,.04);
  --shadow: 0 1px 3px rgba(31,35,40,.08), 0 1px 2px rgba(31,35,40,.04);
  --shadow-lg: 0 8px 24px rgba(140,149,159,.15);
  --transition: .15s ease;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; -webkit-font-smoothing: antialiased; }
a { color: var(--primary); text-decoration: none; transition: color var(--transition); }
a:hover { color: var(--primary-hover); text-decoration: underline; }

.app { min-height: 100vh; display: flex; flex-direction: column; }

.header { background: #24292f; position: sticky; top: 0; z-index: 100; }
.header-inner { max-width: 1280px; margin: 0 auto; padding: 0 24px; height: 56px; display: flex; align-items: center; gap: 32px; }
.logo { font-size: 20px; font-weight: 700; color: #fff; letter-spacing: -.3px; text-decoration: none; }
.logo:hover { color: #fff; text-decoration: none; }
.nav { display: flex; gap: 8px; }
.nav a { font-size: 14px; font-weight: 500; color: rgba(255,255,255,.7); padding: 6px 12px; border-radius: 6px; transition: all var(--transition); }
.nav a:hover, .nav a.router-link-active { color: #fff; background: rgba(255,255,255,.12); text-decoration: none; }

.main { flex: 1; max-width: 1280px; width: 100%; margin: 32px auto; padding: 0 24px; }

.footer { text-align: center; padding: 32px 24px; color: var(--text-muted); font-size: 13px; border-top: 1px solid var(--border); }

/* Shared components */
.card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-sm); }
.card-hover:hover { box-shadow: var(--shadow-lg); }
.page-title { font-size: 24px; font-weight: 700; margin-bottom: 24px; color: var(--text); }

.table { width: 100%; border-collapse: collapse; font-size: 14px; }
.table th { text-align: left; padding: 10px 16px; font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: .4px; border-bottom: 2px solid var(--border); background: var(--bg); white-space: nowrap; }
.table th.text-right { text-align: right; }
.table td { padding: 10px 16px; border-bottom: 1px solid var(--border-light); color: var(--text); }
.table tbody tr { transition: background var(--transition); }
.table tbody tr:hover td { background: var(--card-hover); }

.badge { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 3px; font-weight: 600; letter-spacing: .3px; }
.badge-gold { background: var(--gold-bg); color: var(--gold); }
.badge-silver { background: var(--silver-bg); color: var(--silver); }
.badge-bronze { background: var(--bronze-bg); color: var(--bronze); }
.badge-champion { background: var(--champion-bg); color: var(--champion); }

.num { font-variant-numeric: tabular-nums; }
.text-right { text-align: right; }

.search-input { width: 100%; padding: 10px 16px; font-size: 14px; border: 1px solid var(--border); border-radius: var(--radius); outline: none; transition: all var(--transition); font-family: inherit; }
.search-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(9,105,218,.12); }

.back-link { display: inline-block; font-size: 14px; color: var(--text-secondary); margin-bottom: 20px; cursor: pointer; background: none; border: none; padding: 0; font-family: inherit; }
.back-link:hover { color: var(--primary); text-decoration: underline; }

.empty-state { text-align: center; padding: 80px 24px; color: var(--text-muted); }
.empty-state p { margin-top: 8px; font-size: 14px; }
</style>
