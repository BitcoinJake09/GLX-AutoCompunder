#GLX CLAIM/STAKER BitcoinJake09 11/15/2022

import json
import requests
from requests.auth import HTTPBasicAuth
from requests_html import AsyncHTMLSession
import asyncio
import time
import datetime
import random, string
from beem import Hive
from beem.account import Account
from beem.transactionbuilder import TransactionBuilder
from beembase import operations
from beembase.operations import Custom_json

sleepTime = 60*1 # 1 minute

#ONLY CHANGE VARIABLES IN THIS SECTION!!!
hiveName = 'bitcoinjake09' #replace my name with your HIVE name
wif = "XXXX" #posting key here
#change below to greater times for less RC use
#claimTime is how often you want script to claim, numbers below represented in minutes
claimTime = sleepTime*15 # 15 minutes
#stakeTime is how often you want to stake
stakeTime = sleepTime*15 # 15 minutes
#THANK YOU

def timeNow(): #gets current time function
    #thank https://peakd.com/@zimos for time suggestion
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time

def getGLXPbalance(): #gets claimable GLX/GLXP balance
    r = requests.get('https://validator.genesisleaguesports.com/players/'+hiveName+'/balances/GLXP')
    jsonData = json.loads(r.text)
    d=jsonData["balance"]
    return d

def getGLXbalance(): #get liquid balance/stakable
    r = requests.get('https://validator.genesisleaguesports.com/players/'+hiveName+'/balances/GLX')
    jsonData = json.loads(r.text)
    d=jsonData["balance"]
    return d

isRunning = False #for main loop check
balance24 = getGLXPbalance() #for 24 hour snapshot to show balance increase
time24 = datetime.datetime.now() #used for the balance snapshot
staked24 = 0 #used for balance snapshot

async def main():
    #main event loop
    global isRunning #make sure we only run once
    if isRunning is False:
        print("Started") #shows we are about to start tasks
        #before we start, lets print balances:
        print(str(timeNow()) + ": CanStake: " + str(getGLXbalance()))
        print(str(timeNow()) + ": totalBalance: " + str(getGLXPbalance()))
        asyncio.create_task(claimNow()) #claim loop
        asyncio.create_task(stakeNow()) #stake loop
        asyncio.create_task(update24()) #balance snap loop
        print("Working...") #done with main function since loops are running after :D
        isRunning = True
    await asyncio.sleep(100000 * 60) #really long sleep or main stops

async def claimNow():
    while True:
        print(str(timeNow()) + ": totalBalance: " + str(getGLXPbalance()))
        tx = TransactionBuilder() #lets build a tx
        payload = {"token":"GLX","to_player":hiveName,"qty":0} #payload basically what the tx says to do
        new_json = { #found these in the hive explorer after i did my first few tx's and just put in right code format
              "required_auths": [],
              "required_posting_auths": [hiveName],
              "id": "gls-plat-stake_tokens",
              "json": payload
            }
        tx.appendOps(Custom_json(new_json)) #add ops to tx
        tx.appendWif(wif) #add key
        tx.sign() #sign
        tx.broadcast() #broadcast
        await asyncio.sleep(claimTime) #wait for next time

async def stakeNow():
    global staked24
    await asyncio.sleep(30) #sleep for 30 seconds at start to offset stakes 30 seconds after claims :D
    while True:
        canStake = getGLXbalance()
        staked24 = staked24 + canStake
        tx = TransactionBuilder()
        payload = {"token":"GLX","qty":canStake}
        new_json = {
              "required_auths": [],
              "required_posting_auths": [hiveName],
              "id": "gls-plat-stake_tokens",
              "json": payload
            }
        tx.appendOps(Custom_json(new_json))
        tx.appendWif(wif)
        tx.sign()
        tx.broadcast()
        print(str(timeNow()) + ": " + str(canStake) + " STAKED!")
        await asyncio.sleep(stakeTime)

async def update24():
    global time24, staked24, balance24
    while True: #every 24 hours this should spit out some numbers xD
        t24 = time24 + datetime.timedelta(hours = 24)
        if t24 < datetime.datetime.now():
            print(str(timeNow()) + ": " + str(staked24) + " STAKED in 24 hours!! \n Balance increased from: " + str("{0:.3f}".format(balance24)) + " to: " +str("{0:.3f}".format(getGLXPbalance())) + " GLX!")
            balance24 = getGLXPbalance()
            staked24 = 0
            time24 = datetime.datetime.now()
        await asyncio.sleep(sleepTime)

if __name__ == "__main__":
    asyncio.run(main())
