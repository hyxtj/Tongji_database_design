-- 为 users 表添加邮箱验证相关字段
-- 在MySQL客户端或phpMyAdmin中执行此SQL

USE traffic;

-- 添加邮箱验证字段
ALTER TABLE users 
ADD COLUMN email_verified BOOLEAN DEFAULT FALSE COMMENT '邮箱是否已验证',
ADD COLUMN verification_code VARCHAR(10) DEFAULT NULL COMMENT '验证码',
ADD COLUMN verification_code_expires DATETIME DEFAULT NULL COMMENT '验证码过期时间';

-- 为现有用户设置邮箱已验证(避免影响现有用户登录)
UPDATE users SET email_verified = TRUE;

-- 查看更新后的表结构
DESCRIBE users;

-- 查看所有用户
SELECT id, username, email, is_admin, email_verified FROM users;
