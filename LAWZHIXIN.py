import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import json
import os


class Timer:
#Initialization(Variables/Constructors)
    def __init__(self):
        self.CurrentTime =0
        self.OriginalTime =0
        self.isRunning = False
        self.TimerThread = None
        self.StartTime = None

#GETTER and SETTER
        
    def get_CurrentTime(self):
        return self.CurrentTime
    def set_CurrentTime(self, value):
        if value < 0:
            self.CurrentTime = 0
        else:
            self.CurrentTime = value

    def get_OriginalTime(self):
        return self.OriginalTime
    def set_OriginalTime(self, value):
        if value <= 0:
            raise ValueError("Timer duration must be positive")
        self.OriginalTime = value

            
#The Format Of Time like 00:00
    def FormatTime(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{int(mins):02d}:{int(secs):02d}"

#Set Time（Set the time to countdown)
    def SetTime(self, seconds):
        self.CurrentTime = seconds
        self.OriginalTime = seconds

#Start Time(Start the countdown)
    def Start(self):
        if not self.isRunning and self.CurrentTime > 0:
            self.isRunning = True
            self.StartTime = datetime.now()
            self.TimerThread = threading.Thread(target=self.RunTimer)
            self.TimerThread.daemon = True
            self.TimerThread.start()

#Stop Time(Pause countdown function)
    def Pause(self):
        if self.isRunning:
            self.isRunning = False

#Reset Time(Reset the countdown to original time--25:00--)
    def Reset(self):
        self.isRunning = False
        self.CurrentTime = self.OriginalTime

#Run Timer(The countdown function)
    def RunTimer(self):
        while self.isRunning and self.CurrentTime > 0:
            time.sleep(1)
            #stop 1 seconds deducte 1 CurrentTime
            if self.isRunning:
                self.CurrentTime -= 1
                #show the GUI of the Timer immediately
                self.OnTick()
        #If the time is countdown to 0, call the OnTimerFinished function
        if self.CurrentTime == 0 and self.isRunning:
            self.OnTimerFinished()

#Do nothing because OnTick And On TimerFinished mean it would nothing happen in here
    def OnTick(self):
        pass
    def OnTimerFinished(self):
        pass

#=================================================================================================
class SessionManager:

#Create a tempelary records in session
    def __init__(self, RecordsFile = "SessionRecords.json"):
        self.RecordsFile = RecordsFile
        self.SessionRecords = []
        #Check History about the session of recorded
        self.LoadRecords()

#Add a new record
    def AddRecords(self, record):
        self.SessionRecords.append(record)
        self.SaveRecords()

#Save a new record
    def SaveRecords(self):
        try:
            with open(self.RecordsFile, 'w') as f:
                json.dump(self.SessionRecords, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save records: {str(e)}")

    def LoadRecords(self):
        try:
            if os.path.exists(self.RecordsFile):
                #open file for read
                with open (self.RecordsFile,'r') as f:
                    self.SessionRecords =json.load(f)
        #Ensure when open is smooth
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load records: {str(e)}")
            self.SessionRecords = []

#Clear all the records
    def ClearRecords(self):
        self.SessionRecords=[]
        self.SaveRecords()
#================================================================================
#Inheritance of Timer
class PomodoroTimer(Timer):
    def __init__(self,root):
        super().__init__() #Call the Timer Construction
        self.root =root # root is GUI
        self.root.title("My Study Tools Box--Pomodoro Timer")
        self.root.geometry("600x700")
        self.root.resizable(True, True)

        #Basic Timer Setting
        self.WorkTime =25*60
        self.ShortBreak =5*60
        self.LongBreak =15*60
        self.SessionsBreak =4

        #Pomodoro Status
        self.isBreak =False
        self.SessionCount =0

        #Save the all session and record in json file
        self.sessionsManager= SessionManager ("PomodoroRecord.json")
        self.SetTime(self.WorkTime)
        self.soundEnabled = tk.BooleanVar(value=True)
        self.popupEnabled = tk.BooleanVar(value=True)

        self.design()
        self.UpdateDisplay()

        #GUI design
    def design(self):
        notebook= ttk.Notebook(self.root) #Notebook is like Create Tab
        notebook.pack(fill="both", expand=True, pady=10)
        self.TimerFrame = ttk.Frame(notebook, padding="20")
        notebook.add(self.TimerFrame, text="Timer")
        self.RecordsFrame = ttk.Frame(notebook, padding="20")
        notebook.add(self.RecordsFrame, text="Records")
        self.SetupTimerTab()
        self.SetupRecordsTab()

    def SetupTimerTab(self):
        #Title
        self.titleLabel =ttk.Label(self.TimerFrame, text="~WORK SESSION~", font=("Arial", 16, "bold"))
        self.titleLabel.grid(row=0, column=0, columnspan=3, pady=(0,20))    

        self.timeLabel =ttk.Label(self.TimerFrame, text="25:00", font=("Arial", 48, "bold"), foreground="red")
        self.timeLabel.grid(row=1, column=0, columnspan=3, pady=(0,20))

        infoFrame= ttk.Frame(self.TimerFrame)
        infoFrame.grid(row=2, column=0, columnspan=3, pady=(0,20))
            
        #Session
        self.sessionLabel= ttk.Label(infoFrame, text="Session: 0", font=("Arial",12))
        self.sessionLabel.grid(row=0, column=0, padx=(0,20))
        self.TotalTimeLabel= ttk.Label(infoFrame, text="Total Time: 0hours 0min",font=("Arial",12))
        self.TotalTimeLabel.grid(row=0, column=1)
        
        #Button
        ButtonFrame= ttk.Frame(self.TimerFrame)
        ButtonFrame.grid(row=3, column=0, columnspan=3, pady=(0,20))

        self.Startbtn= ttk.Button(ButtonFrame, text="Start", command= self.StartTimer, width=10)
        self.Startbtn.grid(row=0, column=0, padx=(0,10))
        self.Pausebtn= ttk.Button(ButtonFrame, text="Pause", command= self.PauseTimer, width=10)
        self.Pausebtn.grid(row=0, column=1, padx=(0,10))
        self.Resetbtn= ttk.Button(ButtonFrame, text="Reset", command= self.ResetTimer, width=10)
        self.Resetbtn.grid(row=0, column=2, padx=(0,10))
        self.Skipbtn= ttk.Button(ButtonFrame, text="Skip", command= self.SkipTimer, width=10)
        self.Skipbtn.grid(row=0, column=3)

        #Progress Bar
        self.Progress= ttk.Progressbar(self.TimerFrame, length=400, mode='determinate')
        self.Progress.grid(row=4, column=0, columnspan=3, padx=(0,20), sticky=(tk.W, tk.E))

        #Choice of Time
        ChooseFrame= ttk.LabelFrame(self.TimerFrame, text="Choice Of Time", padding="10")
        ChooseFrame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0,20))

        customFrame = ttk.Frame(ChooseFrame)
        customFrame.grid(row=2, column=0, columnspan=3, pady=(15, 5), sticky=(tk.W, tk.E))
        
        ttk.Label(customFrame, text="Custom Time (minutes):").grid(row=0, column=0, padx=(0,10))
        
        # Entry for custom minutes input
        self.customTimeEntry = ttk.Entry(customFrame, width=10)
        self.customTimeEntry.grid(row=0, column=1, padx=(0,10))
        
        # Button to set custom time
        ttk.Button(customFrame, text="Set Custom Time", 
                  command=self.setCustomTime, width=15).grid(row=0, column=2)
        
        # Bind Enter key to set custom time
        self.customTimeEntry.bind('<Return>', lambda event: self.setCustomTime())


    #=================================================================================================
    #Record Tab GUI
    def SetupRecordsTab(self):
        headerFrame=ttk.Frame(self.RecordsFrame)
        headerFrame.pack(fill="x", pady=(0,10))

        ttk.Label(headerFrame, text="Session Records", font=("Arial", 14, "bold")).pack(side="left")
        btnFrame=ttk.Frame(headerFrame)
        btnFrame.pack(side="right")
        ttk.Button(btnFrame, text="Clear All", command=self.ClearRecords).pack(side="left", padx=(0,5))
        ttk.Button(btnFrame, text="Refresh", command=self.RefreshRecords).pack(side="left")

        columns=("Date", "Type", "Duration", "Completed", "Start Time", "End Time")
        self.RecordsTree=ttk.Treeview(self.RecordsFrame, columns=columns, show="headings", height=15)
        for col in columns:
            self.RecordsTree.heading(col, text=col)
            self.RecordsTree.column(col, width=100)

        #Scrollbar
        scrollbar= ttk.Scrollbar(self.RecordsFrame, orient="vertical", command=self.RecordsTree.yview)
        self.RecordsTree.configure(yscrollcommand=scrollbar.set)
        self.RecordsTree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        #Summary Record (To record the session number and the total time)
        SummaryFrame= ttk.LabelFrame(self.RecordsFrame, text="Today's Summary", padding="10")
        SummaryFrame.pack(fill="x", pady=(10,0))
        self.SummaryLabel= ttk.Label(SummaryFrame, text="", font=("Arial",10))
        self.SummaryLabel.pack()
        self.RefreshRecords()

    #===================================================================================
    

    def setCustomTime(self):
        if self.isRunning:
            messagebox.showwarning("Timer Running", "Please pause or stop the timer before setting a new time.")
            return
            
        try:
            # Get the input value
            inputValue = self.customTimeEntry.get().strip()
            
            # Check if input is empty
            if not inputValue:
                messagebox.showwarning("Invalid Input", "Please enter a number of minutes.")
                return
            
            # Convert to integer
            minutes = int(inputValue)
            
            # Validate the range (between 1 and 999 minutes)
            if minutes <= 0:
                messagebox.showerror("Invalid Input", "Please enter a positive number of minutes.")
                return
            elif minutes > 999:
                messagebox.showerror("Invalid Input", "Please enter a number less than 1000 minutes.")
                return
            
            # Set the custom time
            self.SetTime(minutes * 60)
            self.isBreak = False
            self.UpdateDisplay()
            
            # Clear the input field
            self.customTimeEntry.delete(0, tk.END)
            
            # Show confirmation
            messagebox.showinfo("Custom Time Set", f"Timer set to {minutes} minute(s). Click Start to begin.")
            
        except ValueError:
            # Handle non-numeric input
            messagebox.showerror("Invalid Input", "Please enter a valid number of minutes (e.g., 25, 30, 60).")
        except Exception as e:
            # Handle any other unexpected errors
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def UpdateDisplay(self):
        self.timeLabel.config(text=self.FormatTime(self.CurrentTime))
        self.sessionLabel.config(text=f"Session:{self.SessionCount}")

        totalSeconds=sum(record['duration'] for record in self.sessionsManager.SessionRecords if record['completed']) 
        hours, remainder= divmod(totalSeconds, 3600)
        minutes,_=divmod(remainder,60)
        self.TotalTimeLabel.config(text=f"Total Time:{hours}hrs {minutes}min")

        #Progress Bar
        if self.OriginalTime>0:
            progressValue=((self.OriginalTime-self.CurrentTime)/self.OriginalTime)*100
            self.Progress['value']=progressValue

        #Update Title
        if self.isBreak:
            #if the remainder of SessionCount can divide 4(SessionBreak) equal to 0 and SessionCount>0 would occurs Long Break
            if self.SessionCount % self.SessionsBreak==0 and self.SessionCount>0:
                self.titleLabel.config(text="LONG BREAK")
                self.timeLabel.config(foreground="green")
            else:
                self.titleLabel.config(text="SHORT BREAK")
                self.timeLabel.config(foreground="green")
        else:
            self.titleLabel.config(text="WORK SESSIONS")
            self.timeLabel.config(foreground="red")

    def StartTimer(self):
        self.Start()

    def PauseTimer(self):
        self.Pause()

    def ResetTimer(self):
        self.Reset()
        self.isBreak=False
        self.SetTime(self.WorkTime)
        self.SessionCount=0
        self.UpdateDisplay()

