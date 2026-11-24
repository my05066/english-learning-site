<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Icon from './Icon.vue'
import decks from './data/words.json'
import { markWord, playAudio, record, remember, shuffle, state } from './store.js'

const route = useRoute()
const entries = decks.flatMap(deck => deck.words.map(entry => ({ ...entry, deck: deck.id })))
const entryByWord = new Map(entries.map(entry => [entry.word, entry]))
const masteryLabels = ['待学习', '初识', '熟悉', '已掌握']
const mastery = entry => state.mastery[entry.word] || 0
const learned = deck => deck.words.filter(entry => Object.hasOwn(state.mastery, entry.word)).length
const page = computed(() => route.params.deck ? 'deck' : route.path.split('/')[2] || 'index')
const deck = computed(() => decks.find(item => item.id === route.params.deck))
const isFlash = computed(() => route.query.mode === 'flash')
const isRetry = computed(() => route.query.source === 'wrong')
const query = ref('')
const normal = value => String(value ?? '').normalize('NFKC').trim().toLowerCase()
const matches = (value, search) => {
  const candidate = normal(value)
  if (candidate.includes(search)) return true
  if (!/^[a-z]{3,}$/.test(search) || !/^[a-z]+$/.test(candidate)) return false
  let index = 0
  for (const char of candidate) if (char === search[index]) index++
  return index === search.length
}
const searchResults = computed(() => {
  const search = normal(query.value)
  return search ? entries.filter(entry => [entry.word, entry.cn, entry.phonetic].some(value => matches(value, search))) : []
})
const audioError = ref(false)
async function speak(entry) {
  audioError.value = !(await playAudio('words', entry.word))
}

const cardIndex = ref(0)
const flipped = ref(false)
const card = computed(() => deck.value?.words[cardIndex.value])
const deckLink = (id, word, flash = false) => ({
  path: '/words/' + id,
  query: { ...(word ? { word } : {}), ...(flash ? { mode: 'flash' } : {}) }
})
function cardPath(entry) {
  const params = new URLSearchParams({ word: entry.word })
  if (isFlash.value) params.set('mode', 'flash')
  return route.path + '?' + params
}
function moveCard(step) {
  const length = deck.value.words.length
  cardIndex.value = (cardIndex.value + step + length) % length
  flipped.value = false
  audioError.value = false
  remember(deck.value.name + ' · ' + card.value.word, cardPath(card.value))
  if (state.autoplayWord && card.value) speak(card.value)
}
function gradeCard(known) {
  const entry = card.value
  markWord(entry, known)
  record(deck.value.name, cardPath(entry))
  moveCard(1)
}

