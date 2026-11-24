<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Questions from './Questions.vue'
import articles from './data/reading.json'
import { addWrong, record, remember, state } from './store.js'

const route = useRoute()
const article = computed(() => articles.find(item => item.id === route.params.id))
const filter = ref('')
const filtered = computed(() => articles.filter(item => !filter.value || item.level === filter.value))
const saved = computed(() => state.reading[article.value?.id])
const activeWord = ref(null)
const dialog = ref(null)
const seconds = ref(0)
let timer
let start = null
let elapsed = 0
let timingDone = false

function wordForms(word) {
  const base = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return word.endsWith('y') ? base + '|' + base.slice(0, -1) + 'ies' : base + '(?:s|es)?'
}

const annotatedParagraphs = computed(() => {
  if (!article.value) return []
  const glossary = article.value.glossary
  const wordMatchers = glossary.map(entry => new RegExp('^(?:' + wordForms(entry.word) + ')$', 'i'))
  const expression = new RegExp('\\b(' + glossary.map(entry => wordForms(entry.word)).join('|') + ')\\b', 'gi')
  return article.value.paragraphs.map(paragraph => paragraph.split(expression).map((text, index) => {
    const entry = index % 2 ? glossary[wordMatchers.findIndex(matcher => matcher.test(text))] : null
    return { text, entry: entry ? { ...entry, example: paragraph.match(/[^.!?]+[.!?]*/g)?.find(sentence => sentence.includes(text))?.trim() ?? paragraph, level: article.value.level } : null }
  }))
})
const questions = computed(() => article.value?.questions.map(question => ({
  ...question, prompt: '[' + question.kind + '] ' + question.prompt
})) ?? [])

function refreshTime() {
  seconds.value = Math.floor((elapsed + (start === null ? 0 : performance.now() - start)) / 1000)
}

function setClock() {
  const shouldRun = article.value && !document.hidden && !timingDone
  if (start !== null && !shouldRun) {
    elapsed += performance.now() - start
    start = null
  } else if (start === null && shouldRun) {
    start = performance.now()
  }
  refreshTime()
}

onMounted(() => {
  timer = setInterval(refreshTime, 1000)
  document.addEventListener('visibilitychange', setClock)
})
onUnmounted(() => {
  clearInterval(timer)
  document.removeEventListener('visibilitychange', setClock)
})
watch(article, item => {
  start = null
  elapsed = 0
  timingDone = false
  setClock()
  if (dialog.value?.open) dialog.value.close()
  activeWord.value = null
  if (item) remember(item.title, route.path)
}, { immediate: true })

function timestamp(total) {
  return Math.floor(total / 60) + ' 分 ' + String(total % 60).padStart(2, '0') + ' 秒'
}

function complete(score) {
  if (!article.value) return
  timingDone = true
  setClock()
  state.reading[article.value.id] = { score, seconds: seconds.value, completed: true }
  record(article.value.title, route.path)
}

function showWord(entry) {
  activeWord.value = entry
  dialog.value?.showModal()
}

function saveWord() {
  addWrong(activeWord.value)
  state.favorites[activeWord.value.word.toLowerCase()] = { ...activeWord.value }
}
</script>

