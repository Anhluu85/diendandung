from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from functools import wraps
import jwt
from models.database import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data.get('user_id')
            if current_user is None:
                return jsonify({'message': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        except Exception as e:
            print(f"Lỗi giải mã token: {e}")
            return jsonify({'message': 'Something went wrong'}), 500
        return f(current_user, *args, **kwargs)
    return decorated

@admin_bp.route('/points/earn-by-phone', methods=['POST'])
@token_required
def admin_earn_points_by_phone(current_user):
    data = request.get_json()
    phone_number = data.get('phone_number')
    total_amount = data.get('total_amount')
    transaction_id = data.get('transaction_id')

    if not all([phone_number, total_amount, transaction_id]):
        return jsonify({'error': 'Thiếu thông tin cần thiết (số điện thoại, tổng tiền, mã giao dịch)'}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        user = cursor.execute("SELECT zalo_id FROM users WHERE phone_number = ?", (phone_number,)).fetchone()
        if not user:
            close_db(conn)
            return jsonify({'error': f'Không tìm thấy người dùng với số điện thoại {phone_number}'}), 404

        zalo_id = user['zalo_id']
        existing_transaction = cursor.execute("SELECT id FROM point_transactions WHERE transaction_id = ?", (transaction_id,)).fetchone()
        if existing_transaction:
            close_db(conn)
            return jsonify({'message': 'Giao dịch này đã được xử lý trước đó'}), 200

        points_earned = total_amount // 10000
        cursor.execute("UPDATE users SET points = points + ? WHERE zalo_id = ?", (points_earned, zalo_id))
        cursor.execute("INSERT INTO point_transactions (user_zalo_id, points_change, type, description, transaction_id, purchase_amount, purchase_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (zalo_id, points_earned, 'earn', f"Tích điểm (Admin) từ giao dịch #{transaction_id}", transaction_id, total_amount, datetime.now()))
        conn.commit()
        close_db(conn)
        return jsonify({'message': f'Đã tích {points_earned} điểm cho số điện thoại {phone_number} (Zalo ID: {zalo_id})'}), 200

    except sqlite3.IntegrityError as e:
        close_db(conn)
        return jsonify({'error': f'Lỗi cơ sở dữ liệu: {e}'}), 400
    except Exception as e:
        close_db(conn)
        return jsonify({'error': f'Lỗi không xác định: {e}'}), 500

def close_db(conn):
    if conn:
        conn.close()
