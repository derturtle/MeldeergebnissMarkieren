# MeldeergebnissMarkieren
Diese ist ein kleines Hilfsprogramm, welches Vereine in Meldeergebnissen (Schwimmsport) markiert. Außerdem zieht es 
noch die Daten zu jedem start aus dem Meldeergebnis und erstelle eine Meldeliste für jeden Aktiven von dem Verein

## Installation

1. Python installieren z.B. von der offiziellen webseite https://www.python.org/ oder unter Linux aus den Paketquellen
   * **Wichtig** python sollte so installiert werden, dass das "python" commando im Pfad zur verfügung steht
2. Diese repository clonen
```commandline
git clone https://github.com/derturtle/MeldeergebnissMarkieren.git
```
3. In das entsprechende Verzeichnis wechseln
4. Python venv umgebung erstellen
``` commandline
python -m venv venv
```
5. In die python umgebung wechseln und mit pip die folgenden Pakete installieren
   * argparse
   * pypdf
   * pdfminer.six
   * windows-curses (nur windows)

*Unix*

Python umgebung starten
```commandline
source ./venv/bin/activate
```
Packete installieren
```commandline
pip install argparse pypdf pdfminer.six
```

*Windows*

Python umgebung starten
```commandline 
.\venv\Scripts\activate.bat
```
Packete installieren
```commandline
pip install argparse pypdf pdfminer.six windows-curses
```

6. Program starten
```commandline
python highlightClub.py
```

## Was macht das Program?

Mit dem Program ist es möglich ein Meldeergebnis vom Schwimmen zu scannen. Die Daten die extrahiert werden, stehen 
intern als eine art Datenbank zur Verfügung. Mit dieser ist es dann möglich jedes auftreten eines Vereins in einer Farbe
der Wahl zu markieren. Es können auch mehrere Vereine in unterschiedlichen Farben markiert werden. Weiterhin fällt pro 
Verein eine html-datei aus dem Program heraus, in dem die Kampfrichter aufgelistet werden sowie alle Starts der Aktiven 
mit Wettkampfnummer, Lauf und Bahn.

### Feature liste

* Markiert einen Verein mit einer Farbe der wahl
* Markiert weitere Vereine in anderen Farbe [nur GUI]
* Erstellt für jeden Verein ein eigenes Meldeergebnis, in dem dieser in einer Farbe der Wahl markiert ist [nur GUI]
* Für jeden Verein wird eine html-Datei erstellt, in dem sich alle Kampfrichter sowie jeder Aktive mit Wettkampf Nummer, Lauf und Bahn aufgelistet werden 

## GUI

Die GUI ist eine einfache Oberfläche, die ein bisschen dem Unix editor Nano nachempfunden ist. Man kann in ihr mit den 
Tasten Pfeiltasten und Enter navigieren, alle anderen Tasten werden unten im Menu angezeigt. 

### Tasten

* **^X**  -  STRG+X - Beenden
* **^B**  -  STRG+B - Zurück
* **^D**  -  STRG+D - Verzeichnis wechseln
* **^O**  -  STRG+O - Neue Farbe hinzufügen
* **^P**  -  STRG+P, Bild up - Nächste Seite
* **^N**  -  STRG+N, Bild up - Vorherige Seite
* Enter - Bestätigung

## Command line Argumente

Weiterhin gibt es die Möglichkeit das Program via Command line anzusprechen. Dazu siehe Hilfe
```commandline
python highlightClub.py -h
```
## ini-Datei

Wenn das Programm gestartet wird, wir automatisch eine ini-Datei mit dem Namen *.result_config.ini* angelegt. In dieser 
ini-Datei gibt es folgende Sektionen:

* PDFParseValues
* Colors
* Default

### PDFParseValues

**Wichtig** an der Sektion PDFParseValues keine Änderungen vornehmen ansonsten kann es sein, das das Program nicht mehr 
funktioniert.

### Colors

Hier können eigene Farben definiert werden. Diese sollten in der Form *"Name = #FFFFFF"* angelegt werden, wobei der 
Farbwert in hex angegeben wird. Folgende Farben werden direkt unterstützt:

* yellow *(#FFFF00)*
* grey_75 *(#BFBFBF)*
* grey *(#808080)*
* cyan *(#00FFFF)*
* green *(#00FF00)*
* lite_green *(#80FF00)*
* lite_blue *(#0080FF)*
* magenta *(#FF00FF)*
* orange *(#FF8000)*

### Default

Hier werden default Einstellungen gespeichert. Folgende Einträge sind möglich oder werden abgespeichert:

* offset - Wenn eine zeile markiert wird, der Offset in Pixeln, Default = 1
* color - Die Default farbe die ausgewählt wird, Default = yellow
* club - Der Verein der vorausgewählt ist.
* color_\<n\> - Weitere default farben für weitere Vereine
* club_\<n\> - Weitere Vereine die ausgewählt werden
* search_path - Der Pfad in dem die Meldeergebnisse gesucht werden, Default = "Downloads" 

## Offene Punkte

Hier noch ein paar Punkte die eventuell noch folgen:

* Einzelne Schwimmer (extra) markieren
* Commandline erweitern auf alle Vereine
* Einen installer für Windows und Unix bauen (der alles automatisch installiert)

## Fragen, Anregungen, Fehler

Da ich das ganze für mich mache, da ich das selber brauche bin ich für Anregungen und Fragen offen. Sollte es Fehler 
geben schickt mir bitte das Meldeergebnis mit, damit ich es Testen kann!    