const savedWrong = computed(() => Object.values(state.wrong))
const savedFavorites = computed(() => Object.values(state.favorites).map(entry => typeof entry === 'string' ? entryByWord.get(entry) : entry).filter(entry => entry?.word))
const selectedDeck = ref('')
const spellMode = ref('audio')
const round = ref([])
const questionIndex = ref(0)
const attempt = ref('')
const chosen = ref(null)
const score = ref(0)
const finished = ref(false)
const question = computed(() => round.value[questionIndex.value])
const isQuiz = computed(() => page.value === 'quiz')
const modeLabel = computed(() => isQuiz.value ? '四选一测验' : '拼写练习')
const canSound = entry => entryByWord.has(entry?.word)
function resetRound() {
  round.value = []
  questionIndex.value = 0
  chosen.value = null
  score.value = 0
  finished.value = false
  attempt.value = ''
  audioError.value = false
}
function questionsFor(entry) {
  const mode = Math.random() < 0.5 ? 'word' : 'cn'
  const optionKey = mode === 'word' ? 'cn' : 'word'
  const answer = entry[optionKey]
  const options = new Set([answer])
  for (const option of shuffle(entries)) {
    options.add(option[optionKey])
    if (options.size === 4) break
  }
  return { entry, prompt: entry[mode], answer, options: shuffle([...options]), direction: mode === 'word' ? '英译中' : '中译英' }
}
function startRound() {
  resetRound()
  const chosenDeck = decks.find(item => item.id === selectedDeck.value)
  const pool = isRetry.value ? savedWrong.value : chosenDeck?.words || entries
  round.value = shuffle(pool).slice(0, 10).map(entry => (isQuiz.value ? questionsFor(entry) : { entry, answer: entry.word }))
}
function grade(answer) {
  if (chosen.value !== null || !question.value || !answer.trim()) return
  const current = question.value
  chosen.value = answer
  const correct = normal(answer) === normal(current.answer)
  if (correct) score.value++
  markWord(current.entry, correct)
  record(modeLabel.value, route.fullPath)
}
function nextQuestion() {
  if (chosen.value === null) return
  if (questionIndex.value === round.value.length - 1) {
    finished.value = true
    return
  }
  questionIndex.value++
  chosen.value = null
  attempt.value = ''
  audioError.value = false
}
function optionClass(option) {
  if (chosen.value === null) return ''
  if (option === question.value.answer) return 'correct'
  return option === chosen.value ? 'incorrect' : ''
}
watch(() => route.fullPath, () => {
  resetRound()
  selectedDeck.value = decks.some(item => item.id === route.query.deck) ? route.query.deck : ''
  flipped.value = false
  const index = deck.value?.words.findIndex(entry => entry.word === route.query.word) ?? -1
  cardIndex.value = Math.max(0, index)
  if (card.value) remember(deck.value.name + ' · ' + card.value.word, cardPath(card.value))
}, { immediate: true })
</script>

