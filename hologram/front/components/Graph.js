import * as React from 'react'
import { Line } from 'react-chartjs-2'

const colors = [
  '#2ecc71',
  '#3498db',
  '#9b59b6',
  '#f1c40f',
  '#e67e22',
  '#e74c3c'
]

function movingAverage (data, window) {
  const averagedData = []
  const queue = []
  for (let i = 0; i < data.length; ++i) {
    if (queue.length > window) {
      queue.shift()
    }
    queue.push(data[i].y)
    let sum = 0.0
    for (let value of queue) {
      sum += value
    }
    averagedData.push({
      x: data[i].x,
      y: parseFloat(sum) / queue.length
    })
  }
  return averagedData
}

export default class Graph extends React.Component {
  render () {
    const contents = this.props.contents
    const x = this.props.x
    const y = this.props.y
    const window = this.props.windowSize
    const datasets = []
    let minX = 1000000
    let maxX = -1000000
    let minY = 1000000
    let maxY = -1000000
    for (let i = 0; i < contents.length; ++i) {
      const content = contents[i]
      if (this.props.actives.indexOf(content.dirName) === -1) {
        continue
      }
      const data = []
      const color = colors[i % colors.length]
      for (let row of content.data) {
        if (row[x] < minX) {
          minX = row[x]
        } else if (row[x] > maxX) {
          maxX = row[x]
        }
        if (row[y] < minY) {
          minY = row[y]
        } else if (row[y] > maxY) {
          maxY = row[y]
        }
        data.push({x: row[x], y: row[y]})
      }
      datasets.push({
        data: movingAverage(data, window),
        label: content.dirName,
        backgroundColor: color,
        borderColor: color,
        pointBorderColor: color,
        pointHoverBackgroundColor: color,
        pointRadius: 0.0,
        fill: false
      })
    }
    const data = {
      datasets: datasets
    }
    const options = {
      scales: {
        xAxes: [{
          type: 'linear',
          position: 'bottom',
          ticks: {
            min: minX,
            max: maxX
          }
        }],
        yAxes: [{
          ticks: {
            min: minY,
            max: maxY
          }
        }]
      },
      animation: {
        duration: 0
      },
      hover: {
        animationDuration: 0
      },
      responsiveAnimationDuration: 0
    }
    return (
      <Line data={data} options={options} />
    )
  }
}
