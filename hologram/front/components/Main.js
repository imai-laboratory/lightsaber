import * as React from 'react'
import DirectoryStore from '../stores/DirectoryStore'
import ContentStore from '../stores/ContentStore'
import HeaderStore from '../stores/HeaderStore'
import TableStore from '../stores/TableStore'
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
    TableStore.addChangeListener(() => {
      this.setState({
        table: TableStore.getAll()
      })
    })

    this.state = {
      directories: [],
      contents: [],
      parameters: [],
      header: HeaderStore.getAll(),
      table: TableStore.getAll()
    }
  }

  componentDidMount () {
    AppActions.loadDirectories()
  }

  render () {
    const state = this.state
    const axis = state.contents.length > 0 ? Object.keys(state.contents[0].data[0]) : []
    const files = state.directories.length > 0 ? state.directories[0].files : []
    console.log(state)
    return (
      <div>
        <Header
          options={axis}
          files={files}
          x={state.header.x}
          y={state.header.y}
          file={state.header.file}
          windowSize={state.header.windowSize} />
        {state.contents.length > 0 ?
          <Graph
            contents={state.contents}
            x={state.header.x}
            y={state.header.y}
            windowSize={state.header.windowSize}
            actives={state.table.actives} />
          : ''
        }
        <ParameterTable
          parameters={state.parameters}
          actives={state.table.actives} />
      </div>
    )
  }
}

