<script setup lang="ts">
import { ref } from 'vue'

const loading = ref(false); const error = ref(''); const preview = ref<any>(null)
const filename = ref(''); const title = ref(''); const date = ref('')
const teams = ref<any[]>([]); const roster = ref<any>(null)

function pm(v:string):string{const s=(v||'').trim().toLowerCase();if(['gold','金奖','金牌','金'].includes(s))return'gold';if(['silver','银奖','银牌','银'].includes(s))return'silver';if(['bronze','铜奖','铜牌','铜'].includes(s))return'bronze';return''}
function tb(v:any):boolean{return['Y','YES','TRUE','1'].includes(String(v??'').trim().toUpperCase())}

function handle(e:Event){
  const f=(e.target as HTMLInputElement).files?.[0];if(!f)return
  loading.value=true;error.value='';preview.value=null;filename.value=f.name.replace(/\.\w+$/,'')
  const r=new FileReader();r.onload=ev=>{
    try{
      const t=ev.target!.result as string;const ls=t.split(/\r?\n/).filter(l=>l.trim())
      let hi=-1;for(let i=0;i<ls.length;i++)if(ls[i].split('\t')[0]?.trim()==='Rank'){hi=i;break}
      if(hi<0){error.value='找不到 Rank 表头行';loading.value=false;return}
      const ts:any[]=[];const ro:any={teams:{} as Record<string,any>}
      for(let i=hi+1;i<ls.length;i++){
        const c=ls[i].split('\t');if(!c[0]?.trim()||c[0].trim().startsWith('#')||c[0].trim().startsWith(','))continue
        const rk=parseInt(c[0])||0;const og=(c[2]||'').trim();const tn=(c[3]||'').trim()
        const uf=tb(c[7]);const gl=tb(c[8]);let md='';const dm:Record<string,string>={}
        const rawPrize=(c[9]||'').trim()
        if(rawPrize){
          if(rawPrize.includes(';')||rawPrize.includes('=')){
            for(const p of rawPrize.split(';')){
              const eq=p.indexOf('=');if(eq>0)dm[p.substring(0,eq).trim()]=p.substring(eq+1).trim()
            }
            const mo={gold:3,silver:2,bronze:1};let best=0
            for(const m of Object.values(dm)){const v=mo[m]||0;if(v>best){best=v;md=m}}
          }else{md=pm(rawPrize)}
        }
        const ms:any[]=[];for(let j=4;j<=6;j++){const n=(c[j]||'').trim();if(n)ms.push({name:n,gender:''})}
        const ids=new Set(ts.map(t=>t.id));let tid:string;let ct=1
        if(rk>0){tid=`T${String(rk).padStart(3,'0')}`;while(ids.has(tid)){tid=`T${String(rk).padStart(3,'0')}_${ct}`;ct++}}
        else{tid=`T${String(ts.length+1).padStart(3,'0')}`;while(ids.has(tid)){tid=`T${String(ts.length+1).padStart(3,'0')}_${ct}`;ct++}}
        ts.push({id:tid,name:tn,organization:og,official:!uf,rank:rk,orgRank:parseInt(c[1])||0,solved:0,penalty:0,problems:[],medal:md,division_medals:dm,members:ms,girl_team:gl,champion:''});ro.teams[tid]={members:ms,organization_override:null}
      }
      const ob:Record<string,number>={};const obt:Record<string,string>={}
      for(const t of ts){if(!t.official||!t.organization)continue;if(!(t.organization in ob)||t.rank<ob[t.organization]){ob[t.organization]=t.rank;obt[t.organization]=t.id}}
      const so=Object.entries(ob).sort((a,b)=>a[1]-b[1]);const lb=['冠军','亚军','季军']
      for(let i=0;i<Math.min(3,so.length);i++){const tm=ts.find(t=>t.id===obt[so[i][0]]);if(tm)tm.champion=lb[i]}
      teams.value=ts;roster.value=ro;preview.value={teamCount:ts.length,officialCount:ts.filter((t:any)=>t.official).length};loading.value=false
    }catch(e:any){error.value='解析失败: '+e.message;loading.value=false}
  };r.readAsText(f)
}
function dc(){
  const cd={title:title.value||filename.value,year:2026,date:date.value,teams:teams.value,problems:[],awards:{gold:teams.value.filter((t:any)=>t.medal==='gold').length,silver:teams.value.filter((t:any)=>t.medal==='silver').length,bronze:teams.value.filter((t:any)=>t.medal==='bronze').length}}
  dl(JSON.stringify(cd,null,2),'contest_data.json')
}
function dr(){dl(JSON.stringify(roster.value,null,2),'roster.json')}
function dl(d:string,n:string){const b=new Blob([d],{type:'application/json'});const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download=n;a.click();URL.revokeObjectURL(u)}
</script>

