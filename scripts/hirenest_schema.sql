CREATE DATABASE IF NOT EXISTS `HireNest`;
USE `HireNest`;

DROP TABLE IF EXISTS `Admin_Audit_Log`;
DROP TABLE IF EXISTS `User_Sessions`;
DROP TABLE IF EXISTS `Email_Verification_Tokens`;
DROP TABLE IF EXISTS `User_Settings`;
DROP TABLE IF EXISTS `Seeker_Assessment_Attempts`;
DROP TABLE IF EXISTS `Assessment_Questions`;
DROP TABLE IF EXISTS `Skills_Assessments`;
DROP TABLE IF EXISTS `Job_Reports`;
DROP TABLE IF EXISTS `Payment_History`;
DROP TABLE IF EXISTS `Employer_Subscriptions`;
DROP TABLE IF EXISTS `Subscription_Plans`;
DROP TABLE IF EXISTS `Messages`;
DROP TABLE IF EXISTS `Notification`;
DROP TABLE IF EXISTS `Job_Alerts`;
DROP TABLE IF EXISTS `Saved_Jobs`;
DROP TABLE IF EXISTS `Company_Review`;
DROP TABLE IF EXISTS `Interview`;
DROP TABLE IF EXISTS `Applications`;
DROP TABLE IF EXISTS `Jobs`;
DROP TABLE IF EXISTS `Employee`;
DROP TABLE IF EXISTS `Job_Seekers`;
DROP TABLE IF EXISTS `User`;

