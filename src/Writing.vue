<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import writing from './data/writing.json'
import { state, record, remember } from './store.js'

const route = useRoute()
const router = useRouter()
const templates = writing.templates
const prompts = writing.prompts
const exams = [...new Set(templates.map(template => template.exam))]
const exam = ref('')
const editor = ref(null)
const timer = ref(null)

const page = computed(() => route.path.split('/')[2] || 'library')
const template = computed(() => templates.find(item => item.id === route.params.id))
const prompt = computed(() => prompts.find(item => item.id === route.query.prompt))
const practiceTemplate = computed(() => templates.find(item => item.id === prompt.value?.templateId))
const activeDraft = computed(() => state.drafts[prompt.value?.id])
const text = computed(() => activeDraft.value?.text || '')
const count = computed(() => (text.value.match(/[A-Za-z0-9]+(?:[’,.'-][A-Za-z0-9]+)*/g) || []).length)
const draftList = computed(() => Object.entries(state.drafts)
  .map(([id, draft]) => ({ prompt: prompts.find(item => item.id === id), ...draft }))
  .filter(item => item.prompt)
  .sort((a, b) => b.updatedAt - a.updatedAt))
const filtered = computed(() => exam.value ? templates.filter(item => item.exam === exam.value) : templates)

let runningDraft
let lastTick = 0

function ensureDraft() {
  const id = prompt.value.id
  state.drafts[id] ??= { text: '', seconds: 0, submitted: false, checks: {}, updatedAt: Date.now() }
  return state.drafts[id]
}

function saveText(value) {
  const draft = ensureDraft()
  draft.text = value
  draft.updatedAt = Date.now()
}

function updateClock() {
  const elapsed = Math.floor((Date.now() - lastTick) / 1000)
  if (!runningDraft || elapsed <= 0) return
  runningDraft.seconds += elapsed
  runningDraft.updatedAt = Date.now()
  lastTick += elapsed * 1000
}

function stopClock() {
  if (timer.value === null) return
  updateClock()
  clearInterval(timer.value)
  timer.value = null
  runningDraft = undefined
}

function toggleClock() {
  if (timer.value !== null) {
    stopClock()
    return
  }
  runningDraft = ensureDraft()
  lastTick = Date.now()
  timer.value = setInterval(updateClock, 500)
}

function formatTime(seconds = 0) {
  return [Math.floor(seconds / 60), seconds % 60].map(value => String(value).padStart(2, '0')).join(':')
}

async function insertFrame(frame) {
  const start = editor.value?.selectionStart ?? text.value.length
  const end = editor.value?.selectionEnd ?? start
  const before = text.value.slice(0, start)
  const after = text.value.slice(end)
  const prefix = before && !/\s$/.test(before) ? ' ' : ''
  const suffix = after && !/^\s/.test(after) ? ' ' : ''
  saveText(before + prefix + frame + suffix + after)
  await nextTick()
  if (!editor.value) return
  editor.value.focus()
  const position = start + prefix.length + frame.indexOf('____')
  editor.value.setSelectionRange(position, position + 4)
}

function selectPrompt(event) {
  const id = event.target.value
  router.replace({ path: '/writing/practice', query: id ? { prompt: id } : {} })
}

function submit() {
  if (!text.value.trim()) return
  stopClock()
  activeDraft.value.submitted = true
  activeDraft.value.updatedAt = Date.now()
  record(`写作 · ${prompt.value.title}`, route.fullPath)
}

function revise() {
  activeDraft.value.submitted = false
  activeDraft.value.checks = {}
  activeDraft.value.updatedAt = Date.now()
}

function removeDraft(id) {
  if (window.confirm('确定删除这篇作文？正文、自评和计时记录都会被清除。')) {
    delete state.drafts[id]
  }
}

watch(() => route.fullPath, () => {
  stopClock()
  if (page.value === 'practice' && prompt.value) remember('写作 · ' + prompt.value.title, route.fullPath)
}, { immediate: true })
onBeforeUnmount(stopClock)
</script>

<template>
  <div class="writing">
    <div class="writing-header">
      <div>
        <p class="muted writing-mode">自评模式，无 AI 批改</p>
        <h1>{{ page === 'template' ? template?.name || '模板不存在' : page === 'practice' ? '写作练习' : page === 'drafts' ? '我的作文' : '写作模板' }}</h1>
        <p v-if="page === 'library'" class="muted">从文章框架和范文入手，练习把观点写清楚。</p>
        <p v-if="page === 'drafts'" class="muted">草稿与自评记录保存在此浏览器。</p>
      </div>
      <div class="writing-actions">
        <RouterLink v-if="page !== 'library'" to="/writing" class="btn">模板库</RouterLink>
        <RouterLink v-if="page !== 'practice'" to="/writing/practice" class="btn">写作练习</RouterLink>
        <RouterLink v-if="page !== 'drafts'" to="/writing/drafts" class="btn">我的作文</RouterLink>
      </div>
    </div>

    <template v-if="page === 'library'">
      <div class="writing-actions writing-filters" role="group" aria-label="按考试筛选">
        <button class="btn" :class="{ secondary: exam }" :aria-pressed="!exam" @click="exam = ''">全部</button>
        <button v-for="item in exams" :key="item" class="btn" :class="{ secondary: exam !== item }" :aria-pressed="exam === item" @click="exam = item">{{ item }}</button>
      </div>
      <p v-if="!filtered.length" class="panel empty-state" role="status">当前分类暂无模板。可以查看全部模板。</p>
      <div v-else class="grid">
        <RouterLink v-for="item in filtered" :key="item.id" class="panel writing-card" :to="`/writing/template/${item.id}`">
          <span class="tag">{{ item.exam }}</span>
          <h2>{{ item.name }}</h2>
          <p class="muted">{{ item.outline }}</p>
        </RouterLink>
      </div>
    </template>

    <template v-else-if="page === 'template' && template">
      <div class="panel writing-block">
        <span class="tag">{{ template.exam }}</span>
        <h2>段落框架</h2>
        <p>{{ template.outline }}</p>
        <ol class="outline">
          <li v-for="(step, index) in template.structure" :key="step.name">
            <strong>{{ step.name }}</strong>
            <p>{{ step.detail }}</p>
            <p lang="en" class="frame">{{ template.sentenceFrames[index].text }}</p>
          </li>
        </ol>
      </div>
      <div class="panel writing-block">
        <h2>范文 <span class="tag">{{ template.wordCount }} 词</span></h2>
        <p class="frame" lang="en">{{ prompts.find(item => item.id === template.id)?.prompt }}</p>
        <p class="essay" lang="en">{{ template.sampleEssay }}</p>
      </div>
      <div class="panel writing-block">
        <h2>高级表达</h2>
        <dl class="phrase-grid">
          <div v-for="item in template.usefulPhrases" :key="item.phrase">
            <dt lang="en">{{ item.phrase }}</dt>
            <dd class="muted">{{ item.cn }}</dd>
          </div>
        </dl>
      </div>
      <div class="panel writing-block">
        <h2>自查清单</h2>
        <ul><li v-for="item in template.checklist" :key="item">{{ item }}</li></ul>
        <RouterLink class="btn" :to="{ path: '/writing/practice', query: { prompt: template.id } }">用此模板练习</RouterLink>
      </div>
    </template>

    <template v-else-if="page === 'practice'">
      <div class="panel writing-block">
        <label for="writing-prompt"><strong>选择练习题</strong></label>
        <select id="writing-prompt" :value="prompt?.id || ''" @change="selectPrompt">
          <option value="">请选择题目</option>
          <optgroup v-for="group in exams" :key="group" :label="group">
            <option
              v-for="item in prompts.filter(entry => templates.some(t => t.id === entry.templateId && t.exam === group))"
              :key="item.id"
              :value="item.id"
            >{{ item.title }}</option>
          </optgroup>
        </select>
        <template v-if="prompt">
          <h2>{{ prompt.title }}</h2>
          <p lang="en" class="essay">{{ prompt.prompt }}</p>
          <RouterLink :to="`/writing/template/${practiceTemplate.id}`">查看关联模板</RouterLink>
        </template>
      </div>
      <div v-if="prompt" class="practice-grid">
        <div class="panel writing-block">
          <h2>写作区</h2>
          <div class="writing-actions editor-toolbar">
            <span>{{ count }} / {{ practiceTemplate.target }} 词</span>
            <span>用时 {{ formatTime(activeDraft?.seconds) }}</span>
            <button v-if="!activeDraft?.submitted" class="btn" @click="toggleClock">{{ timer === null ? '开始计时' : '暂停计时' }}</button>
          </div>
          <progress :value="Math.min(count, practiceTemplate.target)" :max="practiceTemplate.target" aria-label="目标词数进度"></progress>
          <label for="composition" class="editor-label">作文正文</label>
          <textarea
            id="composition"
            ref="editor"
            lang="en"
            :value="text"
            :readonly="activeDraft?.submitted"
            placeholder="Write your response here."
            @input="saveText($event.target.value)"
          ></textarea>
          <div class="writing-actions">
            <button v-if="activeDraft?.submitted" class="btn" @click="revise">继续编辑</button>
            <button v-else class="btn" :disabled="!text.trim()" @click="submit">交卷并自评</button>
            <span v-if="activeDraft" class="muted">已保存到此浏览器</span>
          </div>
        </div>
        <aside class="panel writing-block">
          <template v-if="activeDraft?.submitted">
            <h2>自评清单</h2>
            <p class="muted">逐项对照正文，勾选已经做到的项目。</p>
            <label v-for="(item, index) in practiceTemplate.checklist" :key="item" class="check-item">
              <input v-model="activeDraft.checks[index]" type="checkbox" @change="activeDraft.updatedAt = Date.now()" />
              <span>{{ item }}</span>
            </label>
          </template>
          <template v-else>
            <h2>套用句型</h2>
            <div v-for="frame in practiceTemplate.sentenceFrames" :key="frame.text" class="insert-frame">
              <strong>{{ frame.section }}</strong>
              <p lang="en">{{ frame.text }}</p>
              <button class="btn" @click="insertFrame(frame.text)">插入句型</button>
            </div>
          </template>
        </aside>
      </div>
    </template>

    <template v-else-if="page === 'drafts'">
      <div v-if="!draftList.length" class="panel writing-block empty-state">暂无作文。<RouterLink to="/writing/practice">选择一道练习题</RouterLink>开始写作。</div>
      <div v-for="item in draftList" :key="item.prompt.id" class="panel writing-block">
        <span class="tag">{{ item.submitted ? '已交卷' : '草稿' }}</span>
        <h2>{{ item.prompt.title }}</h2>
        <p class="draft-preview muted">{{ item.text.trim().slice(0, 150) || '尚未填写正文' }}</p>
        <div class="writing-actions">
          <RouterLink class="btn" :to="{ path: '/writing/practice', query: { prompt: item.prompt.id } }">{{ item.submitted ? '查看正文和自评' : '继续写作' }}</RouterLink>
          <button class="btn" @click="removeDraft(item.prompt.id)">删除</button>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.writing { overflow-wrap: anywhere; }
.writing-header { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 1rem; margin-bottom: 1.25rem; }
.writing-header h1 { margin: .2rem 0 .35rem; }
.writing-header p { margin: 0; }
.writing-mode { font-size: .875rem; }
.writing-actions { display: flex; flex-wrap: wrap; align-items: center; gap: .625rem; }
.writing-filters { margin-bottom: 1.25rem; }
.writing-card { display: block; color: inherit; text-decoration: none; min-width: 0; }
.writing-card h2 { font-size: 1.125rem; margin: 1rem 0 .5rem; }
.writing-card p { margin: 0; }
.writing-block { margin-bottom: 1rem; min-width: 0; }
.writing-block h2 { margin: .25rem 0 .8rem; font-size: 1.25rem; }
.writing-block > .tag + h2 { margin-top: 1rem; }
.outline { padding-inline-start: 1.5rem; }
.outline li + li { margin-top: 1rem; }
.outline p { margin: .25rem 0; }
.frame, .essay { line-height: 1.75; }
.essay { max-width: 72ch; white-space: pre-wrap; }
.phrase-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 230px), 1fr)); gap: 1rem; }
.phrase-grid dt { font-weight: 650; }
.phrase-grid dd { margin-inline-start: 0; }
select { display: block; width: min(100%, 34rem); margin: .625rem 0 1rem; }
.practice-grid { display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 1fr); gap: 1rem; align-items: start; }
.editor-toolbar { margin-bottom: .5rem; }
progress { width: 100%; height: .6rem; }
.editor-label { display: block; margin: .75rem 0 .375rem; }
textarea { min-height: 18rem; width: 100%; resize: vertical; margin-bottom: .75rem; box-sizing: border-box; font: inherit; line-height: 1.6; }
.insert-frame + .insert-frame { margin-top: 1rem; }
.insert-frame p { line-height: 1.5; margin: .3rem 0 .5rem; }
.check-item { display: flex; align-items: start; gap: .625rem; margin-bottom: 1rem; }
.check-item input { width: 1rem; height: 1rem; margin-top: .2rem; flex: 0 0 auto; }
.draft-preview { white-space: pre-wrap; }
@media (max-width: 768px) {
  .practice-grid { grid-template-columns: minmax(0, 1fr); gap: 0; }
}
</style>
