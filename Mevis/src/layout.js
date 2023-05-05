import React, {useState} from "react";
import { Layout, Menu, theme} from "antd";
import {
    AppstoreOutlined,
    MailOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import 'antd/dist/reset.css';
import "./layout.css";
import SerialPanel from "./pages/serialPanel";
import SensorPanel from "./pages/sensorPanel";
import InfoPanel from "./pages/infoPanel";
import ChartsSet from "./pages/chartsSet";
import banner from "./res/mevis_banner.png"
const { Header, Content, Sider } = Layout;

const items: MenuProps['items'] = [
    {
        label: '页面1',
        key: 'mail',
        icon: <MailOutlined />,
    },
    {
        label: '页面2',
        key: 'app',
        icon: <AppstoreOutlined />,
    },
];
const App: React.FC = () => {
    const {
        token: { colorBgContainer },
    } = theme.useToken();

    const [current, setCurrent] = useState('mail');

    const onClick: MenuProps['onClick'] = (e) => {
        console.log('click ', e);
        setCurrent(e.key);
    };
    return (
        <Layout>
            {/*顶部配置*/}
            <Header className="header">
                <div className="logo">
                    <img id="banner" alt={"banner"} src={banner}/>
                </div>
                <div className="header-title">
                    <h1>磁触觉感知框架</h1>
                </div>
                <div className="header-extra">设置</div>
            </Header>
            <Layout>
                <Sider width={260} style={{ background: colorBgContainer }}>
                    {/*串口配置卡片*/}
                    <SerialPanel/>
                    {/*传感器配置卡片*/}
                    <SensorPanel/>
                    {/*软件说明卡片*/}
                    <InfoPanel/>
                </Sider>
                <Layout style={{ padding: '0 24px 24px' }}>
                    <Menu onClick={onClick} selectedKeys={[current]} mode="horizontal" items={items} />
                    <Content
                        style={{
                            padding: 24,
                            margin: 0,
                            minHeight: 280,
                            maxHeight: 660,
                            background: colorBgContainer,
                        }}
                    >
                        {/*图标组, based on echarts*/}
                        <ChartsSet/>
                    </Content>
                </Layout>
            </Layout>
            <footer style={{ textAlign: 'center' }}>
                Mevis Magnet-Tactile Framework ©2023 Created by ultralyj
            </footer>
        </Layout>
    );
};

export default App;