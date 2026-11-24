<script setup>
import { computed, nextTick, ref, shallowRef, watch } from 'vue'
import { useRoute } from 'vue-router'
import Icon from './Icon.vue'
import { navigation } from './navigation.js'
import { state } from './store.js'

const route = useRoute()
const bottom = navigation.filter(item => ['home', 'words', 'listening', 'reading', 'me'].includes(item.icon))
const isActive = item => item.path === '/' ? route.path === '/' : route.path === item.path || route.path.startsWith(item.path + '/')
const searchDialog = ref()
const searchField = ref()
const query = ref('')
const searchIndex = shallowRef([])
const searchStatus = ref('idle')
const mainContent = ref()
let pageAnimation

const results = computed(() => {
  const tokens = query.value.toLowerCase().trim().split(/\s+/).filter(Boolean)
  return tokens.length ? searchIndex.value.filter(item => tokens.every(token => (item.title + ' ' + item.text).toLowerCase().includes(token))).slice(0, 24) : []
})
function focusMain() { mainContent.value?.focus() }
async function openSearch() {
  query.value = ''
  searchDialog.value.showModal()
  await nextTick()
  searchField.value?.focus()
  if (searchStatus.value === 'ready' || searchStatus.value === 'loading') return
  searchStatus.value = 'loading'
  try {
    const { searchIndex: index } = await import('./search.js')
    searchIndex.value = index
    searchStatus.value = 'ready'
  } catch {
    searchStatus.value = 'error'
  }
}
watch(() => route.fullPath, () => searchDialog.value?.close())
watch(() => route.path, (_, previous) => {
  pageAnimation?.cancel()
  if (!previous || matchMedia('(prefers-reduced-motion: reduce)').matches) return
  pageAnimation = mainContent.value?.animate(
    [{ opacity: 0.85, transform: 'translateY(3px)' }, { opacity: 1, transform: 'translateY(0)' }],
    { duration: 160, easing: 'ease-out' }
  )
}, { flush: 'post' })
</script>

<template>
  <a href="#main-content" class="skip-link" @click.prevent="focusMain">跳到内容</a>
  <header class="topbar">
    <div class="topbar-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-icon"><Icon name="reading" :size="23"/></span>
        <span><strong>英语角</strong><small>ENGLISH CORNER</small></span>
      </RouterLink>
      <nav class="desktop-nav" aria-label="主导航">
        <RouterLink v-for="item in navigation" :key="item.path" :to="item.path" :class="{ active: isActive(item) }">{{ item.nav }}</RouterLink>
      </nav>
      <div class="top-actions">
        <button class="icon-button" aria-label="全站搜索" title="全站搜索" @click="openSearch"><Icon name="search" :size="20"/></button>
        <button class="icon-button" :aria-label="state.theme === 'dark' ? '切换浅色模式' : '切换深色模式'" :title="state.theme === 'dark' ? '切换浅色模式' : '切换深色模式'" @click="state.theme = state.theme === 'dark' ? 'light' : 'dark'"><Icon :name="state.theme === 'dark' ? 'sun' : 'moon'" :size="20"/></button>
      </div>
    </div>
  </header>
  <main ref="mainContent" id="main-content" class="site-main" tabindex="-1"><RouterView/></main>
  <footer class="site-footer"><span>英语角 · English Corner</span><span>学习记录保存在当前浏览器</span></footer>
  <nav class="bottom-nav" aria-label="移动端导航">
    <RouterLink v-for="item in bottom" :key="item.path" :to="item.path" :class="{ active: isActive(item) }"><Icon :name="item.icon" :size="21"/>{{ item.nav }}</RouterLink>
  </nav>
  <dialog ref="searchDialog" class="search-dialog" aria-labelledby="search-title" @click.self="searchDialog.close()">
    <div class="search-body">
      <div class="split"><h2 id="search-title">全站搜索</h2><button class="icon-button" aria-label="关闭" @click="searchDialog.close()"><Icon name="close"/></button></div>
      <input ref="searchField" v-model="query" type="search" placeholder="搜索单词、文章或写作模板" aria-label="搜索关键词">
      <p v-if="searchStatus === 'loading'" class="muted" role="status">正在加载搜索索引…</p>
      <p v-else-if="searchStatus === 'error'" class="muted" role="status">搜索索引加载失败。关闭后可重新打开搜索。</p>
      <p v-else-if="!results.length" class="muted" role="status">{{ query.trim() ? '没有找到相关内容。' : '输入英文单词、中文释义或标题。' }}</p>
      <ul v-else class="search-results">
        <li v-for="(item, index) in results" :key="index"><RouterLink :to="item.to" @click="searchDialog.close()"><span><strong>{{ item.title }}</strong><small>{{ item.text }}</small></span><span class="tag">{{ item.kind }}</span></RouterLink></li>
      </ul>
    </div>
  </dialog>
</template>
