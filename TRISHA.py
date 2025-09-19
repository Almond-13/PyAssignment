from tkinter import *
from tkinter import ttk
import tkinter.messagebox
from datetime import datetime

class Expense:
    def __init__(self, date, name, amount, category, account, note=""):
        # Use setters for validation when initializing
        self.set_date(date)
        self.set_name(name)
        self.set_amount(amount)
        self.set_category(category)
        self.set_account(account)
        self.set_note(note)

    # --- DATE ---
    def get_date(self):
        return self._date

    def set_date(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")  # validate format
            self._date = value
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    # --- NAME ---
    def get_name(self):
        return self._name

    def set_name(self, value):
        if not value.strip():
            raise ValueError("Expense name cannot be empty")
        self._name = value.strip()

    # --- AMOUNT ---
    def get_amount(self):
        return self._amount

    def set_amount(self, value):
        try:
            val = float(value)
            if val <= 0:
                raise ValueError("Amount must be greater than 0")
            self._amount = val
        except ValueError:
            raise ValueError("Amount must be a valid number")

    # --- CATEGORY ---
    def get_category(self):
        return self._category

    def set_category(self, value):
        if not value.strip():
            raise ValueError("Category cannot be empty")
        self._category = value.strip()

    # --- ACCOUNT ---
    def get_account(self):
        return self._account

    def set_account(self, value):
        if not value.strip():
            raise ValueError("Account cannot be empty")
        self._account = value.strip()

    # --- NOTE ---
    def get_note(self):
        return self._note

    def set_note(self, value):
        self._note = value.strip()

    # --- FILE FORMAT + STR ---
    def to_file_format(self):
        return f"{self._date}|{self._name}|{self._amount}|{self._category}|{self._account}|{self._note}\n"

    def __str__(self):
        return f"[{self.__class__.__name__}] {self._date}: {self._name} - RM{self._amount:.2f}"


class FixedExpense(Expense):
    def __init__(self, date, name, amount, category, account, note=""):
        super().__init__(date, name, amount, category, account, note)

    def to_file_format(self):
        # Add a marker for "Fixed" so you know type when reloading
        return f"FIXED|{super().to_file_format()}"

    def __str__(self):
        return f"[FIXED] {self.get_date()}: {self.get_name()} - RM{self.get_amount():.2f}"


class VariableExpense(Expense):
    def __init__(self, date, name, amount, category, account, note=""):
        super().__init__(date, name, amount, category, account, note)

    def to_file_format(self):
        return f"VARIABLE|{super().to_file_format()}"

    def __str__(self):
        return f"[VARIABLE] {self.get_date()}: {self.get_name()} - RM{self.get_amount():.2f}"


class SortableTreeview(ttk.Treeview):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def make_sortable(self):
        for col in self["columns"]:
            self.heading(col, text=col, command=lambda c=col: self.sort_treeview(c, False))

    def sort_treeview(self, col, reverse):
        items = [(self.set(k, col), k) for k in self.get_children('')]
        # Try numeric (amount), then date, then text
        def try_parse_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d")
            except Exception:
                return None

        try:
            # amount column contains "RM" prefix sometimes
            items.sort(key=lambda t: float(t[0].replace("RM", "").strip()), reverse=reverse)
        except Exception:
            # try date
            dates = [try_parse_date(t[0]) for t in items]
            if all(d is not None for d in dates):
                items.sort(key=lambda t: datetime.strptime(t[0], "%Y-%m-%d"), reverse=reverse)
            else:
                items.sort(key=lambda t: t[0], reverse=reverse)

        for index, (val, k) in enumerate(items):
            self.move(k, '', index)
        self.heading(col, command=lambda: self.sort_treeview(col, not reverse))


class ExpenseTracker:
    def __init__(self, parent_window=None):
        if parent_window is None:
            self.window = Tk()
            self.is_standalone = True
        else:  
            self.window = Toplevel(parent_window)
            self.is_standalone = False
        self.window.title("Expense Tracker")
        self.file_path = "expenses.txt"
        self.budgets_file = "budgets.txt"
        self.expenses = []
        self.monthly_budgets = {}  # Store budget for each month-year like "2024-08"

        # Load existing data
        self.load_expenses()
        self.load_budgets()

        # StringVar
        self.date = StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.expense = StringVar()
        self.amount = StringVar()
        self.category = StringVar()
        self.account = StringVar()
        self.filter_year = StringVar(value=datetime.now().strftime("%Y"))
        self.filter_month = StringVar(value=datetime.now().strftime("%m"))

        # Left frame
        frame1 = Frame(self.window)
        frame1.pack(side=LEFT, anchor=N, padx=10, pady=9)

        # Expense Date
        label_date = Label(frame1, text="Date (YYYY-MM-DD):")
        label_date.grid(row=0, column=0, padx=2, pady=5, sticky=W)
        entry_date = Entry(frame1, textvariable=self.date, width=15)
        entry_date.grid(row=0, column=1, padx=2, pady=5, sticky=W)

        # Expense Name
        Label(frame1, text="Expense Name:").grid(row=1, column=0, padx=2, pady=5, sticky=W)
        Entry(frame1, textvariable=self.expense, width=20).grid(row=1, column=1, padx=2, pady=5, sticky=W)

        # Expense Amount
        label_amount = Label(frame1, text="Expense Amount:")
        label_amount.grid(row=2, column=0, padx=2, pady=5, sticky=W)
        entry_amount = Entry(frame1, textvariable=self.amount, width=20)
        entry_amount.grid(row=2, column=1, padx=2, pady=5, sticky=W)

        # Category Dropdown
        label_cat = Label(frame1, text="Category:")
        label_cat.grid(row=3, column=0, padx=2, pady=5, sticky=W)
        categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
        self.category.set("Select category")
        option = OptionMenu(frame1, self.category, *categories)
        option.grid(row=3, column=1, padx=2, pady=5, sticky=W)

        # Account Dropdown
        label_acc = Label(frame1, text="Account:")
        label_acc.grid(row=4, column=0, padx=2, pady=5, sticky=W)
        accounts = ["Cash", "Bank", "Card", "TnG", "Other"]
        self.account.set("Select account")
        option2 = OptionMenu(frame1, self.account, *accounts)
        option2.grid(row=4, column=1, padx=2, pady=5, sticky=W)

        # Note
        label_note = Label(frame1, text="Note:")
        label_note.grid(row=5, column=0, padx=2, pady=5, sticky=W)
        self.note_text = Text(frame1, height=3, width=25)
        self.note_text.grid(row=5, column=1, padx=2, pady=5, sticky=W)

        # Save Button
        save_exp = Button(frame1, text="Save Expense", command=self.save_expense, bg="green", fg="white")
        save_exp.grid(row=6, columnspan=2, pady=10)

        # Budget setting
        label_budget = Label(frame1, text="Monthly Budget:")
        label_budget.grid(row=7, column=0, sticky=W, pady=5)
        self.budget_var = StringVar()
        entry_budget = Entry(frame1, textvariable=self.budget_var, width=30)
        entry_budget.grid(row=7, column=1, sticky=W)
        budget = Button(frame1, text="Set Budget", command=self.set_budget, bg="orange", fg="black")
        budget.grid(row=7, column=2, sticky=W, pady=5)

        # Right top frame for filters
        frame2 = Frame(self.window)
        frame2.pack(side=TOP, anchor=N, padx=10, pady=10)

        label_filtyear = Label(frame2, text="Filter Year:")
        label_filtyear.grid(row=0, column=0, sticky=W, pady=5)
        entry_filtyear = Entry(frame2, textvariable=self.filter_year, width=8)
        entry_filtyear.grid(row=0, column=1, sticky=W, padx=5)

        label_filtmonth = Label(frame2, text="Filter Month:")
        label_filtmonth.grid(row=1, column=0, sticky=W, pady=5)
        months = [f"{i:02d}" for i in range(1, 13)]
        option3 = OptionMenu(frame2, self.filter_month, *months)
        option3.grid(row=1, column=1, sticky=W, padx=5)

        label_filtcat = Label(frame2, text="Filter Category:")
        label_filtcat.grid(row=2, column=0, sticky=W, pady=5)
        filter_categories = ["All", "Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
        self.filter_category = StringVar(value="All")
        option4 = OptionMenu(frame2, self.filter_category, *filter_categories)
        option4.grid(row=2, column=1, sticky=W, padx=5)

        buttons_frame = Frame(frame2)
        buttons_frame.grid(row=3, columnspan=2, pady=10)
        Button(buttons_frame, text="Summarize Expenses", command=self.summarize_expenses, bg="blue", fg="white").pack(side=LEFT, padx=5)
        Button(buttons_frame, text="Delete Selected", command=self.delete_expense, bg="red", fg="white").pack(side=LEFT, padx=5)

        # Right frame for summary
        frame3 = Frame(self.window)
        frame3.pack(side=RIGHT, anchor=N, padx=10, pady=10, fill=BOTH, expand=True)

        Label(frame3, text="Expense Summary:", font=("Arial", 12, "bold")).pack(pady=5)

        self.summary_table = SortableTreeview(
            frame3,
            columns=("Date", "Expense Name", "Amount", "Category", "Account", "Note"),
            show="headings",
            height=15
        )
        self.summary_table.make_sortable()
        self.summary_table.pack(fill=BOTH, expand=True, pady=5)
        self.summary_table.tag_configure("fixed", foreground="blue")
        self.summary_table.tag_configure("variable", foreground="green")

        for col in ("Date", "Expense Name", "Amount", "Category", "Account", "Note"):
            # make sortable (heading command will be overwritten by make_sortable but harmless)
            self.summary_table.heading(col, text=col, command=lambda c=col: self.sort_treeview(c, False))

        self.summary_table.column("Date", width=100, anchor="center")
        self.summary_table.column("Expense Name", width=150, anchor="center")
        self.summary_table.column("Amount", width=80, anchor="center")
        self.summary_table.column("Category", width=100, anchor="center")
        self.summary_table.column("Account", width=100, anchor="center")
        self.summary_table.column("Note", width=200, anchor="center")

        summary_info_frame = Frame(frame3)
        summary_info_frame.pack(fill=X, pady=5)
        self.total_label = Label(summary_info_frame, text="Total: RM0.00", font=("Arial", 12, "bold"), fg="blue")
        self.total_label.pack(side=LEFT, padx=10)
        self.budget_label = Label(summary_info_frame, text="Budget status will appear here.", fg="green")
        self.budget_label.pack(side=RIGHT, padx=10)

        self.summarize_expenses(show_popup=False)

        self.window.mainloop()

    def load_expenses(self):
        try:
            with open(self.file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split('|')
                        if parts[0] == "FIXED":
                            _, date, name, amount, category, account, *note = parts
                            note = note[0] if note else ""
                            self.expenses.append(FixedExpense(date, name, float(amount), category, account, note))
                        elif parts[0] == "VARIABLE":
                            _, date, name, amount, category, account, *note = parts
                            note = note[0] if note else ""
                            self.expenses.append(VariableExpense(date, name, float(amount), category, account, note))
                        else:
                            # backward compatibility (old lines without marker)
                            date, name, amount, category, account = parts[:5]
                            note = parts[5] if len(parts) > 5 else ""
                            self.expenses.append(Expense(date, name, float(amount), category, account, note))
        except FileNotFoundError:
            pass

    def load_budgets(self):
        try:
            with open(self.budgets_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        month_year, budget_amount = line.split('|')
                        self.monthly_budgets[month_year] = float(budget_amount)
        except FileNotFoundError:
            pass

    def save_expense(self):
        if not self.expense.get().strip():
            tkinter.messagebox.showerror("Error", "Please enter an expense name!")
            return
        if not self.amount.get().strip():
            tkinter.messagebox.showerror("Error", "Please enter an amount!")
            return
        if self.category.get() == "Select category":
            tkinter.messagebox.showerror("Error", "Please select a category!")
            return
        if self.account.get() == "Select account":
            tkinter.messagebox.showerror("Error", "Please select an account!")
            return

        try:
            amount = float(self.amount.get())
            if amount <= 0:
                tkinter.messagebox.showerror("Error", "Amount must be greater than 0!")
                return
        except ValueError:
            tkinter.messagebox.showerror("Error", "Please enter a valid number!")
            return

        try:
            datetime.strptime(self.date.get(), "%Y-%m-%d")
        except ValueError:
            tkinter.messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format!")
            return

        note = self.note_text.get("1.0", END).strip()
        # Use inheritance here:
        if self.category.get() in ["Bills"]:  # treat bills as fixed
            expense = FixedExpense(self.date.get(), self.expense.get(), amount, self.category.get(), self.account.get(), note)
        else:  # everything else is variable
            expense = VariableExpense(self.date.get(), self.expense.get(), amount, self.category.get(), self.account.get(), note)

        self.expenses.append(expense)
        self.user_expense_file(expense)

        self.summarize_expenses(show_popup=False)

        self.expense.set("")
        self.amount.set("")
        self.category.set("Select category")
        self.account.set("Select account")
        self.note_text.delete("1.0", END)

        tkinter.messagebox.showinfo("Success", "Expense added successfully!")

    def delete_expense(self):
        selected_item = self.summary_table.selection()
        if not selected_item:
            tkinter.messagebox.showwarning("No Selection", "Please select an expense to delete!")
            return

        item_values = self.summary_table.item(selected_item[0], "values")
        confirm = tkinter.messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n\n"
            f"Date: {item_values[0]}\n"
            f"Expense: {item_values[1]}\n"
            f"Amount: {item_values[2]}\n"
            f"Category: {item_values[3]}"
        )
        if not confirm:
            return

        expense_to_remove = None
        for expense in self.expenses:
            if (expense.get_date() == item_values[0] and
                expense.get_name() == item_values[1] and
                f"RM{expense.get_amount():.2f}" == item_values[2] and
                expense.get_category() == item_values[3] and
                expense.get_account() == item_values[4] and
                expense.get_note() == item_values[5]):
                expense_to_remove = expense
                break

        if expense_to_remove:
            self.expenses.remove(expense_to_remove)
            self.save_all_expenses()
            self.summarize_expenses(show_popup=False)
            tkinter.messagebox.showinfo("Success", "Expense deleted successfully!")
        else:
            tkinter.messagebox.showerror("Error", "Could not find the expense to delete!")

    def summarize_expenses(self, show_popup=True):
        for row in self.summary_table.get_children():
            self.summary_table.delete(row)

        total_expense = 0
        filtered_expenses = []
        for expense in self.expenses:
            try:
                expense_date = datetime.strptime(expense.get_date(), "%Y-%m-%d")
                if self.filter_year.get() and expense_date.year != int(self.filter_year.get()):
                    continue
                if self.filter_month.get() and expense_date.month != int(self.filter_month.get()):
                    continue
                if self.filter_category.get() != "All" and expense.get_category() != self.filter_category.get():
                    continue
                filtered_expenses.append(expense)
            except (ValueError, AttributeError):
                continue

        # sort by date string (YYYY-MM-DD) descending
        filtered_expenses.sort(key=lambda x: x.get_date(), reverse=True)
        for expense in filtered_expenses:
            # Decide tag based on type
            tag = "fixed" if isinstance(expense, FixedExpense) else "variable"
            self.summary_table.insert(
                "", "end",
                values=(expense.get_date(), expense.get_name(), f"RM{expense.get_amount():.2f}", expense.get_category(), expense.get_account(), expense.get_note()),
                tags=(tag,)   # apply color tag
            )
            total_expense += expense.get_amount()

        month_year = f"{self.filter_month.get()}/{self.filter_year.get()}"
        if self.filter_category.get() != "All":
            self.total_label.config(text=f"Total ({self.filter_category.get()}, {month_year}): RM{total_expense:.2f}")
        else:
            self.total_label.config(text=f"Total ({month_year}): RM{total_expense:.2f}")

        current_month_year = f"{self.filter_year.get()}-{self.filter_month.get()}"
        monthly_budget = self.monthly_budgets.get(current_month_year, 0)
        if monthly_budget > 0:
            remaining = monthly_budget - total_expense
            if remaining >= 0:
                self.budget_label.config(text=f"Budget: RM{monthly_budget:.2f} | Remaining: RM{remaining:.2f}", fg="green")
            else:
                self.budget_label.config(text=f"Budget: RM{monthly_budget:.2f} | Over by RM{abs(remaining):.2f}", fg="red")
        else:
            self.budget_label.config(text=f"No budget set for {month_year}", fg="gray")

        if show_popup and filtered_expenses:
            category_totals = {}
            for expense in filtered_expenses:
                category_totals[expense.get_category()] = category_totals.get(expense.get_category(), 0) + expense.get_amount()
            summary_msg = f"Expense Summary ({month_year}):\n\n"
            for cat, amt in category_totals.items():
                summary_msg += f"{cat}: RM{amt:.2f}\n"
            summary_msg += f"\nTotal: RM{total_expense:.2f}"
            tkinter.messagebox.showinfo("Category Summary", summary_msg)

    def set_budget(self):
        if not self.budget_var.get().strip():
            tkinter.messagebox.showerror("Error", "Please enter a budget amount!")
            return
        try:
            budget_amount = float(self.budget_var.get())
            if budget_amount <= 0:
                tkinter.messagebox.showerror("Error", "Budget must be greater than 0!")
                return
            current_month_year = f"{self.filter_year.get()}-{self.filter_month.get()}"
            self.monthly_budgets[current_month_year] = budget_amount
            self.save_all_budgets()
            total_expense = 0
            for expense in self.expenses:
                try:
                    expense_date = datetime.strptime(expense.get_date(), "%Y-%m-%d")
                    if expense_date.year == int(self.filter_year.get()) and expense_date.month == int(self.filter_month.get()):
                        total_expense += expense.get_amount()
                except (ValueError, AttributeError):
                    continue
            remaining = budget_amount - total_expense
            if remaining >= 0:
                self.budget_label.config(text=f"Budget: RM{budget_amount:.2f} | Remaining: RM{remaining:.2f}", fg="green")
            else:
                self.budget_label.config(text=f"Budget: RM{budget_amount:.2f} | Over by RM{abs(remaining):.2f}", fg="red")
            tkinter.messagebox.showinfo("Budget Set", f"Budget set to RM{budget_amount:.2f} for {current_month_year}")
            self.budget_var.set("")
        except ValueError:
            tkinter.messagebox.showerror("Error", "Budget must be a valid number!")

    def get_date_from_expense(self, expense_line):
        return expense_line.strip().split("|")[0]

    def user_expense_file(self, expense):
        try:
            with open(self.file_path, "r") as f:
                expenses = f.readlines()
        except:
            expenses = []
        expenses.append(expense.to_file_format())   # use class method here
        expenses.sort(key=self.get_date_from_expense)
        with open(self.file_path, "w") as f:
            f.writelines(expenses)

    def save_all_expenses(self):
        with open(self.file_path, "w") as f:
            for expense in self.expenses:
                f.write(expense.to_file_format())   # use class method here

    def save_all_budgets(self):
        with open(self.budgets_file, "w") as f:
            for month_year, budget_amount in self.monthly_budgets.items():
                f.write(f"{month_year}|{budget_amount}\n")

    def sort_treeview(self, col, reverse):
        # Get all items
        items = [(self.summary_table.set(k, col), k) for k in self.summary_table.get_children('')]

        # Try to sort as numbers first, otherwise as text
        try:
            items.sort(key=lambda t: float(t[0].replace("RM", "")), reverse=reverse)
        except ValueError:
            # fallback to date-aware sort if column holds dates
            try:
                items.sort(key=lambda t: datetime.strptime(t[0], "%Y-%m-%d"), reverse=reverse)
            except Exception:
                items.sort(key=lambda t: t[0], reverse=reverse)

        # Rearrange items in sorted order
        for index, (val, k) in enumerate(items):
            self.summary_table.move(k, '', index)

        # Reverse sort next time
        self.summary_table.heading(col, command=lambda: self.sort_treeview(col, not reverse))


if __name__ == "__main__":
   app = ExpenseTracker()