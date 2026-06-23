<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContestant } from '@/lib/api'

const route = useRoute(); const router = useRouter()
const data = ref<any>(null); const loading = ref(true)

onMounted(async () => {
  try { data.value = await getContestant(route.params.id as string) } catch { data.value = null }
  loading.value = false
})

const ml: Record<string, string> = { gold: '金奖', silver: '银奖', bronze: '铜奖' }
</script>

<template>
  <div v-if="loading" class="empty-state"><p>加载中...</p></div>
  <div v-else-if="!data" class="empty-state"><p>选手不存在</p></div>
  <div v-else class="page animate-in">
    <button class="back-link" @click="router.back()">&larr; 返回</button>

    <!-- Profile -->
    <div class="card profile-card">
      <div class="avatar">{{ data.name[0] }}</div>
      <div class="info">
        <h1>{{ data.name }}</h1>
        <p class="org-link">
          <router-link :to="`/org/${data.org_id || data.organization}`">{{ data.organization }}</router-link>
        </p>
        <p class="meta-line">
          <span v-if="data.gender" class="gender-tag">{{ data.gender === 'male' ? '男' : '女' }}</span>
          <span>共 {{ data.records.length }} 场比赛</span>
        </p>
      </div>
    </div>

    <!-- Medal Stats -->
    <div class="card stats-card">
      <h2>获奖统计</h2>
      <div class="medal-grid">
        <div class="medal-item">
          <div class="medal-num" style="color: var(--champion)">{{ data.medal_summary?.champion || 0 }}</div>
          <div class="medal-label">冠军</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--gold)">{{ data.medal_summary?.runner_up || 0 }}</div>
          <div class="medal-label">亚军</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--bronze)">{{ data.medal_summary?.third || 0 }}</div>
          <div class="medal-label">季军</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--gold)">{{ data.medal_summary?.gold || 0 }}</div>
          <div class="medal-label">金牌</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--silver)">{{ data.medal_summary?.silver || 0 }}</div>
          <div class="medal-label">银牌</div>
        </div>
        <div class="medal-item">
          <div class="medal-num" style="color: var(--bronze)">{{ data.medal_summary?.bronze || 0 }}</div>
          <div class="medal-label">铜牌</div>
        </div>
      </div>
    </div>

    <!-- Contest Records -->
    <div class="card">
      <div class="section-head">
        <h2>参赛记录</h2>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>日期</th>
            <th>比赛</th>
            <th>队伍</th>
            <th class="text-right">排名</th>
            <th>奖牌</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in data.records" :key="`${r.contest_id}-${r.team_name}`">
            <td class="num date-cell">{{ r.date }}</td>
            <td class="ctitle"><router-link :to="`/contest/${r.contest_id}`">{{ r.contest_title }}</router-link></td>
            <td class="tname">{{ r.team_name }}</td>
            <td class="num text-right">
              <span v-if="r.official">{{ r.rank }} <span class="sep">/</span> {{ r.official_rank }}</span>
              <span v-else class="unoff-rank">{{ r.rank }}</span>
            </td>
            <td>
              <span v-if="r.medal" class="badge" :class="`badge-${r.medal}`">{{ ml[r.medal] }}</span>
              <span v-else class="no-award">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 800px; margin: 0 auto; }

/* Profile */
.profile-card {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 28px;
  margin-bottom: 24px;
}
.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  flex-shrink: 0;
}
.info h1 { font-size: 24px; font-weight: 700; letter-spacing: -0.3px; }
.org-link { font-size: 15px; margin-top: 4px; }
.meta-line {
  color: var(--text-muted);
  font-size: 14px;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.gender-tag {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 99px;
  background: var(--primary-bg);
  color: var(--primary);
  font-weight: 500;
}

/* Stats */
.stats-card { padding: 24px 28px; margin-bottom: 24px; }
.stats-card h2 { font-size: 15px; font-weight: 600; margin-bottom: 20px; }
.medal-grid { display: flex; gap: 40px; }
.medal-item { text-align: center; }
.medal-num { font-size: 34px; font-weight: 700; line-height: 1.1; }
.medal-label { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }

/* Records */
.section-head {
  padding: 20px 24px 0;
  margin-bottom: 8px;
}
.section-head h2 { font-size: 16px; font-weight: 600; }
.date-cell { color: var(--text-secondary); }
.ctitle { max-width: 280px; }
.ctitle a {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text);
  font-weight: 500;
}
.ctitle a:hover { color: var(--primary); opacity: 1; }
.tname {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}
.sep { color: var(--text-muted); font-weight: 400; }
.unoff-rank { color: var(--text-muted); font-style: italic; }
.no-award { color: var(--text-muted); }
</style>
