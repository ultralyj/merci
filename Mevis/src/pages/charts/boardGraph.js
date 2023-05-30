import React from 'react';
import sensorBoard from "../../res/merci_sersorboardv1.0.png"

const chipsPosition = [[333, 110],[236,110], [284.6, 61],[284.6, 159]];
function drawArrow(ctx, fromX, fromY, toX, toY, theta, headLen, width, color) {

    theta = typeof(theta) != 'undefined' ? theta : 30;
    headLen = typeof(theta) != 'undefined' ? headLen : 10;
    width = typeof(width) != 'undefined' ? width : 1;
    // eslint-disable-next-line valid-typeof
    color = typeof(color) != 'color' ? color : '#000';

    // 计算各角度和对应的P2,P3坐标
    let angle = Math.atan2(fromY - toY, fromX - toX) * 180 / Math.PI,
        angle1 = (angle + theta) * Math.PI / 180,
        angle2 = (angle - theta) * Math.PI / 180,
        topX = headLen * Math.cos(angle1),
        topY = headLen * Math.sin(angle1),
        botX = headLen * Math.cos(angle2),
        botY = headLen * Math.sin(angle2);
    let arrowX = fromX - topX,
        arrowY = fromY - topY;

    ctx.moveTo(arrowX, arrowY);
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    arrowX = toX + topX;
    arrowY = toY + topY;
    ctx.moveTo(arrowX, arrowY);
    ctx.lineTo(toX, toY);
    arrowX = toX + botX;
    arrowY = toY + botY;
    ctx.lineTo(arrowX, arrowY);
}

/**
 * @brief 外部调用，更新绘图
 * @param data
 */
export function updateBoardGraph(data) {
    const adjustPros = [[1,0],[1,0],[1,0],[1,0]];
    const c=document.getElementById('board-canvas');
    const ctx=c.getContext('2d');
    ctx.beginPath();
    const w = c.width;
    const h = c.height;
    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle='rgb(255,0,0)';        //颜色
    ctx.lineWidth=2;                    //线宽
    for (let i=0;i<4;i++) {
        const r=Math.abs(adjustPros[i][0]*Math.sqrt(Math.abs(data[i*3])+Math.abs(data[i*3+1])+Math.abs(data[i*3+2])) + adjustPros[i][1]);
        const theta = Math.atan2(data[i*3+1],data[i*3]);
        const toX = chipsPosition[i][0]+3*r*Math.cos(theta);
        const toY = chipsPosition[i][1]+3*r*Math.sin(theta);
        ctx.moveTo(chipsPosition[i][0]+r, chipsPosition[i][1]);
        ctx.arc(chipsPosition[i][0], chipsPosition[i][1], r, 0, 2*Math.PI);
        drawArrow(ctx,chipsPosition[i][0], chipsPosition[i][1],toX,toY,20,10,1.5,'#f00');
    }
    ctx.stroke();
}
class BoardGraph extends React.Component {
    componentDidMount() {
        const ratio = window.devicePixelRatio || 1;
        //canvas元素
        const c=document.getElementById('board-canvas');
        const w=c.width;
        const h=c.height;
        c.width = w * ratio*1.3; // 实际渲染像素
        c.height = h * ratio*1.5; // 实际渲染像素
        c.style.width = `${w*1.3}px`; // 控制显示大小
        c.style.height = `${h*1.5}px`; // 控制显示大小
        let ctx=c.getContext('2d');
        ctx.scale(ratio, ratio)

        // 绘制背景
        ctx.fillStyle = 'rgba(255,255,255,0.15)';
        ctx.fillRect(0,0,1800,900);

    }
    render() {
        return (
            <div id={"chart2"}
                style={{
                    height:"220px",
                    backgroundImage: `url(${sensorBoard})`,
                    backgroundSize:"140% 140%",
                    backgroundPosition: "46% 50%"
                }}>
                <canvas id="board-canvas" style={{width:"100%",height:"100%"}}></canvas>

            </div>
        );
    }
}
export default BoardGraph;