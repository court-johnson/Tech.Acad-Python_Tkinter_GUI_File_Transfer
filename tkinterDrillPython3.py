from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import shutil
import time
import sqlite3
from datetime import timedelta, datetime
from os import path
import os

#File locations
folders = {'Folder A':{'path':'C:\\Users\\court\\Desktop\\Folder A'},
           'Folder B':{'path':'C:\\Users\\court\\Desktop\\Folder B'}}

#Setting the time now to the deadline time of 24 hours
now = datetime.now()
deadline = now + timedelta(hours=-24)

#connecting to the already created database and table
conn = sqlite3.connect('dbDrill.db')
c = conn.cursor()

#Table already exists currently
#c.execute("DROP TABLE IF EXISTS fileCheck")
#c.execute("CREATE TABLE fileCheck(ID INTEGER PRIMARY KEY AUTOINCREMENT, DATE TEXT, TIME TEXT)")

#collecting data from when the last transfer was completed
c.execute("SELECT DATE, TIME FROM fileCheck WHERE ID =(SELECT MAX(ID) FROM fileCheck)")
lastTransferPerformed = c.fetchone()
lastTransferStamp = [str(i) for i in (lastTransferPerformed)]
print(lastTransferStamp)

#--------------------------------------------------------------------------

class Feedback:

    def __init__(self, master):
   
        master.title('Explore California Feedback')
        master.resizable(False, False)
        master.configure(background = '#e1d8b9')

        #styling of the labels, frames, button
        self.style = ttk.Style()
        self.style.configure('TFrame', background = '#8fbc8f')
        self.style.configure('TButton', background = '#20b2aa')
        self.style.configure('TLabel', background = '#8fbc8f', font = ('Arial', 11))
        self.style.configure('TLabelframe', bg = 'white', bd = 2, width = 40, height = 10)
        
        #creating the frame of the window
        self.frame_content = ttk.Frame(master)
        self.frame_content.pack()

        #creating the origin folder choice label and dropdown
        ttk.Label(self.frame_content, text = 'Origin:', style = 'TLabel').grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'w')
        self.origin = ttk.Combobox(self.frame_content)
        self.origin.grid(row = 1, column = 0, padx = 10)
        self.origin.config(values = list(folders.keys()))
    
        #creating the destination folder choice label and dropdown
        ttk.Label(self.frame_content, text = 'Destination:', style = 'TLabel').grid(row = 0, column = 3, padx = 10, pady = 10, sticky = 'w')
        self.destination = ttk.Combobox(self.frame_content)
        self.destination.grid(row = 1, column = 3, padx = 10)
        self.destination.config(values = list(folders.keys()))

        #creating the print out of the last time a file/files were transferred 
        ttk.Label(self.frame_content, text = 'Last Transfer Completed:', style = 'TLabel').grid(row = 2, column = 2, pady = 10, sticky = 'w')
        last_entry = Listbox(self.frame_content, height = 1)
        last_entry.grid(row = 3, column = 2)
        last_entry.insert(1, str(lastTransferStamp))

        #button that binds to the transfer function and popup window advising transfer is completed
        self.transfer = ttk.Button(self.frame_content, text='Transfer', style='TButton')
        self.transfer.grid(row = 4, column = 2, padx = 5, pady = 20)
        self.transfer.bind("<Button-1>", self.transferButtonClicked)
        self.transfer.bind("<Button-1>", self.fileTransfer)
       
#--------------------------------------------------------------------------

    #creating the function that transfers files modified within 24hours
    def fileTransfer(self, event):
        #binding selection of origin and destination folders for variable
        self.origin.bind("<<ComboboxSelected>>")
        self.destination.bind("<<ComboboxSelected>>")
        value_of_origin = self.origin.get()
        value_of_dest = self.destination.get()
        #retrieving the path name of the key value selected
        origin_path = folders[value_of_origin]['path']
        dest_path = folders[value_of_dest]['path']

        #generating the file names from Origin 
        try:
            for root, dir, files in os.walk(origin_path):
                #looping through each file to retrieve the time stamp and pathname
                for file in files:
                    pathname = os.path.join(root, file)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(pathname))
                    #comparing modification time from deadline and moving if appropriate
                    if now >= modified_time >= deadline:
                        print('modified within 24 hours: ' + pathname)
                        shutil.move(pathname, dest_path)
        except Exception as e:
            print(e)
        #printing 'completed' once all files are transferred
        else:
            self.transferButtonClicked(event)
            

#---------------------------------------------------------------------------

    #event defined for transfer
    def transferButtonClicked(self, event):
        popupComplete = tkinter.messagebox.showinfo('Sent', 'Transfer Completed!')
        self.button_clicked_time = time.time()
        self.dataInsert()
        
#--------------------------------------------------------------------------

    #function for adding the timestamp of transfers into the database
    def dataInsert(self):        
        #setting parameters to retrieve the date and the time of when the transfer button is clicked
        p = datetime.now()
        clicked_date = p.strftime("%Y-%m-%d")
        clicked_time = p.strftime("%H:%M")

        #inserting retrieved time and date of when the transfer button was clicked
        c.execute("INSERT INTO fileCheck (DATE, TIME) VALUES (?,?)", (clicked_date, clicked_time))
        conn.commit()

        #disconnecting from database
        c.close()
        conn.close()
        
#--------------------------------------------------------------------------
        
def main():
    root = Tk()
    feedback = Feedback(root)
    root.mainloop()

if __name__ == '__main__':
    main()
