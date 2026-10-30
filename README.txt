HOSTEL FEE MANAGEMENT SYSTEM
Python Tkinter + MySQL | Intermediate MCA Mini Project

SETUP
1. Install Python 3 and MySQL Server 8.0 or later.
2. Open MySQL Workbench.
3. Open database.sql and execute the complete script.
4. Open app.py in VS Code.
5. Install the connector:
      pip install mysql-connector-python
6. In app.py, replace YOUR_MYSQL_PASSWORD with your MySQL root password.
7. Run:
      python app.py

DEMO LOGIN DATA
The schema inserts a sample admin row:
  username: admin
  password: admin123

Note: This starter GUI currently opens directly to the dashboard; the admin row is included for a future login screen. For real deployment, implement a login form and verify password hashes securely.

SUGGESTED TEST FLOW
1. Add a room.
2. Add a student and assign the Room ID shown in the Rooms tab.
3. Generate a fee record for that student.
4. Record a partial payment using its Fee ID.
5. Record the remaining balance.
6. Check the fee status and dashboard totals.

IMPORTANT
- The payment procedure prevents overpayment and uses a transaction.
- Student insertion and fee updates are written to audit_log by triggers.
- calculate_late_fine() is provided as a database function. The starter app does not automatically apply fines; test it in Workbench and extend the fee screen to call it.
- This is an educational starter project. Add role-based authentication, stronger validation, backups and deployment security before real-world use.
