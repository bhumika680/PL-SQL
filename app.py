import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "cpsinghraghav1026",  # Change this
    "database": "hostel_management"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

class HostelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hostel Fee Management System")
        self.root.geometry("1200x760")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#eef2f7")

        # Apply a cleaner, modern ttk theme.
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("TFrame", background="#eef2f7")
        self.style.configure("TLabel", background="#eef2f7",
                             foreground="#243247", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background="#172b4d",
                             foreground="#ffffff", font=("Segoe UI", 21, "bold"))
        self.style.configure("Subtitle.TLabel", background="#172b4d",
                             foreground="#cbd5e1", font=("Segoe UI", 10))
        self.style.configure("TLabelframe", background="#ffffff",
                             bordercolor="#d8e0eb", relief="solid")
        self.style.configure("TLabelframe.Label", background="#ffffff",
                             foreground="#172b4d", font=("Segoe UI", 10, "bold"))
        self.style.configure("TEntry", padding=7, fieldbackground="#ffffff",
                             foreground="#243247")
        self.style.configure("TCombobox", padding=6)
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"),
                             padding=(12, 8), background="#e2e8f0",
                             foreground="#172b4d", borderwidth=0)
        self.style.map("TButton",
                       background=[("active", "#cbd5e1"), ("pressed", "#b8c5d6")])
        self.style.configure("Accent.TButton", background="#2563eb",
                             foreground="#ffffff")
        self.style.map("Accent.TButton",
                       background=[("active", "#1d4ed8"), ("pressed", "#1e40af")],
                       foreground=[("active", "#ffffff")])
        self.style.configure("Danger.TButton", background="#fee2e2",
                             foreground="#991b1b")
        self.style.map("Danger.TButton",
                       background=[("active", "#fecaca")])
        self.style.configure("TNotebook", background="#eef2f7", borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=(18, 11),
                             font=("Segoe UI", 10, "bold"),
                             background="#dfe7f1", foreground="#334155")
        self.style.map("TNotebook.Tab",
                       background=[("selected", "#ffffff"), ("active", "#eaf1fb")],
                       foreground=[("selected", "#1d4ed8")])
        self.style.configure("Treeview", background="#ffffff",
                             fieldbackground="#ffffff", foreground="#243247",
                             rowheight=30, font=("Segoe UI", 9), borderwidth=0)
        self.style.configure("Treeview.Heading", background="#e8eef6",
                             foreground="#172b4d", font=("Segoe UI", 9, "bold"),
                             padding=9, relief="flat")
        self.style.map("Treeview",
                       background=[("selected", "#dbeafe")],
                       foreground=[("selected", "#172b4d")])

        header = tk.Frame(root, bg="#172b4d", height=92)
        header.pack(fill="x")
        header.pack_propagate(False)
        title = ttk.Label(header, text="HOSTEL FEE MANAGEMENT SYSTEM",
                          style="Title.TLabel")
        title.pack(pady=(17, 2))
        subtitle = ttk.Label(header, text="HOSTEL ADMINISTRATION  •  STUDENTS  •  FEES  •  PAYMENTS",
                             style="Subtitle.TLabel")
        subtitle.pack()

        self.root.option_add("*Font", ("Segoe UI", 10))

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=8)

        self.dashboard_tab = ttk.Frame(self.tabs)
        self.students_tab = ttk.Frame(self.tabs)
        self.rooms_tab = ttk.Frame(self.tabs)
        self.fees_tab = ttk.Frame(self.tabs)
        self.payments_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.students_tab, text="Students")
        self.tabs.add(self.rooms_tab, text="Rooms")
        self.tabs.add(self.fees_tab, text="Fee Records")
        self.tabs.add(self.payments_tab, text="Payments")

        self.build_dashboard()
        self.build_students()
        self.build_rooms()
        self.build_fees()
        self.build_payments()
        self.refresh_all()

    def query(self, sql, values=(), fetch=False, commit=False):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, values)
            result = cursor.fetchall() if fetch else None
            if commit:
                conn.commit()
                return True
            return result
        except Error as exc:
            if conn:
                conn.rollback()
            messagebox.showerror("Database error", str(exc))
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def build_dashboard(self):
        ttk.Label(self.dashboard_tab, text="Hostel Overview",
                  font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(22, 12))

        summary_card = tk.Frame(self.dashboard_tab, bg="#ffffff",
                                highlightbackground="#d8e0eb", highlightthickness=1)
        summary_card.pack(fill="x", padx=24, pady=8)

        self.dashboard_text = ttk.Label(
            summary_card, text="", font=("Segoe UI", 13),
            justify="left", background="#ffffff",
            foreground="#243247", padding=24
        )
        self.dashboard_text.pack(anchor="w", fill="x")

        ttk.Button(self.dashboard_tab, text="↻  Refresh Dashboard",
                   style="Accent.TButton",
                   command=self.refresh_dashboard).pack(anchor="w", padx=24, pady=14)

    def refresh_dashboard(self):
        students = self.query("SELECT COUNT(*) FROM students", fetch=True)
        rooms = self.query("SELECT COUNT(*) FROM rooms", fetch=True)
        fees = self.query("SELECT COALESCE(SUM(total_fee + fine - paid_amount),0) FROM fee_records",
                          fetch=True)
        paid = self.query("SELECT COALESCE(SUM(paid_amount),0) FROM fee_records", fetch=True)
        if None in (students, rooms, fees, paid):
            return
        self.dashboard_text.config(
            text=f"Total Students: {students[0][0]}\n\n"
                 f"Total Rooms: {rooms[0][0]}\n\n"
                 f"Total Fees Collected: ₹{paid[0][0]:,.2f}\n\n"
                 f"Outstanding Balance: ₹{fees[0][0]:,.2f}"
        )

    def build_students(self):
        form = ttk.LabelFrame(self.students_tab, text="Student Details", padding=14)
        form.pack(fill="x", padx=18, pady=14)

        labels = ["Name", "Roll Number", "Course", "Phone", "Email", "Admission Date (YYYY-MM-DD)", "Room ID"]
        self.student_entries = {}
        for i, label in enumerate(labels):
            ttk.Label(form, text=label).grid(row=i//4*2, column=(i%4)*2, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(form, width=23)
            entry.grid(row=i//4*2+1, column=(i%4)*2, columnspan=2, sticky="ew", padx=5, pady=3)
            self.student_entries[label] = entry

        buttons = ttk.Frame(self.students_tab)
        buttons.pack(fill="x", padx=18, pady=8)
        ttk.Button(buttons, text="＋  Add Student", style="Accent.TButton", command=self.add_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Update Selected", command=self.update_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Delete Selected", style="Danger.TButton", command=self.delete_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Clear", command=self.clear_student_form).pack(side="left", padx=4)

        cols = ("ID", "Name", "Roll", "Course", "Phone", "Email", "Admission", "Room")
        self.student_tree = ttk.Treeview(self.students_tab, columns=cols, show="headings", height=12)
        for col in cols:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=115, anchor="center")
        self.student_tree.pack(fill="both", expand=True, padx=18, pady=14)
        self.student_tree.bind("<<TreeviewSelect>>", self.select_student)

    def student_values(self):
        e = self.student_entries
        name = e["Name"].get().strip()
        roll = e["Roll Number"].get().strip()
        course = e["Course"].get().strip()
        phone = e["Phone"].get().strip()
        email = e["Email"].get().strip()
        admission = e["Admission Date (YYYY-MM-DD)"].get().strip()
        room = e["Room ID"].get().strip() or None
        if not name or not roll or not course or not admission:
            messagebox.showwarning("Validation", "Name, roll number, course and admission date are required.")
            return None
        try:
            date.fromisoformat(admission)
            room = int(room) if room else None
        except ValueError:
            messagebox.showwarning("Validation", "Enter a valid date (YYYY-MM-DD) and numeric Room ID.")
            return None
        return (name, roll, course, phone, email, admission, room)

    def add_student(self):
        values = self.student_values()
        if values is None:
            return
        result = self.query("""INSERT INTO students
            (name, roll_no, course, phone, email, admission_date, room_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""", values, commit=True)
        if result is not None:
            messagebox.showinfo("Success", "Student added successfully.")
            self.clear_student_form()
            self.refresh_all()

    def selected_student_id(self):
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Select student", "Please select a student from the table.")
            return None
        return self.student_tree.item(selected[0])["values"][0]

    def select_student(self, _event=None):
        selected = self.student_tree.selection()
        if not selected:
            return
        values = self.student_tree.item(selected[0])["values"]
        keys = list(self.student_entries.keys())
        row_values = [values[1], values[2], values[3], values[4], values[5], str(values[6]), values[7] or ""]
        for key, value in zip(keys, row_values):
            self.student_entries[key].delete(0, tk.END)
            self.student_entries[key].insert(0, str(value))

    def update_student(self):
        student_id = self.selected_student_id()
        values = self.student_values()
        if student_id is None or values is None:
            return
        sql = """UPDATE students SET name=%s, roll_no=%s, course=%s, phone=%s,
                 email=%s, admission_date=%s, room_id=%s WHERE student_id=%s"""
        self.query(sql, values + (student_id,), commit=True)
        self.refresh_all()

    def delete_student(self):
        student_id = self.selected_student_id()
        if student_id is None:
            return
        if messagebox.askyesno("Confirm", "Delete this student and their fee records?"):
            self.query("DELETE FROM students WHERE student_id=%s", (student_id,), commit=True)
            self.clear_student_form()
            self.refresh_all()

    def clear_student_form(self):
        for entry in self.student_entries.values():
            entry.delete(0, tk.END)

    def build_rooms(self):
        form = ttk.LabelFrame(self.rooms_tab, text="Add Room", padding=10)
        form.pack(fill="x", padx=18, pady=14)
        self.room_number = ttk.Entry(form, width=18)
        self.room_type = ttk.Combobox(form, values=["Single", "Double", "Triple"], width=15, state="readonly")
        self.room_type.set("Double")
        self.room_capacity = ttk.Entry(form, width=10)
        self.room_fee = ttk.Entry(form, width=15)
        for i, (label, widget) in enumerate([
            ("Room Number", self.room_number), ("Room Type", self.room_type),
            ("Capacity", self.room_capacity), ("Monthly Fee", self.room_fee)
        ]):
            ttk.Label(form, text=label).grid(row=0, column=i, padx=5)
            widget.grid(row=1, column=i, padx=5, pady=5)
        ttk.Button(form, text="＋  Add Room", style="Accent.TButton", command=self.add_room).grid(row=1, column=4, padx=10)

        cols = ("Room ID", "Room Number", "Type", "Capacity", "Monthly Fee", "Occupied")
        self.room_tree = ttk.Treeview(self.rooms_tab, columns=cols, show="headings", height=16)
        for col in cols:
            self.room_tree.heading(col, text=col)
            self.room_tree.column(col, width=150, anchor="center")
        self.room_tree.pack(fill="both", expand=True, padx=18, pady=14)

    def add_room(self):
        try:
            values = (self.room_number.get().strip(), self.room_type.get(),
                      int(self.room_capacity.get()), float(self.room_fee.get()))
            if not values[0] or values[2] < 1 or values[3] < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Enter valid room details.")
            return
        self.query("""INSERT INTO rooms(room_number, room_type, capacity, monthly_fee)
                      VALUES (%s,%s,%s,%s)""", values, commit=True)
        self.refresh_all()

    def build_fees(self):
        form = ttk.LabelFrame(self.fees_tab, text="Generate Monthly Fee", padding=10)
        form.pack(fill="x", padx=18, pady=14)
        self.fee_student = ttk.Entry(form, width=12)
        self.fee_month = ttk.Entry(form, width=18)
        self.fee_amount = ttk.Entry(form, width=14)
        self.fee_due = ttk.Entry(form, width=14)
        fields = [("Student ID", self.fee_student), ("Month", self.fee_month),
                  ("Fee Amount", self.fee_amount), ("Due Date YYYY-MM-DD", self.fee_due)]
        for i, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=i, padx=5)
            widget.grid(row=1, column=i, padx=5, pady=5)
        ttk.Button(form, text="Generate Fee", style="Accent.TButton", command=self.generate_fee).grid(row=1, column=4, padx=8)

        cols = ("Fee ID", "Student ID", "Student", "Month", "Fee", "Fine", "Paid", "Balance", "Status", "Due Date")
        self.fee_tree = ttk.Treeview(self.fees_tab, columns=cols, show="headings", height=15)
        for col in cols:
            self.fee_tree.heading(col, text=col)
            self.fee_tree.column(col, width=105, anchor="center")
        self.fee_tree.pack(fill="both", expand=True, padx=18, pady=14)

    def generate_fee(self):
        try:
            student_id = int(self.fee_student.get())
            month = self.fee_month.get().strip()
            amount = float(self.fee_amount.get())
            due = self.fee_due.get().strip()
            date.fromisoformat(due)
            if not month or amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Enter a valid student ID, month, positive fee and due date.")
            return
        self.query("""INSERT INTO fee_records(student_id, fee_month, total_fee, due_date)
                      VALUES (%s,%s,%s,%s)""", (student_id, month, amount, due), commit=True)
        self.refresh_all()

    def build_payments(self):
        form = ttk.LabelFrame(self.payments_tab, text="Record Payment", padding=10)
        form.pack(fill="x", padx=18, pady=14)
        self.pay_fee_id = ttk.Entry(form, width=12)
        self.pay_amount = ttk.Entry(form, width=15)
        self.pay_method = ttk.Combobox(form, values=["Cash", "UPI", "Card", "Bank Transfer"],
                                       width=18, state="readonly")
        self.pay_method.set("UPI")
        self.pay_ref = ttk.Entry(form, width=22)
        fields = [("Fee ID", self.pay_fee_id), ("Amount", self.pay_amount),
                  ("Method", self.pay_method), ("Reference", self.pay_ref)]
        for i, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=i, padx=5)
            widget.grid(row=1, column=i, padx=5, pady=5)
        ttk.Button(form, text="Submit Payment", style="Accent.TButton", command=self.record_payment).grid(row=1, column=4, padx=8)

        cols = ("Payment ID", "Fee ID", "Amount", "Date", "Method", "Reference")
        self.payment_tree = ttk.Treeview(self.payments_tab, columns=cols, show="headings", height=16)
        for col in cols:
            self.payment_tree.heading(col, text=col)
            self.payment_tree.column(col, width=160, anchor="center")
        self.payment_tree.pack(fill="both", expand=True, padx=18, pady=14)

    def record_payment(self):
        try:
            fee_id = int(self.pay_fee_id.get())
            amount = float(self.pay_amount.get())
            method = self.pay_method.get()
            reference = self.pay_ref.get().strip() or None
            if amount <= 0 or not method:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Enter a valid fee ID and positive payment amount.")
            return
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.callproc("record_hostel_payment", (fee_id, amount, method, reference))
            conn.commit()
            messagebox.showinfo("Success", "Payment recorded successfully.")
            self.refresh_all()
        except Error as exc:
            if conn:
                conn.rollback()
            messagebox.showerror("Payment failed", str(exc))
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def refresh_students(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        rows = self.query("""SELECT student_id, name, roll_no, course, phone, email,
                                    admission_date, room_id FROM students ORDER BY student_id""", fetch=True)
        for row in rows or []:
            self.student_tree.insert("", tk.END, values=row)

    def refresh_rooms(self):
        for item in self.room_tree.get_children():
            self.room_tree.delete(item)
        rows = self.query("""SELECT r.room_id, r.room_number, r.room_type, r.capacity,
                                    r.monthly_fee, COUNT(s.student_id)
                             FROM rooms r LEFT JOIN students s ON r.room_id=s.room_id
                             GROUP BY r.room_id ORDER BY r.room_number""", fetch=True)
        for row in rows or []:
            self.room_tree.insert("", tk.END, values=row)

    def refresh_fees(self):
        for item in self.fee_tree.get_children():
            self.fee_tree.delete(item)
        rows = self.query("""SELECT f.fee_id, f.student_id, s.name, f.fee_month,
                                    f.total_fee, f.fine, f.paid_amount,
                                    (f.total_fee+f.fine-f.paid_amount), f.status, f.due_date
                             FROM fee_records f JOIN students s ON f.student_id=s.student_id
                             ORDER BY f.fee_id DESC""", fetch=True)
        for row in rows or []:
            self.fee_tree.insert("", tk.END, values=row)

    def refresh_payments(self):
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        rows = self.query("""SELECT payment_id, fee_id, amount, payment_date,
                                    payment_method, transaction_ref
                             FROM payments ORDER BY payment_id DESC""", fetch=True)
        for row in rows or []:
            self.payment_tree.insert("", tk.END, values=row)

    def refresh_all(self):
        self.refresh_students()
        self.refresh_rooms()
        self.refresh_fees()
        self.refresh_payments()
        self.refresh_dashboard()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = HostelApp(root)
        root.mainloop()
    except Error as exc:
        messagebox.showerror("Connection error", f"Could not connect to MySQL:\n{exc}")
