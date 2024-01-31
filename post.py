import os 
from dotenv import load_dotenv
import requests
import time
import json

load_dotenv() 
RapidAPIKey = os.environ.get('X-RapidAPI-Key')

def createTracking(trackCode):
    url = "https://postal-ninja.p.rapidapi.com/v1/track"

    payload = { "trackCode": trackCode }
    headers = {
	"content-type": "application/x-www-form-urlencoded",
	"Accept": "application/json; charset=UTF-8",
	"Content-Type": "application/x-www-form-urlencoded",
	"X-RapidAPI-Key": RapidAPIKey,
	"X-RapidAPI-Host": "postal-ninja.p.rapidapi.com"
    }
    response = requests.post(url, data=payload, headers=headers)

    print(response.json()['pkgId'])
    packageId = response.json()['pkgId']
    return packageId

time.sleep(2)

def getTrack(packageId):
    url = f"https://postal-ninja.p.rapidapi.com/v1/track/{packageId}"
    querystring = {"await":"false","lang":"AS_IS"}
    headers = {
        "Accept": "application/json; charset=UTF-8",
        "X-RapidAPI-Key": RapidAPIKey,
        "X-RapidAPI-Host": "postal-ninja.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    # Initialize an empty dictionary to store the events
    events_dict = {}

    # Loop over all events
    i = 0
    for event in data['pkg']['events']:
        # Use the event's id as the key and a dictionary of "dt" and "dsc" as the value
        #events_dict[event['id']] = {'dt': event['dt'], 'dsc': event['dsc']}
        events_dict['event_id'] = i
        events_dict['dt'] = event['dt']
        events_dict['dsc'] = event['dsc']
        i += 1

    return events_dict




