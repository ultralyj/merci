import {Card, Col, Row} from "antd";
import React from "react";
import PlotTactile from "./charts/plotTactile";
import ScatterTactile from "./charts/scatterTactile";
import MeshSensor from "./charts/meshSensor";
import BoardGraph from "./charts/boardGraph";

class ChartsSet extends React.Component {
    render() {
        return (
            <Row gutter={[8,8]}>
                <Col span={12}>
                    <Card bodyStyle={{height:"260px",paddingBottom:"24px"}}>
                        <div style={{position:'absolute',left:'10px'
                            ,top:'0px'}}>原始数据波形</div>
                        <div id={"chart1"} style={{height:"220px"}}>
                            <PlotTactile/>
                        </div>
                    </Card>
                </Col>
                <Col span={12}>
                    <Card bodyStyle={{height:"260px", paddingBottom:"24px",}} >
                        <div style={{position:'absolute',left:'10px'
                            ,top:'0px'}}>常分辨率</div>
                        <div id={"chart4"} style={{height:"220px"}}>
                            <BoardGraph/>
                        </div>
                    </Card>

                </Col>
                <Col span={12}>
                    <Card bodyStyle={{height:"260px",paddingBottom:"24px"}}>
                        <div style={{position:'absolute',left:'10px'
                            ,top:'0px'}}>超分辨率模型推理数据</div>
                        <div id={"chart2"} style={{height:"220px"}}>
                            <ScatterTactile/>
                        </div>
                    </Card>
                </Col>
                <Col span={12}>

                    <Card bodyStyle={{height:"260px",paddingBottom:"24px"}}>
                        <div style={{position:'absolute',left:'10px'
                            ,top:'0px'}}>超分辨率3D重建</div>
                        <div id={"chart3"} style={{height:"220px"}}>
                            <MeshSensor/>
                        </div>
                    </Card>


                </Col>
            </Row>
        );
    }
}

export default ChartsSet;