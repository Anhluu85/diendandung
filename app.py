import streamlit as st
from flask import Flask, jsonify
from threading import Thread
import time
import os
from .config import SECRET_KEY, DATABASE, ZALO_APP_ID, ZALO_APP_SECRET, ZALO_OAUTH_URL, ZALO_USER_INFO_URL, ADMIN_USERNAME, ADMIN_PASSWORD
from .models.database import init_db, check_and_init_db, close_db
from .auth.routes import auth_bp
from .api.user import user_bp
from .api.rewards import rewards_bp
from .api.admin import admin_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DATABASE'] = DATABASE
app.config['ZALO_APP_ID'] = ZALO_APP_ID
app.config['ZALO_APP_SECRET'] = ZALO_APP_SECRET
app.config['ZALO_OAUTH_URL'] = ZALO_OAUTH_URL
app.config['ZALO_USER_INFO_URL'] = ZALO_USER_INFO_URL
app.config['ADMIN_USERNAME'] = ADMIN_USERNAME
app.config['ADMIN_PASSWORD'] = ADMIN_PASSWORD

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(rewards_bp)
app.register_blueprint(admin_bp)

@app.teardown_appcontext
def close_db_connection(exception):
    close_db()

def run_flask_app():
    with app.app_context():
        check_and_init_db(app)
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

if __name__ == '__main__':
    thread = Thread(target=run_flask_app)
    thread.daemon = True
    thread.start()
    time.sleep(2) # Đợi server Flask khởi động

    st.title("Demo Backend API (Chạy trên Streamlit)")
    st.write("Backend Flask đang chạy ở cổng 8080.")
    st.write("Bạn có thể thử gửi GET request đến các endpoint API (ví dụ: /api/user/points?zalo_id=test).")
    st.write("Lưu ý: Đây chỉ là một giải pháp thử nghiệm.")