import os
import time as t
import sys
import playsound
import _thread
import threading
import multiprocessing
import psutil
from tqdm import tqdm
import pickle
import datetime
from datetime import datetime, timedelta
from simplegmail import Gmail
import pyautogui as pa
import pyowm
import pyglet
import pyttsx3
import webbrowser
import speech_recognition as sr
import wikipedia
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from win10toast import ToastNotifier
from goto import with_goto
import face_recognition as fr
import cv2
import csv
import numpy as np
import pandas as pd
import mediapipe as mp
import HandTrackingModule as htm

import AiVirtualMouseProject as avm
# =============================================================================
# from chatterbot import ChatBot
# from chatterbot.trainers import ListTrainer
# from chatterbot.trainers import ChatterBotCorpusTrainer
# from chatterbot.response_selection import get_random_response
# 
# bot = ChatBot(name='Gideon', read_only=False,logic_adapters=["chatterbot.logic.BestMatch"],storage_adapter="chatterbot.storage.SQLStorageAdapter", response_selection_method=get_random_response)
# =============================================================================


num = 1
hr = 12
m = " a.m."
minu = 0
month = " Jan"
date = 1
year = 2020
days = "Someday"
next_day = "tomorrow"
per_of_day = " morning"
hr_a = ''
minu_a = ''
alarm_time = ''
playing_music = False
class_id = '15'
toast = ToastNotifier()
all_threads = []
face_names = []
known_face_names = []
known_face_encodings = []


def gideon_speaks(output):
    global num
    # num += 1
    c_hr, c_minu, c_m = tell_time()
    c_t = str(c_hr) + ":" + str(c_minu) + " " + str(c_m)
    print("Gideon: ", output, "       ("+c_t+")")
    toSpeak = pyttsx3.init()
    voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"

    # Use female voice
    toSpeak.setProperty('voice', voice_id)
    toSpeak.setProperty('rate', 165)
    toSpeak.setProperty('volume', 0.8)
    toSpeak.say(output)
    toSpeak.runAndWait()


def gideon_asks(input_gideon):
    gideon_speaks(input_gideon)
    rObject = sr.Recognizer()
    with sr.Microphone() as source:
        print('Speak..')
        audio = rObject.listen(source)

    try:
        text1 = rObject.recognize_google(audio, language='en')
        print("You : ", text1)
        return text1
    except:
        return gideon_asks("Could not understand you")


def get_audio():
    rObject = sr.Recognizer()
    with sr.Microphone() as source:
        # print('Speak..')
        rObject.adjust_for_ambient_noise(source)
        audio = rObject.listen(source)

    try:
        text1 = rObject.recognize_google(audio, language='en').lower()
    except:
        text1 = ' '

    if "gideon" in text1:
        try:
            text1 = rObject.recognize_google(audio, language='en')
            print("You : ", text1)
            return text1
        except:
            gideon_speaks("Could not understand you")
            return 0
    else:
        return get_audio()


def get_conversation():
    rObject = sr.Recognizer()
    with sr.Microphone() as source:
        # print('Speak..')
        audio = rObject.listen(source)

    try:
        text = rObject.recognize_google(audio, language='en-in')
        print("You : ", text)
        return text
    except:
        get_audio()


# =============================================================================
# def train_bot():
#     corpus_trainer = ChatterBotCorpusTrainer(bot)
#     corpus_trainer.train("chatterbot.corpus.english")
#     gideon_speaks("Speech Drive reboot successful")
# =============================================================================


def wake_word(input_gideon):
    wake = ['gideon', 'hey gideon']
    input_gideon = input_gideon.lower()
    for w in wake:
        if w in input_gideon:
            return True
    return False


def tell_time():
    # tells current time time along with meridian and period of day
    global hr
    hr = int(t.strftime("%H:%M").split(":")[0])
    global m
    m = "a.m."
    global hr_a
    hr_a = ''
    global minu_a
    minu_a = ''
    global per_of_day
    per_of_day = "morning"
    if hr >= 12:
        m = "p.m."
    global minu
    minu = t.strftime("%H:%M").split(":")[1]
    if m == "a.m.":
        per_of_day = "morning"
    elif hr in range(12, 15):
        per_of_day = "afternoon"
    elif hr in range(16, 19):
        per_of_day = "evening"
    else:
        per_of_day = "night"
    if hr != 12:
        hr = hr % 12
    return hr, minu, m


def secs2hours(secs):
    mm, ss = divmod(secs, 60)
    hh, mm = divmod(mm, 60)
    return hh, mm, ss


def tell_date():
    # tells current day's date along with corresponding suffix
    date_time = t.asctime(t.localtime(t.time()))
    cal = date_time.split()
    global month
    month = cal[1]
    global date
    date = int(cal[2])
    global year
    year = cal[4]
    if date in range(4, 20) and date in range(24, 30):
        pass
    elif date % 10 == 1:
        pass
    elif date % 10 == 2:
        pass
    elif date % 10 == 3:
        pass
    else:
        pass
    # gideon_speaks("Today is " + month + " " + str(date) + ", " + year)


def tell_day():
    # tells today's day
    global days
    days = datetime.today().strftime("%A")
    global next_day
    next_day = (datetime.today()+timedelta(days=1)).strftime("%A")
    return days


def welcome(loc="kakinada"):
    # A welcome greeting which tells current time and outside weather conditions when the program is started
    tell_time()
    if per_of_day != 'night':
        greeting = 'Good ' + per_of_day + '.'
    else:
        greeting = ''
    temp_cur, cloud_coverage, humidity, wind_speed = weather()
    desc = greeting + " It\'s " + str(hr) + ":" + str(minu) + " " + m + ", the weather in " + loc + " is " + str(round(temp_cur)) + " degrees with " + cloud_coverage.capitalize() + ". It is " + str(humidity) + "% Humid with a wind speed of " + str(wind_speed) + " MpH"
    # desc = greeting
    gideon_speaks(desc)


def weather(loc="kakinada"):
    # returns current location's weather conditions like cloud coverage, temperature, humidity and wind speed
    owm = pyowm.OWM('your owm key')
    obs = owm.weather_at_place(loc + ",IN")
    w = obs.get_weather()
    weathers = {'cloud_coverage': w.get_clouds(), 'wind': w.get_wind(), 'humidity': w.get_humidity(), 'temp': w.get_temperature(unit='celsius')}
    cloud_coverage = ''
    wind_speed = weathers['wind']['speed']
    humidity = weathers['humidity']
    temp_cur = weathers['temp']['temp']
    # the following lines give the corresponding cloud coverage according to cloud_coverage percentage
    if weathers['cloud_coverage'] in range(0, 11):
        cloud_coverage = 'clear sky'
    elif weathers['cloud_coverage'] in range(11, 51):
        cloud_coverage = 'scattered clouds'
    elif weathers['cloud_coverage'] in range(51, 91):
        cloud_coverage = 'broken clouds'
    elif weathers['cloud_coverage'] in range(91, 101):
        cloud_coverage = 'overcast clouds'
    return temp_cur, cloud_coverage, humidity, wind_speed


