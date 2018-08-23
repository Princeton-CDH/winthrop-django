const path = require("path")
const BundleTracker = require('webpack-bundle-tracker')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = {
    context: __dirname,
    entry: {
        main: './js/main.js',
        search: './js/search.js',
    },
    output: {
        path: path.resolve(__dirname, 'bundles'),
        filename: '[name]-[hash].js',
    },
    module: {
        rules: [
            { // compile Vue Single-File Components (SFCs)
                test: /\.vue$/,
                loader: 'vue-loader',
            },
            { // transpile ES5+ to ES5 using Babel
                test: /\.js$/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env'],
                    }
                },
            },
            { // compile SCSS to CSS, including <style> blocks in SFCs
                test: /\.scss$/,
                use: ['vue-style-loader', 'css-loader', 'sass-loader'],
            }
        ]
    },
    plugins: [
        new BundleTracker({ filename: 'webpack-stats.json' }), // used with django-webpack-loader
        new VueLoaderPlugin() // necessary for vue-loader to work
    ],
    resolve: {
        extensions: ['*', '.js', '.vue', '.scss']
    }
}