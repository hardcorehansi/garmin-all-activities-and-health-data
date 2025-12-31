import os
import json
import time
import gspread
from garminconnect import Garmin
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

def get_garmin_client():
    client = Garmin(os.environ.get('GARMIN_EMAIL'), os.environ.get('GARMIN_PASSWORD'))
    client.login()
    return client

def minutes_to_hm(minutes):
    if not minutes or minutes == 0: return "00:00"
    td = str(timedelta(seconds=int(float(minutes) * 60)))
    parts = td.split(':')
    return f"{parts[0].zfill(2)}:{parts[1]}"

def sync_health():
    lookback_days = 7
    today = datetime.now()
    # Wir prüfen von gestern bis vor 7 Tagen
    start_date = today - timedelta(days=lookback_days)
    
    print(f"🚀 Starte Daily Health Sync (Letzte {lookback_days} Tage)...")
    client = get_garmin_client()
    
    gc = gspread.authorize(Credentials.from_service_account_info(
        json.loads(os.environ.get('GOOGLE_CREDENTIALS')), 
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    ))
    sh = gc.open_by_key(os.environ.get('SHEET_ID'))
    health_sheet = sh.worksheet("Health")
    existing_dates = [row[0] for row in health_sheet.get_all_values()]

    current_date = today - timedelta(days=1)
    while current_date >= start_date:
        target_date = current_date.strftime("%Y-%m-%d")
        
        if target_date in existing_dates:
            current_date -= timedelta(days=1)
            continue

        print(f"🔍 Check {target_date}...")
        weight, steps, rhr, sleep_min, hrv, bp_sys, bp_dia = 0, 0, 0, 0, 0, 0, 0
        any_data = False

        try:
            body = client.get_body_composition(target_date)
            weight = body.get('totalAverage', {}).get('weight', 0) / 1000
            if weight > 0: any_data = True
        except: pass

        try:
            summary = client.get_user_summary(target_date)
            steps = summary.get('totalSteps', 0)
            rhr = summary.get('restingHeartRate', 0)
            if steps > 0 or rhr > 0: any_data = True
        except: pass

        try:
            sleep_data = client.get_sleep_data(target_date)
            sleep_min = sleep_data.get('dailySleepDTO', {}).get('sleepTimeSeconds', 0) / 60
            if sleep_min > 0: any_data = True
        except: pass

        try:
            hrv_data = client.get_hrv_data(target_date)
            hrv = hrv_data.get('hrvSummary', {}).get('lastNightAvg', 0)
            if hrv > 0: any_data = True
        except: pass

        try:
            bp_data = client.get_blood_pressure(target_date)
            summaries = bp_data.get('measurementSummaries', [])
            if summaries and summaries[0].get('measurements'):
                m = summaries[0]['measurements'][-1]
                bp_sys, bp_dia = m.get('systolic', 0), m.get('diastolic', 0)
                if bp_sys > 0: any_data = True
        except: pass

        if any_data:
            health_sheet.append_row([target_date, round(weight, 2), steps, minutes_to_hm(sleep_min), rhr, hrv, bp_sys, bp_dia])
            print(f"  ✅ OK")
        
        time.sleep(2)
        current_date -= timedelta(days=1)

    print("🎉 Health Sync fertig.")

if __name__ == "__main__":
    sync_health()
