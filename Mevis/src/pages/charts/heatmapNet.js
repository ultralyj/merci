import React from 'react'
import * as echarts from "echarts";

let scatterChart;
let chartOption = {
    title: {
        text: 'ECharts 入门示例'
    },
    tooltip: {},
    legend: {
        data: ['销量']
    },
    xAxis: {
        data: ['衬衫', '羊毛衫', '雪纺衫', '裤子', '高跟鞋', '袜子']
    },
    yAxis: {},
    series: [
        {
            name: '销量',
            type: 'bar',
            data: [5, 20, 36, 10, 10, 20]
        }
    ]
};

class HeatmapNet extends React.Component {
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
        scatterChart = echarts.init(document.getElementById('chart-inner3'));
        // 绘制图表，option设置图表格式及源数据
        scatterChart.setOption(chartOption);
        scatterChart.resize();
        window.addEventListener('resize', function() {
            scatterChart.resize();
        });
    }

    render() {
        return (
            <div id="chart-inner3" style={{width:'100%',height:'100%'}}></div>
        );
    }
}
export default HeatmapNet;