from flask import Blueprint, request, jsonify
from datetime import datetime
from models.database import get_db

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/points', methods=['GET'])
def get_user_points():
    user_zalo_id = request.args.get('zalo_id')
    if not user_zalo_id:
        return jsonify({"error": "Missing zalo_id"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT points FROM users WHERE zalo_id = ?", (user_zalo_id,))
    user_data = cursor.fetchone()

    if user_data:
        points = user_data['points']
        return jsonify({"zalo_id": user_zalo_id, "points": points}), 200
    else:
        return jsonify({"error": f"User with zalo_id '{user_zalo_id}' not found"}), 404

@user_bp.route('/register-first-purchase', methods=['POST'])
def register_first_purchase():
    data = request.get_json()
    zalo_id = data.get('zalo_id')
    phone_number = data.get('phone_number')

    if not zalo_id:
        return jsonify({'error': 'Thiếu Zalo User ID'}), 400
    if not phone_number:
        return jsonify({'error': 'Thiếu số điện thoại'}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        user = cursor.execute("SELECT zalo_id FROM users WHERE zalo_id = ?", (zalo_id,)).fetchone()
        if user:
            cursor.execute("UPDATE users SET phone_number = ? WHERE zalo_id = ?", (phone_number, zalo_id))
            conn.commit()
            close_db(conn)
            return jsonify({'message': f'Đã cập nhật số điện thoại cho Zalo ID {zalo_id}'}), 200
        else:
            cursor.execute("INSERT INTO users (zalo_id, phone_number) VALUES (?, ?)", (zalo_id, phone_number))
            conn.commit()
            close_db(conn)
            return jsonify({'message': f'Đã đăng ký người dùng với Zalo ID {zalo_id} và số điện thoại {phone_number}'}), 201
    except sqlite3.IntegrityError as e:
        close_db(conn)
        return jsonify({'error': f'Lỗi cơ sở dữ liệu: {e}'}), 400

@user_bp.route('/<zalo_id>/transactions', methods=['GET'])
def get_user_transactions(zalo_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT points_change, type, created_at, description, transaction_id, purchase_date, purchase_amount
        FROM point_transactions
        WHERE user_zalo_id = ?
        ORDER BY created_at DESC
    """, (zalo_id,))
    transactions = cursor.fetchall()

    if not transactions:
        return jsonify({"message": f"No transactions found for user with zalo_id '{zalo_id}'"}), 200

    transaction_list = []
    for transaction in transactions:
        transaction_list.append({
            "points_change": transaction['points_change'],
            "type": transaction['type'],
            "created_at": transaction['created_at'],
            "description": transaction['description'],
            "transaction_id": transaction['transaction_id'],
            "purchase_date": transaction['purchase_date'],
            "purchase_amount": transaction['purchase_amount']
        })
    return jsonify(transaction_list), 200

@user_bp.route('/points/earn', methods=['POST'])
def earn_points():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body không được để trống"}), 400

    zalo_id = data.get('zalo_id')
    points_to_earn = data.get('points')
    purchase_date_str = data.get('purchase_date')
    purchase_amount = data.get('purchase_amount')

    if not zalo_id or not isinstance(zalo_id, str) or not zalo_id.strip():
        return jsonify({"error": "zalo_id không hợp lệ"}), 400
    if not isinstance(points_to_earn, int) or points_to_earn <= 0:
        return jsonify({"error": "Giá trị điểm không hợp lệ. Phải là một số nguyên dương"}), 400

    purchase_date = None
    if purchase_date_str:
        try:
            purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Định dạng purchase_date không hợp lệ. Sử dụng<ctrl3348>-MM-DD HH:MM:SS hoặc<ctrl3348>-MM-DD"}), 400

    if purchase_amount is not None:
        if not isinstance(purchase_amount, (int, float)):
            return jsonify({"error": "purchase_amount không hợp lệ. Phải là một số"}), 400
        if purchase_amount < 0:
            return jsonify({"error": "purchase_amount không được âm"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT points FROM users WHERE zalo_id = ?", (zalo_id,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": f"Không tìm thấy người dùng với zalo_id '{zalo_id}'"}), 404

    new_points = user['points'] + points_to_earn
    cursor.execute("UPDATE users SET points = ? WHERE zalo_id = ?", (new_points, zalo_id,))
    cursor.execute("""
        INSERT INTO point_transactions (user_zalo_id, points_change, type, created_at, purchase_date, purchase_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (zalo_id, points_to_earn, 'tích', datetime.now(), purchase_date, purchase_amount))
    db.commit()
    return jsonify({"message": f"Đã tích {points_to_earn} điểm thành công. Số dư mới: {new_points}"}), 200