<template>
  <section v-if="page === 'index'">
    <header class="page-head word-head">
      <div class="tag"><Icon name="words" :size="16" /> Vocabulary</div>
      <h1>单词学习</h1>
      <p class="muted">认识新词，反复回想，把记住的词用到真实语境里。</p>
    </header>
    <div class="stack">
      <div class="row">
        <RouterLink class="btn" to="/words/quiz">四选一测验</RouterLink>
        <RouterLink class="btn secondary" to="/words/spelling">拼写练习</RouterLink>
        <RouterLink class="btn secondary" to="/words/wrong">错题本 · {{ savedWrong.length }}</RouterLink>
      </div>
      <label class="word-search">
        <Icon name="search" :size="19" />
        <input v-model="query" type="search" placeholder="搜索英文单词、释义或音标" aria-label="在所有词库搜索" />
      </label>
      <div v-if="query.trim()" class="panel">
        <p class="muted" role="status">{{ searchResults.length ? '找到 ' + searchResults.length + ' 个单词' : '没有找到匹配的单词。试试词根或中文释义。' }}</p>
        <ul v-if="searchResults.length" class="word-list">
          <li v-for="entry in searchResults" :key="entry.word" class="split">
            <RouterLink :to="deckLink(entry.deck, entry.word)">
              <strong>{{ entry.word }}</strong>
              <span class="muted"> · {{ entry.cn }} · {{ entry.level }}</span>
            </RouterLink>
            <button class="icon-button" type="button" :aria-label="'播放 ' + entry.word" @click="speak(entry)"><Icon name="sound" :size="19" /></button>
          </li>
        </ul>
      </div>
      <div v-else class="grid decks">
        <article v-for="item in decks" :key="item.id" class="panel stack deck-card">
          <div class="split"><span class="deck-icon"><Icon name="words" /></span><span class="tag">{{ item.words.length }} 词</span></div>
          <div><h2>{{ item.name }}</h2><p class="muted">{{ item.description }}</p></div>
          <div class="deck-progress">
            <progress :value="learned(item)" :max="item.words.length" :aria-label="item.name + ' 学习进度'" />
            <small class="muted">已学 {{ learned(item) }} / {{ item.words.length }}</small>
          </div>
          <div class="row">
            <RouterLink class="btn" :to="deckLink(item.id)">学习单词</RouterLink>
            <RouterLink class="btn secondary" :to="deckLink(item.id, '', true)">闪卡</RouterLink>
          </div>
        </article>
      </div>
    </div>
  </section>

  <section v-else-if="page === 'deck' && card" class="word-workspace stack">
    <header class="word-head">
      <RouterLink to="/words">返回词库</RouterLink>
      <h1>{{ deck.name }}</h1>
      <p class="muted">{{ isFlash ? '先尝试回忆中文释义，再翻看答案。' : '读出单词，回想含义，然后标记掌握情况。' }}</p>
    </header>
    <nav class="row" aria-label="词库练习模式">
      <RouterLink :class="['btn', { secondary: isFlash }]" :to="deckLink(deck.id, card.word)">学习模式</RouterLink>
      <RouterLink :class="['btn', { secondary: !isFlash }]" :to="deckLink(deck.id, card.word, true)">闪卡模式</RouterLink>
      <RouterLink class="btn secondary" :to="{ path: '/words/quiz', query: { deck: deck.id } }">词库测验</RouterLink>
      <RouterLink class="btn secondary" :to="{ path: '/words/spelling', query: { deck: deck.id } }">拼写练习</RouterLink>
    </nav>
    <label class="autoplay-toggle">
      <input type="checkbox" v-model="state.autoplayWord">
      <span>切换单词时自动播放发音</span>
    </label>
    <article class="panel stack">
      <div class="split">
        <span class="tag">第 {{ cardIndex + 1 }} / {{ deck.words.length }} 张</span>
        <span class="muted">{{ masteryLabels[mastery(card)] }} · {{ mastery(card) }}/3</span>
      </div>
      <div class="flip-shell" :class="{ flipped }">
        <div class="flip-inner">
          <button class="flip-face flip-front" type="button" :tabindex="flipped ? -1 : 0" :aria-hidden="flipped" @click="flipped = true">
            <strong>{{ card.word }}</strong>
            <span v-if="!isFlash">{{ card.phonetic }}</span>
            <small>点击翻卡</small>
          </button>
          <button class="flip-face flip-back" type="button" :tabindex="flipped ? 0 : -1" :aria-hidden="!flipped" @click="flipped = false">
            <strong>{{ card.cn }}</strong>
            <span>{{ card.pos }} {{ card.phonetic }}</span>
            <span lang="en">{{ card.example }}</span>
            <small>{{ card.exampleCn }}</small>
          </button>
        </div>
      </div>
      <div class="row centered">
        <button class="btn secondary" type="button" @click="speak(card)"><Icon name="sound" :size="18" /> 播放发音</button>
        <button class="btn secondary" type="button" :aria-label="flipped ? '显示单词' : '显示释义'" @click="flipped = !flipped">{{ flipped ? '显示单词' : '显示释义' }}</button>
      </div>
      <div class="row centered">
        <button class="btn secondary" type="button" @click="moveCard(-1)">上一张</button>
        <button v-if="!isFlash" class="btn secondary" type="button" @click="gradeCard(false)">不认识</button>
        <button v-if="!isFlash" class="btn" type="button" @click="gradeCard(true)">认识</button>
        <button class="btn secondary" type="button" @click="moveCard(1)">下一张</button>
      </div>
    </article>
  </section>

  <section v-else-if="page === 'quiz' || page === 'spelling'" class="word-workspace stack">
    <header class="word-head">
      <RouterLink :to="isRetry ? '/words/wrong' : '/words'">{{ isRetry ? '返回错题本' : '返回词库' }}</RouterLink>
      <h1>{{ isRetry ? '错题重练 · ' : '' }}{{ modeLabel }}</h1>
    </header>
    <article v-if="!round.length" class="panel stack">
      <p class="muted">{{ isRetry ? '从错题本抽取最多 10 个单词。' : '每组 10 题，提交后即时查看答案和例句。' }}</p>
      <label v-if="!isRetry" class="row">练习词库
        <select v-model="selectedDeck">
          <option value="">全库混合</option>
          <option v-for="item in decks" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
      </label>
      <label v-if="!isQuiz" class="row">出题方式
        <select v-model="spellMode">
          <option value="audio">听读音拼写</option>
          <option value="meaning">看释义拼写</option>
        </select>
      </label>
      <div><button class="btn" type="button" :disabled="isRetry && !savedWrong.length" @click="startRound">开始练习</button></div>
    </article>
    <article v-else-if="finished" class="panel stack">
      <h2>本组练习完成</h2>
      <p>答对 <strong>{{ score }} / {{ round.length }}</strong> 题。</p>
      <div class="row">
        <button class="btn" type="button" @click="startRound">再练一组</button>
        <RouterLink class="btn secondary" to="/words/wrong">查看错题本</RouterLink>
      </div>
    </article>
    <article v-else class="panel stack">
      <div class="split"><span class="tag">第 {{ questionIndex + 1 }} / {{ round.length }} 题</span><span class="muted">{{ question.direction || '拼写' }}</span></div>
      <template v-if="isQuiz">
        <h2>{{ question.prompt }}</h2>
        <div class="options">
          <button v-for="(option, index) in question.options" :key="option" type="button" :disabled="chosen !== null" :class="['option', optionClass(option)]" @click="grade(option)">
            {{ 'ABCD'[index] }}. {{ option }}
          </button>
        </div>
      </template>
      <form v-else class="stack" @submit.prevent="grade(attempt)">
        <div class="row">
          <span v-if="spellMode === 'meaning' || !canSound(question.entry)">{{ question.entry.pos }} {{ question.entry.cn }}</span>
          <button v-if="canSound(question.entry)" class="btn secondary" type="button" @click="speak(question.entry)"><Icon name="sound" :size="18" /> 播放发音</button>
        </div>
        <label class="stack spell-field">
          <span>输入英文单词</span>
          <input v-model="attempt" :disabled="chosen !== null" autocapitalize="off" autocomplete="off" :spellcheck="false" />
        </label>
        <div v-if="chosen === null"><button class="btn" type="submit" :disabled="!attempt.trim()">检查拼写</button></div>
      </form>
      <div v-if="chosen !== null" class="stack">
        <div :class="['notice', normal(chosen) === normal(question.answer) ? 'correct' : 'incorrect']" role="status">
          <strong>{{ normal(chosen) === normal(question.answer) ? '回答正确' : '回答有误' }}</strong>
          <div>{{ question.entry.word }} {{ question.entry.phonetic }} · {{ question.entry.pos }} {{ question.entry.cn }}</div>
          <div v-if="question.entry.example" lang="en">{{ question.entry.example }}</div>
          <div v-if="question.entry.exampleCn">{{ question.entry.exampleCn }}</div>
        </div>
        <div><button class="btn" type="button" @click="nextQuestion">{{ questionIndex + 1 === round.length ? '查看成绩' : '下一题' }}</button></div>
      </div>
    </article>
  </section>

  <section v-else-if="page === 'wrong'" class="word-workspace stack">
    <header class="word-head">
      <RouterLink to="/words">返回词库</RouterLink>
      <h1>单词错题本</h1>
      <p class="muted">错题和学习时标记为不认识的单词会保存在这里。</p>
    </header>
    <div v-if="savedWrong.length" class="row">
      <RouterLink class="btn" to="/words/quiz?source=wrong">重练选择题</RouterLink>
      <RouterLink class="btn secondary" to="/words/spelling?source=wrong">重练拼写</RouterLink>
    </div>
    <article class="panel">
      <h2>待复习 · {{ savedWrong.length }}</h2>
      <p v-if="!savedWrong.length" class="muted">错题本还是空的。练习中答错的单词会出现在这里。</p>
      <ul v-else class="word-list">
        <li v-for="entry in savedWrong" :key="entry.word" class="split">
          <div>
            <strong>{{ entry.word }}</strong> <span class="muted">{{ entry.phonetic }} · {{ entry.cn }}</span>
            <div v-if="entry.example" class="muted" lang="en">{{ entry.example }}</div>
          </div>
          <div class="row">
            <button v-if="canSound(entry)" class="icon-button" type="button" :aria-label="'播放 ' + entry.word" @click="speak(entry)"><Icon name="sound" :size="19" /></button>
            <button class="btn secondary" type="button" @click="delete state.wrong[entry.word.toLowerCase()]">移除</button>
          </div>
        </li>
      </ul>
    </article>
    <article v-if="savedFavorites.length" class="panel">
      <h2>收藏 · {{ savedFavorites.length }}</h2>
      <ul class="word-list">
        <li v-for="entry in savedFavorites" :key="entry.word" class="split">
          <div><strong>{{ entry.word }}</strong> <span class="muted">{{ entry.phonetic }} · {{ entry.cn }}</span></div>
          <div class="row">
            <button v-if="canSound(entry)" class="icon-button" type="button" :aria-label="'播放 ' + entry.word" @click="speak(entry)"><Icon name="sound" :size="19" /></button>
            <button class="btn secondary" type="button" @click="delete state.favorites[entry.word.toLowerCase()]">移除</button>
          </div>
        </li>
      </ul>
    </article>
  </section>

  <section v-else class="panel"><h1>找不到该词库</h1><RouterLink class="btn" to="/words">返回词库</RouterLink></section>
  <p v-if="audioError" class="notice audio-error" role="status">音频未能播放，请重试。</p>
