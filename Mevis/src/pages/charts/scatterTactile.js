import React from 'react'
import * as echarts from "echarts";

let scatterChart;

let chartOption = {
    xAxis: {
        type: 'value',
        axisLine: {
            symbol: ['none', 'arrow'],
        },
        min:-15,
        max: 15,
        minorTick: {
            show: true
        },
        minorSplitLine: {
            show: true
        }
    },
    yAxis: {
        type: 'value',
        axisLine: {
            symbol: ['none', 'arrow'],
        },
        min:-15,
        max: 15,
        minorTick: {
            show: true
        },
        minorSplitLine: {
            show: true
        }
    },

    grid: {
        show:true,
        top:'3%',
        left: '16%',
        width:200,
        height:200,
        containLabel: false
    },
    legend: {
        // Try 'horizontal'
        orient: 'vertical',
        right: 60,
        top: 'center',
        data: ['Email']
    },
    series: [
        {
            name: 'Email',
            symbolSize: 8,
            data: [
                [10.0, 8.04],
                [8.07, 6.95],
                [13.0, 7.58],
                [9.05, 8.81],
                [11.0, 8.33],
                [14.0, 7.66],
                [13.4, 6.81],
                [10.0, 6.33],
                [14.0, 8.96],
                [12.5, 6.82],
                [9.15, 7.2],
                [11.5, 7.2],
                [3.03, 4.23],
                [12.2, 7.83],
                [2.02, 4.47],
                [1.05, 3.33],
                [4.05, 4.96],
                [6.03, 7.24],
                [12.0, 6.26],
                [12.0, 8.84],
                [7.08, 5.82],
                [5.02, 5.68]
            ],
            type: 'scatter',


        }
    ]
};
class ScatterTactile extends React.Component {
    componentDidMount() {
        // 延迟挂载
        setTimeout(() => {
            this.initChart();
        }, 100);

        setInterval(function () {
            scatterChart.setOption({

            });
        }, 100);
    }
    /*生成图表，做了判断，如果不去判断dom有没有生成，
      每次更新图表都要生成一个dom节点*/
    initChart() {
        scatterChart = echarts.init(document.getElementById('chart-inner2'));
        // 绘制图表，option设置图表格式及源数据
        scatterChart.setOption(chartOption);
        scatterChart.resize();
        window.addEventListener('resize', function() {
            scatterChart.resize();
        });
    }

    render() {
        return (
            <div id="chart-inner2" style={{width:'100%',height:'110%'}}></div>
        );
    }
}

export default ScatterTactile;