CREATE TABLE IF NOT EXISTS `User` (
    `User_id` INT PRIMARY KEY AUTO_INCREMENT,
    `First_name` VARCHAR(100),
    `Last_name` VARCHAR(100),
    `Email` VARCHAR(150) UNIQUE,
    `Password` VARCHAR(255),
    `Role` VARCHAR(50),
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Job_Seekers` (
    `Seekers_id` INT PRIMARY KEY AUTO_INCREMENT,
    `User_id` INT,
    `Bio` TEXT,
    `Location` VARCHAR(100),
    `Education` VARCHAR(255),
    `Skills` TEXT,
    `Experiences` TEXT,
    `Resume` VARCHAR(255),
    `Profile_completion_percentage` DECIMAL(5,2) DEFAULT 0.0,
    FOREIGN KEY (`User_id`) REFERENCES `User`(`User_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Employee` (
    `Employee_id` INT PRIMARY KEY AUTO_INCREMENT,
    `User_id` INT,
    `Company_name` VARCHAR(150),
    `Industry` VARCHAR(100),
    `Description` TEXT,
    `Website` VARCHAR(255),
    `Logo` VARCHAR(255),
    `Profile_completion_percentage` DECIMAL(5,2) DEFAULT 0.0,
    FOREIGN KEY (`User_id`) REFERENCES `User`(`User_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Jobs` (
    `Job_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Employee_id` INT,
    `Title` VARCHAR(150),
    `Description` TEXT,
    `Requirement` TEXT,
    `Salary` DECIMAL(10,2),
    `Location` VARCHAR(100),
    `Status` VARCHAR(50),
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`Employee_id`) REFERENCES `Employee`(`Employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Applications` (
    `Application_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Seekers_id` INT,
    `Job_id` INT,
    `Resume` VARCHAR(255),
    `Cover_letter` TEXT,
    `Status` VARCHAR(50),
    `Applied_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`Seekers_id`) REFERENCES `Job_Seekers`(`Seekers_id`),
    FOREIGN KEY (`Job_id`) REFERENCES `Jobs`(`Job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Interview` (
    `Interview_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Application_id` INT,
    `Interview_date` DATE,
    `Interview_time` TIME,
    `Meeting_link` VARCHAR(255),
    `Mode` VARCHAR(50),
    `Status` VARCHAR(50),
    FOREIGN KEY (`Application_id`) REFERENCES `Applications`(`Application_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Company_Review` (
    `Review_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Seekers_id` INT,
    `Employee_id` INT,
    `Review_text` TEXT,
    `Rating` INT,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`Seekers_id`) REFERENCES `Job_Seekers`(`Seekers_id`),
    FOREIGN KEY (`Employee_id`) REFERENCES `Employee`(`Employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Saved_Jobs` (
    `Saved_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Seekers_id` INT,
    `Job_id` INT,
    FOREIGN KEY (`Seekers_id`) REFERENCES `Job_Seekers`(`Seekers_id`),
    FOREIGN KEY (`Job_id`) REFERENCES `Jobs`(`Job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Job_Alerts` (
    `Alert_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Seekers_id` INT,
    `Keyword` VARCHAR(100),
    `Location` VARCHAR(100),
    `Frequency` VARCHAR(50),
    FOREIGN KEY (`Seekers_id`) REFERENCES `Job_Seekers`(`Seekers_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Notification` (
    `Notification_id` INT PRIMARY KEY AUTO_INCREMENT,
    `User_id` INT,
    `Title` VARCHAR(150),
    `Message` TEXT,
    `Is_read` BOOLEAN DEFAULT FALSE,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`User_id`) REFERENCES `User`(`User_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Messages` (
    `Message_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Sender_id` INT,
    `Receiver_id` INT,
    `Message` TEXT,
    FOREIGN KEY (`Sender_id`) REFERENCES `User`(`User_id`),
    FOREIGN KEY (`Receiver_id`) REFERENCES `User`(`User_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Subscription_Plans` (
    `Plan_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Plan_name` VARCHAR(100) NOT NULL,
    `Description` TEXT,
    `Price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `Billing_cycle` VARCHAR(30) NOT NULL DEFAULT 'monthly',
    `Max_job_posts` INT NOT NULL DEFAULT 0,
    `Features_json` JSON NULL,
    `Is_active` BOOLEAN DEFAULT TRUE,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Employer_Subscriptions` (
    `Subscription_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Employee_id` INT NOT NULL,
    `Plan_id` INT NOT NULL,
    `Start_date` DATE NOT NULL,
    `End_date` DATE,
    `Status` VARCHAR(50) NOT NULL DEFAULT 'active',
    `Auto_renew` BOOLEAN DEFAULT FALSE,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`Employee_id`) REFERENCES `Employee`(`Employee_id`),
    FOREIGN KEY (`Plan_id`) REFERENCES `Subscription_Plans`(`Plan_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Payment_History` (
    `Payment_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Subscription_id` INT,
    `Employee_id` INT NOT NULL,
    `Amount` DECIMAL(10,2) NOT NULL,
    `Currency` VARCHAR(10) NOT NULL DEFAULT 'USD',
    `Payment_method` VARCHAR(50),
    `Transaction_reference` VARCHAR(150) UNIQUE,
    `Status` VARCHAR(50) NOT NULL DEFAULT 'paid',
    `Paid_at` DATETIME,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`Subscription_id`) REFERENCES `Employer_Subscriptions`(`Subscription_id`),
    FOREIGN KEY (`Employee_id`) REFERENCES `Employee`(`Employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Job_Reports` (
    `Report_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Job_id` INT NOT NULL,
    `Reporter_user_id` INT NOT NULL,
    `Reason` VARCHAR(255) NOT NULL,
    `Details` TEXT,
    `Status` VARCHAR(50) NOT NULL DEFAULT 'pending',
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `Resolved_at` DATETIME,
    `Resolved_by_user_id` INT,
    FOREIGN KEY (`Job_id`) REFERENCES `Jobs`(`Job_id`),
    FOREIGN KEY (`Reporter_user_id`) REFERENCES `User`(`User_id`),
    FOREIGN KEY (`Resolved_by_user_id`) REFERENCES `User`(`User_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Skills_Assessments` (
    `Assessment_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Title` VARCHAR(150) NOT NULL,
    `Description` TEXT,
    `Duration_minutes` INT,
    `Total_marks` INT,
    `Is_active` BOOLEAN DEFAULT TRUE,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Assessment_Questions` (
    `Question_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Assessment_id` INT NOT NULL,
    `Question_text` TEXT NOT NULL,
    `Question_type` VARCHAR(50) NOT NULL DEFAULT 'mcq',
    `Options_json` JSON NULL,
    `Correct_answer` TEXT,
    `Marks` INT NOT NULL DEFAULT 1,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`Assessment_id`) REFERENCES `Skills_Assessments`(`Assessment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Seeker_Assessment_Attempts` (
    `Attempt_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Assessment_id` INT NOT NULL,
    `Seekers_id` INT NOT NULL,
    `Score` DECIMAL(5,2),
    `Status` VARCHAR(50) DEFAULT 'submitted',
    `Started_at` DATETIME,
    `Submitted_at` DATETIME,
    FOREIGN KEY (`Assessment_id`) REFERENCES `Skills_Assessments`(`Assessment_id`),
    FOREIGN KEY (`Seekers_id`) REFERENCES `Job_Seekers`(`Seekers_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `User_Settings` (
    `Setting_id` INT PRIMARY KEY AUTO_INCREMENT,
    `User_id` INT NOT NULL UNIQUE,
    `Language_code` VARCHAR(10) DEFAULT 'en',
    `Theme` VARCHAR(20) DEFAULT 'light',
    `Email_notifications` BOOLEAN DEFAULT TRUE,
    `In_app_notifications` BOOLEAN DEFAULT TRUE,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `Updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`User_id`) REFERENCES `User`(`User_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Email_Verification_Tokens` (
    `Token_id` INT PRIMARY KEY AUTO_INCREMENT,
    `User_id` INT NOT NULL,
    `Token` VARCHAR(255) NOT NULL UNIQUE,
    `Expires_at` DATETIME NOT NULL,
    `Is_used` BOOLEAN DEFAULT FALSE,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`User_id`) REFERENCES `User`(`User_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `User_Sessions` (
    `Session_id` INT PRIMARY KEY AUTO_INCREMENT,
    `User_id` INT NOT NULL,
    `Session_token` VARCHAR(255) NOT NULL UNIQUE,
    `User_agent` VARCHAR(255),
    `Ip_address` VARCHAR(45),
    `Expires_at` DATETIME,
    `Is_revoked` BOOLEAN DEFAULT FALSE,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`User_id`) REFERENCES `User`(`User_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Admin_Audit_Log` (
    `Audit_id` INT PRIMARY KEY AUTO_INCREMENT,
    `Admin_user_id` INT NOT NULL,
    `Action` VARCHAR(150) NOT NULL,
    `Target_type` VARCHAR(100),
    `Target_id` INT,
    `Details` TEXT,
    `Created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`Admin_user_id`) REFERENCES `User`(`User_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
  