def auto_weather_check():
    # returns current location's weather conditions like cloud coverage, temperature, humidity and wind speed
    c_hr, c_minu, c_m = tell_time()
    if c_m == 'p.m.' and c_hr != 12:
        c_hr += 12
    while True:
        temp_cur, cloud_cover, humidity, wind_speed = weather()
        icon = ''
        desc = ''
        if c_hr < 18:
            if cloud_cover == 'clear sky' and wind_speed < 6:
                icon = "./weather_icons/sunny.ico"
                desc = "Sunny"
            elif wind_speed >= 6:
                if cloud_cover == "clear sky":
                    icon = "./weather_icons/wind.ico"
                    desc = "Clear sky with " + str(wind_speed) + " MpH wind"
                elif cloud_cover != "clear sky":
                    icon = "./weather_icons/cloudy windy morning.ico"
                    desc = "Cloudy with " + str(wind_speed) + " MpH wind"
            elif cloud_cover != "clear sky" and wind_speed < 6:
                icon = "./weather_icons/cloudy morning.ico"
                desc = "Cloudy"
            weather_desc = "Weather : " + desc + "\nTemperature : " + str(temp_cur) + chr(176) + "C \n"
        else:
            if cloud_cover == 'clear sky' and wind_speed < 6:
                icon = "./weather_icons/clear night.ico"
                desc = "Clear sky"
            elif cloud_cover != "clear sky" and wind_speed < 6:
                icon = "./weather_icons/cloudy night.ico"
                desc = "Cloudy"
            elif cloud_cover != "clear sky" and wind_speed >= 6:
                icon = "./weather_icons/windcloudy.ico"
                desc = str(wind_speed) + " MpH wind"
            weather_desc = "Weather : " + desc + "\nTemperature : " + str(temp_cur) + chr(176) + " \n "
        toast.show_toast("Gideon", weather_desc, icon_path=icon, duration=20, threaded=True)
        t.sleep(3600)
    # return temp_cur, cloud_coverage, humidity, wind_speed


def open_settings(input_gideon):
    # opens the type of settings, when asked for, else opens regular system settings
    pa.hotkey('Win', 'i')
    t.sleep(1.5)
    indo = input_gideon.lower().split().index('open')
    inds = input_gideon.lower().split().index('settings')
    setting_type = input_gideon.split()[indo + 1:inds]
    setting = ''
    for x in range(0, len(setting_type)):
        setting += setting_type[x]
        setting += ' '
    if len(setting) != 0:
        t.sleep(0.5)
        pa.typewrite(setting)
        pa.press(['backspace'])
        t.sleep(0.5)
        pa.press('enter')
        t.sleep(0.5)
        pa.press('enter')
    else:
        gideon_speaks("Opening settings")


def search(d, k, path=None):
    # searches for the key 'k' in the list 'PC' and returns the path as per the explorer tree in windows
    if path is None:
        path = []
    if not isinstance(d, dict):
        return False
    if k in d.keys():
        path.append(k)
        return path

    else:
        check = list(d.keys())
        while check:
            first = check[0]
            path.append(first)
            if search(d[first], k, path) is not False:
                break
            else:
                check.pop(0)
                path.pop(-1)
        else:
            return False
        return path


def open_loc(input_gideon="this pc"):
    # opens the asked file, folder, video, application, etc.
    if "open" in input_gideon.lower() or "play" in input_gideon.lower():
        if "episode" in input_gideon.lower():
            if "open" in input_gideon.lower():
                indo = input_gideon.lower().split().index('open')
            else:
                indo = input_gideon.lower().split().index('play')
            if "season" in input_gideon.lower():
                inds = input_gideon.lower().split().index('season')
                seas_no = str(input_gideon.split()[inds + 1])
                ser_name = ''
                for i in range(indo + 1, inds):
                    ser_name += input_gideon.split()[i] + " "
                if "episode" in input_gideon.lower():
                    inde = input_gideon.lower().split().index('episode')
                    ep = str(input_gideon.split()[inde + 1])
                    x = int(ep)
                    if 1 <= x <= 9:
                        ep_no = '0' + str(ep)
                    else:
                        ep_no = str(ep)
                    s_name = ser_name + "_S0" + seas_no + ".E" + ep_no
                    gideon_speaks("Playing " + ser_name + "season " + seas_no + " episode " + ep_no)
                    pa.hotkey('Win', 's')
                    t.sleep(1)
                    pa.typewrite(s_name)
                    t.sleep(1)
                    pa.press('enter')
        else:
            if "open" in input_gideon.lower():
                indo = input_gideon.lower().split().index('open')
            else:
                indo = input_gideon.lower().split().index('play')
            f_name = ''
            if "folder" in input_gideon.lower():
                indf = input_gideon.lower().split().index('folder')
                f_list = input_gideon.split()[indo + 1:indf]
                for f in f_list:
                    f_name += str(f).capitalize()
                    f_name += ' '
            else:
                f_list = input_gideon.split()[indo + 1:]
                for f in f_list:
                    f_name += str(f).capitalize()
                    f_name += ' '
            gideon_speaks("Opening " + f_name)
            pa.hotkey('Win', 's')
            t.sleep(1)
            pa.typewrite(f_name)
            t.sleep(0.75)
            pa.press('enter')
    t.sleep(2)
    pa.hotkey('alt', 'space')
    pa.press('x')


def get_calendar_service():
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
               CREDENTIALS_FILE, SCOPES)
           creds = flow.run_local_server(port=0)

       # Save the credentials for the next run
       with open('token.pickle', 'wb') as token:
           pickle.dump(creds, token)

   service = build('calendar', 'v3', credentials=creds)
   return service


def list_calendars():
   service = get_calendar_service()
   # Call the Calendar API
   # print('Getting list of calendars')
   calendars_result = service.calendarList().list().execute()

   calendars = calendars_result.get('items', [])

   if not calendars:
       gideon_speaks('No calendars found')
   for calendar in calendars:
       summary = calendar['summary']
       id = calendar['id']
       primary = "Primary" if calendar.get('primary') else ""
       # print("%s\t%s\t%s" % (summary, id, primary))


def list_events(day="today"):
   service = get_calendar_service()
   # Call the Calendar API
   now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
   process = multiprocessing.Process(target=auto_update_calendar, name="auto_update_calendar", daemon=False)
   process.start()
   if day == "today":
       max_time = (datetime.utcnow()+timedelta(days=1)).isoformat() + 'Z'
       max_time=max_time.split("T")[0]+"T00:00:00.000000Z"
   elif day == "tomorrow" or next_day == day:
       now = (datetime.utcnow()+timedelta(days=1)).isoformat() + 'Z'
       now=now.split("T")[0]+"T00:00:00.000000Z"
       max_time = (datetime.utcnow()+timedelta(days=2)).isoformat() + 'Z'
       max_time=max_time.split("T")[0]+"T00:00:00.000000Z"
   events_result = service.events().list(
       calendarId='primary', timeMin=now, timeMax=max_time,
       maxResults=10, singleEvents=True,
       orderBy='startTime').execute()
   events = events_result.get('items', [])

   if not events:
       gideon_speaks('No upcoming events found today')
   for event in events:
       start = event['start'].get('dateTime', event['start'].get('date'))
       time_print = start.split("T")[1].split("+")[0]
       gideon_speaks("At " + time_print +", "+ event['summary'])


