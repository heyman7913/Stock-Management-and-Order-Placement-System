from main import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    migrate = Migrate(app, db)
    app.run(host='localhost', port=8000, debug=True)