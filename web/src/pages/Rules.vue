<script setup lang="ts">
import { onMounted } from 'vue'
import katex from 'katex'

const f = [
  { id:'f-team', tex:String.raw`R_{\text{team}} = 400 \cdot \log_{10}\!\left( \sum_{k} 10^{E_k / 400} \right)` },
  { id:'f-seed', tex:String.raw`\text{seed}_i = 1 + \sum_{j \neq i} P(j \text{ beats } i),\quad P = \frac{1}{1 + 10^{(E_i - E_j)/400}}` },
  { id:'f-perf', tex:String.raw`R^* = \text{solve}\!\left( \sqrt{\text{seed} \cdot \text{rank}} \;\right)` },
  { id:'f-update', tex:String.raw`E' = E + K \cdot w_{\text{tier}} \cdot (\text{perf} - E) + \text{inc}` },
]
onMounted(() => f.forEach(({id,tex}) => { const el=document.getElementById(id); if(el)try{katex.render(tex,el,{displayMode:true,throwOnError:false})}catch{} }))
</script>

<template>
<div class="fade-in" style="max-width:760px;margin:0 auto"><h1 class="page-title">Scoring Rules</h1>

  <section style="background:var(--bg2);border:1px solid var(--line);border-radius:var(--r);padding:22px 24px;margin-bottom:16px">
    <h2 style="font-size:15px;font-weight:700;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--line)">Source</h2>
    <p style="font-size:13.5px;color:var(--fg2);line-height:1.7">XIPF uses the <a href="https://github.com/Hei-MaoM/xcpcrating" target="_blank" style="color:var(--accent)">xcpcrating</a> algorithm, based on the Codeforces Elo-inspired rating system.</p>
  </section>

  <section style="background:var(--bg2);border:1px solid var(--line);border-radius:var(--r);padding:22px 24px;margin-bottom:16px">
    <h2 style="font-size:15px;font-weight:700;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--line)">Player Rating</h2>
    <h3 style="font-size:13px;font-weight:600;margin:14px 0 4px;color:var(--fg)">Team Strength</h3>
    <p style="font-size:13px;color:var(--fg2);line-height:1.7;margin-bottom:4px">LSE aggregation of individual expectations <em>E</em> (starting at 1400):</p>
    <div :id="'f-team'" style="padding:10px 14px;margin:4px 0 10px;background:var(--bg3);border-radius:var(--r);border-left:3px solid var(--accent);overflow-x:auto"/>
    <h3 style="font-size:13px;font-weight:600;margin:14px 0 4px;color:var(--fg)">Expected Rank</h3>
    <p style="font-size:13px;color:var(--fg2);line-height:1.7;margin-bottom:4px">Sum of pairwise Elo win probabilities:</p>
    <div :id="'f-seed'" style="padding:10px 14px;margin:4px 0 10px;background:var(--bg3);border-radius:var(--r);border-left:3px solid var(--accent);overflow-x:auto"/>
    <h3 style="font-size:13px;font-weight:600;margin:14px 0 4px;color:var(--fg)">Performance Rating</h3>
    <p style="font-size:13px;color:var(--fg2);line-height:1.7;margin-bottom:4px">Geometric mean of expected and actual ranks, inverted via bisection:</p>
    <div :id="'f-perf'" style="padding:10px 14px;margin:4px 0 10px;background:var(--bg3);border-radius:var(--r);border-left:3px solid var(--accent);overflow-x:auto"/>
    <h3 style="font-size:13px;font-weight:600;margin:14px 0 4px;color:var(--fg)">Rating Update</h3>
    <p style="font-size:13px;color:var(--fg2);line-height:1.7;margin-bottom:4px">Bounded step toward performance, with anti-inflation adjustment:</p>
    <div :id="'f-update'" style="padding:10px 14px;margin:4px 0 10px;background:var(--bg3);border-radius:var(--r);border-left:3px solid var(--accent);overflow-x:auto"/>
    <ul style="font-size:13px;color:var(--fg2);line-height:1.8;padding-left:18px"><li><strong style="color:var(--fg)">K</strong> = 0.40 (base step, cap 0.85)</li><li><strong style="color:var(--fg)">w_tier</strong>: contest weight multiplier</li><li><strong style="color:var(--fg)">No penalty for meeting expectations</strong>: actual rank &le; predicted &rArr; step &ge; 0</li></ul>
  </section>

  <section style="background:var(--bg2);border:1px solid var(--line);border-radius:var(--r);padding:22px 24px;margin-bottom:16px">
    <h2 style="font-size:15px;font-weight:700;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--line)">Tier Weights</h2>
    <div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:13px;border:1px solid var(--line);border-radius:var(--r)">
      <thead><tr><th style="text-align:left;padding:7px 12px;font-size:10px;font-weight:600;color:var(--fg3);text-transform:uppercase;background:var(--bg3);border-bottom:1px solid var(--line)">Tier</th><th style="text-align:left;padding:7px 12px;font-size:10px;font-weight:600;color:var(--fg3);text-transform:uppercase;background:var(--bg3);border-bottom:1px solid var(--line)">Description</th><th style="text-align:right;padding:7px 12px;font-size:10px;font-weight:600;color:var(--fg3);text-transform:uppercase;background:var(--bg3);border-bottom:1px solid var(--line)">Weight</th><th style="text-align:right;padding:7px 12px;font-size:10px;font-weight:600;color:var(--fg3);text-transform:uppercase;background:var(--bg3);border-bottom:1px solid var(--line)">Gate</th></tr></thead>
      <tbody><tr><td style="padding:7px 12px;font-weight:600;color:#ef4444;border-bottom:1px solid var(--line2)">Finals</td><td style="padding:7px 12px;color:var(--fg2);border-bottom:1px solid var(--line2)">CCPC Final, ICPC EC Final</td><td class="tnum rt" style="padding:7px 12px;color:var(--fg2);border-bottom:1px solid var(--line2)">1.5x</td><td style="padding:7px 12px;color:var(--fg2);border-bottom:1px solid var(--line2)">None</td></tr>
      <tr><td style="padding:7px 12px;font-weight:600;color:#3b82f6;border-bottom:1px solid var(--line2)">Regionals</td><td style="padding:7px 12px;color:var(--fg2);border-bottom:1px solid var(--line2)">ICPC/CCPC regional contests</td><td class="tnum rt" style="padding:7px 12px;color:var(--fg2);border-bottom:1px solid var(--line2)">1.3x</td><td style="padding:7px 12px;color:var(--fg2);border-bottom:1px solid var(--line2)">None</td></tr>
      <tr><td style="padding:7px 12px;font-weight:600;color:#facc15;border-bottom:1px solid var(--line2)">Invitationals</td><td style="padding:7px 12px;color:var(--fg2);border-bottom:1px solid var(--line2)">National invitationals, girls, vocational</td><td class="tnum rt" style="padding:7px 12px;color:var(--fg2);border-bottom:1px solid var(--line2)">0.8x</td><td style="padding:7px 12px;color:var(--fg2);border-bottom:1px solid var(--line2)">E &lt; 2000</td></tr>
      <tr><td style="padding:7px 12px;font-weight:600;color:var(--fg3)">Provincials</td><td style="padding:7px 12px;color:var(--fg2)">Province/municipal contests</td><td class="tnum rt" style="padding:7px 12px;color:var(--fg2)">0.7x</td><td style="padding:7px 12px;color:var(--fg2)">E &lt; 1800</td></tr></tbody>
    </table></div>
  </section>

  <section style="background:var(--bg2);border:1px solid var(--line);border-radius:var(--r);padding:22px 24px;margin-bottom:16px">
    <h2 style="font-size:15px;font-weight:700;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--line)">About</h2>
    <p style="font-size:13px;color:var(--fg2);line-height:1.7">Rating system based on <a href="https://github.com/Hei-MaoM/xcpcrating" target="_blank" style="color:var(--accent)">xcpcrating</a>.</p>
    <p style="margin-top:10px"><a href="https://github.com/Hei-MaoM/xcpcrating" target="_blank" style="display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;padding:6px 14px;background:var(--bg3);border:1px solid var(--line);border-radius:var(--r);color:var(--fg);transition:all .12s"><svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg> xcpcrating on GitHub</a></p>
  </section>
</div>
</template>
