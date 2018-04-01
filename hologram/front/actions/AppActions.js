import AppConstants from '../constants/AppConstants'
import AppDispatcher from '../dispatcher/AppDispatcher'
import Api from '../api/Api'

const actions = {
  loadDirectories: () => {
    AppDispatcher.dispatch({
      actionType: AppConstants.LOAD_DIRECTORIES_STARTED
    })
    Api.getDirectories()
      .then((directories) => {
        actions.loadDirectoriesCompleted(directories)
      })
  },
  loadDirectoriesCompleted: (directories) => {
    AppDispatcher.dispatch({
      actionType: AppConstants.LOAD_DIRECTORIES_COMPLETED,
      directories: directories
    })
  }
}