#Function
    def SkipTimer(self):
        if self.isRunning:
            self.Pause()
        self.OnTimerFinished()

    def OnTick(self):
        self.root.after(0, self.UpdateDisplay)
    def OnTimerFinished(self):
        EndTime=datetime.now()
        duration = self.OriginalTime - self.CurrentTime

        SessionRecords={
            'date': self.StartTime.strftime('%Y-%m-%d'),
            'STime':self.StartTime.strftime('%H:%M:%S'),
            'ETime': EndTime.strftime('%H:%M:%S'),
            'type':'Break' 
            if self.isBreak 
            else 'Work',
            'duration':duration,
            'planniedDuration':self.OriginalTime,
            'completed': self.CurrentTime ==0
        }

        self.sessionsManager.AddRecords(SessionRecords)
        self.isRunning=False

        if self.popupEnabled.get():
            if self.isBreak:
                self.isBreak=False
                self.SetTime(self.WorkTime)
                messagebox.showinfo("Break Complete", "Break time is over! Are you ready to Work??")
            else:
                self.SessionCount +=1
                self.isBreak =True

                if self.SessionCount % self.SessionsBreak == 0:
                    self.SetTime(self.LongBreak)
                    message= f"Session{self.SessionCount} complete! \n Time for a Long Break({self.LongBreak//60}minutes)!!"
                else:
                    self.SetTime(self.ShortBreak)
                    message=f"Session{self.SessionCount} complete!\n Time For a Short Break({self.ShortBreak//60}minutes)!!"
                messagebox.showinfo("Session Complete", message)
        self.UpdateDisplay()
        self.RefreshRecords()

    def RefreshRecords(self):
        for item in self.RecordsTree.get_children():
            self.RecordsTree.delete(item)

        for record in reversed(self.sessionsManager.SessionRecords):
            durationMins= record['duration']//60
            durationSecs= record['duration']%60
            durationStr= f"{durationMins}min {durationSecs}sec"
            completed="Yes" if record['completed'] else "No"
            self.RecordsTree.insert('','end',values=(
                record['date'], record['type'], durationStr,completed,record['STime'], record['ETime']
            ))

        today= datetime.now().strftime('%Y-%m-%d')
        todayRecords=[r for r in self.sessionsManager.SessionRecords if r['date']== today and r['completed']]
        WorkSessions=[r for r in todayRecords if r['type'] == 'Work']
        TotalWorkTime= sum(r['duration'] for r in WorkSessions)
        workHrs= TotalWorkTime//3600
        workMin=(TotalWorkTime % 3600)//60
        SummaryText= f"Today: {len(WorkSessions)} Work Session, {workHrs}hrs {workMin}min Total"
        self.SummaryLabel.config(text=SummaryText)

#Clear All Records
    def ClearRecords(self):
        if messagebox.askyesno("Clear Records", "Are you sure you want to clear all records? This cannot be undone."):
            self.sessionsManager.ClearRecords()
            self.RefreshRecords()
            messagebox.showinfo("Clear Records", "All records cleared successfully.")


#=====================================================================================================
#Final Call Main Function
#=====================================================================================================
def main():
    root = tk.Tk()
    PomodoroTimer(root)

    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    root.mainloop()

if __name__ == "__main__":
    main()



        

        
        


            