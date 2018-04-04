path = require('path')

module.exports = {
  context: __dirname,
  entry: [
    './front/index.js'
  ],
  output: {
    path: path.join(__dirname, '/static/js'),
    filename: 'index.js'
  },
 // resolve: {
//  modules: [path.join(__dirname, 'front')],
 //   extensions: ['.js', '.jsx', '.json']
  //},
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              presets: ['react', 'es2015']
            }
          }
        ]
      },
      {
        test: /\.scss$/,
        loaders: ['style-loader', 'css-loader', 'sass-loader']
      }
    ]
  },
  devtool: 'source-map'
}
