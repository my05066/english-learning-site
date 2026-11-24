<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Questions from './Questions.vue'
import lessons from './data/listening.json'
import { audioUrl, record, remember, state } from './store.js'

const route = useRoute()
const lesson = computed(() => lessons.find(item => item.id === route.params.id))
const levels = { A2: '初级', B1: '中级', B2: '中高级', C1: '高级' }
const filter = ref('')
const filtered = computed(() => lessons.filter(item => !filter.value || item.level === filter.value))
const mode = ref('quiz')
const showTranscript = ref(false)
const player = ref(null)
const time = ref(0)
const duration = ref(0)
const playing = ref(false)
const speed = ref(1)
const audioError = ref(false)
const entries = ref({})
const submitted = ref(null)
const dictationScore = computed(() => submitted.value?.filter(Boolean).length ?? 0)
const transcriptLines = computed(() => (lesson.value?.transcript || '').split('\n').filter(line => line.trim()).map(line => {
  const match = line.match(/^([A-Z][A-Za-z ]{0,20}):\s+(.*)$/)
  return match ? { speaker: match[1], text: match[2] } : { speaker: '', text: line }
}))

watch(lesson, (item) => {
  time.value = 0
  duration.value = 0
  playing.value = false
  audioError.value = false
  showTranscript.value = false
  mode.value = 'quiz'
  entries.value = {}
  submitted.value = null
  if (item) remember(item.title, route.path)
}, { immediate: true })

function updatePlayer(event) {
  const audio = event.target
  time.value = audio.currentTime
  duration.value = Number.isFinite(audio.duration) ? audio.duration : 0
  audio.playbackRate = speed.value
}

async function toggleAudio() {
  const audio = player.value
  if (!audio) return
  if (!audio.paused) {
    audio.pause()
    return
  }
  try {
    audioError.value = false
    await audio.play()
  } catch (error) {
    if (player.value === audio && error.name !== 'AbortError') audioError.value = true
  }
}

function seek(event) {
  if (!player.value || duration.value === 0) return
  player.value.currentTime = Number(event.target.value)
  time.value = player.value.currentTime
}

function changeSpeed() {
  if (player.value) player.value.playbackRate = speed.value
}

function timestamp(seconds) {
  const total = Math.floor(seconds)
  return Math.floor(total / 60) + ':' + String(total % 60).padStart(2, '0')
}

function saveResult(field, score) {
  if (!lesson.value) return
  const current = state.listening[lesson.value.id] || {}
  state.listening[lesson.value.id] = { ...current, [field]: score, completed: true }
  record(lesson.value.title, route.path)
}

function checkDictation() {
  submitted.value = lesson.value.dictation.map(({ answer }, index) =>
    (entries.value[index] ?? '').trim().toLowerCase() === answer.toLowerCase())
  saveResult('dictationScore', dictationScore.value)
}
</script>

