import {Card, Col, Row} from "antd";
import React from "react";
import PlotTactile from "./charts/plotTactile";
import ScatterTactile from "./charts/scatterTactile";
import HeatmapNet from "./charts/heatmapNet";
import BoardGraph from "./charts/boardGraph";

class ChartsSet extends React.Component {
    render() {
        return (
            <Row gutter={[8,8]}>
                <Col span={12}>
                    <Card bodyStyle={{height:"260px",paddingBottom:"24px"}}>
                        <div id={"chart1"} style={{height:"220px"}}>
                            <PlotTactile/>
                        </div>
                    </Card>
                </Col>
                <Col span={12}>
                    <Card bodyStyle={{height:"260px",paddingBottom:"24px"}}>
                        <div id={"chart2"} style={{height:"220px"}}>
                            <ScatterTactile/>
                        </div>
                    </Card>

                </Col>
                <Col span={12}>
                    <Card bodyStyle={{height:"260px",paddingBottom:"24px"}}>
                        <div id={"chart3"} style={{height:"220px"}}>
                            <HeatmapNet/>
                        </div>
                    </Card>
                </Col>
                <Col span={12}>
                    <Card bodyStyle={{height:"260px", paddingBottom:"24px",}} >
                        <div id={"chart4"} style={{height:"220px"}}>
                            <BoardGraph/>
                        </div>
                    </Card>

                </Col>
            </Row>
        );
    }
}

export default ChartsSet;