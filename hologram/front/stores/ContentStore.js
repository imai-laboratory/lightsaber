import AppDispatcher from '../dispatcher/AppDispatcher'
import AppConstants from '../constants/AppConstants'
import { EventEmitter } from 'events'

let CHANGE_EVENT = 'change'

let store = []

function jsonize (content) {
  const rows = content.split('\n')
  rows.pop()
  const json = '{"tmp": [' + rows.join(',') + ']}'
  return JSON.parse(json).tmp
}

class ContentStore extends EventEmitter {
  getAll () {
    return store
  }

  emitChange () {
    this.emit(CHANGE_EVENT)
  }

  addChangeListener (callback) {
    this.on(CHANGE_EVENT, callback)
  }

  removeChangeListener (callback) {
    this.removeListener(CHANGE_EVENT, callback)
  }

  getContent (dirName, fileName) {
    const index = getIndex(dirName, fileName)
    if (index === -1) {
      return null
    } else {
      return jsonize(store[index].content)
    }
  }

  getContents (fileName) {
    const contents = []
    for (let i = 0; i < store.length; ++i) {
      const dirName = store[i].dirName
      if (store[i].fileName === fileName) {
        const content = this.getContent(dirName, fileName)
        contents.push({
          dirName: dirName,
          fileName: fileName,
          data: content
        })
      }
    }
    return contents
  }

  getParameters () {
    const parameters = []
    for (let i = 0; i < store.length; ++i) {
      if (store[i].fileName === 'constants.json') {
        const parameter = JSON.parse(store[i].content)
        parameters.push({dirName: store[i].dirName, parameter: parameter})
      }
    }
    return parameters
  }
}

function getIndex (dirName, fileName) {
  let exists = false
  let i = 0
  for (i = 0; i < store.length; ++i) {
    if (store[i].dirName === dirName && store[i].fileName === fileName) {
      exists = true
      break
    }
  }
  if (exists) {
    return i
  } else {
    return -1
  }
}

let contentStore = new ContentStore()
contentStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.actionType) {
    case AppConstants.LOAD_CONTENT_COMPLETED:
      const dirName = action.dirName
      const fileName = action.fileName
      const content = action.content
      const index = getIndex(dirName, fileName)
      if (index === -1) {
        store.push({
          dirName: dirName,
          fileName: fileName,
          content: content
        })
      } else {
        store[index].content = content
      }
      contentStore.emitChange()
      break
  }
})

export default contentStore
