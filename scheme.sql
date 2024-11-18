CREATE TABLE User (
    user_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255)
);

CREATE TABLE Profile (
    profile_id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    job_title VARCHAR(255),
    company VARCHAR(255),
    bio TEXT,
    profile_picture VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Contact_Info (
    contact_id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    contact_type VARCHAR(255),
    contact_value VARCHAR(255),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Palm_Recognition_Activity (
    recognition_id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    scanned_user_id CHAR(36),
    recognition_status BOOLEAN,
    time_scanned TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Analytics (
    analytics_id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    total_scanned INTEGER,
    last_scanned_date TIMESTAMP,
    activity_summary JSON,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Password_Reset (
    reset_id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    reset_token VARCHAR(255),
    token_expiration TIMESTAMP,
    is_used BOOLEAN,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Token_Blacklist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    token VARCHAR(255) UNIQUE,
    blacklisted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);