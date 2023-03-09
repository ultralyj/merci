const { contextBridge, ipcRenderer } = require('electron')

global.electron = require('electron');
window.ipcRenderer = require('electron').ipcRenderer;
window.remote = require('electron').remote;

console.log("preload")
contextBridge.exposeInMainWorld('electronAPI',{
    openSerial: (portInfo) => ipcRenderer.invoke('serial:open',portInfo),
    closeSerial: () => ipcRenderer.invoke('serial:close'),
    requestList: () => ipcRenderer.invoke('serial:request'),
    onListSerial: (ports) => ipcRenderer.on('serial:list',ports),
    dataReadOut: (frame) => ipcRenderer.on('serial:data',frame),
})