def create_event():
   # creates one hour event tomorrow 10 AM IST
   service = get_calendar_service()

   d = datetime.now().date()
   ti = datetime.now().time()
   event_det = gideon_asks("At what time? (example: 10:00 a.m. tomorrow)")
   event_t = event_det.split()[0]
   if ":" in event_t:
       event_hr = event_t.split(":")[0]
       event_min = event_t.split(":")[1]
   else:
       event_hr = event_t
       event_min = "00"
   event_m = event_det.split()[1]
   if "tomorrow" in event_det or "today" in event_det:
       event_day = event_det.split()[2]
       if event_day == "tomorrow":
           event_time = datetime(d.year, d.month, d.day, int(event_hr), int(event_min),)+timedelta(days=1)
       if event_m == "p.m.":
           event_time += timedelta(hours=12)
   else:
       event_time = datetime(d.year, d.month, d.day, int(event_hr), int(event_min))
       if event_m == "p.m.":
           event_time += timedelta(hours=12)
   
# =============================================================================
#    tomorrow = datetime(d.year, d.month, d.day, 9)+timedelta(days=1)
#    today = datetime(d.year, d.month, d.day, ti.hour, ti.minute)+timedelta()
# =============================================================================
   start = event_time.isoformat()
   event_duration = gideon_asks("Duration of event (example: x hour y minutes)")
   dur_hr = int(event_duration.split()[0])
   if "hour" in event_duration.lower():
       dur_hr = int(event_duration.split()[0])
       if "minute" in event_duration.lower():
           dur_min = int(event_duration.split()[2])
       else:
           dur_min = 0
   else:
       dur_hr = 0
       if "minute" in event_duration.lower():
           dur_min = int(event_duration.split()[0])
       else:
           dur_min = 0
   end = (event_time + timedelta(hours=dur_hr, minutes=dur_min)).isoformat()
   summ = gideon_asks("What is the event for?").capitalize()

   event_result = service.events().insert(calendarId='primary',
       body={
           "summary": summ,
           "start": {"dateTime": start, "timeZone": 'Asia/Kolkata'},
           "end": {"dateTime": end, "timeZone": 'Asia/Kolkata'},
       }
   ).execute()

   gideon_speaks("created event")
   data = {'id': [event_result['id']],
 'summary': [event_result['summary']],
 'start': [event_result['start']['dateTime']],
 'end': [event_result['end']['dateTime']]}
   try:
       auto_update_calendar()
   except :
       gideon_speaks("Please close the open Calendar details file")
       auto_update_calendar(15)


def update_event():
    # update the event to tomorrow 9 AM IST
    service = get_calendar_service()

    d = datetime.now().date()
    tomorrow = datetime(d.year, d.month, d.day, 9)+timedelta(days=1)
    start = tomorrow.isoformat()
    end = (tomorrow + timedelta(hours=2)).isoformat()
    
    df1 = pd.read_excel('calendar_details.xlsx')
    print(df1)
    event_index = gideon_asks("Which event do you need me to update. Please tell the index of the event")
    eventid = df1.id[event_index]

    event_result = service.events().update(
    calendarId='primary',
    eventId=eventid,
        body={
           "summary": 'Updated Automating calendar',
           "start": {"dateTime": start, "timeZone": 'Asia/Kolkata'},
           "end": {"dateTime": end, "timeZone": 'Asia/Kolkata'},
           },
        ).execute()

    gideon_speaks("updated event")
    data = {'id': [event_result['id']],
 'summary': [event_result['summary']],
 'start': [event_result['start']['dateTime']],
 'end': [event_result['end']['dateTime']]}
    try:
       auto_update_calendar()
    except :
       gideon_speaks("Please close the open Calendar details file")
       process = multiprocessing.Process(target=auto_update_calendar, name="auto_update_calendar", args=(15,))
       process.start()


def delete_event():
       # Delete the event
       df1 = pd.read_excel('calendar_details.xlsx')
       print(df1)
       event_index = gideon_asks("Which event do you need me to delete. Please tell the index of the event")
       eventid = df1.id[event_index]
       service = get_calendar_service()
       try:
           service.events().delete(
               calendarId='primary',
               eventId=eventid,
           ).execute()
       except:
           gideon_speaks("Failed to delete event")

       gideon_speaks("Event deleted")
       df = pd.read_excel('calendar_details.xlsx')
       df = df[df.id != eventid]
       df = df.drop_duplicates()
       df.to_excel('calendar_details.xlsx')


def auto_update_calendar(delay=0):
   service = get_calendar_service()
   # Call the Calendar API
   now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
   events_result = service.events().list(
       calendarId='primary', timeMin=now,
       maxResults=10, singleEvents=True,
       orderBy='startTime').execute()
   events = events_result.get('items', [])
   data1 = {'id': [],'summary': [],'start': [],'end': []}
   df1 = pd.DataFrame(data1)

   for event in events:
       data = {'id': [event['id']],'summary': [event['summary']],'start': [event['start']['dateTime']],'end': [event['end']['dateTime']]}
       df = pd.DataFrame(data)
       df1 = pd.concat([df1,df],ignore_index=True)
   
   t.sleep(delay)
   try:
       df1.to_excel('calendar_details.xlsx')
   except :
       gideon_speaks("Please close the open Calendar details file")
       process = multiprocessing.Process(target=auto_update_calendar, name="auto_update_calendar", args=(15,))
       process.start()


def gmail_send():
    gmail = Gmail()
    gideon_speaks("Enter the email address of the recipient")
    recpt = input("")
    subj = gideon_asks("Subject of the mail?")
    if "nothing" in subj.lower():
        subj = ""
    msg = gideon_asks("Body of the message")
    if "nothing" in msg.lower():
        msg = ""
    params = {
        "to": recpt,
        "sender": "your email id",
        "subject": subj,
        # "msg_html": "<h1>Woah, my first email!</h1><br />This is an HTML email.",
        "msg_html": msg,
        "signature": True
        }
    message = gmail.send_message(**params)


