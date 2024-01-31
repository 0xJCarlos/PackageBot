import os 
from dotenv import load_dotenv
import requests
import time

load_dotenv() 
RapidAPIKey = os.environ.get('X-RapidAPI-Key')

url = "https://postal-ninja.p.rapidapi.com/v1/track"

payload = { "trackCode": "ENTER_TRACKING_CODE_HERE" }
headers = {
	"content-type": "application/x-www-form-urlencoded",
	"Accept": "application/json; charset=UTF-8",
	"Content-Type": "application/x-www-form-urlencoded",
	"X-RapidAPI-Key": RapidAPIKey,
	"X-RapidAPI-Host": "postal-ninja.p.rapidapi.com"
}

response = requests.post(url, data=payload, headers=headers)

print(response.json()['pkgId'])
pkgId = response.json()['pkgId']

url = "https://postal-ninja.p.rapidapi.com/v1/track/{pkgId}"

querystring = {"await":"false","lang":"AS_IS"}

headers = {
	"Accept": "application/json; charset=UTF-8",
	"X-RapidAPI-Key": RapidAPIKey,
	"X-RapidAPI-Host": "postal-ninja.p.rapidapi.com"
}

time.sleep(2)
response = requests.get(url, headers=headers, params=querystring)

print(response.json())