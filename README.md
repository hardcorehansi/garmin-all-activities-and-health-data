# 🏃‍♂️ Garmin Health & Sport Sync to Google Sheet

![AI-Powered](https://img.shields.io/badge/Developed%20with-Google%20Gemini-blue?style=for-the-badge&logo=googlegemini)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Dieses Projekt synchronisiert automatisch deine **Sport-Aktivitäten** und **Gesundheitsdaten** (Gewicht, Schlaf, HRV, Blutdruck) von Garmin Connect in ein Google Spreadsheet. Die Automatisierung läuft über **GitHub Actions**, sodass kein eigener Server benötigt wird.

## 🚀 Release Notes (v2.0)

* **Intelligente Datenerkennung:** Daten werden nun mit der Option `USER_ENTERED` an Google Sheets gesendet. Das bedeutet: Datumswerte und Zeitdauern werden von Google Sheets sofort als solche erkannt (perfekt für Sortierungen, Filter und Diagramme).
* **Multisport-Metriken (Spalte I):** Dynamische Befüllung der Spalte I je nach Sportart:
    * **Laufen:** Schrittfrequenz (avg. Cadence).
    * **Radfahren:** Trittfrequenz (RPM) – unterstützt Outdoor & Indoor (z.B. Zwift/Tacho).
    * **Schwimmen:** Durchschnittlicher SWOLF-Wert.
* **Zeitformate:** Die Schlafdauer wird nun im standardisierten Format `HH:MM:SS` ausgegeben, was eine direkte Zeitberechnung in Sheets ermöglicht.

## 🌟 Features

-   **Sport-Sync:** Erfasst Distanz, Zeit, Pace, Herzfrequenz, Höhenmeter und sportartenspezifische Metriken.
-   **Health-Sync:** Synchronisiert täglich Gewicht, Schritte, Schlafqualität (HH:MM:SS), Ruhepuls und HRV.
-   **Blutdruck-Spezial:** Unterstützt das Auslesen von manuell in Garmin Connect eingetragenen Blutdruckwerten.
-   **Pace-Logik:** Automatisierte Berechnung von Pace (Laufen), km/h (Rad) und min/100m (Schwimmen) in separaten Spalten.

## 📊 Datenstruktur

### Sport-Tabelle (Spalten A-O)
| Spalte | Inhalt | Format / Info |
| :--- | :--- | :--- |
| **A** | Datum | Echt-Datum (YYYY-MM-DD) |
| **B** | Name | Aktivitätsname |
| **C** | Typ | z.B. running, cycling, swimming |
| **D** | Distanz | km |
| **E** | Zeit | Dauer (HH:MM:SS) |
| **F** | Kalorien | kcal |
| **G** | Ø Puls | bpm |
| **H** | Max Puls | bpm |
| **I** | **Metrik** | **Lauf: Schritte / Rad: RPM / Swim: SWOLF** |
| **J** | HM | Höhenmeter |
| **K** | ID | Garmin Activity ID |
| **L** | m/s | Rohwert Geschwindigkeit |
| **M** | Pace Run | min/km |
| **N** | km/h Bike | Geschwindigkeit |
| **O** | Pace Swim | min/100m |

### Health-Tabelle (Spalten A-H)
`Datum | Gewicht | Schritte | Schlaf (HH:MM:SS) | Ruhepuls | HRV | Systolisch | Diastolisch`

## 🛠 Setup & Installation

### 1. Google Sheets Vorbereitung
1.  Erstelle ein neues Google Spreadsheet mit den Blättern `Sport` und `Health`.
2.  Erstelle in der Google Cloud Console einen **Service Account** und lade den `JSON Key` herunter.
3.  Gib die E-Mail des Service Accounts in deinem Google Sheet als "Editor" frei.

### 2. GitHub Secrets
Hinterlege folgende Werte unter `Settings > Secrets and variables > Actions`:

| Secret | Beschreibung |
| :--- | :--- |
| `GARMIN_EMAIL` | Deine Garmin Connect E-Mail |
| `GARMIN_PASSWORD` | Dein Garmin Connect Passwort |
| `GOOGLE_CREDENTIALS` | Der komplette Inhalt der JSON-Key Datei |
| `SHEET_ID` | Die ID aus der URL deines Google Sheets |

### 1. Deep Sync Garmin (Sport-Aktivitäten + Health)

* **Ziel:** Lädt alle Sport-Aktivitäten ab dem Jahr **2010** bis heute und Health daten 

* **Workflow:** `Deep Sync Garmin bis 2010`

* **Besonderheit:** Nutzt eine größere Batch-Größe (50), um die Historie effizient abzuarbeiten. Dubletten werden automatisch anhand der Garmin-ID übersprungen. In Zeile 29 in deep_sync_garmin_data.py kann das Jahr eingestellt werden 



### 2. Deep Sync Health Data

* **Ziel:** Lädt Gesundheitsdaten (Gewicht, HRV, Blutdruck, Schlaf) für einen spezifischen Zeitraum.

* **Workflow:** `Deep Sync Health Data`

* **Konfiguration:** Im Skript deep_sync_health.py kann ein manuelles `start_date` und `end_date` gesetzt werden (Zeile 24!), um gezielt Jahre oder Monate nachzupflegen.



> [!TIP]

> Diese Workflows sollten manuell über den Tab
---

## 🤝 Credits & Quellen

### Basis-Projekt
Dieses Projekt basiert auf der Arbeit von **[daviderubio/garmin-run-gsheets-sync](https://github.com/daviderubio/garmin-run-gsheets-sync)**. Ein herzliches Dankeschön für die solide Grundlage.

### 🤖 AI-Powered (Release 2.0)
Die Weiterentwicklung zur Version 2.0 erfolgte in intensiver Zusammenarbeit mit **Google Gemini**. Die KI half maßgeblich bei:
* Der Implementierung der `USER_ENTERED` Logik für korrekte Datentypen.
* Der Entwicklung der Multisport-Logik für Spalte I (Cadence/SWOLF).
* Der Fehlerbehebung bei API-Strukturen für Blutdruck und Zwift-Daten.
* Der Optimierung der Zeitformate für eine bessere Auswertbarkeit.

---

## 🎨 Optik & Analyse
Die Zeilen im Sport-Sheet können über die **Bedingte Formatierung** (basierend auf Spalte C) eingefärbt werden. Zur Auswertung im Dashboard empfehlen wir eine `QUERY`-Formel, um die Daten nach Monat oder Sportart zu gruppieren.
