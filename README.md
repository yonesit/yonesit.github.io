# yonesit.github.io

Öffentliche Portfolio-Website von Yones Alizai, Informatiker & Softwareentwickler.

## Zweck und öffentliche Seiten

Die Website stellt Schwerpunkte in künstlicher Intelligenz, Machine Learning,
Systemintegration und Automatisierung sowie die Projekte QuantzAI und
Protocolbridge vor.

- Startseite: <https://yonesit.github.io/>
- [QuantzAI](quantzai.html)
- [Protocolbridge](protocolbridge.html)
- [404-Seite](404.html)
- [Impressum](impressum.html)
- [Datenschutzerklärung](datenschutz.html)

## Lokale Vorschau

Im Repository-Verzeichnis kann ein einfacher lokaler Server gestartet werden:

```powershell
python -m http.server 8000
```

Danach ist die Website unter `http://localhost:8000/` erreichbar.

## Technische Struktur

Die Website ist eine leichte statische HTML/CSS-Seite ohne Frameworks,
Tracking-Skripte oder externe Webfonts. `assets/favicon.svg` enthält das
selbst entwickelte Favicon. `sitemap.xml` und `robots.txt` steuern die
technische Auffindbarkeit.

Die Website enthält ein Impressum und eine Datenschutzerklärung. Externe
Plattformen werden grundsätzlich über normale Links geöffnet; eigene
Tracking- oder Analysedienste sind nicht integriert. Rechtliche Angaben dürfen
nicht ohne ausdrückliche Freigabe verändert werden.

## Lokale Prüfung

```powershell
python scripts/check_site.py
```

Die Prüfung benötigt keine externen Python-Pakete. Externe Links werden dabei
nicht per Netzwerk validiert.

## Veröffentlichung

GitHub Pages veröffentlicht den bestehenden `main`-Branch. Die Dateien
`google3c3f89b6a3da8de0.html` und `BingSiteAuth.xml` sind für die Verifizierung
vorhanden und dürfen nicht verändert oder gelöscht werden.
