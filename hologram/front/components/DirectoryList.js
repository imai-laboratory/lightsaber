import * as React from 'react'

export default class DirectoryList extends React.Component {
  render () {
    const directories = this.props.directories
    return (
      <ul>
        {directories.map((directory) => {
          return (
            <li>
              <span>{directory.directory}</span>
            </li>
          )
        })}
      </ul>
    )
  }
}
