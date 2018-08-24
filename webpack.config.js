const path = require("path")
const BundleTracker = require('webpack-bundle-tracker')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
const MiniCssExtractPlugin = require("mini-css-extract-plugin")

module.exports = {
    context: __dirname,
    entry: {
        main: [
            'babel-polyfill',
            './sitemedia/js/main.js',
            './sitemedia/scss/site.scss'
        ],
        search: './sitemedia/js/search.js',
    },
    output: {
        filename: '[name].bundle.js',
        chunkFilename: '[name].bundle.js',
        path: path.resolve(__dirname, 'sitemedia', 'bundles'),
    },
    module: {
        rules: [
            { // compile Vue Single-File Components (SFCs)
                test: /\.vue$/,
                loader: 'vue-loader',
            },
            { // transpile ES5+ to ES5 using Babel
                test: /\.js$/,
                loader: 'babel-loader',
                include: path.resolve(__dirname, 'js'),
            },
            { // compile SCSS to CSS, including <style> blocks in SFCs
                test: /\.scss$/,
                use: [
                    process.env.NODE_ENV !== 'production' ? 'vue-style-loader' : MiniCssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader',
                ],
            }
        ]
    },
    plugins: [
        new BundleTracker({ filename: 'webpack-stats.json' }), // used with django-webpack-loader
        new VueLoaderPlugin(), // necessary for vue-loader to work
        new BundleAnalyzerPlugin(),
        new MiniCssExtractPlugin({ filename: "[name].css", chunkFilename: "[id].css" })
    ],
    resolve: {
        extensions: ['*', '.js', '.vue', '.scss']
    },
    optimization: {
        splitChunks: {
            cacheGroups: {
                styles: {
                  name: 'styles',
                  test: /\.css$/,
                  chunks: 'all',
                  enforce: true,
                }
            }
        }
    }
}