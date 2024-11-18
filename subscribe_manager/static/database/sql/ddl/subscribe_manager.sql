CREATE TABLE IF NOT EXISTS subscribe_manager (
    file_name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    subscription_userinfo TEXT,
    create_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)