<template>
  <template v-if="lesson">
    <header class="page-head">
      <RouterLink to="/listening">返回听力列表</RouterLink>
      <p><span class="tag">{{ lesson.level }}</span> {{ lesson.topic }}<span v-if="lesson.voice" class="muted"> · 配音：{{ lesson.voice }}</span></p>
      <h1>{{ lesson.title }}</h1>
    </header>
    <section class="panel audio-panel" aria-label="听力播放器">
      <audio :key="lesson.id" ref="player" :src="audioUrl('listening', lesson.id)" preload="metadata"
        @loadedmetadata="updatePlayer" @timeupdate="updatePlayer" @play="playing = true"
        @pause="playing = false" @ended="playing = false" @error="audioError = true"></audio>
      <div class="audio-controls">
        <button class="btn" type="button" @click="toggleAudio">{{ playing ? '暂停' : '播放' }}</button>
        <span>{{ timestamp(time) }} / {{ timestamp(duration) }}</span>
        <input type="range" aria-label="播放进度" :min="0" :max="duration || 1" step=".05" :value="time" :disabled="!duration" @input="seek">
        <select v-model.number="speed" aria-label="播放速度" @change="changeSpeed">
          <option v-for="rate in [0.75, 1, 1.25, 1.5]" :key="rate" :value="rate">{{ rate }}×</option>
        </select>
      </div>
      <p v-if="audioError" class="notice" role="status">音频无法播放，请重新尝试。</p>
      <button class="btn secondary" type="button" :aria-expanded="showTranscript" @click="showTranscript = !showTranscript">{{ showTranscript ? '隐藏原文' : '显示原文' }}</button>
      <div v-if="showTranscript" lang="en" class="transcript">
        <p v-for="(line, index) in transcriptLines" :key="index" class="transcript-line"><strong v-if="line.speaker" class="speaker">{{ line.speaker }}:</strong> {{ line.text }}</p>
      </div>
    </section>
    <div class="practice-modes" aria-label="练习模式">
      <button class="btn" :class="{ secondary: mode !== 'quiz' }" type="button" :aria-pressed="mode === 'quiz'" @click="mode = 'quiz'">理解测验</button>
      <button class="btn" :class="{ secondary: mode !== 'dictation' }" type="button" :aria-pressed="mode === 'dictation'" @click="mode = 'dictation'">听写填空</button>
    </div>
    <Questions v-show="mode === 'quiz'" :key="lesson.id" :questions="lesson.questions" @complete="saveResult('score', $event)" />
    <form v-if="mode === 'dictation'" class="panel stack" @submit.prevent="checkDictation">
      <h2>听写填空</h2>
      <p class="muted">按原文顺序填写五个缺失的词，提交后查看答案。</p>
      <div v-for="(item, index) in lesson.dictation" :key="index" class="dictation-item">
        <label :for="'dictation-' + index" lang="en">{{ index + 1 }}. {{ item.prompt }}</label>
        <input :id="'dictation-' + index" v-model="entries[index]" type="text" :disabled="submitted !== null" autocomplete="off" spellcheck="false" placeholder="输入缺失的英文单词">
        <p v-if="submitted !== null" role="status">{{ submitted[index] ? '正确' : '需要复习' }} · 答案 <strong>{{ item.answer }}</strong></p>
      </div>
      <button v-if="submitted === null" class="btn" type="submit">检查答案</button>
      <p v-else class="notice" role="status">本次听写 {{ dictationScore }} / {{ lesson.dictation.length }} <button class="btn secondary" type="button" @click="submitted = null; entries = {}">重新听写</button></p>
    </form>
  </template>

  <section v-else-if="route.params.id" class="panel">
    <h1>未找到听力材料</h1><RouterLink to="/listening">返回听力列表</RouterLink>
  </section>

  <template v-else>
    <header class="page-head"><h1>听力训练</h1><p class="muted">从日常对话到职场与文化话题，练习听大意、抓细节和听写。</p></header>
    <div class="practice-modes" aria-label="筛选难度">
      <button class="btn" type="button" :class="{ secondary: filter !== '' }" :aria-pressed="filter === ''" @click="filter = ''">全部</button>
      <button v-for="(name, level) in levels" :key="level" class="btn" type="button" :class="{ secondary: filter !== level }" :aria-pressed="filter === level" @click="filter = level">{{ level }} {{ name }}</button>
    </div>
    <p v-if="!filtered.length" class="panel empty-state" role="status">当前难度暂无听力材料。可以选择其他难度。</p>
    <div v-else class="grid">
      <RouterLink v-for="item in filtered" :key="item.id" class="panel lesson-link" :to="'/listening/' + item.id">
        <div><span class="tag">{{ item.level }}</span> <span class="muted">{{ item.topic }}</span></div>
        <h2>{{ item.title }}</h2>
        <p v-if="item.voice" class="muted">配音：{{ item.voice }}</p>
        <p v-if="state.listening[item.id]?.completed">已完成<span v-if="state.listening[item.id].score !== undefined"> · 理解 {{ state.listening[item.id].score }}/4</span><span v-if="state.listening[item.id].dictationScore !== undefined"> · 听写 {{ state.listening[item.id].dictationScore }}/5</span></p>
        <p v-else class="muted">理解测验 · 听写填空</p>
      </RouterLink>
    </div>
  </template>
</template>

<style scoped>
.audio-panel { margin-bottom: 1.2rem; }
.audio-controls { display: flex; flex-wrap: wrap; align-items: center; gap: .8rem; margin-bottom: 1rem; }
.audio-controls input { flex: 1 0 130px; width: auto; min-width: 0; padding: 0; accent-color: var(--indicator); min-height: 30px; }
.transcript { line-height: 1.85; max-width: 72ch; margin-bottom: 0; }
.transcript-line { margin: 0 0 .35em; }
.transcript-line .speaker { color: var(--primary-text, #0f766e); }
.practice-modes { display: flex; gap: .5rem; flex-wrap: wrap; margin: 1rem 0; }
.dictation-item { display: grid; gap: .45rem; }
.dictation-item p { margin: 0; }
.lesson-link { display: block; color: inherit; text-decoration: none; }
.lesson-link h2 { margin: .8rem 0 .45rem; }
.lesson-link p { margin-bottom: 0; }
</style>
