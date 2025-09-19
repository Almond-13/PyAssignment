import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Default grade-to-GPA mapping (used if no settings file exists)
DEFAULT_GRADE_TO_GPA = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D": 1.0, "F": 0.0
}

# Local JSON files for storing GPA records and grade settings
DATA_FILE = "gpa_records.json"
SETTINGS_FILE = "gpa_settings.json"

# Load saved GPA records from JSON file
def load_records():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load records: {e}")
        return {}

# Save GPA records to JSON file
def save_records(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save records: {e}")

# Load grade-to-GPA settings from JSON file
def load_grade_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_GRADE_TO_GPA.copy()
    return DEFAULT_GRADE_TO_GPA.copy()

# Save grade-to-GPA settings to JSON file
def save_grade_settings(grade_to_gpa):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(grade_to_gpa, f, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save grade settings: {e}")

# Base window class providing common utilities
class BaseWindow:
    def center_window(self, win):
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        x = (win.winfo_screenwidth() - w) // 2
        y = (win.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def add_button(self, parent, text, command, col, width=15):
        btn = tk.Button(parent, text=text, command=command, width=width)
        btn.grid(row=0, column=col, padx=5)
        return btn

class GradeSettingsWindow(BaseWindow):
    def __init__(self, parent, grade_to_gpa, callback):
        super().__init__()
        self.parent = parent
        self.grade_to_gpa = grade_to_gpa.copy()
        self.callback = callback
        
        self.win = tk.Toplevel(parent)
        self.win.title("Grade Settings")
        self.win.geometry("400x500")
        self.center_window(self.win)
        self.win.grab_set()  
        
        self.build_ui()
        
    def build_ui(self):
        tk.Label(self.win, text="Customize Grade Scale", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(self.win, text="Set your custom grades and corresponding GPA values", 
                font=("Arial", 10)).pack(pady=5)
        
        # Scrollable frame (with canvas + scrollbar)
        container = tk.Frame(self.win)
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.grades_frame = tk.Frame(canvas)
        
        self.grades_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.grades_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Table header for grade settings
        header_frame = tk.Frame(self.grades_frame)
        header_frame.pack(fill="x", pady=5)
        tk.Label(header_frame, text="Grade", width=10, font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        tk.Label(header_frame, text="GPA Value", width=10, font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5)
        tk.Label(header_frame, text="Action", width=10, font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
        
        # Store entry widgets for grades and GPA values
        self.entries = []
        self.refresh_entries()
        
        button_frame = tk.Frame(self.win)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Add Grade", command=self.add_grade).pack(side="left", padx=5)
        tk.Button(button_frame, text="Reset to Default", command=self.reset_to_default).pack(side="left", padx=5)
        tk.Button(button_frame, text="Save", command=self.save_settings).pack(side="right", padx=5)
        tk.Button(button_frame, text="Cancel", command=self.win.destroy).pack(side="right", padx=5)
    
    def refresh_entries(self):
        # Clear existing grade rows (except header)
        for widget in self.grades_frame.winfo_children():
            if widget != self.grades_frame.winfo_children()[0]:  # Keep table header
                widget.destroy()
        
        # Reset entries list
        self.entries = []
        
        sorted_grades = sorted(self.grade_to_gpa.items(), key=lambda x: x[1], reverse=True)
        
        # Rebuild UI rows for each grade
        for i, (grade, gpa) in enumerate(sorted_grades, start=1):
            frame = tk.Frame(self.grades_frame)
            frame.pack(fill="x", pady=2)
            # Grade input box
            grade_entry = tk.Entry(frame, width=10)
            grade_entry.insert(0, grade)
            grade_entry.grid(row=0, column=0, padx=14)
            # GPA value input box
            gpa_entry = tk.Entry(frame, width=10)
            gpa_entry.insert(0, str(gpa))
            gpa_entry.grid(row=0, column=1, padx=21)
            # Delete button for this grade row
            delete_btn = tk.Button(frame, text="Delete", width=8,
                                 command=lambda idx=len(self.entries): self.delete_grade(idx))
            delete_btn.grid(row=0, column=2, padx=12)
            # Save references for later use
            self.entries.append((grade_entry, gpa_entry, delete_btn))
    
    def add_grade(self):
        grade = simpledialog.askstring("Add Grade", "Enter grade name (e.g., A+, B, C-):")
        if not grade:
            return
            
        gpa_str = simpledialog.askstring("Add Grade", f"Enter GPA value for {grade}:")
        if not gpa_str:
            return
            
        try:
            gpa = float(gpa_str)
            if gpa < 0 or gpa > 4.0:
                self.show_error("GPA value should be between 0.0 and 4.0")
                return
            # Save the new grade (converted to uppercase for consistency)
            self.grade_to_gpa[grade.upper()] = gpa
            
            self.refresh_entries()
        except ValueError:
            self.show_error("Please enter a valid number for GPA value")
    
    def delete_grade(self, idx):
        # Prevent deletion if only one grade remains
        if len(self.entries) <= 1:
            self.show_error("At least one grade must remain")
            return
        
        # Get the grade name from the selected entry
        grade_entry, _, _ = self.entries[idx]
        grade = grade_entry.get().strip().upper()
        
        if messagebox.askyesno("Delete Grade", f"Delete grade {grade}?"):
            if grade in self.grade_to_gpa:
                del self.grade_to_gpa[grade]
            self.refresh_entries()
    
    def reset_to_default(self):
        if messagebox.askyesno("Reset", "Reset to default grade scale?"):
            # Restore grade-to-GPA mapping to default values
            self.grade_to_gpa = DEFAULT_GRADE_TO_GPA.copy()
            self.refresh_entries()
    
    def save_settings(self):
        # Validate and save the current grade-to-GPA mappings
        new_grade_to_gpa = {}
        
        for grade_entry, gpa_entry, _ in self.entries:
            grade = grade_entry.get().strip().upper()
            gpa_str = gpa_entry.get().strip()
            
            if not grade:
                self.show_error("Grade name cannot be empty")
                return
                
            try:
                gpa = float(gpa_str)
                if gpa < 0 or gpa > 4.0:
                    self.show_error(f"GPA value for {grade} should be between 0.0 and 4.0")
                    return
                new_grade_to_gpa[grade] = gpa
            except ValueError:
                self.show_error(f"Invalid GPA value for {grade}: {gpa_str}")
                return
        if not new_grade_to_gpa:
            self.show_error("At least one grade must be defined")
            return
        
        # Save the settings to JSON file
        save_grade_settings(new_grade_to_gpa)
        # Pass the updated settings back to the main application
        self.callback(new_grade_to_gpa)
        self.win.destroy()

# Main application class: GPA Records List Interface
class GPAApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("500x300")
        self.root.title("GPA Records")
        self.records = load_records()  
        self.grade_to_gpa = load_grade_settings()  
        self.calculators = {}  # Dictionary to keep track of open GPA calculator windows
        self.build_main_ui()  

    def get_records(self):
        return self.records

    def set_records(self, new_records):
        if isinstance(new_records, dict):
            self.records = new_records
            self.save_and_refresh()
        else:
            messagebox.showerror("Error", "Records must be a dictionary")

    def get_grade_to_gpa(self):
        return self.grade_to_gpa

    def set_grade_to_gpa(self, new_scale):
        if isinstance(new_scale, dict):
            self.grade_to_gpa = new_scale
            for calc in self.calculators.values():
                calc.grade_to_gpa = new_scale
                calc.refresh_grade_options()
                calc.update_gpa_display()
        else:
            messagebox.showerror("Error", "Grade scale must be a dictionary")

    def build_main_ui(self):
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Grade Scale", command=self.open_grade_settings)
        # Frame for the header (title + new record button)
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(padx=10, pady=10)

        tk.Label(self.list_frame, text="GPA Records", font=("Arial", 14)).grid(row=0, column=0, sticky="w")
        tk.Button(self.list_frame, text="➕ New Record", command=self.new_record).grid(row=0, column=1, sticky="e")

        # Scrollable area for displaying GPA records
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.records_frame = tk.Frame(canvas)

        # Update scroll region when records frame changes
        self.records_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.records_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display all saved GPA records in the scrollable frame
        self.display_records()
    
    def open_grade_settings(self):
        # Open the grade settings window
        # When user saves settings, update the grade scale in app and refresh all open calculator windows
        def on_settings_saved(new_grade_to_gpa):
            self.grade_to_gpa = new_grade_to_gpa
            # Refresh all open calculator windows with new grade scale
            for calc in self.calculators.values():
                calc.grade_to_gpa = new_grade_to_gpa
                calc.refresh_grade_options()
                calc.update_gpa_display()
        
        GradeSettingsWindow(self.root, self.grade_to_gpa, on_settings_saved)

    def display_records(self):
        # Clear old record widgets before redisplaying
        for widget in self.records_frame.winfo_children():
            widget.destroy()

        # Display each saved GPA record
        for idx, (key, value) in enumerate(sorted(self.records.items(), key=lambda x: int(x[0]))):
            name = value['name']
            gpa = value['gpa']
            # Show record information and action buttons
            tk.Label(self.records_frame, text=f"{key}. {name} (GPA: {gpa:.2f})", width=30, anchor="w").grid(row=idx, column=0)
            tk.Button(self.records_frame, text="Open", width=8, command=lambda k=key: self.open_calculator(k)).grid(row=idx, column=1, padx=5, pady=3)
            tk.Button(self.records_frame, text="Rename", width=8, command=lambda k=key: self.rename_record(k)).grid(row=idx, column=2, padx=5, pady=3)
            tk.Button(self.records_frame, text="Delete", width=8, command=lambda k=key: self.delete_record(k)).grid(row=idx, column=3, padx=5, pady=3)

    def new_record(self):
        # Create a new record with the next available ID
        new_id = str(max([int(k) for k in self.records.keys()], default=0) + 1)
        self.open_calculator(new_id, is_new=True)

    def open_calculator(self, key, is_new=False):
        # Open a calculator window for the given record
        if key in self.calculators:
            return
        self.calculators[key] = CalculatorWindow(self, key, is_new=is_new)

    def close_calculator(self, key):
        # Close and remove a calculator window
        if key in self.calculators:
            self.calculators[key].win.destroy()
            del self.calculators[key]

    def rename_record(self, key):
        # Prompt user for a new name and update the record
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=self.records[key]['name'])
        if new_name:
            self.records[key]['name'] = new_name
            self.save_and_refresh()

    def delete_record(self, key):
        # Confirm and delete the selected record
        if messagebox.askyesno("Delete", f"Are you sure to delete record '{self.records[key]['name']}'?"):
            self.records.pop(key)
            self.close_calculator(key)
            self.save_and_refresh()

    def update_record(self, key, courses, gpa):
        # Update courses and GPA for the record
        self.records[key] = self.records.get(key, {'name': f"Record {key}"})
        self.records[key]['courses'] = courses
        self.records[key]['gpa'] = gpa
        self.save_and_refresh()

    def save_and_refresh(self):
        # Save records to file and refresh the list display
        save_records(self.records)
        self.display_records()

# GPA Calculator Window
class CalculatorWindow(BaseWindow):
    def __init__(self, app, key, is_new=False):
        super().__init__()
        self.app = app
        self.key = key
        self.is_new = is_new
        self.grade_to_gpa = app.grade_to_gpa  # Use application's grade-to-GPA settings

        # Load record data (create a new one if not exists)
        if key not in self.app.records:
            self.data = {'name': f"Record {key}", 'courses': [], 'gpa': 0.0}
        else:
            self.data = self.app.records[key]

        # Create GPA calculation window
        self.win = tk.Toplevel()
        self.win.title(self.data['name'])
        self.win.geometry("1000x150")
        self.center_window(self.win)
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)

        self.entries = []
        self.build_ui()

    def build_ui(self):
        # Use Canvas + Scrollbar to wrap entry_frame for scrolling
        entry_canvas = tk.Canvas(self.win, height=200)
        scrollbar = tk.Scrollbar(self.win, orient="vertical", command=entry_canvas.yview)
        self.entry_frame = tk.Frame(entry_canvas)

        self.entry_frame.bind(
            "<Configure>", lambda e: entry_canvas.configure(scrollregion=entry_canvas.bbox("all"))
        )

        entry_canvas.create_window((0, 0), window=self.entry_frame, anchor="nw")
        entry_canvas.configure(yscrollcommand=scrollbar.set)

        entry_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(self.entry_frame, text="Course Grade", 
                width=20, font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=(5, 2))
        tk.Label(self.entry_frame, text="Credit Hours", width=25, font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=(5, 2))

        # Load existing courses or default one row
        for i, (grade, credit) in enumerate(self.data.get('courses', []), start=1):
            self.add_row(grade, credit)

        if not self.entries:
            self.add_row()

        # Function button area
        button_frame = tk.Frame(self.win)
        button_frame.pack(pady=10)
        self.add_button(button_frame, "Add Course", self.add_row, 0)
        self.add_button(button_frame, "Remove Last", self.remove_row, 1)
        self.add_button(button_frame, "Save & Calculate GPA", self.save_and_calc, 2, width=20)
        self.add_button(button_frame, "Show Chart", self.show_chart, 3)

        # GPA display area
        self.result_label = tk.Label(self.win, text="", font=("Arial", 12))
        self.result_label.pack(pady=5)

        self.update_gpa_display()
    
    
    # Refresh all dropdown options (called when level settings change)
    def refresh_grade_options(self):
        sorted_grades = sorted(self.grade_to_gpa.keys(), key=lambda x: self.grade_to_gpa[x], reverse=True)
        
        for grade_combobox, _ in self.entries:
            current_value = grade_combobox.get()
            grade_combobox['values'] = sorted_grades
            
            # Reset to first option if current value is invalid
            if current_value not in sorted_grades and sorted_grades:
                grade_combobox.set(sorted_grades[0])

    def on_close(self):
        self.app.close_calculator(self.key)

    def add_row(self, grade="", credit=""):
        row = len(self.entries)+1
        
        # Use dropdown (combobox) instead of text input for grade selection
        grade_combobox = ttk.Combobox(self.entry_frame, width=15, state="readonly")
        
        # Sort grade options by GPA value (descending)
        sorted_grades = sorted(self.grade_to_gpa.keys(), key=lambda x: self.grade_to_gpa[x], reverse=True)
        grade_combobox['values'] = sorted_grades
        
        # Set default selection
        if grade and grade in self.grade_to_gpa:
            grade_combobox.set(grade)  
        elif sorted_grades:
            grade_combobox.set(sorted_grades[0])  # Default to highest grade
            
        grade_combobox.grid(row=row, column=0, padx=5, pady=2)
        
        credit_entry = tk.Entry(self.entry_frame, width=25)
        credit_entry.insert(0, credit)
        credit_entry.grid(row=row, column=1, padx=5, pady=2)
        
        self.entries.append((grade_combobox, credit_entry))
        credit_entry.focus_set()  # Auto-focus on credit input

    def remove_row(self):
        if self.entries:
            grade_combobox, credit_entry = self.entries.pop()
            grade_combobox.destroy()
            credit_entry.destroy()
    
    # Save all course data, validate inputs, and calculate GPA
    def save_and_calc(self):
        total_points = 0
        total_credits = 0
        courses = []

        for grade_combobox, credit_entry in self.entries:
            grade = grade_combobox.get().strip().upper()
            credit = credit_entry.get().strip()

            # Skip empty rows (no credit hours entered)
            if not credit:
                continue

            # Grade is selected from dropdown, should always be valid
            if grade not in self.grade_to_gpa:
                # This should not happen, but check for safety
                available_grades = ', '.join(sorted(self.grade_to_gpa.keys(), key=lambda x: self.grade_to_gpa[x], reverse=True))
                self.show_error(f"Invalid grade: {grade}\nAvailable grades: {available_grades}")
                return

            # Validate credit hours input
            try:
                credit = float(credit)
                if credit <= 0:
                    self.show_error(f"Credit hours must be greater than 0: {credit}")
                    return
            except ValueError:
                self.show_error(f"Invalid credit hours: {credit}\nPlease enter a valid number.")
                return

            total_points += self.grade_to_gpa[grade] * credit
            total_credits += credit
            courses.append((grade, credit))

        if total_credits == 0:
            self.show_error("Please enter at least one course with valid credit hours.")
            return

        gpa = total_points / total_credits

        # Initialize record on first save
        if self.is_new:
            self.app.records[self.key] = {'name': self.data['name'], 'courses': [], 'gpa': 0.0}
            self.is_new = False

        self.app.update_record(self.key, courses, gpa)
        self.update_gpa_display()

    def update_gpa_display(self):
        gpa = self.app.records.get(self.key, {}).get('gpa', 0.0)
        color = "green" if gpa >= 3.0 else "red"
        self.result_label.config(text=f"Your GPA is: {gpa:.2f}", fg=color)

    def show_chart(self):
        all_courses = self.app.records.get(self.key, {}).get('courses', [])
        valid_courses = [(g, c) for g, c in all_courses if g in self.grade_to_gpa and isinstance(c, (int, float))]
        if not valid_courses:
            self.show_error("No valid courses with valid credit hours to show chart.")
            return

        # Calculate total credits for each grade
        grade_credits = {}
        for grade, credit in valid_courses:
            if grade in grade_credits:
                grade_credits[grade] += credit
            else:
                grade_credits[grade] = credit

        grades = list(grade_credits.keys())
        credits = list(grade_credits.values())

        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = plt.cm.Set3(range(len(grades)))  # Different colors for each grade
        
        wedges, texts, autotexts = ax.pie(credits, labels=grades, colors=colors, autopct='%1.1f%%', startangle=90)
        
        # Improve label style
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        ax.set_title("Grade Distribution (Credit Hours)", fontsize=14, fontweight='bold')
        
        legend_labels = [f'{grade}: {credit:.1f} credits' for grade, credit in zip(grades, credits)]
        ax.legend(wedges, legend_labels, title="Grades", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        chart_win = tk.Toplevel(self.win)
        chart_win.title("Grade Distribution Chart")
        chart_win.geometry("900x600") 
        canvas = FigureCanvasTkAgg(fig, master=chart_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = GPAApp(root)
    root.mainloop()