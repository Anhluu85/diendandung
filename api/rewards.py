from flask import Blueprint, request, jsonify
from datetime import datetime
from models.database import get_db

rewards_bp = Blueprint('rewards', __name__, url_prefix='/api/rewards')

@rewards_bp.route('', methods=['GET'])
def get_rewards():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, points_cost FROM rewards")
    rewards_data = cursor.fetchall()

    rewards = []
    for row in rewards_data:
        rewards.append({
            "id": row['id'],
            "name": row['name'],
            "points_cost": row['points_cost']
        })
    return jsonify(rewards), 200

@rewards_bp.route('/<int:reward_id>/redeem', methods=['POST'])
def redeem_reward(reward_id):
    user_zalo_id = request.args.get('zalo_id')
    if not user_zalo_id or not isinstance(user_zalo_id, str) or not user_zalo_id.strip():
        return jsonify({"error": "Thiếu hoặc zalo_id không hợp lệ"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT name, points_cost FROM rewards WHERE id = ?", (reward_id,))
    reward = cursor.fetchone()
    if not reward:
        return jsonify({"error": f"Không tìm thấy phần thưởng với id '{reward_id}'"}), 404

    cursor.execute("SELECT points FROM users WHERE zalo_id = ?", (user_zalo_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"error": f"Không tìm thấy người dùng với zalo_id '{user_zalo_id}'"}), 404

    if user['points'] < reward['points_cost']:
        return jsonify({"error": "Không đủ điểm"}), 400

    new_points = user['points'] - reward['points_cost']
    cursor.execute("UPDATE users SET points = ? WHERE zalo_id = ?", (new_points, user_zalo_id,))
    cursor.execute("INSERT INTO redemptions (user_zalo_id, reward_id, redeemed_at) VALUES (?, ?, ?)",
                   (user_zalo_id, reward_id, datetime.now()))
    db.commit()

    return jsonify({"message": f"Đã đổi thành công '{reward['name']}'. Số điểm còn lại: {new_points}"}), 200
