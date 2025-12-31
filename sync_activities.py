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

def seconds_to_hms(seconds):
    if not seconds: return "00:00:00"
    return str(timedelta(seconds=int(float(seconds))))

def format_run_pace(ms):
    if not ms or ms <= 0: return ""
    seconds_per_km = 1000 / ms
    return f"{int(seconds_per_km // 60):02d}:{int(seconds_per_km % 60):02d}"

def format_swim_pace(ms):
    if not ms or ms <= 0: return ""
    seconds_100m = 100 / ms
    return f"{int(seconds_100m // 60):02d}:{int(seconds_100m % 60):02d}"

def sync_activities():
    # DYNAMISCHES DATUM: Heute minus 7 Tage
    lookback_days = 7
    stop_date = datetime.now() - timedelta(days=lookback_days)
    
    print(f"🚀 Starte Daily Sport Sync (Letzte {lookback_days} Tage)...")
    client = get_garmin_client()
    
    gc = gspread.authorize(Credentials.from_service_account_info(
        json.loads(os.environ.get('GOOGLE_CREDENTIALS')), 
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    ))
    sh = gc.open_by_key(os.environ.get('SHEET_ID'))
    sport_sheet = sh.worksheet("Sport")

    all_rows = sport_sheet.get_all_values()
    existing_ids = [row[10] for row in all_rows if len(row) > 10]
    
    # Wir laden die letzten 50 Aktivitäten (sollte für 7 Tage locker reichen)
    activities = client.get_activities(0, 50)
    new_rows = []

    for act in activities:
        start_time_str = act.get('startTimeLocal', '')
        act_date = datetime.strptime(start_time_str[:10], '%Y-%m-%d')
        
        if act_date < stop_date:
            continue

        act_id = str(act.get('activityId'))
        if act_id in existing_ids:
            continue

        type_key = act.get('activityType', {}).get('typeKey', '').lower()
        avg_speed_ms = round(act.get('averageSpeed', 0), 3)
        
        pace_run = format_run_pace(avg_speed_ms) if "running" in type_key else ""
        speed_bike = round(avg_speed_ms * 3.6, 2) if any(x in type_key for x in ["cycling", "biking"]) else ""
        pace_swim = format_swim_pace(avg_speed_ms) if "swimming" in type_key else ""

        new_rows.append([
            start_time_str[:10], act.get('activityName', '-'), type_key,
            round(act.get('distance', 0) / 1000, 2), seconds_to_hms(act.get('duration', 0)),
            act.get('calories', 0), act.get('averageHR', 0), act.get('maxHR', 0),
            0, round(act.get('elevationGain', 0), 0), act_id,
            avg_speed_ms, pace_run, speed_bike, pace_swim
        ])

    if new_rows:
        new_rows.reverse()
        sport_sheet.append_rows(new_rows)
        print(f"  ✅ {len(new_rows)} neue Aktivitäten hinzugefügt.")
    else:
        print("  💤 Alles aktuell.")

if __name__ == "__main__":
    sync_activities()
