import words from './data/words.json'
import listening from './data/listening.json'
import reading from './data/reading.json'
import writing from './data/writing.json'

export const searchIndex = [
  ...words.flatMap(deck => deck.words.map(word => ({ title: word.word, text: word.cn, kind: '单词', to: { path: '/words/' + deck.id, query: { word: word.word } } }))),
  ...listening.map(item => ({ title: item.title, text: item.topic, kind: '听力', to: '/listening/' + item.id })),
  ...reading.map(item => ({ title: item.title, text: item.topic, kind: '阅读', to: '/reading/' + item.id })),
  ...writing.templates.map(item => ({ title: item.name, text: item.exam, kind: '写作', to: '/writing/template/' + item.id }))
]
