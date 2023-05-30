const {SerialPort} = require("serialport");
const { DelimiterParser } = require('@serialport/parser-delimiter')
require('./window')

let port;
/**
 * 更新串口列表，并发送到前端
 */
async function listSerialPorts() {
    await SerialPort.list().then((ports, err) => {
        //console.log('ports', ports);
        window.webContents.send('serial:list',ports);
    })
}


function serial(){
    window.webContents.session.on('select-serial-port', (event, portList, webContents, callback) => {
        console.log(portList)
        //Add listeners to handle ports being added or removed before the callback for `select-serial-port`
        //is called.
        window.webContents.session.on('serial-port-added', (event, port) => {
            console.log('serial-port-added FIRED WITH', port)
            //Optionally update portList to add the new port
        })

        window.webContents.session.on('serial-port-removed', (event, port) => {
            console.log('serial-port-removed FIRED WITH', port)
            //Optionally update portList to remove the port
        })

        event.preventDefault()
        if (portList && portList.length > 0) {
            callback(portList[0].portId)
        } else {
            console.log("Could not find any matching devices")
            callback('') //Could not find any matching devices
        }
    })

    window.webContents.session.setPermissionCheckHandler((webContents, permission, requestingOrigin, details) => {
        if (permission === 'serial' && details.securityOrigin === 'file:///') {
            return true
        }

        return false
    })

    window.webContents.session.setDevicePermissionHandler((details) => {
        if (details.deviceType === 'serial' && details.origin === 'file://') {
            return true
        }

        return false
    })
}

/**
 * 打开串口的回调函数
 * @returns {Promise<void>}
 */
async function handleSerialOpen(event, portInfo) {
    console.log("serial opening...");
    port = new SerialPort({
        path:portInfo.path,
        baudRate: portInfo.baud,    // 波特率
        dataBits: 8,                // 数据位
        parity: 'none',             // 奇偶校验
        stopBits: 1,                // 停止位
        flowControl: false,
        autoOpen:false              // 不自动打开
    });
    port.open(function (error){
        if(error){
            console.log("open serial failed, error:" + error);
        }
        else{
            console.log("open serial" +portInfo.path+"successfully")
        }
    })
    const parser = port.pipe(new DelimiterParser({ delimiter: '\n' })); // 以 \n 分隔处理数据
    parser.on('data', chunk => {
        const dataSplit = chunk.toString().split(',');
        window.webContents.send('serial:data',dataSplit);

    });
    return false;
}

async function handleSerialClose() {
    console.log("closing...")
    port.close(function (error) {
        if(error){
            console.log("close serial failed, error:" + error);
        }
        else{
            console.log("close serial successfully")
        }
    });
}

/**
 * 更新请求串口列表的回调函数（异步）
 * @returns {Promise<void>}
 */
async function handleRequestList() {
    //console.log("update list...")
    await listSerialPorts();
}

module.exports = {
    listSerialPorts,
    serial,
    handleSerialOpen,
    handleSerialClose,
    handleRequestList,
}

