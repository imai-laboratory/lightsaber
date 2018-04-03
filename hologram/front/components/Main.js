import * as React from 'react'
import DirectoryStore from '../stores/DirectoryStore'
import ContentStore from '../stores/ContentStore'
import HeaderStore from '../stores/HeaderStore'
import AppActions from '../actions/AppActions'
import DirectoryList from './DirectoryList'
import ParameterTable from './ParameterTable'
import Header from './Header'
import Graph from './Graph'

export default class Main extends React.Component {
  constructor (props) {
    super(props)
    DirectoryStore.addChangeListener(() => {
      this.setState({directories: DirectoryStore.getAll()})
    })
    ContentStore.addChangeListener(() => {
      this.setState({
        contents: ContentStore.getContents(this.state.header.file),
        parameters: ContentStore.getParameters()
      })
    })
    HeaderStore.addChangeListener(() => {
      const state = HeaderStore.getAll()
      this.setState({
        contents: ContentStore.getContents(state.file),
        header: state
      })
    })

    this.state = {
      directories: [],
      contents: [],
      parameters: [],
      header: HeaderStore.getAll()
    }
  }

  componentDidMount () {
    AppActions.loadDirectories()
  }

  render () {
    const state = this.state
    console.log(state)
    const axis = state.contents.length > 0 ? Object.keys(state.contents[0].data[0]) : []
    const files = state.directories.length > 0 ? state.directories[0].files : []
    return (
      <div>
        <Header
          options={axis}
          files={files}
          x={state.header.x}
          y={state.header.y}
          file={state.header.file} />
        {state.contents.length > 0 ?
          <Graph contents={state.contents} x={state.header.x} y={state.header.y} />
          : ''
        }
        <ParameterTable parameters={state.parameters} />
      </div>
    )
  }
}

