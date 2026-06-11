import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'

import Home from './pages/Home.vue'
import Contestant from './pages/Contestant.vue'
import Contestants from './pages/Contestants.vue'
import Organization from './pages/Organization.vue'
import Organizations from './pages/Organizations.vue'
import Contest from './pages/Contest.vue'
import Contests from './pages/Contests.vue'

import Import from './pages/Import.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/contestant/:id', component: Contestant },
  { path: '/contestants', component: Contestants },
  { path: '/org/:id', component: Organization },
  { path: '/orgs', component: Organizations },
  { path: '/contest/:id', component: Contest },
  { path: '/contests', component: Contests },
  { path: '/import', component: Import },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

const app = createApp(App)
app.use(router)
app.mount('#app')
