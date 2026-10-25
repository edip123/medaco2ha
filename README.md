# Westnetz MeDaCo für Home Assistant

Custom Integration, die die Smart-Meter-Daten (intelligentes Messsystem) aus dem
MeDaCo-Portal von Westnetz bzw. Westenergie Metering abholt und als
Langzeitstatistik in Home Assistant schreibt. Die Werte lassen sich direkt im
Energie-Dashboard als Netzbezug und Netzeinspeisung auswählen.

> **Status:** Läuft seit Oktober 2026 gegen das Live-Portal von Westnetz mit
> zwei Zählpunkten (Hausstrom mit Einspeisung, Wärmepumpe). Version 0.2.0
> behebt den Import von Zählern, deren erste Stunde angebrochen ist, und
> behandelt vorläufige Werte.

## Wie es funktioniert

- Die Integration meldet sich wie der Browser am Portal an (Formular-Login)
  und liest die Zählpunkte und ihre Messreihen aus.
- Alle 15 Minuten holt sie die Viertelstundenwerte der Register 1.29.0 (Bezug)
  und 2.29.0 (Einspeisung) seit dem letzten Import, beim ersten Start die
  letzten 365 Tage.
- Die Werte werden zu Stundenwerten zusammengefasst und als externe Statistik
  `medaco:<zählpunkt>_1_1_1_29_0` (Bezug) bzw. `..._2_29_0` (Einspeisung)
  importiert. Die jüngste Stunde wird erst übernommen, wenn alle vier
  Viertelstunden vorliegen. Angebrochene Stunden davor (etwa die erste Stunde
  nach dem Zählereinbau oder eine Lücke) werden mit den vorhandenen Werten
  importiert, damit sie den Rest nicht blockieren.
- Das Gateway überträgt in der Regel einmal täglich. Bis dahin zeigt das
  Portal für den laufenden Tag Schätzwerte (Status „v“, vorläufig). Die
  Integration überspringt diese standardmäßig und wartet auf die gemessenen
  Werte („W“) bzw. Ersatzwerte („E“). Wer die Schätzwerte trotzdem sofort
  sehen will, schaltet in den Optionen „Vorläufige Werte importieren“ ein.
- Bei jedem Lauf werden die letzten Tage (Standard: 2, einstellbar) erneut
  abgerufen und vorhandene Stunden überschrieben. So landen Korrekturen des
  Portals, etwa vorläufige Werte, die endgültig werden, in der Statistik.
- Pro Zählpunkt gibt es zwei Diagnose-Sensoren: importierter Zählerstand und
  Datenstand (letzte vollständige Stunde). Mit Debug-Logging für
  `custom_components.medaco` protokolliert die Integration die gefundenen
  Zählpunkte und Messreihen sowie jeden Import.

## Installation (HACS)

1. HACS → Integrationen → Menü → Benutzerdefinierte Repositories →
   `https://github.com/DGne-Nurag/medaco2ha`, Kategorie „Integration“.
2. „Westnetz MeDaCo“ installieren und Home Assistant neu starten.
3. Einstellungen → Geräte & Dienste → Integration hinzufügen → „Westnetz MeDaCo“,
   Portal wählen und mit den MeDaCo-Zugangsdaten anmelden.
4. Energie-Dashboard → Netzverbrauch hinzufügen → Statistik „… Bezug“ wählen.
5. Optional: Einstellungen → Geräte & Dienste → Westnetz MeDaCo → Konfigurieren,
   um vorläufige Werte zu übernehmen oder das Neueinlesen anzupassen.

## Hinweise zu den Daten

- Die Werte kommen mit Verzug. Für Live-Anzeigen (heutiger Tag) eignet sich
  MeDaCo nicht, dafür sind die Werte ab dem Vortag die amtlichen Zählerwerte.
- Statistiken lassen sich auch in Karten verwenden, zum Beispiel in der
  Karte „Statistikdiagramm“ mit der Statistik-ID `medaco:…`.

## Entwicklung

```bash
pip install pytest-homeassistant-custom-component
pytest -q
```

Die Tests prüfen das Auslesen der Portal-Antworten und starten die
Integration in einem Test-Home-Assistant gegen ein simuliertes Portal.
