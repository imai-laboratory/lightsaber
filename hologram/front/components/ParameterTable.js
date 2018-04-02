import * as React from 'react'

export default class ParameterTable extends React.Component {
  render () {
    const parameters = this.props.parameters
    const keys = []
    for (let i = 0; i < parameters.length; ++i) {
      for (let key of Object.keys(parameters[i].parameter)) {
        if (keys.indexOf(key) === -1) {
          keys.push(key)
        }
      }
    }
    return (
      <table>
        <thead>
          <tr>
            <th>{'parameter'}</th>
            {parameters.map((parameter) => {
              return (
                <td>{parameter.dirName}</td>
              )
            })}
          </tr>
        </thead>
        <tbody>
          {keys.map((key) => {
            return (
              <tr>
                <th>{key}</th>
                {parameters.map((parameter) => {
                  const value = key in parameter.parameter ? parameter.parameter[key] : 'none'
                  return (
                    <td>{value}</td>
                  )
                })}
              </tr>
            )
          })}
        </tbody>
      </table>
    )
  }
}