def set_alarm(alarmtime, day="today", msg=""):
    c_hr = int(t.strftime("%H:%M:%S").split(":")[0])
    c_hr = c_hr % 12
    c_minu = int(t.strftime("%H:%M:%S").split(":")[1])
    c_s = int(t.strftime("%H:%M:%S").split(":")[2])
    x, y, c_m = tell_time()
    day = alarm_freq(day)
    g_minu = 0
    g_hr = 0
    hours = 0
    minutes = 0
    msg = msg.capitalize()
    try:
        a_hr = int(alarmtime.split(":")[0])
        a_minu = int(alarmtime.split(":")[1].split(" ")[0])
        a_m = alarmtime.split(":")[1].split(" ")[1]
        if c_m == a_m:
            g_hr = a_hr - c_hr
            if (a_minu - c_minu) < 0:
                g_minu = 60 - abs(a_minu - c_minu)
                g_hr -= 1
            else:
                g_minu = abs(a_minu - c_minu)
            if g_hr < 0:
                g_hr += 24
        elif (c_m == "a.m." and a_m == "p.m.") or (c_m == "p.m." and a_m == "a.m."):
            g_hr = a_hr - c_hr
            if (a_minu - c_minu) < 0:
                g_minu = 60 - abs(a_minu - c_minu)
                g_hr -= 1
            else:
                g_minu = abs(a_minu - c_minu)
            g_hr += 12
            if g_hr < 0:
                g_hr += 24
        try:
            hours = int(g_hr)
            minutes = int(g_minu)
        except ValueError:
            print("Invalid numeric value")

        if minutes < 0 and hours < 0:
            print("value of duration in minutes should be >= 0")

        minutes += hours * 60
        seconds = minutes * 60 - c_s

        try:
            if seconds >= 0:
                if len(msg) == 0:
                    gideon_speaks("Alarm set for " + str(a_hr) + ":" + str(a_minu) + " " + a_m)
                else:
                    gideon_speaks("Reminder for " + msg + " set for " + str(a_hr) + ":" + str(a_minu) + " " + a_m)
                multiprocessing.Process(target=auto_alarm_save, name="alarm_save").start()
                t.sleep(seconds)
            t1 = threading.Thread(target=sound_alarm, daemon=False)
            t1.start()
            if len(msg) == 0:
                toast.show_toast("Alarm", "Time's up", duration=10, threaded=True)
            else:
                toast.show_toast("Reminder", msg, duration=10, threaded=True)
            while True:
                k = 1
        except KeyboardInterrupt:
            print('Alarm turned off')
            sys.exit(1)
    except:
        tim = gideon_asks("I did not understand you, alarm for what time?")
        set_alarm(tim)


def sound_alarm():
    playsound.playsound('1.mp3', True)
    t.sleep(1)


def alarm_freq(day):
    if day == "today":
        day = tell_day()
    elif day == "tomorrow":
        tell_day()
        day = next_day
    return day


def auto_alarm_save():
    alarm_time_list = []
    alarm_day_list = []
    msg_list = []
    for thread in all_threads:
        print(thread)
        alarm_time_list.append(str(thread).split("(")[1].split(",")[0].split("thread_")[1])
        print(str(thread).split("(")[1].split(","))
    print(alarm_time_list)


def set_reminder(rem_time, msg):
    set_alarm(rem_time, msg)


def time_compare(p_t, c_t, n_t):
    return t.strptime(p_t, '%H:%M') <= t.strptime(c_t, '%H:%M') <= t.strptime(n_t, '%H:%M')


def class_check(day, c_hr, c_minu):
    c_t = str(c_hr) + ":" + str(c_minu)
    global class_id
    df = pd.read_excel('sem6tt.xlsx')
    df=df.fillna('Free')
    tt = df.to_dict()
    if time_compare("8:30", c_t, "15:35"):
        if time_compare("8:30", c_t, "9:20"):
            tt_hr = 0
        elif time_compare("9:30", c_t, "10:20"):
            tt_hr = 1
        elif time_compare("10:45", c_t, "11:35"):
            tt_hr = 2
        elif time_compare("11:45", c_t, "12:35"):
            tt_hr = 3
        elif time_compare("13:45", c_t, "14:35"):
            tt_hr = 4
        elif time_compare("14:45", c_t, "15:35"):
            tt_hr = 5
        else:
            tt_hr = 6
    else:
        tt_hr = -1
    if tt_hr in [0,1,2,3,4,5]:
        class_name = tt[day][tt_hr]
    elif tt_hr == 6:
        class_name = 'Break'
    elif tt_hr == -1:
        class_name = 'none'
    return class_name


def classes_day(day):
    c_hr = int(t.strftime("%H:%M").split(":")[0])
    c_day = tell_day()
    if c_day != day and c_hr >= 9:
        c_hr = 9
    class_list = ['none']
    if day != 'Saturday' and day != 'Sunday':
        for i in range(0, 8):
            if class_list[len(class_list) - 1] != class_check(day, c_hr, '00'):
                class_list.append(class_check(day, c_hr, '00'))
            c_hr += 1
        while class_list.count('Break'):
            class_list.remove('Break')
        while class_list.count('none'):
            class_list.remove('none')
        suf = ''
        if len(class_list) > 1 or len(class_list) == 0:
            suf = "classes"
        elif len(class_list) == 1:
            suf = "class"
        gideon_speaks(day + "\'s Time Table shows " + str(len(class_list)) + " " + suf)
        c_hr = int(t.strftime("%H:%M").split(":")[0])
        c_day = tell_day()
        if c_day != day and c_hr >= 9:
            c_hr = 9
        for c in class_list:
            if "Lab" in c:
                gideon_speaks(c + " in hours " + str(c_hr - 9 + 1) + " and " + str(c_hr - 9 + 2))
                c_hr += 2
            else:
                gideon_speaks(c + " in hour " + str(c_hr - 9 + 1))
                c_hr += 1
    else:
        gideon_speaks("You have nothing on your Time Table")


def auto_class_check():
    c_hr, c_minu, c_m = tell_time()
    if c_m == 'p.m.' and c_hr != 12:
        c_hr += 12
    c_t = str(c_hr) + ":" + str(c_minu)
    while True:
        if time_compare("8:20", c_t, "8:30") or time_compare("9:25", c_t, "9:35") or time_compare("10:35", c_t, "10:50") or time_compare("11:40", c_t, "11:50") or time_compare("13:35", c_t, "13:50") or time_compare("14:40", c_t, "14:50"):
            auto = class_check(tell_day(), c_hr, c_minu)
            if auto != 'none':
                if "Lab" in auto:
                    gideon_speaks("You have " + auto + " now")
                    toast.show_toast("Gideon", auto+" class", duration=10, threaded=True)
                    t.sleep(7200)
                    with_goto(auto_class_check)
                else:
                    gideon_speaks("You have "+auto+" class now")
                    toast.show_toast("Gideon", auto + " class", duration=10, threaded=True)
                    t.sleep(3600)
                    with_goto(auto_class_check)
        else:
            t.sleep(60)
            with_goto(auto_class_check)


