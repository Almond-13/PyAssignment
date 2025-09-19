import tkinter as tk
from LAWZHIXIN import main as po
from CHANSIMYEE import GPAApp
from TRISHA import ExpenseTracker


def open_pomodoro():
    po()

def open_cgpa():
    new_win = tk.Toplevel(root)
    GPAApp(new_win)

def open_expanse():
    ExpenseTracker(root)

root = tk.Tk()
root.title("Welcome to My Toolbox")
root.geometry("800x500")
root.configure(bg="#FFE5B4")  

title = tk.Label(root, text="Welcome to Study Toolbox", font=("Helvetica", 24, "bold"), bg="#FFE5B4", fg="#C85A17")
title.pack(pady=30)


button_frame = tk.Frame(root, bg="#FFE5B4")
button_frame.pack(pady=20)

btn1 = tk.Button(button_frame, text="🍅 Pomodoro Timer ", command=open_pomodoro,
                 font=("Arial", 16), width=20, bg="white", fg="#C85A17")
btn1.grid(row=0, column=0, padx=20, pady=10)

btn2 = tk.Button(button_frame, text="🎓 GPA Calculator", command=open_cgpa,
                 font=("Arial", 16), width=20, bg="white", fg="#C85A17")
btn2.grid(row=1, column=0, padx=20, pady=10)

btn3 = tk.Button(button_frame, text="💰 Expense Tracker", command=open_expanse,
                 font=("Arial", 16), width=20, bg="white", fg="#C85A17")
btn3.grid(row=2, column=0, padx=20, pady=10)


root.mainloop()
