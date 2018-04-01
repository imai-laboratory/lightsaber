import * as React from 'react'
import DirectoryStore from '../stores/DirectoryStore'
import AppActions from '../actions/AppActions'
import DirectoryList from './DirectoryList'

class Main extends React.Component {
  constructor (props) {
    super(props)
    DirectoryStore.addChangeListener(() => {
      this.setState({directories: DirectoryStore.getAll()})
    })

    this.state = {
      directories: []
    }
  }

  componentDidMount () {
    AppActions.loadDirectories()
  }

  render () {
    console.log('test')
    const state = this.state
    return (
      <div>
        <DirectoryList directories={state.directories} />
      </div>
    )
  }
}