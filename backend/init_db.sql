-- 创建数据库
CREATE DATABASE IF NOT EXISTS car_sales DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE car_sales;

-- 1. 月度整体销量表
CREATE TABLE IF NOT EXISTS monthly_overall (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    total_sales DECIMAL(15,2) COMMENT '乘用车总销量',
    nev_sales DECIMAL(15,2) COMMENT '新能源车销量',
    ice_sales DECIMAL(15,2) COMMENT '燃油车销量',
    bev_sales DECIMAL(15,2) COMMENT '纯电销量',
    phev_sales DECIMAL(15,2) COMMENT '插电混动销量',
    hybrid_sales DECIMAL(15,2) COMMENT '其他混动销量',
    nev_penetration_rate DECIMAL(5,2) COMMENT '新能源渗透率(%)',
    data_type ENUM('retail','wholesale') DEFAULT 'retail' COMMENT '零售/批发口径',
    source VARCHAR(50) DEFAULT 'cpca' COMMENT '数据来源标识',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_year_month_type (year, month, data_type)
) ENGINE=InnoDB;

-- 2. 品牌月度销量表
CREATE TABLE IF NOT EXISTS monthly_brand (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    brand_name VARCHAR(100) NOT NULL COMMENT '品牌名称',
    brand_name_en VARCHAR(100) COMMENT '品牌英文名',
    sales_volume DECIMAL(15,2) COMMENT '月销量',
    rank INT COMMENT '排名',
    prev_month_rank INT COMMENT '上月排名',
    yoy_growth DECIMAL(8,2) COMMENT '同比增速(%)',
    mom_growth DECIMAL(8,2) COMMENT '环比增速(%)',
    is_nev TINYINT(1) DEFAULT 0 COMMENT '是否新能源品牌',
    source VARCHAR(50) DEFAULT 'cpca' COMMENT '数据来源',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_year_month_brand_source (year, month, brand_name, source)
) ENGINE=InnoDB;

-- 3. 车型月度销量表
CREATE TABLE IF NOT EXISTS monthly_model (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    model_name VARCHAR(200) NOT NULL COMMENT '车型名称',
    brand_id BIGINT COMMENT '所属品牌ID',
    sales_volume DECIMAL(15,2) COMMENT '月销量',
    rank INT COMMENT '排名',
    segment VARCHAR(50) COMMENT '级别(A00/A0/B/C/D)',
    energy_type VARCHAR(20) COMMENT '能源类型',
    source VARCHAR(50) DEFAULT 'cpca' COMMENT '数据来源',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_brand_id (brand_id),
    INDEX idx_year_month (year, month)
) ENGINE=InnoDB;

-- 4. 数据采集日志表
CREATE TABLE IF NOT EXISTS data_collection_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL COMMENT '任务类型(market/brand/model)',
    status ENUM('pending','success','failed') DEFAULT 'pending' COMMENT '任务状态',
    records_count INT DEFAULT 0 COMMENT '入库记录数',
    error_message TEXT COMMENT '错误信息',
    started_at DATETIME COMMENT '开始时间',
    finished_at DATETIME COMMENT '结束时间',
    INDEX idx_task_type (task_type),
    INDEX idx_status (status)
) ENGINE=InnoDB;