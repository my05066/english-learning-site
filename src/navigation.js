export const modules = [
  { icon: 'words', title: '单词学习', nav: '单词', path: '/words', detail: '词库、闪卡与拼写练习', color: 'green', count: '4 套词库' },
  { icon: 'listening', title: '听力训练', nav: '听力', path: '/listening', detail: '精听、理解测验与听写', color: 'orange', count: '20 篇听力' },
  { icon: 'reading', title: '分级阅读', nav: '阅读', path: '/reading', detail: '阅读原文，积累新词', color: 'blue', count: '12 篇文章' },
  { icon: 'writing', title: '写作练习', nav: '写作', path: '/writing', detail: '拆解范文，练习限时写作', color: 'purple', count: '16 个模板' },
  { icon: 'grammar', title: '语法小课', nav: '语法', path: '/grammar', detail: '掌握规则，完成随堂小测', color: 'rose', count: '12 节小课' },
  { icon: 'phrases', title: '常用表达', nav: '表达', path: '/phrases', detail: '在真实语境中积累词块', color: 'gold', count: '60 个表达' }
]
export const navigation = [
  { icon: 'home', nav: '首页', path: '/' }, ...modules, { icon: 'me', nav: '我的', path: '/me' }
]
