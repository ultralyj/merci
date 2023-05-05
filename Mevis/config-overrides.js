const {override, fixBabelImports, addLessLoader} = require('customize-cra');
const path = require('path');
const paths = require("react-scripts/config/paths");

// 全局加载AntD
module.exports = override(
    fixBabelImports('import',
        {
            libraryName: "antd-mobile",
            libraryDirectory: "es",
            style: "css"
        }),
    addLessLoader({
        javascriptEnabled: true,
        modifyVars: {"@primary-color": "#1DA57A"}
    })
);

// 修改打包路径
paths.appBuild = path.join(path.dirname(paths.appBuild), './static')