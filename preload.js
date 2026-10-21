'use strict';
const { contextBridge, ipcRenderer } = require('electron');
const inv = (c, ...a) => ipcRenderer.invoke(c, ...a);
contextBridge.exposeInMainWorld('beast', {
  status: () => inv('vault:status'),
  create: p => inv('vault:create', p),
  unlock: p => inv('vault:unlock', p),
  save: j => inv('vault:save', j),
  lock: () => inv('vault:lock'),
  changePass: (o, n, j) => inv('vault:change', o, n, j),
  activity: () => inv('vault:activity'),
  setMinutes: m => inv('vault:minutes', m),
  saveFile: (n, t) => inv('file:save', n, t),
  onLocked: cb => ipcRenderer.on('vault:locked', () => cb())
});
