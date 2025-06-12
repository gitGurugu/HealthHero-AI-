CREATE TABLE user_roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL CHECK (role_name IN ('admin_role', 'doctor_role', 'regular_user_role'))
);
INSERT INTO user_roles (role_name) VALUES 
('admin_role'), 
('doctor_role'), 
('regular_user_role');

-- CREATE TABLE users (
--     user_id BIGSERIAL PRIMARY KEY,
--     username VARCHAR(50) UNIQUE NOT NULL,
--     encrypted_password VARCHAR(100) NOT NULL,
--     gender CHAR(1) CHECK (gender IN ('M','F')),
--     birthdate DATE NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     role_id INT REFERENCES user_roles(role_id)
-- );

CREATE TABLE health_data (
    record_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    record_date DATE NOT NULL,
    height DECIMAL(5,2) CHECK (height > 0),
    weight DECIMAL(5,1) CHECK (weight BETWEEN 30 AND 300),
    systolic_pressure SMALLINT CHECK (systolic_pressure BETWEEN 50 AND 250),
    diastolic_pressure SMALLINT CHECK (diastolic_pressure BETWEEN 30 AND 150),
    blood_sugar DECIMAL(4,1),
    cholesterol DECIMAL(4,1) CHECK (cholesterol >= 0),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- CREATE TABLE prediction_model (
--     model_version VARCHAR(20) PRIMARY KEY,
--     description TEXT,
--     created_on DATE
-- );

-- CREATE TABLE prediction_results (
--     prediction_id BIGSERIAL PRIMARY KEY,
--     user_id BIGINT NOT NULL,
--     model_version VARCHAR(20),
--     prediction_date DATE,
--     risk_diabetes DECIMAL(3,2),
--     risk_heart DECIMAL(3,2),
--     weight_prediction FLOAT8,
--     FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
--     FOREIGN KEY (model_version) REFERENCES prediction_model(model_version)
-- );

CREATE TABLE diet_record (
    record_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    record_date DATE NOT NULL,
    calories INT CHECK (calories >= 0),
    food_detail TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE exercise_log (
    log_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    exercise_type VARCHAR(50),
    duration_minutes INT CHECK (duration_minutes > 0),
    log_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- CREATE TABLE recommendation (
--     rec_id SERIAL PRIMARY KEY,
--     user_id BIGINT,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     content TEXT,
--     source_type VARCHAR(20), -- e.g., 'AI', 'Doctor', 'System'
--     prediction_id BIGINT REFERENCES prediction_results(prediction_id),
--     FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
-- );

-- CREATE TABLE health_log (
--     log_id SERIAL PRIMARY KEY,
--     user_id BIGINT,
--     log_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     action_type VARCHAR(50),
--     action_detail TEXT,
--     device_info TEXT,
--     FOREIGN KEY (user_id) REFERENCES users(user_id)
-- );

-- CREATE TABLE ddl_log (
--     log_id SERIAL PRIMARY KEY,
--     command_tag TEXT,
--     object_type TEXT,
--     object_name TEXT,
--     executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- 索引
CREATE INDEX idx_health_user_date ON health_data(user_id, record_date DESC);
CREATE INDEX idx_diet_user_date ON diet_record(user_id, record_date);
CREATE INDEX idx_exercise_user_date ON exercise_log(user_id, log_date DESC);


-- 3. 创建视图
-- Doctor视角：用户最新健康记录
CREATE OR REPLACE GLOBAL VIEW v_user_latest_health AS
SELECT u.username, h.user_id, h.record_date, h.weight, h.systolic_pressure, h.diastolic_pressure, h.blood_sugar
FROM users u
JOIN health_data h ON u.user_id = h.user_id
WHERE h.record_date = (
    SELECT MAX(h2.record_date)
    FROM health_data h2
    WHERE h2.user_id = h.user_id
);

-- Doctor视角：最近10天健康记录
CREATE OR REPLACE GLOBAL VIEW v_recent_health AS
SELECT u.username, h.user_id, h.record_date, h.height, h.weight, h.blood_sugar, h.cholesterol
FROM users u
JOIN health_data h ON u.user_id = h.user_id
WHERE h.record_date >= CURRENT_DATE - INTERVAL '10 days'
ORDER BY h.user_id, h.record_date DESC;

-- Doctor视角：预测结果摘要
CREATE OR REPLACE GLOBAL VIEW v_prediction_summary AS
SELECT u.username, p.user_id, p.model_version, p.prediction_date, p.risk_diabetes, p.risk_heart
FROM prediction_results p
JOIN users u ON p.user_id = u.user_id;

-- User视角：个人健康数据
CREATE OR REPLACE VIEW v_my_health AS
SELECT *
FROM health_data
WHERE user_id = current_setting('app.current_user_id')::BIGINT;

-- User视角：个人预测结果
CREATE OR REPLACE VIEW v_my_predictions AS
SELECT *
FROM prediction_results
WHERE user_id = current_setting('app.current_user_id')::BIGINT;

-- User视角：个人饮食记录
CREATE OR REPLACE VIEW v_my_diet AS
SELECT *
FROM diet_record
WHERE user_id = current_setting('app.current_user_id')::BIGINT;

-- 创建可插入视图，用于INSTEAD OF触发器示范
CREATE OR REPLACE GLOBAL VIEW v_insertable_my_diet AS
SELECT * FROM diet_record;


-- 4. 触发器与函数

-- 4.1 健康数据变化后自动更新预测结果
CREATE OR REPLACE FUNCTION update_prediction_after_health_data()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE prediction_results
  SET 
    risk_diabetes = ROUND(random(), 2),
    risk_heart = ROUND(random(), 2),
    weight_prediction = NEW.weight,
    prediction_date = CURRENT_DATE
  WHERE user_id = NEW.user_id AND model_version = 'v1.0';

  IF NOT FOUND THEN
    INSERT INTO prediction_results(user_id, model_version, prediction_date, risk_diabetes, risk_heart, weight_prediction)
    VALUES (NEW.user_id, 'v1.0', CURRENT_DATE, ROUND(random(), 2), ROUND(random(), 2), NEW.weight);
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_prediction_after_health
AFTER INSERT OR UPDATE ON health_data
FOR EACH ROW EXECUTE PROCEDURE update_prediction_after_health_data();

-- 4.2 health_data 插入时记录日志
CREATE OR REPLACE FUNCTION log_health_insert()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO health_log(user_id, log_at, action_type, action_detail)
  VALUES (NEW.user_id, CURRENT_TIMESTAMP, 'INSERT', 'New health data inserted');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_insert_health
AFTER INSERT ON health_data
FOR EACH ROW EXECUTE PROCEDURE log_health_insert();

-- 4.3 health_data 删除时记录日志（模拟deleted表）
CREATE OR REPLACE FUNCTION log_health_delete()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO health_log(user_id, log_at, action_type, action_detail)
  VALUES (OLD.user_id, CURRENT_TIMESTAMP, 'DELETE', 'Deleted health record');
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_delete_health
AFTER DELETE ON health_data
FOR EACH ROW
EXECUTE PROCEDURE log_health_delete();

-- 4.4 assign_db_role 触发器
CREATE OR REPLACE FUNCTION assign_db_role()
RETURNS TRIGGER AS $$
DECLARE
  db_role TEXT;
  sql TEXT;
BEGIN
  -- 获取角色名
  SELECT role_name INTO db_role FROM user_roles WHERE role_id = NEW.role_id;

  IF NOT FOUND THEN
    RAISE NOTICE '未找到对应的角色ID：%', NEW.role_id;
    RETURN NEW;
  END IF;

  -- 尝试创建数据库登录角色（如果不存在）
  BEGIN
    EXECUTE format('CREATE ROLE %I WITH LOGIN PASSWORD %L', NEW.username, 'DefaultPassword123');
  EXCEPTION
    WHEN duplicate_object THEN
      RAISE NOTICE '角色 % 已存在，跳过创建。', NEW.username;
  END;

  -- 授权角色权限
  EXECUTE format('GRANT %I TO %I', db_role, NEW.username);

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_assign_db_role ON users;

CREATE TRIGGER trg_assign_db_role
AFTER INSERT ON users
FOR EACH ROW
EXECUTE PROCEDURE assign_db_role();


-- 4.5 INSTEAD OF触发器示例：对v_insertable_my_diet视图插入进行替代处理
CREATE OR REPLACE FUNCTION trg_instead_insert_diet()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO diet_record(user_id, record_date, calories, food_detail)
  VALUES (
    current_setting('app.current_user_id')::BIGINT,
    NEW.record_date, NEW.calories, NEW.food_detail
  );
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_instead_insert_diet
INSTEAD OF INSERT ON v_insertable_my_diet
FOR EACH ROW
EXECUTE PROCEDURE trg_instead_insert_diet();

-- 4.6 DDL事件触发器：记录DDL操作到ddl_log表
CREATE OR REPLACE FUNCTION log_ddl_command()
RETURNS EVENT_TRIGGER AS $$
BEGIN
  INSERT INTO ddl_log(command_tag, object_type, object_name)
  SELECT
    tg_tag,
    objtype,
    objname
  FROM pg_event_trigger_ddl_commands();
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER trg_ddl_logger
ON ddl_command_end
EXECUTE PROCEDURE log_ddl_command();


-- 5. 用户功能函数和存储过程

-- 5.1 计算BMI
CREATE OR REPLACE FUNCTION calc_bmi(weight DECIMAL, height DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
  RETURN weight / POWER(height / 100, 2);
END;
$$ LANGUAGE plpgsql;

-- 5.2 获取最近5条健康记录
CREATE OR REPLACE FUNCTION recent_health(uid BIGINT)
RETURNS TABLE(record_date DATE, weight DECIMAL, blood_sugar DECIMAL) AS $$
BEGIN
  RETURN QUERY
  SELECT record_date, weight, blood_sugar
  FROM health_data
  WHERE user_id = uid
  ORDER BY record_date DESC
  LIMIT 5;
END;
$$ LANGUAGE plpgsql;

-- 5.3 显示用户健康数据（过程）
CREATE OR REPLACE PROCEDURE get_user_health(IN uid BIGINT)
AS
DECLARE
  record RECORD;
BEGIN
  RAISE NOTICE 'User % health data:', uid;
  FOR record IN SELECT * FROM health_data WHERE user_id = uid LOOP
    RAISE NOTICE '%', record;
  END LOOP;
END;

-- 5.4
CREATE OR REPLACE FUNCTION delete_user_and_role(p_username VARCHAR)
RETURNS VOID AS $$
DECLARE
  v_user_id BIGINT;
  v_requester TEXT := CURRENT_USER;
  v_requester_id BIGINT;
  v_requester_role TEXT;
BEGIN
  -- 获取当前登录者的用户ID和角色
  SELECT user_id, r.role_name INTO v_requester_id, v_requester_role
  FROM users u
  JOIN user_roles r ON u.role_id = r.role_id
  WHERE u.username = v_requester;

  IF NOT FOUND THEN
    RAISE EXCEPTION '当前用户 % 在用户表中未找到', v_requester;
  END IF;

  -- 权限判断逻辑：
  IF v_requester_role = 'admin_role' THEN
    -- 管理员可以删除任何人，无需检查
    NULL;

  ELSIF v_requester_role IN ('doctor_role', 'regular_user_role') THEN
    -- 普通用户只能删除自己
    IF p_username <> v_requester THEN
      RAISE EXCEPTION '用户 % 无权限删除其他用户，仅可删除自己', v_requester;
    END IF;

  ELSE
    RAISE EXCEPTION '未知角色 %，拒绝操作', v_requester_role;
  END IF;

  -- 获取被删除用户ID（确认存在）
  SELECT user_id INTO v_user_id FROM users WHERE username = p_username;
  IF NOT FOUND THEN
    RAISE EXCEPTION '待删除的用户 % 不存在', p_username;
  END IF;

  -- 删除 users 表记录（会触发 ON DELETE CASCADE）
  DELETE FROM users WHERE username = p_username;

  -- 删除对应数据库登录角色
  EXECUTE format('DROP ROLE IF EXISTS %I', p_username);

  RAISE NOTICE '用户 % 及其数据库角色已成功删除', p_username;

END;
$$ LANGUAGE plpgsql;


REVOKE ALL ON FUNCTION delete_user_and_role(VARCHAR) FROM PUBLIC;

GRANT EXECUTE ON FUNCTION delete_user_and_role(VARCHAR) TO admin_role;
GRANT EXECUTE ON FUNCTION delete_user_and_role(VARCHAR) TO doctor_role;
GRANT EXECUTE ON FUNCTION delete_user_and_role(VARCHAR) TO regular_user_role;


-- 6. 角色创建与权限分配

-- 创建角色
CREATE ROLE admin_role WITH PASSWORD 'openGauss@123';
CREATE ROLE doctor_role WITH PASSWORD 'openGauss@123';
CREATE ROLE regular_user_role WITH PASSWORD 'openGauss@123';

-- 授权 admin 全权限（表和序列）
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO admin_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO admin_role;

-- 未来新对象默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO admin_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO admin_role;


REVOKE ALL ON 
  v_user_latest_health, v_recent_health, v_prediction_summary, 
  v_my_health, v_my_predictions, v_my_diet
FROM PUBLIC;

GRANT SELECT ON 
  v_user_latest_health, v_recent_health, v_prediction_summary 
TO doctor_role;

GRANT SELECT ON 
  v_my_health, v_my_predictions, v_my_diet 
TO regular_user_role;

-- 授权执行函数权限
GRANT EXECUTE ON FUNCTION recent_health(BIGINT) TO doctor_role, admin_role;
GRANT EXECUTE ON FUNCTION calc_bmi(DECIMAL, DECIMAL) TO regular_user_role, doctor_role, admin_role;

-- 授权触发器相关表操作
GRANT INSERT, UPDATE ON health_data TO doctor_role;
GRANT INSERT ON diet_record TO regular_user_role;


-- 7.1 检查用户数
DO $$
DECLARE
    user_total INT;
BEGIN
    SELECT COUNT(*) INTO user_total FROM users;
    IF user_total > 100 THEN
        RAISE NOTICE '用户数超过100';
    ELSE
        RAISE NOTICE '用户数未超过100';
    END IF;
END;
$$;

-- 7.2 遍历用户
DO $$
DECLARE
    rec RECORD;
    user_cursor CURSOR FOR SELECT user_id, username FROM users;
BEGIN
    OPEN user_cursor;
    LOOP
        FETCH user_cursor INTO rec;
        EXIT WHEN NOT FOUND;
        RAISE NOTICE 'User ID: %, Username: %', rec.user_id, rec.username;
    END LOOP;
    CLOSE user_cursor;
END;
$$;



-- 1. 备份与还原命令（命令行使用）
-- 备份：gs_dump smart_health -f backup.sql
-- 还原：gsql -d smart_health -f backup.sql

-- 2. 数据库恢复技术
-- 2.1 记录删除前数据（触发器 + 备份表）
CREATE TABLE deleted_health_data_backup (
    backup_id SERIAL PRIMARY KEY,
    original_record_id INT,
    user_id BIGINT,
    record_date DATE,
    weight DECIMAL(5,1),
    blood_pressure VARCHAR(7),
    blood_sugar DECIMAL(4,1),
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION backup_deleted_health_data()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO deleted_health_data_backup(original_record_id, user_id, record_date, weight, blood_pressure, blood_sugar)
    VALUES (OLD.record_id, OLD.user_id, OLD.record_date, OLD.weight, OLD.blood_pressure, OLD.blood_sugar);
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_backup_health_delete
BEFORE DELETE ON health_data
FOR EACH ROW EXECUTE FUNCTION backup_deleted_health_data();

-- 2.2 恢复删除数据的辅助函数
CREATE OR REPLACE FUNCTION restore_health_data(backup_id INT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO health_data(user_id, record_date, weight, blood_pressure, blood_sugar)
    SELECT user_id, record_date, weight, blood_pressure, blood_sugar
    FROM deleted_health_data_backup
    WHERE backup_id = restore_health_data.backup_id;
END;
$$ LANGUAGE plpgsql;


