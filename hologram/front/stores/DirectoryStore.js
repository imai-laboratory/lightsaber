import AppDispatcher from '../dispatcher/AppDispatcher'
import AppConstants from '../constants/AppConstants'
import { EventEmitter } from 'events'

let CHANGE_EVENT = 'change'

let store = []

class DirectoryStore extends EventEmitter {
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

let directoryStore = new DirectoryStore()
directoryStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.actionType) {
    case AppConstants.LOAD_DIRECTORIES_COMPLETED:
      store = action.directories
      directoryStore.emitChange()
      break
  }
})

export default directoryStore
