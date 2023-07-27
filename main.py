from urls.urls import *

if __name__ == '__main__':
    # Create all tables in DB
    # db.create_all()
    # Run Engine
    app.run(host='127.0.0.1', port=8000, debug=True)
