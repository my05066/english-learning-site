<script setup>
import { computed, ref, watch } from 'vue'
const props = defineProps({ questions: { type: Array, required: true } })
const emit = defineEmits(['complete'])
const selected = ref({})
watch(() => props.questions, () => { selected.value = {} })
const score = computed(() => props.questions.filter((q, index) => selected.value[index] === q.answer).length)
const finished = computed(() => Object.keys(selected.value).length === props.questions.length)

function answer(index, option) {
  if (selected.value[index] !== undefined) return
  selected.value[index] = option
  if (finished.value) emit('complete', score.value)
}
</script>

<template>
  <div class="stack questions">
    <p v-if="finished" class="notice" role="status"><strong>本次得分 {{ score }} / {{ questions.length }}</strong> <button type="button" class="btn secondary" @click="selected = {}">再练一次</button></p>
    <section v-for="(q, index) in questions" :key="index" class="panel">
      <h3>{{ index + 1 }}. {{ q.prompt }}</h3>
      <div class="options">
        <button v-for="(option, i) in q.options" :key="i" type="button" class="option" :class="{ correct: selected[index] !== undefined && i === q.answer, incorrect: selected[index] === i && i !== q.answer }" :disabled="selected[index] !== undefined" @click="answer(index, i)">
          <strong>{{ 'ABCD'[i] }}</strong> {{ option }}
        </button>
      </div>
      <p v-if="selected[index] !== undefined" role="status">{{ selected[index] === q.answer ? '回答正确。' : '正确答案是 ' + 'ABCD'[q.answer] + '。' }}{{ q.explanation }}</p>
    </section>
  </div>
</template>
