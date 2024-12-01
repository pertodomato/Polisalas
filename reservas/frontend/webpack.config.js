const path = require('path');

module.exports = {
  entry: './src/index.js', // Caminho para o arquivo principal do React
  output: {
    path: path.resolve(__dirname, '../static/reservas/js/'),
    filename: 'fale_conosco_bundle.js', // Nome do bundle gerado
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        },
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  mode: 'production',
};
