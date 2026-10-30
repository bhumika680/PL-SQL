CREATE DATABASE IF NOT EXISTS hostel_management;
USE hostel_management;

CREATE TABLE IF NOT EXISTS admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(20) NOT NULL UNIQUE,
    room_type VARCHAR(30) NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    monthly_fee DECIMAL(10,2) NOT NULL CHECK (monthly_fee >= 0)
);

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    roll_no VARCHAR(30) NOT NULL UNIQUE,
    course VARCHAR(50) NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100),
    admission_date DATE NOT NULL,
    room_id INT,
    CONSTRAINT fk_student_room FOREIGN KEY (room_id)
        REFERENCES rooms(room_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS fee_records (
    fee_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    fee_month VARCHAR(20) NOT NULL,
    total_fee DECIMAL(10,2) NOT NULL,
    fine DECIMAL(10,2) NOT NULL DEFAULT 0,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    due_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    UNIQUE KEY uq_student_month (student_id, fee_month),
    CONSTRAINT fk_fee_student FOREIGN KEY (student_id)
        REFERENCES students(student_id) ON DELETE CASCADE,
    CHECK (total_fee >= 0 AND fine >= 0 AND paid_amount >= 0)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    fee_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(30) NOT NULL,
    transaction_ref VARCHAR(100),
    CONSTRAINT fk_payment_fee FOREIGN KEY (fee_id)
        REFERENCES fee_records(fee_id) ON DELETE CASCADE,
    CHECK (amount > 0)
);

CREATE TABLE IF NOT EXISTS audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT IGNORE INTO admin(username, password_hash)
VALUES ('admin', SHA2('admin123', 256));

INSERT IGNORE INTO rooms(room_number, room_type, capacity, monthly_fee)
VALUES
('A-101', 'Double', 2, 6500.00),
('A-102', 'Triple', 3, 5500.00),
('B-201', 'Single', 1, 8500.00);

DELIMITER //

DROP FUNCTION IF EXISTS calculate_late_fine;
DROP PROCEDURE IF EXISTS record_hostel_payment;
DROP TRIGGER IF EXISTS trg_student_insert;
DROP TRIGGER IF EXISTS trg_fee_update;
DROP PROCEDURE IF EXISTS sp_list_pending_fees;

CREATE FUNCTION calculate_late_fine(
    p_due_date DATE,
    p_total_fee DECIMAL(10,2),
    p_rate DECIMAL(5,2)
)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE days_late INT DEFAULT 0;
    SET days_late = GREATEST(DATEDIFF(CURDATE(), p_due_date), 0);
    RETURN ROUND((p_total_fee * p_rate / 100) * days_late, 2);
END//

CREATE PROCEDURE record_hostel_payment(
    IN p_fee_id INT,
    IN p_amount DECIMAL(10,2),
    IN p_method VARCHAR(30),
    IN p_reference VARCHAR(100)
)
BEGIN
    DECLARE v_total DECIMAL(10,2);
    DECLARE v_fine DECIMAL(10,2);
    DECLARE v_paid DECIMAL(10,2);
    DECLARE v_due DATE;
    DECLARE v_remaining DECIMAL(10,2);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT total_fee, fine, paid_amount, due_date
      INTO v_total, v_fine, v_paid, v_due
      FROM fee_records
     WHERE fee_id = p_fee_id
     FOR UPDATE;

    IF p_amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Payment must be greater than zero';
    END IF;

    SET v_remaining = (v_total + v_fine) - v_paid;

    IF p_amount > v_remaining THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Payment exceeds outstanding balance';
    END IF;

    INSERT INTO payments(fee_id, amount, payment_method, transaction_ref)
    VALUES (p_fee_id, p_amount, p_method, p_reference);

    UPDATE fee_records
       SET paid_amount = paid_amount + p_amount,
           status = CASE
               WHEN paid_amount + p_amount >= total_fee + fine THEN 'Paid'
               ELSE 'Partial'
           END
     WHERE fee_id = p_fee_id;

    INSERT INTO audit_log(action, description)
    VALUES ('PAYMENT', CONCAT('Payment of ', p_amount, ' recorded for fee ID ', p_fee_id));

    COMMIT;
END//

CREATE PROCEDURE sp_list_pending_fees()
BEGIN
    DECLARE v_done INT DEFAULT 0;
    DECLARE v_student VARCHAR(100);
    DECLARE v_month VARCHAR(20);
    DECLARE v_balance DECIMAL(10,2);

    DECLARE pending_cursor CURSOR FOR
        SELECT s.name, f.fee_month, (f.total_fee + f.fine - f.paid_amount)
        FROM fee_records f
        JOIN students s ON s.student_id = f.student_id
        WHERE f.status <> 'Paid';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    OPEN pending_cursor;
    read_loop: LOOP
        FETCH pending_cursor INTO v_student, v_month, v_balance;
        IF v_done = 1 THEN
            LEAVE read_loop;
        END IF;
        SELECT v_student AS student_name, v_month AS fee_month,
               v_balance AS outstanding_balance;
    END LOOP;
    CLOSE pending_cursor;
END//

CREATE TRIGGER trg_student_insert
AFTER INSERT ON students
FOR EACH ROW
BEGIN
    INSERT INTO audit_log(action, description)
    VALUES ('STUDENT_INSERT', CONCAT('New student added: ', NEW.name, ', Roll: ', NEW.roll_no));
END//

CREATE TRIGGER trg_fee_update
AFTER UPDATE ON fee_records
FOR EACH ROW
BEGIN
    IF OLD.paid_amount <> NEW.paid_amount OR OLD.status <> NEW.status THEN
        INSERT INTO audit_log(action, description)
        VALUES ('FEE_UPDATE', CONCAT('Fee ID ', NEW.fee_id, ' updated. Paid amount: ', NEW.paid_amount,
                                    ', Status: ', NEW.status));
    END IF;
END//

DELIMITER ;

-- Example: create one monthly fee record for a student.
-- INSERT INTO fee_records(student_id, fee_month, total_fee, due_date)
-- VALUES (1, 'November 2026', 6500, '2026-11-10');
