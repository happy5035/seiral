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

if __name__ == '__main__':
    # socketio.run(app=app, host='127.0.0.1', port=8088)
    try:
        print(1/0)
    except ZeroDivisionError as e:
        print(e)
        raise Exception(e)
    except Exception as e:
        print(e)

    pass
