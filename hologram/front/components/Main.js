import * as React from 'react'
import DirectoryStore from '../stores/DirectoryStore'
import ContentStore from '../stores/ContentStore'
import AppActions from '../actions/AppActions'
import DirectoryList from './DirectoryList'
import ParameterTable from './ParameterTable'

export default class Main extends React.Component {
  constructor (props) {
    super(props)
    DirectoryStore.addChangeListener(() => {
      this.setState({directories: DirectoryStore.getAll()})
    })
    ContentStore.addChangeListener(() => {
      this.setState({
        contents: ContentStore.getAll(),
        parameters: ContentStore.getParameters()
      })
    })

    this.state = {
      directories: [],
      contents: [],
      parameters: []
    }
  }

  componentDidMount () {
    AppActions.loadDirectories()
  }

  render () {
    const state = this.state
    console.log(state.parameters)
    return (
      <div>
        <DirectoryList directories={state.directories} />
        <ParameterTable parameters={state.parameters} />
      </div>
    )
  }
}
