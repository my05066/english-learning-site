<script setup>
defineProps({ name: String, size: { type: Number, default: 22 } })
const paths = {
  home: 'M3 10l9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z M9 21v-7h6v7',
  words: 'M4 19V5a2 2 0 0 1 2-2h13v18H6a2 2 0 1 1 0-4h13 M8 7h7 M8 11h5',
  listening: 'M3 14v-3a9 9 0 0 1 18 0v3 M3 13h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M21 13h-3a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2z',
  reading: 'M12 6v15 M3 4c4-1 7 0 9 2 2-2 5-3 9-2v15c-4-1-7 0-9 2-2-2-5-3-9-2z',
  writing: 'M12 20H4v-8 M8 16l1-4L19 2l3 3-10 10z M16 5l3 3',
  grammar: 'M4 5h16 M4 10h12 M4 15h16 M4 20h10',
  phrases: 'M20 11a7 7 0 0 1-7 7H9l-5 3 1-5a7 7 0 0 1 4-12h4a7 7 0 0 1 7 7z M8 10h8 M8 13h5',
  me: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2 M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0z',
  search: 'M21 21l-5-5 M18 11a7 7 0 1 1-14 0 7 7 0 0 1 14 0z',
  moon: 'M20 15A9 9 0 0 1 9 4a9 9 0 1 0 11 11z',
  sun: 'M12 2v2 M12 20v2 M2 12h2 M20 12h2 M5 5l2 2 M17 17l2 2 M19 5l-2 2 M7 17l-2 2 M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0z',
  flame: 'M12 2c1 5 6 6 6 12a6 6 0 0 1-12 0c0-2 1-4 3-6 0 3 1 3 1 3 3-3 2-6 2-9z',
  sound: 'M4 9h4l5-4v14l-5-4H4z M16 9c2 2 2 4 0 6 M19 6c3 3 3 9 0 12',
  close: 'M6 6l12 12 M18 6L6 18'
}
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="paths[name] || paths.words"/></svg>
</template>
