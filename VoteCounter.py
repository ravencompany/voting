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

# stuff from matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# csv reader for voter aliases
import csv
# regular expression parser
import re


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '13sq0PKc-D1NlFySgHGb4OMpymYVa_mnPXwcvH6p_J1U'
SAMPLE_RANGE_NAME = 'Form responses 1!A2:C'


def getPopulateData(scanFlag):  # with scanflag false, do not actually harvest, just set tbl_data and vote_data. had scope issues otherwise.
    global tbl_data
    global vote_data
    # reset table data
    vote_data=[0., 0., 0.]

    for k in voter_keys:
        voter_tstamp[k]= "---"
        voter_vote[k]=""

    # populate from sheet
    values=False
    if scanFlag:
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
    
    strip_pre=re.compile(".* ")
    strip_space=re.compile("\s")

    if not values:
        print('No data found.')
    else:
        #print('Timestamp, Codeword, response:')
        #i=0
        for row in values:
            if len(row)<3:
                continue
            codeword=strip_space.sub("",row[1]).lower()
            if codeword in voter_keys:
                #print(codeword + " detected")
                voter_tstamp[codeword]=strip_pre.sub("",row[0])
                voter_vote[codeword]=row[2]
            else:
                print(codeword + " not matched!")

    tbl_data=[]
    k=0
    for i in range(0,18):
        tbl_data.append([])
        for j in range(0,2):
            k=voter_keys[i+18*j]
            tbl_data[i].append(voter_name[k])
            tbl_data[i].append(voter_tstamp[k])

    for key in voter_keys:
        if voter_vote[key] in xlabelD:
            vote_data[xlabelD[voter_vote[key]]]+=1
    
    #print("getPopulateData ended vote_data=" + repr(vote_data))
    
def init():  # only required for blitting to give a clean slate.
    getPopulateData(True)
    #print("vote_data in init: " + repr(vote_data))
    if tableActive:
        for i in range(0,18):
            for j in range(0,4):
                textObj=the_table[i+1,j].get_text()
                textObj.set_text(tbl_data[i][j])
    if barsActive:
        maxh=1
        for i in range(len(xlabels)):
            bar_chart[i].set_height(vote_data[i])
            if vote_data[i]>maxh:
                maxh=vote_data[i]
        artists[-1].set_ylim(0,maxh) # if barsActive, actual axes shuld be last artist
    return artists


def animate(k):
    init()
    return artists

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

    # initialise codeword dereferencing
    global voter_name
    global voter_tstamp
    global voter_vote
    global voter_keys
    voter_name={}
    voter_tstamp={}
    voter_vote={}
    voter_keys=[]
    f = open("codewordBackref.csv", "r")
    csviter = csv.reader(f)
    for row in csviter:
        voter_name[row[0]]=row[1]
        voter_tstamp[row[0]]="---"
        # ensure consistent ordering
        voter_keys.append(row[0])


    # Initialise MATPLOTLIB table
    global the_table
    global bar_chart
    global artists
    global tableActive
    global barsActive
    artists=[]
    nplots=1
    tableActive=True
    barsActive=True

    global xlabels
    global xlabelD
    xlabelD={}
    xlabels=("For", "Against", "Abstain")
    for i in range(len(xlabels)):
        xlabelD[xlabels[i]]=i
    
    getPopulateData(False)

    while True:
        config=input("Request [T]able and/or [B]ar chart?")
        tableActive=bool(re.search("t",config,re.I))
        barsActive=bool(re.search("b",config,re.I))

        if (not(tableActive or barsActive)):
            break

        fig, axs =plt.subplots(1,tableActive + barsActive)
        
        if tableActive:
            if barsActive: # if the other side does not exist, axs will not be subscriptable
                tmpAx=axs[0]
                tmpAx.set_position([0.05, 0.1, 0.4, 0.8])
            else:
                tmpAx=axs
                tmpAx.set_position([0.05, 0.1, 0.9, 0.8])
            collabel=("Voter", "last count", "Voter", "last count")
            #tmpAx.axis('tight')
            tmpAx.axis('off')
            the_table = tmpAx.table(cellText=tbl_data,colLabels=collabel,loc='center')
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(10)
            cellDict=the_table.get_celld()
            for coord,aCell in cellDict.items():
                aCell.set_height(1/16)
                aCell.set_width(0.3-0.11*(coord[1] & 1))
            artists.append(the_table)
        

        if barsActive:
            if tableActive: # if the other side does not exist, axs will not be subscriptable
                tmpAx=axs[1]
            else:
                tmpAx=axs
            x=range(len(xlabels))
            bar_chart = tmpAx.bar(x,vote_data)
            tmpAx.set_xticks(x)
            tmpAx.set_xticklabels(xlabels)
            artists.extend(bar_chart) # bar char itself not an artist, but contains rects which are
            artists.append(tmpAx) # axes also count as an artist, and will need to be animated

        if tableActive:
            ani = animation.FuncAnimation(
            fig, animate, init_func=init, interval=1000, blit=False)
            #print('animation implied by table')

        plt.show()

if __name__ == '__main__':
    main()
# [END sheets_quickstart]


# Simplifying modes.
# Table only: continuous update with Last. Secret ballot "vote is open"
# bars only: no animation no update, use buffered.  Secret ballot "vote is closed"
# bars+table: continuous update with last. "Test mode"