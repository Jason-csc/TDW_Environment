const path = require("path");

module.exports = {
  mode: "development",
  entry: "./tdweb/js/main.jsx",
  output: {
    path: path.join(__dirname, "/tdweb/static/js/"),
    filename: "bundle.js",
  },
  devtool: "source-map",
  module: {
    rules: [
      {
        // Test for js or jsx files
        test: /\.jsx?$/,
        // Exclude external modules from loader tests
        exclude: /node_modules/,
        loader: "babel-loader",
        options: {
          presets: ["@babel/preset-env", "@babel/preset-react"],
        },
      },
      {
        test: /\.(png|jpg|jpeg|gif)$/,
        loader: "file-loader",
        options:{
          name:'[path][name].[ext]',
        },
      },
    ],
  },
  resolve: {
    extensions: [".js", ".jsx"],
  },
};
