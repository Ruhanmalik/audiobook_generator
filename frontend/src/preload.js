// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
  showItemInFolder: async (relativePath) => {
    return await ipcRenderer.invoke('show-item-in-folder', relativePath);
  },
  openFile: async (relativePath) => {
    return await ipcRenderer.invoke('open-file', relativePath);
  }
});
