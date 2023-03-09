import {Button, Card, Col, Row, Radio, Divider, Select, Switch} from "antd";
import React, {useState} from "react";
import type { RadioChangeEvent } from 'antd';
import {RocketOutlined} from "@ant-design/icons";

const optionsWithDisabled = [
    { label: '默认输出', value: 'normal' },
    { label: '事件驱动', value: 'event' },
    { label: '测试', value: 'test', disabled: true },
];





class SensorPanel extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            outputMethod: 'normal',
            enableInfer:  false,
            aiModel: 'ReSkin'
        };

    }

    handleAiModelChange = (value: string) => {
        console.log(`selected ${value}`);
        this.setState({aiModel:value});
    };

    handleEnableInfer = (checked: boolean) => {
        console.log(`selected ${checked}`);
        this.setState({enableInfer:checked});
    };
    handleOutputMethodChange = (value: string) => {
        console.log(`port ${value}`);
        this.setState({outputMethod:value});
    };

    render() {
        return (
            <Card
                title={<div><RocketOutlined /> 传感器配置</div>}
                style={{ margin:4 }}
            >
                <Row gutter={[8, 8]}>
                    <Col span={24}>
                        输出模式
                    </Col>
                    <Col span={24}>
                        <Radio.Group
                            options={optionsWithDisabled}
                            onChange={this.handleOutputMethodChange}
                            value={this.state.outputMethod}
                            optionType="button"
                            buttonStyle="solid"
                            size={"small"}
                        />
                    </Col>
                    <Divider style={{marginBottom: 0, marginTop: 0}}/>
                    <Col span={10}>推理模型：</Col>
                    <Col span={14}>
                        <Select
                            defaultValue= {this.state.aiModel}
                            style={{width: '100%'}}
                            onChange={this.handleAiModelChange}
                            options={[
                                { value: 'LSTM', label: 'LSTM'},
                                { value: 'CNN', label: 'CNN'},
                                { value: 'ReSkin', label: 'ReSkin'},
                            ]}
                        />
                    </Col>
                    <Col span={10}>推理使能：</Col>
                    <Col span={14}>
                        <Switch
                            checkedChildren="开启"
                            unCheckedChildren="关闭"
                            defaultChecked={false}
                            onChange={this.handleEnableInfer}
                            style={{float:"left"}}
                        />
                    </Col>
                </Row>
            </Card>
        );
    }

}

export default SensorPanel;