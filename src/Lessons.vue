<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Icon from './Icon.vue'
import Questions from './Questions.vue'
import grammar from './data/grammar.json'
import phrases from './data/phrases.json'
import { playAudio, record, remember, state } from './store.js'

const route = useRoute()
const lesson = computed(() => grammar.find(item => item.id === route.params.id))
const groups = [...new Set(phrases.map(item => item.group))]
const group = ref(groups[0])
const filtered = computed(() => phrases.filter(entry => entry.group === group.value))
const audioError = ref('')
watch(() => route.query.group, value => {
  if (groups.includes(value)) group.value = value
}, { immediate: true })
watch(group, () => { audioError.value = '' })
watch(lesson, item => { if (item) remember(item.title, route.path) }, { immediate: true })
async function speak(item) {
  audioError.value = ''
  if (await playAudio('phrases', item.id)) {
    state.phrases[item.id] = true
    record('常用表达 · ' + item.group, '/phrases?group=' + encodeURIComponent(item.group))
  } else {
    audioError.value = '无法播放该表达的音频，请确认设备允许网页播放声音。'
  }
}
function complete(score) {
  state.grammar[lesson.value.id] = { score }
  record(lesson.value.title, route.path)
}
</script>

<template>
  <div v-if="route.path === '/phrases'" class="stack">
    <header class="page-head"><h1>常用表达</h1><p class="muted">按场景积累词块，听美式发音，读例句。</p></header>
    <div class="row" aria-label="表达场景"><button v-for="name in groups" :key="name" class="btn" :class="{ secondary: group !== name }" :aria-pressed="group === name" @click="group = name">{{ name }}</button></div>
    <p v-if="audioError" class="notice" role="status">{{ audioError }}</p>
    <p v-if="!filtered.length" class="panel empty-state" role="status">当前场景暂无表达。可以选择其他场景。</p>
    <div v-else class="grid">
      <article v-for="item in filtered" :key="item.id" class="panel">
        <div class="split"><h2>{{ item.phrase }}</h2><button class="icon-button" :aria-label="'播放 ' + item.phrase" @click="speak(item)"><Icon name="sound"/></button></div>
        <p>{{ item.cn }}</p><p lang="en">{{ item.example }}</p><p class="muted">{{ item.exampleCn }}</p>
      </article>
    </div>
  </div>
  <div v-else-if="lesson" class="stack">
    <RouterLink to="/grammar">全部语法小课</RouterLink>
    <header><h1>{{ lesson.title }}</h1></header>
    <section class="panel"><h2>用法</h2><p>{{ lesson.summary }}</p></section>
    <section class="panel"><h2>例句</h2><ul><li v-for="example in lesson.examples" :key="example.en"><strong lang="en">{{ example.en }}</strong><p class="muted">{{ example.cn }}</p></li></ul></section>
    <section class="panel"><h2>易错点</h2><p>{{ lesson.pitfall }}</p></section>
    <h2>随堂小测</h2>
    <Questions :key="lesson.id" :questions="lesson.questions" @complete="complete"/>
  </div>
  <div v-else-if="route.params.id" class="panel"><h1>找不到这节课</h1><RouterLink to="/grammar">全部语法小课</RouterLink></div>
  <div v-else class="stack">
    <header class="page-head"><h1>语法小课</h1><p class="muted">从时态到主谓一致，用例句理解规则，再做五道小测。</p></header>
    <p v-if="!grammar.length" class="panel empty-state" role="status">暂无语法小课。</p>
    <div v-else class="grid"><RouterLink v-for="item in grammar" :key="item.id" :to="'/grammar/' + item.id" class="panel lesson-link"><h2>{{ item.title }}</h2><p class="muted">{{ item.summary }}</p><span class="tag">{{ state.grammar[item.id] ? '得分 ' + state.grammar[item.id].score + '/5' : '5 道随堂练习' }}</span></RouterLink></div>
  </div>
</template>

<style scoped>
.lesson-link { color:var(--ink); }
h2 { margin-bottom:.45em; }
li + li { margin-top:.65rem; }
</style>
