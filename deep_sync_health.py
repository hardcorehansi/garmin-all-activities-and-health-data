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

# Release 2: Angepasst auf HH:MM:SS Format
def minutes_to_hms(minutes):
    try:
        if not minutes or minutes == 0: return "00:00:00"
        total_seconds = int(float(minutes) * 60)
        # timedelta erzeugt HH:MM:SS, zfill sorgt für führende Nullen
        return str(timedelta(seconds=total_seconds)).zfill(8)
    except:
        return "00:00:00"

def sync_health():
    # --- DATUMSBEREICH EINSTELLEN ---
    start_date_str = "2024-01-01"  # DEIN START (VON)
    end_date_str = "2026-12-31"    # DEIN ENDE (BIS)
    
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    print(f"🚀 Starte Deep Health Sync von {start_date_str} bis {end_date_str}...")
    
    try:
        client = get_garmin_client()
    except Exception as e:
        print(f"❌ Garmin Login fehlgeschlagen: {e}")
        return

    # Google Setup
    gc = gspread.authorize(Credentials.from_service_account_info(
        json.loads(os.environ.get('GOOGLE_CREDENTIALS')), 
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    ))
    sh = gc.open_by_key(os.environ.get('SHEET_ID'))
    health_sheet = sh.worksheet("Health")

    # Vorhandene Daten laden um Dubletten zu vermeiden
    existing_dates = [row[0] for row in health_sheet.get_all_values()]

    current_date = start_date
    while current_date <= end_date:
        target_date = current_date.strftime("%Y-%m-%d")
        
        if target_date in existing_dates:
            print(f"⏩ {target_date} bereits vorhanden. Überspringe...")
            current_date += timedelta(days=1)
            continue

        print(f"🔍 Hole Daten für {target_date}...")
        
        weight, steps, rhr, sleep_min, hrv, bp_sys, bp_dia = 0, 0, 0, 0, 0, 0, 0
        any_data = False

        # 1. GEWICHT
        try:
            body = client.get_body_composition(target_date)
            weight = body.get('totalAverage', {}).get('weight', 0) / 1000
            if weight > 0: any_data = True
        except: pass

        # 2. SCHRITTE & RHR
        try:
            summary = client.get_user_summary(target_date)
            steps = summary.get('totalSteps', 0)
            rhr = summary.get('restingHeartRate', 0)
            if steps > 0 or rhr > 0: any_data = True
        except: pass

        # 3. SCHLAF
        try:
            sleep_data = client.get_sleep_data(target_date)
            sleep_min = sleep_data.get('dailySleepDTO', {}).get('sleepTimeSeconds', 0) / 60
            if sleep_min > 0: any_data = True
        except: pass

        # 4. HRV
        try:
            hrv_data = client.get_hrv_data(target_date)
            hrv = hrv_data.get('hrvSummary', {}).get('lastNightAvg', 0)
            if hrv > 0: any_data = True
        except: pass

        # 5. BLUTDRUCK
        try:
            bp_data = client.get_blood_pressure(target_date)
            summaries = bp_data.get('measurementSummaries', [])
            if summaries:
                measurements = summaries[0].get('measurements', [])
                if measurements:
                    bp_sys = measurements[-1].get('systolic', 0)
                    bp_dia = measurements[-1].get('diastolic', 0)
                    if bp_sys > 0: any_data = True
        except: pass

        # Speichern wenn Daten vorhanden
        if any_data:
            # Release 2: USER_ENTERED für automatische Datum- und Zeit-Erkennung
            health_sheet.append_row([
                target_date, 
                round(weight, 2), 
                steps, 
                minutes_to_hms(sleep_min), 
                rhr, 
                hrv, 
                bp_sys, 
                bp_dia
            ], value_input_option='USER_ENTERED')
            print(f"  ✅ Daten gespeichert.")
        else:
            print(f"  💤 Keine Daten gefunden.")

        time.sleep(1) # Kleine Pause für API Stabilität
        current_date += timedelta(days=1)

    print(f"🎉 Deep Health Sync abgeschlossen!")

if __name__ == "__main__":
    sync_health()
