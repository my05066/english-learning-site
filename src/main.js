import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

const words = () => import('./Words.vue')
const listening = () => import('./Listening.vue')
const reading = () => import('./Reading.vue')
const writing = () => import('./Writing.vue')
const lessons = () => import('./Lessons.vue')
const overview = () => import('./Overview.vue')

const router = createRouter({
  history: createWebHashHistory(),
  scrollBehavior(to, from, saved) { return saved || (to.path !== from.path ? { top: 0 } : undefined) },
  routes: [
    { path: '/', component: overview },
    ...['/words', '/words/quiz', '/words/spelling', '/words/wrong', '/words/:deck'].map(path => ({ path, component: words })),
    ...['/listening', '/listening/:id'].map(path => ({ path, component: listening })),
    ...['/reading', '/reading/:id'].map(path => ({ path, component: reading })),
    ...['/writing', '/writing/template/:id', '/writing/practice', '/writing/drafts'].map(path => ({ path, component: writing })),
    ...['/grammar', '/grammar/:id', '/phrases'].map(path => ({ path, component: lessons })),
    { path: '/me', component: () => import('./MyProgress.vue') },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

createApp(App).use(router).mount('#app')
