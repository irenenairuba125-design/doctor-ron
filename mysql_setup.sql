-- Run this in MySQL Workbench (or the mysql client) before `python manage.py migrate`.
CREATE DATABASE IF NOT EXISTS hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Optional: a dedicated user instead of root (change the password!)
CREATE USER IF NOT EXISTS 'hms_user'@'localhost' IDENTIFIED BY 'ChangeMe@123';
GRANT ALL PRIVILEGES ON hospital_db.* TO 'hms_user'@'localhost';
FLUSH PRIVILEGES;
