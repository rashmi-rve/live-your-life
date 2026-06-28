-- Run this once against your MySQL server before starting the app:
--   mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS village_journey
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE village_journey;

-- One row per visitor who reaches a house and is greeted by name
CREATE TABLE IF NOT EXISTS house_entries (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    session_id    VARCHAR(64)  NOT NULL,
    house_size    TINYINT      NOT NULL,   -- 1 (smallest) .. 5 (largest)
    visitor_name  VARCHAR(120) NOT NULL,
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id)
) ENGINE=InnoDB;

-- One row per visitor who chooses development and claims the award
CREATE TABLE IF NOT EXISTS award_entries (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    session_id    VARCHAR(64)  NOT NULL,
    visitor_name  VARCHAR(120) NOT NULL,
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id)
) ENGINE=InnoDB;
