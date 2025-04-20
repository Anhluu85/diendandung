import os
import toml

# Đường dẫn đến file secrets.toml
secrets_file_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")

SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
DATABASE = 'loyalty.db'

# Thông tin Zalo API
ZALO_APP_ID = '1701849455681669153'
ZALO_APP_SECRET = 'vMQf2c6LL5C1VD2VuQ31'
ZALO_OAUTH_URL = 'https://oauth.zaloapp.com/v3/access_token'
ZALO_USER_INFO_URL = 'https://graph.zalo.me/v2.0/me'

# Thông tin Admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Đọc SECRET_KEY từ secrets.toml
if os.path.exists(secrets_file_path):
    try:
        secrets = toml.load(secrets_file_path)
        secret_key_from_file = secrets.get("app", {}).get("secret_key")
        if secret_key_from_file:
            SECRET_KEY = secret_key_from_file
            print("Đã tải SECRET_KEY từ secrets.toml")
        else:
            print("Không tìm thấy 'secret_key' trong file secrets.toml, sử dụng giá trị mặc định (KHÔNG DÙNG CHO PRODUCTION)")
    except toml.TomlDecodeError as e:
        print(f"Lỗi khi đọc file secrets.toml: {e}, sử dụng giá trị mặc định (KHÔNG DÙNG CHO PRODUCTION)")
else:
    print(f"Không tìm thấy file secrets.toml tại: {secrets_file_path}, sử dụng giá trị mặc định (KHÔNG DÙNG CHO PRODUCTION)")

print(f"Đường dẫn file database Flask đang dùng: {os.path.abspath(DATABASE)}")
