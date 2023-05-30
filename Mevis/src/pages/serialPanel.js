/**
 * @brief 串口配置面板
 * @author ultralyj(1951578@tongji.edu.cn)
 * @date 2023/2/19
 */

import {Button, Card, Col, Row, Select, Avatar, Divider} from "antd";
import React, {useState} from "react";
import {ApiOutlined, PoweroffOutlined, SearchOutlined, HeatMapOutlined} from "@ant-design/icons";

import {updatePlotTactile} from "./charts/plotTactile.js"
import {updateBoardGraph} from "./charts/boardGraph";
import {upDataMesh} from "./charts/meshSensor";
import {func} from "three/nodes";
import {updatePressTactile} from "./charts/scatterTactile";

class SerialPanel extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            loading: false,
            port:0,
            baud:115200,
            serialList:[{ value: '-1', label: '未搜索到端口', disabled: true }],
            serialCom:'未搜索到端口',
            opened:false,
            openButton:  '打开串口',
        };

    }
    componentDidMount() {
        /**
         * 更新端口列表
         */
        // 3d模型触点模拟测试
        // let x = -10;
        // let y = -10;
        // let t1 = window.setTimeout(function () {
        //     let t2 = window.setInterval(function () {
        //         console.log(x,y);
        //         upDataMesh(x,y,1);
        //         x+=0.2;
        //         y+=0.2;
        //         if(x>=8){
        //             x=-8;
        //             y=-8;
        //         }
        //     }, 100);
        // }, 2000);


        window.electronAPI.onListSerial((_event, ports) => {
            if(ports.length>0){
                let comList = ports.map((item,index) => {
                    return Object.assign({},{'value':item.path,'label':item.friendlyName})
                })
                this.setState({serialList:comList});
                if(this.state.serialCom == '未搜索到端口'){
                    this.setState({serialCom:comList[0].value});
                    this.setState({port:comList[0].value});
                }
            }
            else {
                this.setState({serialList:[{ value: '-1', label: '未搜索到端口', disabled: true }]});
                this.setState({serialCom:'未搜索到端口'});
            }
        })
        /**
         * 数据帧传输到前端(核心)
         */
        window.electronAPI.dataReadOut((_event, frame) => {
            let crc = 0.0;

            if(frame.length==13) {
                // 求和校验数据
                for (let i=0; i<12; i++) {
                    crc+=parseFloat(frame[i]);
                }
                if(Math.abs(crc-frame[12])<0.5) {
                    updatePlotTactile(frame);
                    updateBoardGraph(frame);
                    updatePressTactile(frame);
                }
            }


        })
    }

    componentWillUnmount() {
        // 退出之前关闭串口
        if(this.state.opened === true){
            window.electronAPI.closeSerial();
        }
    }

    render(){
        return(
            <Card
                title= {<div><ApiOutlined /> 串口配置</div>}
                extra = {<a href="#">高级</a>}
                style = {{ margin:4 }}
                headStyle = {{verticalAlign:"middle"}}
            >

                <Row gutter={[8, 8]}>
                    <Col span={10}>端口：</Col>
                    <Col span={14}>
                        <Select
                            defaultValue={this.state.serialList[0].value}
                            dropdownMatchSelectWidth={false}
                            style={{ width: '100%' }}
                            onChange={this.handlePortChange}
                            options={this.state.serialList}
                            value={this.state.serialCom}
                        />
                    </Col>
                    <Col span={10}>波特率：</Col>
                    <Col span={14}>
                        <Select
                            defaultValue="115200"
                            style={{width: '100%'}}
                            onChange={this.handleBaudChange}
                            options={[
                                { value: '9600', label: '9600'},
                                { value: '14400', label: '14400'},
                                { value: '19200', label: '19200'},
                                { value: '38400', label: '38400'},
                                { value: '115200', label: '115200'},
                                { value: '460800', label: '460800'},
                            ]}
                        />
                    </Col>
                    <Divider style={{marginBottom: 0, marginTop: 0}}/>
                    <Col span={5}>
                        <Button icon={<SearchOutlined />} onClick={() => window.electronAPI.requestList()}/>
                    </Col>
                    <Col span={5}>
                        <Button icon={<HeatMapOutlined />} onClick={() => this.emitTestSignal()}/>
                    </Col>
                    <Col span={14}>
                        <Button
                            id={"serial-open-button"}
                            type="primary"
                            block={true}
                            icon={<PoweroffOutlined />}
                            loading= {this.state.loading}
                            onClick={() => this.enterLoading(1)}

                        >
                            {this.state.openButton}
                        </Button>
                    </Col>
                </Row>
            </Card>
        );
    };

    emitTestSignal() {
        console.log("emit test signal");
    }
    async enterLoading(index: number)  {
        if(this.state.opened === false){
            this.setState({opened:true});
            // 关闭状态，开启串口
            if(this.state.serialCom !== '未搜索到端口'){
                let portInfo = {path:this.state.serialCom,baud:this.state.baud};
                // 进入打开串口的加载状态
                this.setState({loading:true});
                await window.electronAPI.openSerial(portInfo);
                this.setState({loading:false});
                this.setState({openButton:'关闭串口'});
            }
        }
        else{
            // 关闭状态，开启串口
            await window.electronAPI.closeSerial();
            this.setState({openButton:'打开串口'});
            this.setState({opened:false});
        }
    }
    handlePortChange = (value: string) => {
        console.log(`port ${value}`);
        this.setState({serialCom:value});
    };

    handleBaudChange = (value: string) => {
        console.log(`baud ${value}`);
        this.setState({baud:parseInt(value)});
    };
}


export default SerialPanel;