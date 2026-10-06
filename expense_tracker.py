import tkinter as tk
from tkinter import ttk, messagebox
import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import re
import urllib.parse
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import certifi
    ca = certifi.where()
except ImportError:
    ca = None

def clean_mongo_uri(uri):
    """Encodes special characters in URI password like # or @ if unencoded."""
    if not uri or uri.startswith("mongodb://localhost") or uri.startswith("mongodb://127.0.0.1"):
        return uri
    match = re.match(r'^(mongodb(?:\+srv)?://)([^:]+):([^@]+)@(.+)$', uri)
    if match:
        prefix, user, password, rest = match.groups()
        unquoted = urllib.parse.unquote(password)
        encoded_password = urllib.parse.quote_plus(unquoted)
        return f"{prefix}{user}:{encoded_password}@{rest}"
    return uri

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Expense Tracker")
        self.root.geometry("900x600")
        self.root.configure(padx=20, pady=20)

        # Database connection
        raw_uri = os.environ.get("MONGO_URI", "mongodb+srv://srvidhyuth81_db_user:Vidhyuth%232008@cluster0.vqsqxdf.mongodb.net/?appName=Cluster0")
        mongo_uri = clean_mongo_uri(raw_uri)
        try:
            kwargs = {"serverSelectionTimeoutMS": 5000}
            if ca:
                kwargs["tlsCAFile"] = ca
            self.client = pymongo.MongoClient(mongo_uri, **kwargs)
            # Check connection
            self.client.server_info()
            self.db = self.client["expense_tracker_db"]
            self.collection = self.db["expenses"]
        except Exception as e:
            err_msg = str(e)
            if "SSL" in err_msg or "ServerSelectionTimeoutError" in err_msg or "tlsv1 alert" in err_msg:
                detailed_msg = (
                    "Could not connect to MongoDB Atlas cluster.\n\n"
                    "Common Causes & Solutions:\n"
                    "1. MongoDB Atlas IP Whitelist (Network Access):\n"
                    "   Go to MongoDB Atlas -> Network Access -> Add IP Address.\n"
                    "   Select 'Allow Access from Anywhere' (0.0.0.0/0) or add your current IP.\n\n"
                    "2. Database Credentials:\n"
                    "   Ensure your database username & password in .env are correct.\n\n"
                    f"Technical Details:\n{err_msg[:250]}"
                )
            else:
                detailed_msg = f"Could not connect to MongoDB:\n{e}"
            messagebox.showerror("Database Connection Error", detailed_msg)
            root.destroy()
            return

        # Variables
        self.date_var = tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
        self.desc_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.categories = ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Health", "Other"]
        self.selected_id = None

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Form Frame
        form_frame = tk.LabelFrame(self.root, text="Expense Entry", padx=10, pady=10)
        form_frame.pack(fill="x", pady=(0, 20))

        tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(form_frame, textvariable=self.date_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        tk.Entry(form_frame, textvariable=self.desc_var, width=30).grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(form_frame, textvariable=self.amount_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Category:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, values=self.categories, state="readonly")
        category_combo.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        category_combo.current(0)

        # Button Frame
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        tk.Button(btn_frame, text="Add Expense", command=self.add_expense, width=15, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Update Expense", command=self.update_expense, width=15, bg="#2196F3", fg="white").grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Delete Expense", command=self.delete_expense, width=15, bg="#f44336", fg="white").grid(row=0, column=2, padx=10)
        tk.Button(btn_frame, text="Clear Form", command=self.clear_form, width=15).grid(row=0, column=3, padx=10)

        # Main Content Frame (Treeview + Summary)
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill="both", expand=True)

        # Treeview for records
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        columns = ("ID", "Date", "Description", "Amount", "Category")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        
        self.tree.column("ID", width=0, stretch=tk.NO) # Hide ID column
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Description", width=250, anchor="w")
        self.tree.column("Amount", width=100, anchor="e")
        self.tree.column("Category", width=120, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Summary Frame
        self.summary_frame = tk.LabelFrame(content_frame, text="Expense Summary", padx=10, pady=10)
        self.summary_frame.pack(side="right", fill="y", ipadx=10)

        self.total_label = tk.Label(self.summary_frame, text="Total Spent: $0.00", font=("Helvetica", 12, "bold"))
        self.total_label.pack(pady=(0, 15), anchor="w")

        tk.Label(self.summary_frame, text="By Category:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))

        self.cat_summary_labels = {}
        for cat in self.categories:
            lbl = tk.Label(self.summary_frame, text=f"{cat}: $0.00")
            lbl.pack(anchor="w", pady=2)
            self.cat_summary_labels[cat] = lbl

    def load_data(self):
        # Clear existing tree data
        for row in self.tree.get_children():
            self.tree.delete(row)

        expenses = self.collection.find().sort("date", pymongo.DESCENDING)
        total_spent = 0.0
        cat_totals = {cat: 0.0 for cat in self.categories}

        for exp in expenses:
            amount = exp.get("amount", 0.0)
            self.tree.insert("", tk.END, values=(
                str(exp["_id"]),
                exp.get("date", ""),
                exp.get("description", ""),
                f"${amount:.2f}",
                exp.get("category", "")
            ))
            total_spent += amount
            cat = exp.get("category", "")
            if cat in cat_totals:
                cat_totals[cat] += amount
            else:
                cat_totals[cat] = amount

        self.update_summary(total_spent, cat_totals)

    def update_summary(self, total, cat_totals):
        self.total_label.config(text=f"Total Spent: ${total:.2f}")
        for cat, lbl in self.cat_summary_labels.items():
            amt = cat_totals.get(cat, 0.0)
            lbl.config(text=f"{cat}: ${amt:.2f}")

    def add_expense(self):
        date = self.date_var.get()
        desc = self.desc_var.get()
        amount_str = self.amount_var.get()
        category = self.category_var.get()

        if not all([date, desc, amount_str, category]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("Input Error", "Amount must be a number")
            return

        expense_data = {
            "date": date,
            "description": desc,
            "amount": amount,
            "category": category
        }
        
        self.collection.insert_one(expense_data)
        messagebox.showinfo("Success", "Expense added successfully")
        self.clear_form()
        self.load_data()

    def update_expense(self):
        if not self.selected_id:
            messagebox.showwarning("Selection Error", "Please select an expense to update")
            return

        date = self.date_var.get()
        desc = self.desc_var.get()
        amount_str = self.amount_var.get()
        category = self.category_var.get()

        if not all([date, desc, amount_str, category]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("Input Error", "Amount must be a number")
            return

        update_data = {
            "$set": {
                "date": date,
                "description": desc,
                "amount": amount,
                "category": category
            }
        }
        
        self.collection.update_one({"_id": ObjectId(self.selected_id)}, update_data)
        messagebox.showinfo("Success", "Expense updated successfully")
        self.clear_form()
        self.load_data()

    def delete_expense(self):
        if not self.selected_id:
            messagebox.showwarning("Selection Error", "Please select an expense to delete")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?")
        if confirm:
            self.collection.delete_one({"_id": ObjectId(self.selected_id)})
            messagebox.showinfo("Success", "Expense deleted successfully")
            self.clear_form()
            self.load_data()

    def clear_form(self):
        self.date_var.set(datetime.today().strftime('%Y-%m-%d'))
        self.desc_var.set("")
        self.amount_var.set("")
        self.category_var.current(0)
        self.selected_id = None
        
        # Deselect treeview items
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            self.selected_id = values[0]
            self.date_var.set(values[1])
            self.desc_var.set(values[2])
            self.amount_var.set(values[3].replace('$', '')) # Remove $ sign for editing
            self.category_var.set(values[4])

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
