import socketserver
import threading

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xjtu'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})
    print(message)


import traceback


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        import dill as pickle
        try:
            pickle.loads(data)()
        except Exception as e:
            traceback.print_exc(e)
            pass
        pass


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def handle_error(self, request, client_address):
        print(request, client_address)
        pass

    pass


def setup_tcp_server():
    HOST, PORT = "localhost", 8083
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    pass
def find_params_by_name(name):
    import json
    params = json.load(open('params.json'))
    for p in params:
        if p['item_name'] == name:
            return p
        pass


if __name__ == '__main__':
    # setup_tcp_server()
    # while True:
    #     pass
    print(find_params_by_name('temp_freq'))
