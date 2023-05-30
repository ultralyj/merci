const { io } = require('socket.io-client');

const socket = io('http://0.0.0.0:5978');

function cnn_init() {
    socket.on('connect', () => {
        console.log('connected python server');
    });

    const frame = [ -5.7, -5.7, 343.16, 105.9, 51.6, 297.66, 34.5, 232.8, 340.74, 113.7, 111.6, 383.33];
    socket.emit('require_cnn', frame,(response) => {
        console.log(response); // ok
    });
}

module.exports = {
    cnn_init,
}



