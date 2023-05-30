import eventlet
import socketio
import cnn

sio = socketio.Server()
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def require_cnn(sid, data):
    if(isinstance(data,list)):
        if(len(data)==12):
            print('get frame')
            p = cnn.predict(data)
    return p

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    cnn.init()
    eventlet.wsgi.server(eventlet.listen(('', 5978)), app)
