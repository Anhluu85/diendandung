from flask import Blueprint, request, jsonify, current_app
import requests
import json
from datetime import datetime, timedelta
import jwt
from ..models.database import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def token_required(roles=None): # roles là một danh sách các vai trò được phép
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401
            try:
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = data.get('user_id')
                user_role = data.get('role') # Giả sử thông tin vai trò có trong token
                if current_user is None:
                    return jsonify({'message': 'Invalid token'}), 401
                if roles and user_role not in roles:
                    return jsonify({'message': 'Permission denied!'}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired!'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token!'}), 401
            except Exception as e:
                print(f"Lỗi giải mã token: {e}")
                return jsonify({'message': 'Something went wrong'}), 500
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

@auth_bp.route('/zalo', methods=['POST'])
def auth_zalo():
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"error": "Missing authorization code"}), 400

    code = data['code']
    token_payload = {
        'app_id': current_app.config['ZALO_APP_ID'],
        'grant_type': 'authorization_code',
        'code': code,
        'secret_key': current_app.config['ZALO_APP_SECRET']
    }

    try:
        token_response = requests.post(current_app.config['ZALO_OAUTH_URL'], data=token_payload)
        token_response.raise_for_status()
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        if not access_token:
            return jsonify({"error": "Failed to retrieve access token from Zalo"}), 401

        user_info_headers = {
            'access_token': access_token
        }
        user_info_response = requests.get(current_app.config['ZALO_USER_INFO_URL'], headers=user_info_headers)
        user_info_response.raise_for_status()
        user_info = user_info_response.json()
        zalo_user_id = user_info.get('id')
        if not zalo_user_id:
            return jsonify({"error": "Failed to retrieve user ID from Zalo"}), 401

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT zalo_id, points FROM users WHERE zalo_id = ?", (zalo_user_id,))
        user = cursor.fetchone()

        if user is None:
            cursor.execute("INSERT INTO users (zalo_id) VALUES (?)", (zalo_user_id,))
            db.commit()
            user = {'zalo_id': zalo_user_id, 'points': 0}
        else:
            user = dict(user)

        return jsonify({"zalo_id": user['zalo_id'], "points": user['points']}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Zalo: {e}"}), 500
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Error decoding JSON response from Zalo: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Yêu cầu đăng nhập thiếu thông tin'}), 401

    username = auth.get('username')
    password = auth.get('password')

    if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        token_payload = {
            'user_id': username,
            'exp': expiration_time
        }
        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token, 'expires_in': 3600}), 200

    return jsonify({'message': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401