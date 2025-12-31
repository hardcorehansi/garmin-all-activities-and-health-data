# 🏃‍♂️ Garmin Health & Sport Sync to Google Sheet



![AI-Powered](https://img.shields.io/badge/Developed%20with-Google%20Gemini-blue?style=for-the-badge&logo=googlegemini)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Dieses Projekt synchronisiert automatisch deine **Sport-Aktivitäten** und **Gesundheitsdaten** (Gewicht, Schlaf, HRV, Blutdruck) von Garmin Connect in ein Google Spreadsheet. Die Automatisierung läuft über **GitHub Actions**, sodass kein eigener Server benötigt wird.

## 🌟 Features

- **Sport-Sync:** Erfasst Distanz, Zeit, Pace, Herzfrequenz und Höhenmeter.
- **Health-Sync:** Synchronisiert täglich Gewicht, Schritte, Schlafqualität, Ruhepuls und HRV.
- **Blutdruck-Spezial:** Unterstützt das Auslesen von manuell in Garmin Connect eingetragenen Blutdruckwerten.
- **Multisport-Support:** werden als eine Aktivität ausgegeben.
- **Ausgabe-Sportspezifische Pace:** Laufen km/min,Rad km/h u. Schwimmen min/100m in eigener spalte

## 🛠 Setup & Installation

### 1. Google Sheets Vorbereitung
1. Erstelle ein neues Google Spreadsheet mit den Blättern `Sport` und `Health`.
2. Erstelle in der Google Cloud Console einen **Service Account** und lade den `JSON Key` herunter.
3. Gib die E-Mail des Service Accounts in deinem Google Sheet als "Editor" frei.

### 2. GitHub Secrets
Hinterlege folgende Werte unter `Settings > Secrets and variables > Actions`:

| Secret | Beschreibung |
| :--- | :--- |
| `GARMIN_EMAIL` | Deine Garmin Connect E-Mail |
| `GARMIN_PASSWORD` | Dein Garmin Connect Passwort |
| `GOOGLE_CREDENTIALS` | Der komplette Inhalt der JSON-Key Datei |
| `SHEET_ID` | Die ID aus der URL deines Google Sheets |

### 3. Automatisierung (Cronjob)
Die Synchronisation erfolgt über GitHub Actions. Standardmäßig ist das System so eingestellt, dass es die letzten **7 Tage** prüft, um Dubletten zu vermeiden und API-Limits zu schonen.

## 🔄 Deep Sync (Historische Daten)

Neben dem täglichen Sync (letzte 7 Tage) verfügt dieses Repository über zwei spezialisierte Workflows für den Import deiner gesamten Historie:

### 1. Deep Sync Garmin (Sport-Aktivitäten + Health)
* **Ziel:** Lädt alle Sport-Aktivitäten ab dem Jahr **2010** bis heute und Health daten 
* **Workflow:** `Deep Sync Garmin bis 2010`
* **Besonderheit:** Nutzt eine größere Batch-Größe (50), um die Historie effizient abzuarbeiten. Dubletten werden automatisch anhand der Garmin-ID übersprungen. In Zeile 29 in deep_sync_garmin_data.py kann das Jahr eingestellt werden 

### 2. Deep Sync Health Data
* **Ziel:** Lädt Gesundheitsdaten (Gewicht, HRV, Blutdruck, Schlaf) für einen spezifischen Zeitraum.
* **Workflow:** `Deep Sync Health Data`
* **Konfiguration:** Im Skript deep_sync_health.py kann ein manuelles `start_date` und `end_date` gesetzt werden (Zeile 24!), um gezielt Jahre oder Monate nachzupflegen.

> [!TIP]
> Diese Workflows sollten manuell über den Tab **"Actions"** in GitHub gestartet werden, wenn eine vollständige Wiederherstellung der Daten im Google Sheet notwendig ist.


## 📊 Datenstruktur

### Sport-Tabelle (Spalten A-O)
`Datum | Name | Typ | Distanz (km) | Zeit | Kalorien | Ø Puls | Max Puls | Gewicht | HM | ID | m/s | Pace Run | km/h Bike | Pace Swim`

### Health-Tabelle (Spalten A-H)
`Datum | Gewicht | Schritte | Schlaf (h:mm) | Ruhepuls | HRV | Systolisch | Diastolisch`

## 🎨 Optik & Analyse
Die Zeilen im Sport-Sheet werden über die **Bedingte Formatierung** (basierend auf Spalte C) eingefärbt. Zur Auswertung wird eine `QUERY`-Formel genutzt, die Daten nach Jahr, Monat und Sportart gruppiert.

---

## 🤝 Credits & Quellen

### Basis-Projekt
Dieses Projekt startete als Fork bzw. basiert auf der großartigen Arbeit von **[daviderubio/garmin-run-gsheets-sync](https://github.com/daviderubio/garmin-run-gsheets-sync)**. Ein herzliches Dankeschön für die solide Grundlage der Garmin-API-Anbindung.

### KI-gestützte Weiterentwicklung
Um spezifische Anforderungen wie alle Aktivitäten und detaillierte Gesundheitsmetriken abzudecken, wurde der ursprüngliche Code in intensiver Zusammenarbeit mit **Google Gemini** umfassend erweitert:

* **Erweiterte Health-Metriken:** Integration von HRV (Heart Rate Variability) und Ruhepuls.
* **Blutdruck-Extraktion:** Entwicklung einer spezialisierten Logik, um manuell eingetragene Blutdruckwerte aus Garmin Connect auszulesen.
* **Auswertung aller Aktivitäten** Multisport wird als eine Zeile ausgegeben!
* **Flexible Zeiträume:** Implementierung von Daily-Sync (7 Tage) und historischen Deep-Sync Funktionen.
* **Dashboard-Optimierung:** Anpassung der Datenstruktur für automatisierte Google Sheets Dashboards (QUERY-Anbindung).

---

## 🤖 AI-Powered
Entwickelt mit Unterstützung von **Google Gemini**. Die KI half dabei, komplexe API-Strukturen zu entschlüsseln, Fehler in der Datenverarbeitung zu beheben und eine saubere, wartbare Skript-Architektur für GitHub Actions zu erstellen.