<template>
  <template v-if="article">
    <header class="page-head">
      <RouterLink to="/reading">返回阅读列表</RouterLink>
      <p><span class="tag">{{ article.level }}</span> {{ article.topic }} · {{ article.wordCount }} 词 · 预计 {{ article.minutes }} 分钟</p>
      <h1>{{ article.title }}</h1>
      <p class="muted">本次阅读 {{ timestamp(seconds) }}<span v-if="saved?.completed"> · 上次 {{ saved.score }}/5，{{ timestamp(saved.seconds) }}</span></p>
    </header>

    <article class="panel article-copy" lang="en">
      <p v-for="(paragraph, paragraphIndex) in annotatedParagraphs" :key="paragraphIndex">
        <template v-for="(part, index) in paragraph" :key="index"><button v-if="part.entry" class="word-link" type="button" aria-haspopup="dialog" @click="showWord(part.entry)">{{ part.text }}</button><template v-else>{{ part.text }}</template></template>
      </p>
    </article>

    <dialog ref="dialog" class="panel glossary-dialog" aria-labelledby="glossary-title" @click.self="dialog?.close()">
      <div v-if="activeWord" class="glossary-body">
        <div class="glossary-heading">
          <h2 id="glossary-title" lang="en">{{ activeWord.word }}</h2>
          <button class="btn secondary" type="button" @click="dialog.close()">关闭</button>
        </div>
        <p class="muted">{{ activeWord.phonetic }}</p>
        <p>{{ activeWord.cn }}</p>
        <button class="btn" type="button" :disabled="!!state.wrong[activeWord.word.toLowerCase()] && !!state.favorites[activeWord.word.toLowerCase()]" @click="saveWord">
          {{ state.wrong[activeWord.word.toLowerCase()] && state.favorites[activeWord.word.toLowerCase()] ? '已收藏并加入错题本' : '收藏并加入错题本' }}
        </button>
      </div>
    </dialog>

    <section class="reading-questions" aria-labelledby="reading-question-title">
      <h2 id="reading-question-title">阅读理解</h2>
      <Questions :key="article.id" :questions="questions" @complete="complete" />
    </section>
  </template>

  <section v-else-if="route.params.id" class="panel">
    <h1>未找到阅读材料</h1><RouterLink to="/reading">返回阅读列表</RouterLink>
  </section>

  <template v-else>
    <header class="page-head"><h1>阅读训练</h1><p class="muted">按难度选文章，点击文中生词查看释义，读完试试理解题。</p></header>
    <div class="reading-levels" aria-label="筛选难度">
      <button v-for="level in ['', 'A2', 'B1', 'B2', 'C1']" :key="level" type="button" class="btn" :class="{ secondary: filter !== level }" :aria-pressed="filter === level" @click="filter = level">{{ level || '全部' }}</button>
    </div>
    <p v-if="!filtered.length" class="panel empty-state" role="status">当前难度暂无文章。可以选择其他难度。</p>
    <div v-else class="grid">
      <RouterLink v-for="item in filtered" :key="item.id" class="panel reading-link" :to="'/reading/' + item.id">
        <div><span class="tag">{{ item.level }}</span> <span class="muted">{{ item.topic }}</span></div>
        <h2>{{ item.title }}</h2>
        <p class="muted">{{ item.wordCount }} 词 · 约 {{ item.minutes }} 分钟</p>
        <p v-if="state.reading[item.id]?.completed">已完成 · {{ state.reading[item.id].score }}/5</p>
      </RouterLink>
    </div>
  </template>
</template>

<style scoped>
.article-copy { margin-bottom: 2rem; }
.article-copy p { margin: 0 auto 1.2rem; max-width: 69ch; font-size: clamp(1rem, 2vw, 1.16rem); line-height: 1.9; }
.article-copy p:last-child { margin-bottom: 0; }
.word-link { display: inline; padding: 0; border: 0; border-radius: 0; background: transparent; color: inherit; font-weight: 700; text-decoration: underline dotted; text-decoration-color: var(--indicator); text-underline-offset: .22em; min-height: 0; }
.word-link:hover { color:var(--primary-text); }
.glossary-dialog { color: var(--ink); width: min(430px, calc(100vw - 2rem)); max-width: 100%; margin: auto; }
.glossary-dialog::backdrop { background: rgb(12 24 28 / .53); }
.glossary-heading { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
.glossary-heading h2 { margin: 0; }
.reading-levels { display: flex; gap: .5rem; flex-wrap: wrap; margin: 1rem 0; }
.reading-link { display: block; color: inherit; text-decoration: none; }
.reading-link h2 { margin: .8rem 0 .45rem; }
.reading-link p { margin-bottom: 0; }
</style>
