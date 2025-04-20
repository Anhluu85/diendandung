-- Bảng người dùng
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zalo_id TEXT UNIQUE NOT NULL,
    phone_number TEXT UNIQUE,
    points INTEGER DEFAULT 0,
    first_purchase_date DATETIME
);

-- Bảng phần thưởng
CREATE TABLE IF NOT EXISTS rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    points_cost INTEGER NOT NULL
);

-- Bảng lịch sử đổi thưởng
CREATE TABLE IF NOT EXISTS redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_zalo_id TEXT NOT NULL,
    reward_id INTEGER NOT NULL,
    redeemed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_zalo_id) REFERENCES users(zalo_id),
    FOREIGN KEY (reward_id) REFERENCES rewards(id)
);

-- Bảng lịch sử giao dịch điểm
CREATE TABLE IF NOT EXISTS point_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_zalo_id TEXT NOT NULL,
    points_change INTEGER NOT NULL,
    type TEXT NOT NULL, -- 'earn' hoặc 'redeem'
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    transaction_id TEXT UNIQUE, -- Mã giao dịch từ hệ thống khác (nếu có)
    purchase_date DATETIME, -- Ngày mua hàng (nếu là giao dịch tích điểm)
    purchase_amount REAL,   -- Tổng tiền giao dịch (nếu là giao dịch tích điểm)
    FOREIGN KEY (user_zalo_id) REFERENCES users(zalo_id)
);

-- Thêm một số phần thưởng mẫu (nếu bạn chưa có dữ liệu)