</template>

<style scoped>
.word-head h1 { margin-top:.35em; }
.word-workspace { max-width:760px;margin-inline:auto; }
.word-head .tag { margin-bottom:4px; }
.decks { grid-template-columns:repeat(2,minmax(0,1fr)); }
.deck-card { align-content:start; }
.deck-icon { display:grid;place-items:center;width:48px;height:48px;border-radius:13px;background:var(--teal-soft);color:var(--primary-text); }
.deck-card:nth-child(2n) .deck-icon { background:var(--surface-soft);color:var(--primary-text);box-shadow:inset 0 -3px var(--accent); }
.deck-progress progress { width:100%;display:block;height:9px;margin-bottom:7px; }
.word-search { display:flex;align-items:center;gap:10px;padding-inline:12px;background:var(--surface);border:1px solid var(--control-line);border-radius:12px;max-width:600px;color:var(--muted); }
.word-search input { flex:1;min-width:0;border:0;background:transparent;padding-inline:3px; }
.word-list { list-style:none;padding:0;margin:0; }
.word-list li { padding:9px 0;border-bottom:1px solid var(--line); }
.word-list li:last-child { border-bottom:0; }
.flip-shell { perspective:900px; }
.flip-inner { display:grid;transform-style:preserve-3d;transition:transform .38s ease; }
.flipped .flip-inner { transform:rotateY(180deg); }
.flip-face { grid-area:1/1;min-height:240px;border-radius:14px;border:1px solid var(--line);backface-visibility:hidden;display:grid;align-content:center;justify-items:center;gap:8px;text-align:center;background:var(--teal-soft);color:var(--ink);padding:22px 14px;overflow-wrap:anywhere; }
.flip-front strong { font-size:clamp(2rem,7vw,3.4rem);line-height:1.1; }
.flip-back { transform:rotateY(180deg);background:var(--surface-soft); }
.flip-back strong { font-size:clamp(1.5rem,5vw,2.3rem); }
.flip-face small { color:var(--muted); }
.centered { justify-content:center; }
.spell-field { gap:5px; }
.audio-error { margin:14px auto 0;max-width:760px; }
.autoplay-toggle { display:inline-flex;align-items:center;gap:9px;cursor:pointer;font-size:.95rem;color:var(--ink);background:var(--surface);border:1px solid var(--control-line);border-radius:999px;padding:8px 14px;align-self:flex-start; }
.autoplay-toggle input { width:18px;height:18px;accent-color:var(--teal,#0f766e);cursor:pointer; }
@media (max-width:600px) { .decks { grid-template-columns:1fr; } .flip-face { min-height:200px; } }
</style>
