# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START sheets_quickstart]
from __future__ import print_function

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app_gui import *

# stuff from matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# csv reader for voter aliases
import csv
# regular expression parser
import re
# basic math
import math


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of the spreadsheet that contains ID ref codes and Display Names
IDENTITIES_SHEET_ID = '163CQ-9v3S5YYA1mFO7el1PI-QbpmfDPK-fSeLECaqrk'
IDENTITIES_RANGE_NAME = 'Form responses 1!B2:D'

# The ID and range of the spreadsheet that contains ID ref codes and Vote responses
VOTES_SPREADSHEET_ID = '13sq0PKc-D1NlFySgHGb4OMpymYVa_mnPXwcvH6p_J1U'
VOTES_RANGE_NAME = 'Form responses 1!A2:C'

# Thoughts on data structure and architecture:
# Data structure "voter_data", a dictionary of objects indexed by refcode
#    Voter(s) display name: disp_name
#    Max votes: max_votes
#    vote total: tot_votes
#    datagrid object from app_gui, or None
# Backref list of "voter_keys", ordered by display name
# Dictionary "vote_count", indexed by eg "For"
# Object "gui", with constructor, attributes, methods, why not. In seperate file

voter_data={}

class voter:
    disp_name="undefined"
    max_votes=0
    tot_votes=1
    exists=True
    def __init__(self,row=[]):
        if len(row)>=2:
            self.disp_name=row[1]
        if len(row)>=3:
            self.max_votes=int(row[2])
        self.datagrid=datagrid(gui.frm_main,name=self.disp_name,status=self.vote_status())
    def update(self,row=[]):
        if len(row)>=2:
            self.disp_name=row[1]
        if len(row)>=3:
            self.max_votes=int(row[2])
        self.datagrid.let(name=self.disp_name,status=self.vote_status())
    def vote_status(self):
        return "".join((lambda i:
                    "\N{BULLET}" if (i<self.tot_votes)
                    else "\N{WHITE BULLET}")(i) 
                    for i in range(self.max_votes))
        


def sync_voters():
    #fetch data from IDENTITIES_SHEET
    result = sheet.values().get(spreadsheetId=IDENTITIES_SHEET_ID,
                                range=IDENTITIES_RANGE_NAME).execute()
    values = result.get('values', [])
    
    #handle case where a voter is removed
    #start by un-exist-ing all current
    for i in voter_data.items():
        i.exists=False

    # log if anything updates that would rebuild gui
    upd=False

    strip_space=re.compile(r"\s")
    if not values:
        print('No data found.')
        return False
    else:
        for row in values:
            if len(row)<2:
                continue
            refcode=strip_space.sub("",row[0])
            if refcode in voter_data:
                # handle update
                print(f"{refcode} found again, updating")
                #
                voter_data[refcode].exists=True
                # Note, update only updates max_votes if present
                # Keeping - someone might resubmit their name
                upd=voter_data[refcode].update(row) or upd
            else:
                #instantiate voter, pasing row for convenience
                voter_data[refcode]=voter(row)
                upd=True

    for k, i in filter(lambda e: not e[1].exists, voter_data.items()):
        voter_data.pop[k]
        print(f"refcode {k} deleted")
        upd=True

    return True

def sync_gui(**kwargs):
    for i in gui.onGrid:
        i.remove()
    gui.onGrid.clear()

    if "maxcols" in kwargs:
        gui.maxcols=kwargs["maxcols"]
        print(f"Max cols now {gui.maxcols}")

    i=0
    j=0
    refcodes=[(lambda k,i:(k,i.disp_name.casefold()))(k,i) for k, i in voter_data.items()]
    refcodes.sort(key=lambda e:e[1])
    #print(str(refcodes))
    rows=math.ceil(len(refcodes)/gui.maxcols)
    # Note, possible not all cols are used
    # e.g. 4 items, 3 cols needs 2 rows. 2 rows gives 2 cols.
    # Keeping this behaviour, because more optimal packing

    #maintain some "spare" cells for padding out
    while len(gui.spares)<rows:
        gui.spares.append(datagrid(gui.frm_main))

    for k,name in refcodes:
        if i>=rows:
            j=j+1
            i=0
        voter_data[k].datagrid.grid(i,j)
        gui.onGrid.append(voter_data[k].datagrid)
        i=i+1
    while i<rows: # complete using spares
        gui.spares[i].grid(i,j)
        gui.onGrid.append(gui.spares[i])
        i=i+1

    # config rows and cols to match resulting grid
    cols=j+1
    while gui.rows<rows:
        gui.frm_main.rowconfigure(gui.rows, weight=1, minsize=30)
        print(f"set row {gui.rows+1}")
        gui.rows=gui.rows+1
    while gui.cols<cols:
        gui.frm_main.columnconfigure(gui.cols, weight=1, minsize=75)
        print(f"set col {gui.cols+1}")
        gui.cols=gui.cols+1
    while gui.rows>rows:
        gui.rows=gui.rows-1
        gui.frm_main.rowconfigure(gui.rows, weight=0, minsize=0)
        print(f"unset row {gui.rows+1}")
    while gui.cols>cols:
        gui.cols=gui.cols-1
        gui.frm_main.columnconfigure(gui.cols, weight=0, minsize=0)
        print(f"unset col {gui.cols+1}")
        


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    global sheet
    sheet = service.spreadsheets()

    # instantiate app_gui
    global gui
    gui=app_gui()
    gui.maxcols=4
    # col/row config linked to change in rows/cols
    gui.cols=0
    gui.rows=0
    gui.spares=[]
    gui.window.bind("<Left>", lambda e:sync_gui(maxcols=gui.maxcols-1 if gui.maxcols>1 else 1))
    gui.window.bind("<Right>", lambda e:sync_gui(maxcols=gui.maxcols+1))

    # initialise codeword dereferencing
    # if sync_voters flags for gui update, do it
    sync_voters() and sync_gui()

    gui.Show()

if __name__ == '__main__':
    main()
# [END sheets_quickstart]


# Simplifying modes.
# Table only: continuous update with Last. Secret ballot "vote is open"
# bars only: no animation no update, use buffered.  Secret ballot "vote is closed"
# bars+table: continuous update with last. "Test mode"