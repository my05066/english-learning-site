<script setup>
import { computed } from 'vue'
import Icon from './Icon.vue'
import { modules } from './navigation.js'
import { daysAgo, state, streak } from './store.js'
import daily from './data/daily.js'

const hasActivity = computed(() => Object.values(state.days).some(count => count > 0))
const goal = 5
const today = computed(() => state.days[daysAgo(0)] || 0)
const chain = computed(streak)
const percent = computed(() => Math.min(100, today.value / goal * 100))
const now = new Date()
const dayNumber = Math.floor(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()) / 86400000)
const quote = daily[dayNumber % daily.length]
const hour = now.getHours()
const greeting = hour < 11 ? '早上好' : hour < 14 ? '中午好' : hour < 19 ? '下午好' : '晚上好'
const week = computed(() => {
  const mondayOffset = (new Date().getDay() + 6) % 7
  return ['一', '二', '三', '四', '五', '六', '日'].map((label, index) => {
    const offset = mondayOffset - index
    return { label, count: offset >= 0 ? state.days[daysAgo(offset)] || 0 : 0, today: offset === 0 }
  })
})
const weekMax = computed(() => Math.max(goal, ...week.value.map(day => day.count)))
</script>

<template>
  <div class="dashboard">
    <section class="hero">
      <div class="hero-content">
        <div class="hero-label"><span class="hero-dot"></span> {{ new Intl.DateTimeFormat('zh-CN', { month:'long', day:'numeric', weekday:'long' }).format(now) }}</div>
        <h1>{{ greeting }}，开始今天的英语练习。</h1>
        <p>从一个单词、一段听力或一篇短文开始。</p>
        <RouterLink class="hero-action" :to="state.last?.path || '/words'">{{ state.last ? '继续上次学习' : '从单词开始' }}</RouterLink>
      </div>
      <div v-if="hasActivity" class="hero-side" aria-label="今日学习进度">
        <div class="hero-streak"><Icon name="flame" :size="17"/> 连续学习 <strong>{{ chain }}</strong> 天</div>
        <div class="hero-meter">
          <div class="ring" :style="{ '--percent': percent + '%' }" role="progressbar" aria-label="今日学习进度" :aria-valuenow="percent"><div><strong>{{ Math.min(today, goal) }}/{{ goal }}</strong><small>今日目标</small></div></div>
          <div><strong>今日学习</strong><p>{{ today >= goal ? '目标已达成' : '再完成 ' + (goal - today) + ' 项学习' }}</p></div>
        </div>
      </div>
      <div v-else class="hero-side onboarding">
        <h2>第一次来？</h2>
        <p>试着完成一张单词卡。你的今日进度和学习记录会在这里显示。</p>
      </div>
    </section>
    <div class="dashboard-columns">
      <section class="module-section">
        <div class="section-title"><h2>学习模块</h2><p class="muted">按你的节奏，练习听、读、写。</p></div>
        <div class="module-grid">
          <RouterLink v-for="item in modules" :key="item.path" :to="item.path" class="module-card panel">
            <span class="module-icon" :class="item.color"><Icon :name="item.icon" :size="23"/></span>
            <div><h3>{{ item.title }}</h3><p>{{ item.detail }}</p></div>
            <small>{{ item.count }}</small>
          </RouterLink>
        </div>
      </section>
      <aside class="dashboard-aside">
        <section class="panel quote">
          <div class="quote-head"><h2>每日一句</h2><span aria-hidden="true">“</span></div>
          <blockquote lang="en">{{ quote[0] }}</blockquote><p class="muted">{{ quote[1] }}</p>
        </section>
        <section v-if="week.some(day => day.count > 0)" class="panel chart-panel">
          <div class="split"><h2>本周学习</h2><span class="muted">{{ week.reduce((sum, day) => sum + day.count, 0) }} 次</span></div>
          <div class="chart">
            <div v-for="day in week" :key="day.label" class="chart-day" :class="{ 'chart-today': day.today }">
              <div class="bar-bg" :title="'周' + day.label + '：' + day.count + ' 次'" role="img" :aria-label="'周' + day.label + '，' + day.count + ' 次'"><div :style="{ height: day.count / weekMax * 100 + '%' }"></div></div><small>{{ day.label }}</small>
            </div>
          </div>
        </section>
        <section v-if="state.last" class="panel resume"><h2>继续学习</h2><RouterLink :to="state.last.path">{{ state.last.label }}</RouterLink></section>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.dashboard { display:grid; gap:28px; }
