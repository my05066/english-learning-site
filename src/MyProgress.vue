<script setup>
import { computed } from 'vue'
import { clearData, daysAgo, state, streak } from './store.js'
import decks from './data/words.json'
import listening from './data/listening.json'
import reading from './data/reading.json'
import grammar from './data/grammar.json'
import phrases from './data/phrases.json'
import writing from './data/writing.json'

const completed = value => Object.values(value).filter(item => item && (item.completed || typeof item.score === 'number')).length
const vocabulary = decks.flatMap(deck => deck.words)
const wordsTotal = vocabulary.length
const stats = computed(() => [
  { label: '已学单词', value: vocabulary.filter(entry => Object.hasOwn(state.mastery, entry.word)).length, total: wordsTotal, path: '/words' },
  { label: '听力完成', value: completed(state.listening), total: listening.length, path: '/listening' },
  { label: '阅读完成', value: completed(state.reading), total: reading.length, path: '/reading' },
  { label: '语法完成', value: completed(state.grammar), total: grammar.length, path: '/grammar' },
  { label: '作文草稿', value: Object.keys(state.drafts).length, total: writing.prompts.length, path: '/writing/drafts' },
  { label: '已听表达', value: Object.keys(state.phrases).length, total: phrases.length, path: '/phrases' },
  { label: '连续天数', value: streak() }
])
function exportData() {
  const file = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(file)
  const link = Object.assign(document.createElement('a'), { href: url, download: 'english-corner-' + daysAgo(0) + '.json' })
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
function erase() {
  if (window.confirm('清除当前浏览器中的学习记录、错题和作文草稿？')) clearData()
}
</script>

<template>
  <div class="stack">
    <header class="page-head"><h1>我的学习</h1><p class="muted">查看学习进度、错题和写作草稿。</p></header>
    <div class="grid">
      <article v-for="stat in stats" :key="stat.label" class="panel">
        <component :is="stat.path ? 'RouterLink' : 'span'" :to="stat.path">{{ stat.label }}</component>
        <p class="stat-value">{{ stat.value }} <small v-if="stat.total" class="muted">/ {{ stat.total }}</small></p>
        <progress v-if="stat.total" :value="stat.value" :max="stat.total" :aria-label="stat.label"/>
      </article>
    </div>
    <section class="panel">
      <h2>学习记录</h2>
      <div class="actions"><RouterLink class="btn" to="/words/wrong">单词错题本 · {{ Object.keys(state.wrong).length }}</RouterLink><RouterLink class="btn secondary" to="/writing/drafts">我的作文</RouterLink></div>
      <div v-if="Object.keys(state.favorites).length" class="saved-words"><h3>阅读生词收藏</h3><div class="row"><span v-for="(entry, word) in state.favorites" :key="word" class="tag">{{ entry?.word || word }} {{ entry?.cn || '' }}</span></div></div>
    </section>
    <section class="panel"><h2>本地数据管理</h2><div class="actions"><button class="btn secondary" @click="exportData">导出学习记录</button><button class="btn danger" @click="erase">清除学习记录</button></div></section>
  </div>
</template>

<style scoped>
.stat-value { font-size:1.8rem; font-weight:750; margin:0; }
.stat-value small { font-size:.95rem; }
progress { width:100%; }
.saved-words { margin-top:20px; }
</style>
