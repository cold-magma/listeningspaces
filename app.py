from botter import create_app,socketio,db

app = create_app()

db.create_all(app=app)

if __name__ == "__main__":
    socketio.run(app)