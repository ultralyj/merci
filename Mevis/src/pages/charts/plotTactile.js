import React from 'react'
import * as echarts from 'echarts';

let chartData = {
    xAxis:[],
    data:[[],[],[],
        [],[],[],
        [],[],[],
        [],[],[],]
}
let plotChart;
let plotLock = false;
let chartOption = {
    animation:false,
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        data: ['x1', 'y1', 'z1','x2', 'y2', 'z2','x3', 'y3', 'z3','x4', 'y4', 'z4']
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        boundaryGap: false,
        data: chartData.xAxis
    },
    yAxis: {
        type: 'value',
        max:200,
        min:-200,
        scale: true,
    },
    series: [
        {
            name: 'x1',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            data: chartData.data[0]
        },
        {
            name: 'y1',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            animationDuration: 0,
            data: chartData.data[1]
        },
        {
            name: 'z1',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            animationDuration: 0,
            data: chartData.data[2]
        },
        {
            name: 'x2',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            data: chartData.data[3]
        },
        {
            name: 'y2',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            animationDuration: 0,
            data: chartData.data[4]
        },
        {
            name: 'z2',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            animationDuration: 0,
            data: chartData.data[5]
        },
        {
            name: 'x3',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            data: chartData.data[6]
        },
        {
            name: 'y3',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            animationDuration: 0,
            data: chartData.data[7]
        },
        {
            name: 'z3',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            animationDuration: 0,
            data: chartData.data[8]
        },
        {
            name: 'x4',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            data: chartData.data[9]
        },
        {
            name: 'y4',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            animationDuration: 0,
            data: chartData.data[10]
        },
        {
            name: 'z4',
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
                width: 1
            },
            animationDuration: 0,
            data: chartData.data[11]
        },
    ]
};
export function updatePlotTactile(data) {
    plotLock = true;
    // 生成横坐标ID序号
    if(chartData.xAxis.length===0){
        chartData.xAxis.push(0);
    }
    else {
        chartData.xAxis.push(parseInt(chartData.xAxis.slice(-1))+1);
    }
    // 压入数据
    for (let i=0;i<12;i++){
        chartData.data[i].push(data[i]);
        if(chartData.xAxis.length>=200){
            chartData.data[i].shift();
        }
    }
    if(chartData.xAxis.length>=200){
        chartData.xAxis.shift();
    }
    plotLock = false;
}
class PlotTactile extends React.Component {
    componentDidMount() {
        // 延迟挂载
        setTimeout(() => {
            this.initChart();
            setInterval(function () {
                if(plotLock == false) {
                    //plotChart.clear();
                    plotChart.setOption({
                        xAxis: {
                            data: chartData.xAxis
                        },
                        series: [
                            {
                                name: 'x1',
                                data: chartData.data[0]
                            },
                            {
                                name: 'y1',
                                data: chartData.data[1]
                            },
                            {
                                name: 'z1',
                                data: chartData.data[2]
                            },
                            {
                                name: 'x2',
                                data: chartData.data[3]
                            },
                            {
                                name: 'y2',
                                data: chartData.data[4]
                            },
                            {
                                name: 'z2',
                                data: chartData.data[5]
                            },
                            {
                                name: 'x3',
                                data: chartData.data[6]
                            },
                            {
                                name: 'y3',
                                data: chartData.data[7]
                            },
                            {
                                name: 'z3',
                                data: chartData.data[8]
                            },
                            {
                                name: 'x4',
                                data: chartData.data[9]
                            },
                            {
                                name: 'y4',
                                data: chartData.data[10]
                            },
                            {
                                name: 'z4',
                                data: chartData.data[11]
                            }
                        ]
                    });
                }
            }, 50);
        }, 100);
    }
    /*生成图表，做了判断，如果不去判断dom有没有生成，
      每次更新图表都要生成一个dom节点*/
    initChart() {
        plotChart = echarts.init(document.getElementById('chart-inner1'));
        // 绘制图表，option设置图表格式及源数据
        plotChart.setOption(chartOption);
        plotChart.resize();
        window.addEventListener('resize', function() {
            plotChart.resize();
        });
    }

    render() {
        return (
            <div id="chart-inner1" style={{width:'100%',height:'100%'}}></div>
        );
    }
}

export default PlotTactile;