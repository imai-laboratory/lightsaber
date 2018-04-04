import AppDispatcher from '../dispatcher/AppDispatcher'
import AppConstants from '../constants/AppConstants'
import { EventEmitter } from 'events'

let CHANGE_EVENT = 'change'

let store = {
  x: null,
  y: null,
  file: null,
  windowSize: 1
}

class HeaderStore extends EventEmitter {
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
}

let headerStore = new HeaderStore()
headerStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.actionType) {
    case AppConstants.CHANGE_X_AXIS:
      store.x = action.value
      headerStore.emitChange()
      break
    case AppConstants.CHANGE_Y_AXIS:
      store.y = action.value
      headerStore.emitChange()
      break
    case AppConstants.CHANGE_FILE:
      store.file = action.file
      headerStore.emitChange()
      break
    case AppConstants.CHANGE_WINDOW_SIZE:
      store.windowSize = action.value > 0 ? action.value : 1
      headerStore.emitChange()
      break
  }
})

export default headerStore
