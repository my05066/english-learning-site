import { reactive, watch } from 'vue'
import wordAudio from './data/word-audio.json'

const key = 'english-corner-v1'
const defaults = () => ({
  mastery: {}, wrong: {}, favorites: {}, listening: {}, reading: {}, grammar: {},
  drafts: {}, phrases: {}, days: {}, last: null, theme: 'light', autoplayWord: true
})
let saved
try { saved = JSON.parse(localStorage.getItem(key)) } catch {}
export const state = reactive({ ...defaults(), ...saved })
watch(state, () => {
  try { localStorage.setItem(key, JSON.stringify(state)) } catch {}
  document.documentElement.dataset.theme = state.theme
}, { deep: true, immediate: true, flush: 'sync' })
export function clearData() { Object.assign(state, defaults(), { theme: state.theme }) }

export function dateKey(date = new Date()) {
  return [date.getFullYear(), date.getMonth() + 1, date.getDate()]
    .map(value => String(value).padStart(2, '0')).join('-')
}
export function daysAgo(count) {
  const date = new Date()
  date.setDate(date.getDate() - count)
  return dateKey(date)
}
export function streak() {
  let offset = state.days[daysAgo(0)] ? 0 : 1
  let count = 0
  while (state.days[daysAgo(offset++)]) count++
  return count
}
export function record(label, path) {
  const today = dateKey()
  state.days[today] = (state.days[today] || 0) + 1
  if (label && path) remember(label, path)
}
export function remember(label, path) { state.last = { label, path } }

export function addWrong(entry) { state.wrong[entry.word.toLowerCase()] = { ...entry } }
export function markWord(entry, known) {
  const word = (typeof entry === 'string' ? entry : entry.word).toLowerCase()
  const previous = state.mastery[word] || 0
  state.mastery[word] = known ? Math.min(3, previous + 1) : Math.max(0, previous - 1)
  if (!known && typeof entry !== 'string') addWrong(entry)
}
export function shuffle(array) {
  const result = [...array]
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  return result
}
export function audioFilename(id) {
  return String(id).toLowerCase().trim().replace(/[^a-z0-9'-]+/g, '-').replace(/^-+|-+$/g, '') + '.mp3'
}
export function audioUrl(category, id) {
  const mapped = category === 'words' ? wordAudio[id] : undefined
  return import.meta.env.BASE_URL + 'audio/' + category + '/' + encodeURIComponent(mapped || audioFilename(id))
}
let sound
let playSeq = 0
export async function playAudio(category, id) {
  const seq = ++playSeq
  sound?.pause()
  sound = new Audio(audioUrl(category, id))
  try { await sound.play(); return true } catch { return seq !== playSeq }
}
