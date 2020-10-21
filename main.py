from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import pyttsx3
import pytz
import speech_recognition as sr
import subprocess
#selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

#for selenium
PATH = "C:\Program Files (x86)\chromedriver"


#some global lists
GOOGLE_SEARCH=["search","find","define","google"]
NOTE_STRS = ["make a note", "write", "remember this", "type this"]
CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]


DAYS= ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
MONTHS=["january","febuary","march","april","may","june","july","august","september","octuber","november","december"]

#function that outputs the text as an audio from laptop
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


#function that inputs speech and returns its text
def get_audio():
    r= sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
        toText=""

        try:
            toText=r.recognize_google(audio)
            print(toText)
        except Exception as e:
            print("Exception: "+ str(e))

        return toText.lower()


#from google documentation for authentication
def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

#edited google doc code which inputs date and returns events on that date
def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            speak(event["summary"])

#this changed text from user and puts it in a proper date format
def get_date(text):
    text=text.lower()
    today=datetime.date.today()

    if text.count("today")>0:
        return today

    day=-1
    day_of_week=-1
    month=-1
    year=today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word)+1

        elif word in DAYS:
            day_of_week= DAYS.index(word)

        elif word.isdigit():
            day=int(word)


    if month<today.month and month != -1:
        year=year+1

    if day<today.day and month== -1 and day !=-1:
        month=month+1

    if month==-1 and day==-1 and day_of_week!=-1:
        current_day_of_week = today.weekday()
        dif=day_of_week-current_day_of_week

        if dif<0:
            dif= dif+7
            if text.count("next")>=1:
                dif+=dif

        return today+ datetime.timedelta(dif)

    if day != -1:
        return datetime.date(month=month, day=day, year=year)

#making a note
def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    subprocess.Popen(["notepad.exe", file_name])

#searching something on google
def search_google(driver,text):

    # driver = webdriver.Chrome(PATH)
    driver.get("http://www.google.com")
    search= driver.find_element_by_name("q")
    search.send_keys(f"{text}")
    search.send_keys(Keys.RETURN)

#################################################################################

WAKE = "hello"
SERVICE = authenticate_google()

while True:
    print("Listening")
    text = get_audio()

    if text.count(WAKE) > 0:
        speak("Hello, How can i help you ")
        text = get_audio()


        for phrase in CALENDAR_STRS:
            if phrase in text:
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("Please Try Again")

        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down? ")
                write_down = get_audio()
                note(write_down)
                speak("I've made a note of that.")

        for phrase in GOOGLE_SEARCH:
            if phrase in text:
                speak("What would you like me to search? ")
                find = get_audio()
                driver=webdriver.Chrome(PATH)
                search_google(driver,find)
                speak("Here's what i found")
