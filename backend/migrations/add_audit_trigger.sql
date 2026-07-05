-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NOT NULL,
    action VARCHAR(20) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(50) DEFAULT 'SYSTEM'
);

-- STATEMENT_SPLIT

-- 创建触发器：当插入新的交通事件时记录日志
DROP TRIGGER IF EXISTS after_traffic_event_insert;

-- STATEMENT_SPLIT

CREATE TRIGGER after_traffic_event_insert
AFTER INSERT ON traffic_events
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, action, new_value, changed_by)
    VALUES ('traffic_events', NEW.id, 'INSERT', 
            CONCAT('Event Type: ', NEW.event_type, ', Status: ', IFNULL(NEW.status, 'N/A')), 
            'SYSTEM');
END;

-- STATEMENT_SPLIT

-- 创建触发器：当交通事件状态更新时记录日志
DROP TRIGGER IF EXISTS after_traffic_event_update;

-- STATEMENT_SPLIT

CREATE TRIGGER after_traffic_event_update
AFTER UPDATE ON traffic_events
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status OR OLD.event_type != NEW.event_type THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_value, new_value, changed_by)
        VALUES ('traffic_events', NEW.id, 'UPDATE', 
                CONCAT('Status: ', IFNULL(OLD.status, 'N/A'), ', Type: ', OLD.event_type),
                CONCAT('Status: ', IFNULL(NEW.status, 'N/A'), ', Type: ', NEW.event_type),
                'SYSTEM');
    END IF;
END;
