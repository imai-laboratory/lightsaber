import AppDispatcher from '../dispatcher/AppDispatcher'
import AppConstants from '../constants/AppConstants'
import { EventEmitter } from 'events'

let CHANGE_EVENT = 'change'

let store = {
  actives: []
}

class TableStore extends EventEmitter {
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

let tableStore = new TableStore()
tableStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.actionType) {
    case AppConstants.ENABLE_DIRECTORY:
      store.actives.push(action.value)
      tableStore.emitChange()
      break
    case AppConstants.DISABLE_DIRECTORY:
      for (let i = 0; i < store.actives.length; ++i) {
        if (store.actives[i] === action.value) {
          store.actives.splice(i, 1)
        }
      }
      tableStore.emitChange()
      break
  }
})

export default tableStore
