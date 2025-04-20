import sqlite3

DATABASE = 'loyalty.db'

def add_reward(name, points_cost):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rewards (name, points_cost) VALUES (?, ?)", (name, points_cost))
    conn.commit()
    conn.close()
    print(f"Đã thêm phần thưởng: {name} - {points_cost} điểm")

if __name__ == '__main__':
    add_reward("Giảm 10% cho đơn hàng tiếp theo", 50)
    add_reward("Miễn phí giao hàng", 100)
    add_reward("Quà tặng đặc biệt", 200)
    # Thêm các phần thưởng khác tùy ý