# Structure
# Grid, main frame, lower frame (fixed height)
#    Main frame, grid of frames, containing packed labels (like gridTest) *
#    Lower frame, Grid of Labels
#
# * Each grid box associated to an object in a List
#       lbl_name, lbl_votes, refcode, frm_self

import tkinter as tk

class app_gui:
    cols=2             # default columns
    maingridframes=[]  # List for storage of datagrid objects
    def __init__(self):
        window=tk.Tk()
        window.rowconfigure(0, weight=1, minsize=50)
        window.columnconfigure(0, weight=1, minsize=75)
        self.frm_main = tk.Frame(master=window, relief=tk.SUNKEN, borderwidth=1)
        self.frm_main.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        #tk.Label(master=self.frm_main, text="main frame").pack() # dummy content
        window.rowconfigure(1, weight=0, minsize=30)
        self.frm_lower = tk.Frame(master=window, relief=tk.SUNKEN, borderwidth=1)
        self.frm_lower.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
        #tk.Label(master=self.frm_lower, text="lower frame").pack() # dummy content
        #self.showLower()
        self.window=window
    def showLower(self):
        self.frm_lower.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
    def Show(self):
        self.window.mainloop()
        



if __name__ == '__main__':
    test=app_gui()
    test.Show()