-- 创建数据库
CREATE DATABASE IF NOT EXISTS car_sales DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE car_sales;

-- 1. 销售数据表（支持月度/季度/年度，零售/产量，所有/新能源/纯电）
CREATE TABLE IF NOT EXISTS sales_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    sales DECIMAL(15,2) COMMENT '销量（万辆）',
    data_type ENUM('retail','production') NOT NULL DEFAULT 'retail' COMMENT '零售/产量口径',
    date_type ENUM('monthly','quarterly','yearly') NOT NULL DEFAULT 'monthly' COMMENT '时间维度',
    level_type ENUM('all','nev','bev') NOT NULL DEFAULT 'all' COMMENT '车型级别',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_sales_data_unique (year, month, data_type, date_type, level_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='总销量数据（易车API）';

-- 2. 品牌元数据表
CREATE TABLE IF NOT EXISTS brand_meta (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL COMMENT '品牌名称',
    brand_name_en VARCHAR(100) COMMENT '品牌英文名',
    master_id INT COMMENT '外部系统品牌ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_brand_name (brand_name)
) ENGINE=InnoDB;

-- 3. 品牌销量表
CREATE TABLE IF NOT EXISTS brand_sales (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    brand_id BIGINT NOT NULL COMMENT '品牌ID(外键)',
    sales_volume DECIMAL(15,2) COMMENT '销量',
    data_type ENUM('retail','wholesale','production') DEFAULT 'retail' COMMENT '零售/批发/产量口径',
    date_type ENUM('monthly','quarterly','yearly') DEFAULT 'monthly' COMMENT '时间维度',
    level_type ENUM('all','nev','bev') DEFAULT 'all' COMMENT '车型级别',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_brand_sales_unique (year, month, brand_id, data_type, date_type, level_type),
    INDEX idx_brand_id (brand_id),
    CONSTRAINT fk_brand_sales_brand_meta FOREIGN KEY (brand_id) REFERENCES brand_meta(id)
) ENGINE=InnoDB;

-- 4. 数据采集日志表
CREATE TABLE IF NOT EXISTS data_collection_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL COMMENT '任务类型(market/brand)',
    status ENUM('pending','success','failed') DEFAULT 'pending' COMMENT '任务状态',
    records_count INT DEFAULT 0 COMMENT '入库记录数',
    error_message TEXT COMMENT '错误信息',
    started_at DATETIME COMMENT '开始时间',
    finished_at DATETIME COMMENT '结束时间',
    INDEX idx_task_type (task_type),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- 5. 车系占比数据表（乘联会官方国别细分）
CREATE TABLE IF NOT EXISTS origin_share_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL COMMENT '年份',
    month INT NOT NULL COMMENT '月份',
    origin VARCHAR(20) NOT NULL COMMENT '车系(自主/德系/日系/美系/欧系/韩系/其他)',
    sales_volume DECIMAL(15,4) COMMENT '销量(万辆)',
    data_type ENUM('retail','wholesale') DEFAULT 'retail' COMMENT '零售/批发口径',
    UNIQUE KEY uk_year_month_origin_type (year, month, origin, data_type),
    INDEX idx_year_month (year, month),
    INDEX idx_origin (origin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='车系占比数据(乘联会官方)';