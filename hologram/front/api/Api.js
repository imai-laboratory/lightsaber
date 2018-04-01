import * as SuperAgent from 'superagent'

export default class Api {
  static getDirectories() {
    return new Promise((resolve, reject) => {
      SuperAgent.get('/dirs')
        .set('Content-type:', 'json/application')
        .then((err, res) => {
          if (res.ok) {
            resolve(res.body)
          } else {
            reject(err)
          }
        })
    })
  }
}