<template>
  <div class="pg">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h1 class="page-title" style="margin-bottom:0">导入数据</h1>
      <a href="https://github.com/dbywsc/XIPF/blob/main/CONTRIBUTING.md" target="_blank" class="doc-link">说明文档 &rarr;</a>
    </div>
    <div class="card" style="padding:24px;margin-bottom:24px">
      <div class="form-row">
        <label>名称 <input v-model="title" type="text" placeholder="2026 年 CCPC 全国邀请赛（城市）" class="inp" /></label>
        <label>日期 <input v-model="date" type="date" class="inp" /></label>
      </div>
      <div class="up" @dragover.prevent @drop.prevent="(e:any)=>{const f=e.dataTransfer?.files?.[0];if(f){const i=document.getElementById('fi') as HTMLInputElement;const d=new DataTransfer();d.items.add(f);i.files=d.files;i.dispatchEvent(new Event('change'))}}">
        <input id="fi" type="file" accept=".csv,.tsv" @change="handle" />
        <p>拖拽或点击上传 .csv 文件</p>
      </div>
      <div v-if="loading" class="msg">解析中...</div>
      <div v-if="error" class="msg err">{{ error }}</div>
    </div>

    <div v-if="preview" class="card" style="padding:24px;margin-bottom:24px">
      <h2>预览</h2>
      <p style="color:var(--text-secondary);font-size:14px;margin:4px 0 16px">{{ preview.teamCount }} 支队伍（{{ preview.officialCount }} 正式）</p>
      <div class="btns"><button class="btn pri" @click="dc">下载 contest_data.json</button><button class="btn" @click="dr">下载 roster.json</button></div>
      <div class="ns">
        <h3>下一步</h3>
        <ol><li>下载两个 JSON 文件</li><li>放入 <code>contests/YYYY/城市_类型/</code></li><li>运行 <code>python scripts/build.py</code></li></ol>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pg { max-width: 640px; margin: 0 auto; }
.doc-link { font-size: 14px; color: var(--text-secondary); text-decoration: none; }
.doc-link:hover { color: var(--primary); }
.form-row { display: flex; gap: 16px; margin-bottom: 20px; }
.form-row label { flex: 1; font-size: 13px; color: var(--text-secondary); font-weight: 500; }
.inp { display: block; width: 100%; margin-top: 4px; padding: 8px 12px; font-size: 14px; border: 1px solid var(--border); border-radius: 6px; outline: none; font-family: inherit; }
.inp:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(9,105,218,.1); }
.up { border: 2px dashed var(--border); border-radius: 10px; padding: 40px; text-align: center; cursor: pointer; transition: all var(--transition); }
.up:hover { border-color: var(--primary); background: #f6f8fb; }
.up p { color: var(--text-muted); font-size: 14px; margin-top: 8px; }
.msg { text-align: center; padding: 12px; font-size: 14px; margin-top: 12px; }
.msg.err { color: #cf222e; }
h2 { font-size: 17px; font-weight: 600; margin-bottom: 4px; }
h3 { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
.btns { display: flex; gap: 10px; margin: 12px 0 16px; }
.btn { padding: 8px 20px; border: 1px solid var(--border); border-radius: 8px; background: #fff; cursor: pointer; font-size: 14px; font-family: inherit; transition: all var(--transition); }
.btn.pri { background: var(--primary); color: #fff; border-color: var(--primary); }
.btn:hover { opacity: .85; }
.ns { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
.ns ol { padding-left: 20px; color: var(--text-secondary); font-size: 14px; }
.ns li { margin-bottom: 6px; }
.ns code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-sm); }
</style>