def face_recog():
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    face_locations = []
    face_encodings = []
    global face_names
    face_names = []
    process_this_frame = True

    while True:
        ret, frame = video_capture.read()
        rgb_frame = frame[:, :, ::-1]

        if process_this_frame:
            face_locations = fr.face_locations(rgb_frame)
            face_encodings = fr.face_encodings(rgb_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                matches = fr.compare_faces(known_face_encodings, face_encoding)
                fname = "Unknown"
                face_distances = fr.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    fname = known_face_names[int(best_match_index)]
                face_names.append(fname)
        process_this_frame = not process_this_frame
        for (top, right, bottom, left), fname in zip(face_locations, face_names):
            # cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, fname, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        # cv2.imshow('Video', frame)
        # Hit 'q' on the keyboard to quit!
        if (cv2.waitKey(1) & 0xFF == ord('q')) or len(face_names) != 0:
            break
    video_capture.release()
    cv2.destroyAllWindows()
    return face_names


def wiki(input_gideon):
    if 'wikipedia' in input_gideon:
        statement = input_gideon.replace("wikipedia ", "")
        try:
            results = wikipedia.summary(statement, sentences=2)
            gideon_speaks("According to Wikipedia, " + results)
        except:
            gideon_speaks("Could not find anything about " + statement)


def google_search(input_gideon=""):
    if "for" in input_gideon:
        ind_for = input_gideon.lower().split().index('for')
        ind_on = input_gideon.lower().split().index('on')
    elif "how" in input_gideon.lower():
        ind_for = input_gideon.lower().split().index('how')
        ind_on = len(input_gideon)
    else:
        ind_for = input_gideon.lower().split().index('search')
        ind_on = input_gideon.lower().split().index('on')
    if "how" not in input_gideon:
        query_l = input_gideon.split(' ')[ind_for + 1:ind_on]
    else:
        query_l = input_gideon.split(' ')[ind_for:ind_on]
    query = '+'.join(query_l)
    query2 = ' '.join(query_l)
    process = multiprocessing.Process(target=wiki, name="wikipedia", args=("wikipedia "+query2,))
    process.start()
    t.sleep(3)
    gideon_speaks("Showing results for " + query2 + " on Google")
    gs = 'https://www.google.in/#q=' + query
    webbrowser.open(gs)
    


def amazon_search(input_gideon=""):
    if "for" in input_gideon:
        ind_for = input_gideon.lower().split().index('for')
        ind_on = input_gideon.lower().split().index('on')
    else:
        ind_for = input_gideon.lower().split().index('search')
        ind_on = input_gideon.lower().split().index('on')
    query_l = input_gideon.split(' ')[ind_for + 1:ind_on]
    query = '+'.join(query_l)
    query2 = ' '.join(query_l)
    gideon_speaks("Showing results for " + query2 + " on Amazon")
    gs = 'https://www.amazon.in/s?k=' + query
    webbrowser.open(gs)


def youtube_play(input_gideon=""):
    if "for" in input_gideon:
        ind_for = input_gideon.lower().split().index('for')
    elif "open" in input_gideon.lower():
        ind_for = input_gideon.lower().split().index('open')
    elif "play" in input_gideon.lower():
        ind_for = input_gideon.lower().split().index('play')
    else:
        ind_for = input_gideon.lower().split().index('search')
    if "on" in input_gideon:
        ind_on = input_gideon.lower().split().index('on')
    else:
        ind_on = input_gideon.split().index('Youtube')
    if "song" in input_gideon.lower() or "songs" in input_gideon.lower():
        if "song" in input_gideon:
            try:
                ind_on = input_gideon.lower().split().index('song')
            except:
                pass
        else:
            try:
                ind_on = input_gideon.split().index('songs')
            except:
                pass
    else:
        ind_on = input_gideon.split().index('on')
    query_l = input_gideon.split(' ')[ind_for + 1:ind_on]
    query = '+'.join(query_l)
    query2 = ' '.join(query_l)
    gideon_speaks("Opening " + query2 + " on Youtube")
    gs = 'https://m.youtube.com/results?search_query=' + query
    webbrowser.open(gs)
    if "play" in input_gideon.lower() or "open" in input_gideon.lower():
        gideon_speaks("Playing " + query2 + " on Youtube")
        t.sleep(2)
        pa.press('tab')
        t.sleep(0.9)
        pa.press('enter')


def spotify_play(input_gideon=""):
    pa.hotkey('win', 's')
    t.sleep(2)
    pa.typewrite("spotify")
    t.sleep(1.5)
    pa.press('enter')
    t.sleep(5)
    pa.hotkey('alt', 'space')
    pa.press('x')
    if "for" in input_gideon:
        ind_for = input_gideon.lower().split().index('for')
    elif "open" in input_gideon.lower():
        ind_for = input_gideon.lower().split().index('open')
    elif "play" in input_gideon.lower():
        ind_for = input_gideon.lower().split().index('play')
    else:
        ind_for = input_gideon.lower().split().index('search')
    if "on" in input_gideon:
        ind_on = input_gideon.lower().split().index('on')
    else:
        ind_on = input_gideon.split().index('spotify')
    if "song" in input_gideon.lower() or "songs" in input_gideon.lower():
        if "song" in input_gideon:
            try:
                ind_on = input_gideon.lower().split().index('song')
            except:
                pass
        else:
            try:
                ind_on = input_gideon.split().index('songs')
            except:
                pass
    else:
        ind_on = input_gideon.split().index('on')
    query_l = input_gideon.split(' ')[ind_for + 1:ind_on]
    query = ' '.join(query_l)
    query = query.capitalize()
    gideon_speaks("Playing " + query + " on spotify")
    pa.hotkey('ctrl', 'l')
    t.sleep(1)
    pa.typewrite(query)
    if "play" in input_gideon.lower() or "open" in input_gideon.lower():
        t.sleep(2.5)
        pa.click(382, 254)


def restart():
    pa.hotkey('ctrl', 'f5')


# =============================================================================
# def conversation(input):
#     user_input = input
#     response = bot.get_response(user_input)
#     if "?" in str(response):
#         user_input = gideon_asks(str(response))
#         with_goto(conversation(user_input))
#     else:
#         gideon_speaks(str(response))
#     conversation(get_conversation())
# =============================================================================


# =============================================================================
# def play_video(vidpath):
#     window = pyglet.window.Window()
#     player = pyglet.media.Player()
#     source = pyglet.media.StreamingSource()
#     MediaLoad = pyglet.media.load(vidpath)
# 
#     player.queue(MediaLoad)
#     player.play()
# 
#     @window.event
#     def on_draw():
#         if player.source and player.source.video_format:
#             player.get_texture().blit(50, 50)
# =============================================================================


def battery_check():
    # gives the current battery and charging status of the system
    battery = psutil.sensors_battery()
    h, m, s = secs2hours(battery.secsleft)
    if battery.power_plugged:
        if battery.percent != 100:
            chrg_stat = "charging"
        else:
            chrg_stat = "Fully charged"
        desc = "."
    else:
        if battery.percent >= 30:
            chrg_stat = "discharging"
        else:
            chrg_stat = "running on backup power, connect to a power source"
        desc = ". Should last for " + str(h) + " hours " + str(m) + " minutes"
    gideon_speaks("Power at " + str(battery.percent) + "% and " + chrg_stat + desc)


def auto_battery_check():
    while True:
        battery = psutil.sensors_battery()
        if battery.power_plugged and battery.percent == 100:
            toast.show_toast("Gideon", "Battery is fully charged", duration=10, threaded=True)
            gideon_speaks("Battery is fully charged")
            t.sleep(1800)
            continue
        elif battery.percent == 30 and not battery.power_plugged:
            toast.show_toast("Gideon", "Battery : 30% ", duration=10, threaded=True)
            gideon_speaks("Power at " + str(battery.percent) + "%, switching to power saving mode")
            t.sleep(300)
            continue
        elif battery.percent == 20 and not battery.power_plugged:
            chrg_stat = "critically low"
            toast.show_toast("Gideon", "Battery : 20% ", duration=10, threaded=True)
            gideon_speaks("Power at " + str(battery.percent) + "%")
            t.sleep(300)
            continue
        elif battery.percent < 20 and not battery.power_plugged:
            chrg_stat = "critically low"
            toast.show_toast("Gideon", "Battery : " + chrg_stat + " ", duration=10, threaded=True)
            gideon_speaks("Power at " + str(battery.percent) + "% and " + chrg_stat + ".")
            t.sleep(300)
            continue


def process_text(input_gideon):
    # processes the text and calls the respective methods according to detected keywords in the input_gideon statement
    if len(input_gideon.split()) == 1 and "gideon" in input_gideon.lower():
        input_gideon = gideon_asks("")
        process_text(input_gideon)
    elif "and" in input_gideon or "then" in input_gideon:
        if "and" in input_gideon:
            pass
        else:
            pass
        p_list = input_gideon.split('and')
        process_text(p_list[0])
        process_text(p_list[1])
# =============================================================================
#     elif ("reboot" in input_gideon or "train" in input_gideon) and ("speech" in input_gideon or "speed") and "drive" in input_gideon:
#         gideon_speaks("Rebooting speech drive")
#         p = multiprocessing.Process(target=train_bot, name="Speech drive training", daemon=False)
#         p.start()
# =============================================================================
    elif "restart" in input_gideon and "program" in input_gideon:
        pa.hotkey('ctrl', 'f5')
    elif "hello" in input_gideon or "hi" in input_gideon or "hai" in input_gideon:
        gideon_speaks("Hello")
    elif ("play" in input_gideon.lower() or "open" in input_gideon.lower() or "search" in input_gideon.lower()) and (
            "YouTube" in input_gideon):
        youtube_play(input_gideon)
    elif ("search" in input_gideon and "google" in input_gideon.lower()) or "google" in input_gideon.lower():
        google_search(input_gideon)
    elif "search" in input_gideon and "YouTube" not in input_gideon and "Amazon" not in input_gideon:
        input_gideon += " on google"
        google_search(input_gideon)
    elif "how" in input_gideon.lower() and "weather" not in input_gideon.lower():
        google_search(input_gideon)
    elif ("search" in input_gideon and "amazon" in input_gideon.lower()) or "amazon" in input_gideon.lower() or (
            "order" in input_gideon.lower() or "buy" in input_gideon.lower() or "look for" in input_gideon.lower() or "purchase" in input_gideon.lower()):
        if "on amazon" not in input_gideon:
            input_gideon += " on amazon"
        if "order" in input_gideon:
            input_gideon = input_gideon.replace("order", "search for")
        elif "buy" in input_gideon:
            input_gideon = input_gideon.replace("buy", "search for")
        elif "look for" in input_gideon:
            input_gideon = input_gideon.replace("look for", "search for")
        elif "purchase" in input_gideon.lower():
            input_gideon = input_gideon.replace("purchase", "search for")
        amazon_search(input_gideon)
    elif "about" in input_gideon or "wikipedia" in input_gideon.lower():
        query = input_gideon.replace("wikipedia", "")
        query = query.split(" about ")[1]
        wiki("wikipedia " + query)
    elif "Gmail" in input_gideon and "open" in input_gideon:
        gs = 'https://mail.google.com/mail/u/0/#inbox'
        gideon_speaks("Opening Gmail")
        webbrowser.open(gs)
    elif "Outlook" in input_gideon and "open" in input_gideon:
        gs = 'http://outlook.com/mail/inbox'
        gideon_speaks("Opening Outlook")
        webbrowser.open(gs)
    elif ("play" in input_gideon or "open" in input_gideon) and ("Playlist" in input_gideon or (
            "music" in input_gideon or "songs" in input_gideon.lower() or "song" in input_gideon.lower())) and (
            "next" not in input_gideon.lower() and "previous" not in input_gideon.lower()):
        if "YouTube" in input_gideon or "spotify" in input_gideon.lower():
            if "YouTube" in input_gideon:
                app_name = "YouTube"
            else:
                app_name = "spotify"
        else:
            app_name = gideon_asks("How would you like me to play the song, on spotify or on Youtube?")
        if "spotify" in app_name.lower():
            input_gideon += " on spotify"
            if "playlist" in input_gideon:
                input_gideon.replace("playlist ", "")
            spotify_play(input_gideon.lower())
        else:
            input_gideon += " on YouTube"
            youtube_play(input_gideon)
    elif "alarm" in input_gideon.lower() and "set" in input_gideon.lower():
        msg = ""
        if "for" in input_gideon:
            alarm = input_gideon.split("for ")[1]
        else:
            alarm = gideon_asks("Alarm for what time?")
        if "today" in input_gideon:
            a_day = tell_day()
        elif "tomorrow" in input_gideon:
            tell_day()
            a_day = next_day
        elif "day" in input_gideon:
            a_day = input_gideon.split("on ")[1]
        else:
            a_day = tell_day()
        prcss = multiprocessing.Process(target=set_alarm, name="alarm_thread_" + alarm + "," + a_day + "," + msg, args=(alarm, a_day, msg))
        prcss.start()
        all_threads.append(prcss)
    elif "reminder" in input_gideon.lower() and "set" in input_gideon.lower():
        if "for" in input_gideon:
            alarm = input_gideon.split("for ")[1]
        else:
            alarm = gideon_asks("Reminder for what time?")
        msg = gideon_asks("what is the reminder for?")
        if "today" in input_gideon:
            a_day = tell_day()
        elif "tomorrow" in input_gideon:
            tell_day()
            a_day = next_day
        elif "day" in input_gideon:
            a_day = input_gideon.split("on ")[1]
        else:
            a_day = tell_day()
        prcss = multiprocessing.Process(target=set_alarm, name="alarm_thread_" + alarm + "," + a_day + "," + msg, args=(alarm, a_day, msg))
        prcss.start()
        all_threads.append(prcss)
    elif "dismiss" in input_gideon and "alarm" in input_gideon:
        c_hr, c_minu, c_m = tell_time()
        all_alarms = []
        for thread in all_threads:
            all_alarms.append(str(thread).split("(")[1].split(",")[0])
        try:
            dismiss_alarm = all_alarms.index("alarm_thread_" + str(c_hr) + ":" + c_minu + " " + c_m)
            try:
                multiprocessing.Process.terminate(all_threads[dismiss_alarm])
                all_threads.pop(dismiss_alarm)
                all_alarms.pop(dismiss_alarm)
                gideon_speaks("Alarm has been dismissed")
            except:
                gideon_speaks("Could not dismiss alarm")
        except:
            gideon_speaks("No alarms found")
    elif "delete" in input_gideon and "alarm" in input_gideon:
        all_alarms = []
        for thread in all_threads:
            all_alarms.append(str(thread).split("(")[1].split(",")[0].split("thread_")[1])
        print(all_alarms)
        del_time = gideon_asks("Which alarm should I delete?")
        if del_time != "cancel" or "none":
            try:
                multiprocessing.Process.terminate(all_threads[all_alarms.index(del_time)])
                all_threads.pop(all_alarms.index(del_time))
                all_alarms.pop(all_alarms.index(del_time))
                gideon_speaks(del_time + " alarm has been deleted")
            except:
                gideon_speaks("Could not find " + del_time + " alarm")
    elif "event" in input_gideon.lower() and "create" in input_gideon.lower():
        create_event()
    elif ("event" in input_gideon.lower() and "list" in input_gideon.lower()) or "calendar" in input_gideon.lower():
        if "tomorrow" in input_gideon.lower():
            list_events("tomorrow")
        else:
            list_events()
    elif "pause video" in input_gideon or "resume video" in input_gideon:
        pa.press('space')
    elif "close" in input_gideon.lower() and "window" in input_gideon.lower():
        pa.hotkey('alt', 'f4')
    elif "minimise" in input_gideon.lower() and "window" in input_gideon.lower():
        pa.hotkey('alt', 'space')
        pa.press('n')
    elif "maximise" in input_gideon.lower() and "window" in input_gideon.lower():
        pa.hotkey('alt', 'space')
        pa.press('x')
    elif "windows search" in input_gideon.lower():
        pa.hotkey('win', 's')
    elif "notifications" in input_gideon.lower():
        pa.hotkey('win', 'a')
    elif "select" in input_gideon and "all" in input_gideon:
        pa.hotkey('ctrl', 'a')
    elif "save" in input_gideon:
        pa.hotkey('ctrl', 's')
    elif "copy" in input_gideon:
        if "in" in input_gideon:
            ind_in = input_gideon.lower().split().index('in')
            add = input_gideon.split('in')
            open_loc(add[ind_in + 1])
        elif "from" in input_gideon:
            ind_in = input_gideon.lower().split().index('from')
            add = input_gideon.split('from')
            open_loc(add[ind_in + 1])
        if "all" in input_gideon:
            pa.hotkey('ctrl', 'a')
        pa.hotkey('ctrl', 'c')
    elif "cut" in input_gideon:
        pa.hotkey('ctrl', 'x')
    elif "paste" in input_gideon:
        if "in" in input_gideon:
            add = input_gideon.split('in')
            open_loc("open" + add[1])
        elif "from" in input_gideon:
            add = input_gideon.split('from')
            open_loc("open" + add[1])
        t.sleep(2)
        pa.hotkey('ctrl', 'v')
    elif "shutdown" in input_gideon.lower() and ("system" in input_gideon.lower() or "device" in input_gideon.lower() or "computer" in input_gideon.lower()):
                auth = gideon_asks("Are you sure you want me to shutdown the system?")
                if "yes" in str(auth).lower() or "yep" in str(auth).lower() or "yeah" in str(auth).lower():
                    if hr <= 20:
                        gideon_speaks("Good Bye, have a nice day")
                    else:
                        gideon_speaks("Good night " + master_user)
                    os.system("shutdown /s /t  30")
    elif "restart" in input_gideon.lower() and ("system" in input_gideon.lower() or "device" in input_gideon.lower() or "computer" in input_gideon.lower()):
                auth = gideon_asks("Are you sure you want me to restart the system?")
                if "yes" in str(auth).lower() or "yep" in str(auth).lower() or "yeah" in str(auth).lower():
                    gideon_speaks("Restarting System ")
                    os.system("shutdown /r /t  30")
    elif "open" in input_gideon and "new" in input_gideon and ("file" in input_gideon or "document" in input_gideon):
        if "word" in input_gideon.lower() or "text" in input_gideon.lower():
            pa.hotkey('win', 's')
            t.sleep(1)
            pa.typewrite("word")
            t.sleep(0.5)
            pa.press('enter')
            t.sleep(9)
            pa.click(336, 237)
        if "index" in input_gideon.lower():
            t.sleep(5)
            pa.hotkey('ctrl', 's')
            t.sleep(0.5)
            f_name_l = input_gideon.split('as')
            f_name = f_name_l[1]
            f_name = f_name.capitalize()
            pa.typewrite(f_name)
            loc = gideon_asks("Would you like me to save it in amrita blr folder")
            if "yes" in loc:
                t.sleep(0.5)
                pa.click(1064, 672)
            else:
                pass
    elif ("pause" in input_gideon or "resume" in input_gideon or "play" in input_gideon) and (
            "music" in input_gideon or "audio" in input_gideon):
        pa.press('playpause')
    elif ("mute" in input_gideon or "unmute" in input_gideon) and not (
            "mic" in input_gideon or "microphone" in input_gideon):
        pa.press('volumemute')
    elif ("mute" in input_gideon or "unmute" in input_gideon) and (
            "mic" in input_gideon or "microphone" in input_gideon):
        pa.hotkey('ctrl', 'shift', 'm')
    elif "increase" in input_gideon and "brightness" in input_gideon:
        pa.hotkey('fn', 'f3')
    elif ("decrease" in input_gideon or "reduce" in input_gideon) and "brightness" in input_gideon:
        pa.hotkey('fn', 'f2')
    elif "increase" in input_gideon and "volume" in input_gideon and "%" in input_gideon:
        indp = input_gideon.lower().find('%')
        p = int(input_gideon[indp - 2:indp])
        p = int(p / 2)
        for i in range(1, p):
            pa.press('volumeup')
    elif "decrease" in input_gideon and "volume" in input_gideon:
        indp = input_gideon.lower().find('%')
        p = int(input_gideon[indp - 2:indp])
        p = int(p / 2)
        for i in range(1, p):
            pa.press('volumedown')
    elif "play next song" in input_gideon or "play next track" in input_gideon or "skip song" in input_gideon or "skip track" in input_gideon or "next song" in input_gideon:
        pa.press('nexttrack')
    elif "play previous song" in input_gideon or "play previous track" in input_gideon or "previous song" in input_gideon:
        pa.press('prevtrack', 2, 0.4)
    elif "restart song" in input_gideon or (
            "start from" in input_gideon.lower() and "beginning" in input_gideon.lower()) or "previous song" in input_gideon:
        pa.press('prevtrack')
    elif "switch to desktop two" in input_gideon:
        pa.hotkey('ctrl', 'Win', 'right')
    elif "switch to desktop one" in input_gideon:
        pa.hotkey('ctrl', 'Win', 'left')
    elif ("time" in input_gideon or "what time is it" in input_gideon or "What is the time" in input_gideon) and "table" not in input_gideon:
        hr1, minu1, m1 = tell_time()
        gideon_speaks("The time is " + str(hr1) + ":" + str(minu1) + " " + m1)
    elif "date" in input_gideon or "what is the date" in input_gideon:
        tell_date()
        gideon_speaks("Today is " + month + " " + str(date) + ", " + year)
    elif "what day" in input_gideon or "what is the day" in input_gideon:
        gideon_speaks("Today is " + tell_day())
    elif "who am i" in input_gideon.lower():
        names_list = face_recog()
        names = ''
        if len(names_list) == 1:
            names = names_list[0]
        elif len(names_list) >= 1:
            names = ''
            for name in names_list:
                names += name + ", "
        gideon_speaks("I am currently talking to "+ names)
    elif "what classes" in input_gideon or ("check" in input_gideon and "time table" in input_gideon):
        if "today" in input_gideon:
            classes_day(tell_day())
        elif "tomorrow" in input_gideon:
            tell_day()
            classes_day(next_day)
        elif "day" in input_gideon:
            day = input_gideon.split("on ")[2]
            classes_day(day)
        else:
            classes_day(tell_day())
    elif "time table" in input_gideon:
        open_loc('open timetable')
    elif "what class do I have now" in input_gideon:
        c_hr = int(t.strftime("%H:%M").split(":")[0])
        c_minu = int(t.strftime("%H:%M").split(":")[1])
        class_name = class_check(tell_day(), c_hr, c_minu)
        response = ''
        if class_name != "none":
            response = gideon_asks("You have " + class_name + " class now, Would you like me to open the class")
        else:
            gideon_speaks("You have no class right now")
        if "yes" in response or "Yes" in response:
            open_loc("open microsoft teams")
            class_check(tell_day(), c_hr, c_minu)
            t.sleep(1.5)
            pa.hotkey('ctrl', 'e')
            t.sleep(1)
            print(class_id)
            pa.typewrite(class_id)
            t.sleep(0.2)
            pa.press('down')
            t.sleep(0.5)
            pa.press('enter')
        else:
            pass
    elif "activate" in input_gideon.lower() and ("hand control" in input_gideon.lower() or "virtual mouse" in input_gideon.lower()):
        process = multiprocessing.Process(target=avm.virtualMouse, name="Virtual_Mouse", daemon=False)
        process.start()
        # avm.virtualMouse()
    elif "open" in input_gideon.lower() or "play" in input_gideon.lower():
        if "this pc" in input_gideon.lower() or "explorer" in input_gideon.lower():
            pa.hotkey('Win', 'e')
        elif "settings" in input_gideon.lower():
            open_settings(input_gideon)
        else:
            open_loc(input_gideon)
    elif "battery" in input_gideon or "power" in input_gideon:
        battery_check()
    elif "weather" in input_gideon:
        if "in" in input_gideon:
            loc = input_gideon.split(' in ')
            try:
                temp_cur, cloud_coverage, humidity, wind_speed = weather(loc[1])
                desc = "The weather in " + loc[1] + " is " + str(
                    round(temp_cur)) + " degrees with " + cloud_coverage.capitalize() + ". It is " + str(
                    humidity) + "% Humid with a wind speed of " + str(wind_speed) + " MpH"
            except:
                desc = "Unable to locate " + loc[1] + " on the map"
        else:
            try:
                temp_cur, cloud_coverage, humidity, wind_speed = weather()
                desc = "The weather in Kakinada is " + str(
                    round(temp_cur)) + " degrees with " + cloud_coverage.capitalize() + ". It is " + str(
                    humidity) + "% Humid with a wind speed of " + str(wind_speed) + " MpH"
            except:
                desc = "Unable to locate " + loc[1] + " on the map"
        gideon_speaks(desc)
# =============================================================================
#     else:
#         conversation(input_gideon)
# =============================================================================


if __name__ == "__main__":
    # welcome()
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    CREDENTIALS_FILE = 'credentials.json'
    hr, minu, m = tell_time()
    tell_date()
    tell_day()
    if m == 'p.m.' and hr != 12:
        hr += 12
    ti = str(hr) + ":" + str(minu)
    temp, cloud, humid, wind = weather()
    icon_path = ''
    if hr < 18:
        if cloud == 'clear sky' and wind < 6:
            icon_path = "./weather_icons/sunny.ico"
        elif wind >= 6:
            if cloud == "clear sky":
                icon_path = "./weather_icons/wind.ico"
            elif cloud != "clear sky":
                icon_path = "./weather_icons/cloudy windy morning.ico"
        elif cloud != "clear sky" and wind < 6:
            icon_path = "./weather_icons/cloudy morning.ico"
    else:
        if cloud == 'clear sky' and wind < 6:
            icon_path = "./weather_icons/clear night.ico"
        elif cloud != "clear sky" and wind < 6:
            icon_path = "./weather_icons/cloudy night.ico"
        elif cloud != "clear sky" and wind >= 6:
            icon_path = "./weather_icons/windcloudy.ico"
    known_face_encodings = []
    known_face_names = []
    with open("Face Encodings.dat", 'rb') as f:
        all_face_encodings = pickle.load(f)
    for i in range(0, len(all_face_encodings) - 1):
        key, val = next(iter(all_face_encodings.items()))
        known_face_encodings.append(val)
        known_face_names.append(key)
    gideon_speaks("Standby, for Retinal and Biometric scan")
# =============================================================================
#     vidpath="Face_id.mp4"
#     process = multiprocessing.Process(target=play_video, name="play_video", args=(vidpath), daemon=False)
#     process.start()
# =============================================================================
    master_user = "Your name which you give for your Face image"
    names_list = face_recog()
    names = ''
    if len(names_list) == 1:
        names = names_list[0]
    elif len(names_list) >= 1:
        names = ''
        for name in names_list:
            names += name + ", "
    if master_user in names:
        gideon_speaks("Retinal and Biometric scan complete")
        gideon_speaks("Identity confirmed")
        toast.show_toast("Gideon", "Welcome, " + names + " ", icon_path=icon_path, duration=10, threaded=True)
        # gideon_speaks("Hello " + names + ", I am Gideon, an Interactive Artificial Consciousness programmed to operate this device's Critical Systems and to aid you in your daily routines")
        gideon_speaks("Hello " + names)
        # welcome()
        process = multiprocessing.Process(target=auto_battery_check, name="auto_battery_check", daemon=False)
        process.start()
# =============================================================================
#         process = multiprocessing.Process(target=auto_update_calendar, name="auto_update_calendar", daemon=False)
#         process.start()
# =============================================================================
# =============================================================================
#         process = multiprocessing.Process(target=auto_class_check, name="auto_class_check", daemon=False)
#         process.start()
# =============================================================================
        process = multiprocessing.Process(target=auto_weather_check, name="auto_weather_check", daemon=False)
        process.start()
        while 1:
            text = str(get_audio())
            if text == 0:
                continue
            elif "goodbye" in str(text).lower() or "bye" in str(text).lower() or "sleep" in str(text).lower():
                auth = gideon_asks("Are you sure there is nothing else I can do for you?")
                # auth = pa.confirm(text="Close \'gideon\' program ?", title='gideon', buttons=['Yes', 'Cancel'])
                # pa.confirm("Close \'gideon\' program")
                if "yes" in str(auth).lower() or "yep" in str(auth).lower() or "yeah" in str(auth).lower():
                    if hr <= 20:
                        gideon_speaks("Good Bye, have a nice day")
                    else:
                        gideon_speaks("Good night " + master_user)
                    break
            process_text(text)
    else:
        playsound.playsound('ironman_unauthorized.mp3')
# =============================================================================
#         if len(names_list) == 1 and names == 'Unknown':
#             auth = gideon_asks("Your ID doesn't seem to be in my database, would you like to add your face ID?")
#             if "yes" in str(auth).lower() or "yep" in str(auth).lower() or "yeah" in str(auth).lower():
#                 camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#                 return_value, image = camera.read()
#                 name = input("Enter name: ")
#                 cv2.imwrite('E:/amrita_blr/Programming/python_2020/Faces/' + name + '.jpg', image)
#                 camera.release()
#                 with open("Face Encodings.dat", 'rb') as f:
#                     all_face_encodings = pickle.load(f)
#                 image1 = fr.load_image_file("./Faces/" + name + ".jpg")
#                 all_face_encodings[name] = fr.face_encodings(image1)[0]
#                 with open("Face Encodings.dat", 'wb') as f:
#                     pickle.dump(all_face_encodings, f)
#         elif len(names_list) == 1 and names != 'Unknown':
#             names.replace(master_user, "")
#         elif len(names_list) >= 1:
#             names = ''
#             for name in names_list:
#                 names += name + ", "
#             names.replace(master_user + ", ", "")
# =============================================================================
        # gideon_speaks("You are not authorized to access this area " + names)
        t.sleep(5)
        restart()
