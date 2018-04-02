import AppConstants from '../constants/AppConstants'
import AppDispatcher from '../dispatcher/AppDispatcher'
import Api from '../api/Api'

const actions = {
  loadDirectories: () => {
    AppDispatcher.dispatch({
      actionType: AppConstants.LOAD_DIRECTORIES_STARTED
    })
    Api.getDirectories()
      .then((data) => {
        actions.loadDirectoriesCompleted(data.dirs)
      })
  },
  loadDirectoriesCompleted: (directories) => {
    AppDispatcher.dispatch({
      actionType: AppConstants.LOAD_DIRECTORIES_COMPLETED,
      directories: directories
    })
    for (let directory of directories) {
      actions.loadContent(directory.directory, 'constants.json')
    }
  },
  loadContent: (dirName, fileName) => {
    AppDispatcher.dispatch({
      actionType: AppConstants.LOAD_CONTENT_STARTED,
      dirName: dirName,
      fileName: fileName
    })
    Api.getContent(dirName, fileName)
      .then((data) => {
        actions.loadContentCompleted(dirName, fileName, data.content)
      })
  },
  loadContentCompleted: (dirName, fileName, content) => {
    AppDispatcher.dispatch({
      actionType: AppConstants.LOAD_CONTENT_COMPLETED,
      dirName: dirName,
      fileName: fileName,
      content: content
    })
  }
}

export default actions
