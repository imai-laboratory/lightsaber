import * as React from 'react'
import DirectoryStore from '../stores/DirectoryStore'
import ContentStore from '../stores/ContentStore'
import AppActions from '../actions/AppActions'
import DirectoryList from './DirectoryList'
import ParameterTable from './ParameterTable'
import Graph from './Graph'

export default class Main extends React.Component {
  constructor (props) {
    super(props)
    DirectoryStore.addChangeListener(() => {
      this.setState({directories: DirectoryStore.getAll()})
    })
    ContentStore.addChangeListener(() => {
      this.setState({
        contents: ContentStore.getContents('reward.json'),
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
    return (
      <div>
        <Graph contents={state.contents} x={'step'} y={'reward'} />
        <ParameterTable parameters={state.parameters} />
      </div>
    )
  }
}
