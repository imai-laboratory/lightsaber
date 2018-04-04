import * as React from 'react'
import AppActions from '../actions/AppActions'

export default class Header extends React.Component {
  changeXAxis (e) {
    AppActions.changeXAxis(e.target.value)
  }

  changeYAxis (e) {
    AppActions.changeYAxis(e.target.value)
  }

  changeFile (e, options) {
    AppActions.changeFile(e.target.value)
    AppActions.changeXAxis(options[0])
    AppActions.changeYAxis(options[0])
  }

  changeWindowSize (e) {
    AppActions.changeWindowSize(e.target.value)
  }

  render () {
    const options = this.props.options.length > 0 ? this.props.options : ['']
    const files = this.props.files.length > 0 ? this.props.files : ['']
    const selectedX = this.props.x === null ? this.props.options[0] : this.props.x
    const selectedY = this.props.y === null ? this.props.options[0] : this.props.y
    const selectedFile = this.props.file === null ? this.props.files[0] : this.props.file
    const toOptions = (values) => values.map(value => (<option value={value}>{value}</option>))
    const windowSize = this.props.windowSize
    return (
      <div>
        <select value={selectedX} onChange={this.changeXAxis}>
          {toOptions(options)}
        </select>
        <select value={selectedY} onChange={this.changeYAxis}>
          {toOptions(options)}
        </select>
        <select value={selectedFile} onChange={(e) => this.changeFile(e, options)}>
          {toOptions(files)}
        </select>
        <input type="number" value={windowSize} onChange={this.changeWindowSize} />
      </div>
    )
  }
}
