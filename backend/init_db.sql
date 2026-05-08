-- 创建数据库
CREATE DATABASE IF NOT EXISTS car_sales DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE car_sales;

-- 1. 销售数据表（支持月度/年度）
CREATE TABLE IF NOT EXISTS sales_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    total_sales DECIMAL(15,2) COMMENT '乘用车总销量',
    nev_sales DECIMAL(15,2) COMMENT '新能源车销量',
    ice_sales DECIMAL(15,2) COMMENT '燃油车销量',
    bev_sales DECIMAL(15,2) COMMENT '纯电销量',
    phev_sales DECIMAL(15,2) COMMENT '插电混动销量',
    hybrid_sales DECIMAL(15,2) COMMENT '其他混动销量',
    data_type ENUM('retail','wholesale','production') DEFAULT 'retail' COMMENT '零售/批发/产量口径',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_year_month_type (year, month, data_type)
) ENGINE=InnoDB;

-- 2. 品牌元数据表
CREATE TABLE IF NOT EXISTS brand_meta (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL COMMENT '品牌名称',
    brand_name_en VARCHAR(100) COMMENT '品牌英文名',
    origin VARCHAR(20) COMMENT '车系(自主/德系/日系/美系/欧系/韩系/其他)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_brand_name (brand_name)
) ENGINE=InnoDB;

-- 3. 品牌销量表
CREATE TABLE IF NOT EXISTS brand_sales (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    brand_name VARCHAR(100) NOT NULL COMMENT '品牌名称',
    sales_volume DECIMAL(15,2) COMMENT '销量',
    yoy_growth DECIMAL(8,2) COMMENT '同比增速(%)',
    mom_growth DECIMAL(8,2) COMMENT '环比增速(%)',
    data_type ENUM('retail','wholesale','production') DEFAULT 'retail' COMMENT '零售/批发/产量口径',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_year_month_brand_source (year, month, brand_name, data_type),
    INDEX idx_brand_name (brand_name)
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