.hero { min-height:270px; display:grid; grid-template-columns:minmax(0,1fr) minmax(230px,.44fr); align-items:center; gap:30px; padding:34px clamp(22px,4vw,48px); border-radius:22px; color:#fff; background:radial-gradient(ellipse at 83% 0%,#105d54 0%,transparent 58%),linear-gradient(128deg,#103d40,#0c6159); box-shadow:0 15px 30px #14473d28; overflow:hidden; }
.hero-content { position:relative; }
.hero-label { display:flex; gap:8px; align-items:center; color:#def3ef; font-size:.9rem; font-weight:650; margin-bottom:13px; }
.hero-dot { width:7px; height:7px; border-radius:50%; background:#ffc369; }
.hero h1 { font-size:clamp(1.95rem,4.15vw,3rem); max-width:660px; margin-bottom:.28em; }
.hero p { color:#e0f4f0; }
.hero-action { display:inline-flex; padding:9px 18px; margin-top:8px; background:#ffc56d; color:#38280e; border-radius:10px; font-weight:750; }
.hero-action:hover { background:#ffda9e; }
.hero-side { padding:18px; border:1px solid #e2fff344; border-radius:16px; background:#ffffff12; }
.onboarding h2 { font-size:1.25rem; }
.hero-streak { display:flex; align-items:center; gap:5px; color:#ffe3a7; margin-bottom:15px; font-size:.86rem; }
.hero-meter { display:flex; align-items:center; gap:13px; }
.hero-meter p { margin:1px 0 0; font-size:.85rem; }
.ring { flex:none; width:82px; aspect-ratio:1; border-radius:50%; background:conic-gradient(#ffc56d var(--percent),#e4fff137 0); padding:5px; }
.ring > div { width:100%; height:100%; border-radius:50%; display:grid; place-content:center; text-align:center; line-height:1.2; background:#185c56; }
.ring strong { font-size:1.25rem; }
.ring small { color:#e0f4f0; font-size:.7rem; margin-top:2px; }
.dashboard-columns { display:grid; grid-template-columns:minmax(0,2.3fr) minmax(250px,1fr); align-items:start; gap:20px; }
.section-title h2,.dashboard-aside h2 { margin-bottom:5px; }
.section-title { margin-bottom:15px; }
.module-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:13px; }
.module-card { display:grid; gap:12px; color:var(--ink); padding:17px; transition:transform .18s,border-color .18s; }
.module-card:hover { border-color:var(--primary-text); transform:translateY(-3px); }
.module-card h3 { margin-bottom:4px; }
.module-card p { color:var(--muted); font-size:.87rem; }
.module-card small { font-size:.8rem; color:var(--primary-text); font-weight:700; }
.module-icon { width:43px; height:43px; display:grid; place-items:center; border-radius:12px; background:#dff3ec; color:#126258; }
.orange { background:#fff0da; color:#935110; }.blue { background:#e3effb; color:#285b82; }.purple { background:#eee7fa; color:#654899; }.rose { background:#fbe8ee; color:#9a4763; }.gold { background:#f9f0d8; color:#855c12; }
.dashboard-aside { display:grid; gap:13px; }
.dashboard-aside .panel { padding:18px; }
.quote { background:var(--teal-soft); }
.quote-head { display:flex; justify-content:space-between; align-items:center; }
.quote-head span { color:var(--primary-text); font:700 3rem/.7 Georgia,serif; }
.quote blockquote { margin:8px 0 6px; color:var(--ink); font:600 1.25rem/1.35 Georgia,serif; }
.quote p { font-size:.87rem; }
.chart { display:grid; grid-template-columns:repeat(7,minmax(0,1fr)); gap:8px; margin-top:10px; }
.chart-day { display:grid; justify-items:center; gap:3px; color:var(--muted); }
.bar-bg { width:min(100%,22px); height:63px; border-radius:5px; background:var(--surface-soft); display:flex; align-items:end; overflow:hidden; }
.bar-bg div { width:100%; background:var(--indicator); border-radius:5px; }
.chart-today { color:var(--primary-text); font-weight:750; }
.chart-today .bar-bg { background:var(--teal-soft); }
.chart-today .bar-bg div { background:var(--accent); }
@media(max-width:1000px) { .module-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media(max-width:767px) {
  .hero { grid-template-columns:1fr; padding:22px; gap:18px; }
  .hero h1 { font-size:1.95rem; }
  .hero-side { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; padding:12px; }
  .hero-side.onboarding { display:block; }
  .hero-streak { margin:0; }
  .ring { width:57px; padding:4px; }
  .ring strong { font-size:1rem; }
  .ring small { font-size:.61rem; }
  .hero-meter { gap:8px; }
  .hero-meter p { font-size:.74rem; }
  .dashboard-columns { grid-template-columns:1fr; }
}
</style>
