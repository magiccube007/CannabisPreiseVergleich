
# CannabisPreiseVergleich
Dieser Telegramm-Bot wurde entwickelt, um Patienten bei der Suche nach den besten Preisen für medizinisches Cannabis in verschiedenen Apotheken zu unterstützen. Der Bot ermöglicht es Patienten, die Preise für medizinisches Cannabis in den verschiedenen Online-Apotheken zu vergleichen und das beste Angebot zu finden. Das Projekt hat ursprünglich als Spaß-Projekt zur Semestervorbereitung und als Übung in Python gestartet. Ich habe es dann aufgrund des großen Interesses im Cannabis-Medic-Forum  weiter ausgebaut.(Beitrag wurde mittlerweile entfernt, da nicht transparent genug bei OpenSource?)
## Verwendung

Dieses Projekt bietet die folgenden Befehle:

- `/help`: Gibt einen Hilfe-Text aus
- `/getAllStrains`: Gibt alle verfügbaren Strains aus
- `/search "keyword"`: Gibt alle Strains aus, die das Keyword enthalten
- `/getPrices "index1" "index2"...`: Gibt die Preise der Strain mit dem Index zurück
- `/getBelow "amount"`: Gibt alle Strains zurück, die bei einer der Apotheken unter einem bestimmten Preis verfügbar sind
- `/getLoaded`: Gibt die Anzahl der geladenen Strains pro Apotheke zurück
- `/getBestDeal "amount:index1,index2..." "amount:index1,index2..."`: Probiert den besten Preis für den Kauf von zwei Strains zu ermitteln. Hierbei werden für jede der beiden Strains eine Menge, als auch mögliche Optionen angegeben. Bsp.: `/getBestDeal 10:2,3 8:4,6` probiert den besten Preis zu ermitteln, wenn 10g von der ersten Strain gekauft werden sollen und dafür nur die Strains mit den IDs 2 & 3 in Frage kommen. Also auch wenn 8g von der zweiten Strain gekauft werden soll und dafür nur die Strains mit den IDs 4 & 6 in Frage kommen

### Admin-Befehle

Die folgenden Befehle sind nur für Admins zugänglich:

- `/updatePrices`: Updated die Datenbank mit den Preisen
- `/addUser "telegramm_user_id"`: Fügt einen neuen User hinzu


## Technische Details
Der Bot wurde mithilfe der Bibliothek python-telegram-bot entwickelt. Dieser nutzt dabei Selenium mit dem chromedriver in Kombination mit beatifulsoup, um die daten von den Webseiten der Apotheken zu verarbeiten.
### Aktuell unterstützte Apotheken
[Helios-Apotheke](https://helios-cannabis.de/)

[Grünhorn-Apotheke](https://www.gruenhorn.de/)

[Abc-Apotheke](https://abc-cannabis.de/)

[420Brokkoli-Apotheke](https://420brokkoli.de/)

[Cannflos-Apotheke](https://cannflos-apo.de/)

[GrüneBlüte-Apotheke](https://gruenebluete.de/)

[Cannabisapo24-Apotheke](https://cannabisapo24.de/)

Weitere können gerne Angefragt werden. Hierbei ist nur wichtig, dass es eine Seite zum abrufen der Preise gibt, auf welcher diese in € pro Gramm angezeigt werden.
## Installation
### Mit Docker (empfohlen):
Die Anleitung wurde lediglich unter Windows 10 getestet, sollte aber bei anderen Systemen ähnlich funktionieren.
1. [Docker](https://www.docker.com/products/docker-desktop/) installieren. Dies sollte ziemlich selbst erklärend sein. Einfach den Anweisungen folgen, ihr müsst nach der Installation euren PC neu starten.
2. Das Projekt herunterladen. Dafür einfach in der github-Repo oben rechts auf 'Code' und 'Download Zip' klicken. ![Siehe](https://i.imgur.com/XlUk5I3.png)
3. Wenn ihr die Zip heruntergeladen und gespeichert habt, müsst ihr diese entpacken. Dies macht ihr mit rechts Klick auf die Datein und 'Alle extrahieren'.  In dem Fenster, welches sich anschließend öffnet  'Extrahieren' drücken.![siehe](https://i.imgur.com/wwZ7FFB.png)
4. Danach geht ihr in den eben extrahierten Ordner (Wichtig nicht in die Zip-Datein) und öffnet die Datei 'config' und füllt eure Einlog-Daten für die jeweilige Apotheke ein. Falls ihr für eine der Apotheken keinen Zugang habt setzt einfach `ACTIVE = False`, ansonsten `ACTIVE = True`.
Hierbei ist wichtig, dass ihr den Chrome-Path leer lasst. 
Unter Telegram müsst ihr ADMIN_ID, TOKEN und BOT_USERNAME ausfüllen. Wie ihr den Token und Username (der, der mit Bot enden muss) bekommt, seht ihr [hier](https://www.siteguarding.com/en/how-to-get-telegram-bot-api-token).
Wie ihr die Admin-Id bekommt, seht ihr [hier](https://cobrasystems.nl/telegram-user-id/).
5.  Nachdem ihr, die config-Datei gespeichert habt, müsst ihr nur noch auf die Batch-Datein 'Install' doppelklicken. Sobald diese fertig ist (kann eine weile dauern) und sich das Fenster wieder schließt, könnt ihr den Bot in Telegramm benutzen. Um den Bot zu stoppen bzw. zu einem späteren Zeitpunkt wieder zu starten einfach auf die Batch-Datei 'start_stop' doppelklicken. Es empfiehlt sich, direkt die Datenbank mit `/updatePrices` zu aktualisieren (auch dies kann eine Weile dauern).
### Ohne Docker:
Hierauf werde ich erstmal nicht weiter eingehen. Kurz gefasst, ihr müsst in der config zusätzlich einen Path zum chromedriver setzten und die Requirments installieren. Anschließend einfach die 'telegrammbot' Python-Datei starten.

## Requirments
-   beautifulsoup4
-   configparser
-   regex
-   selenium
-   pandas
-   python-telegram-bot

    `pip install beautifulsoup4 configparser regex selenium pandas python-telegram-bot`

## Wichtig 
Der Großteil des Textes für das Readme wurde von ChatGPT generiert und kann somit Fehler enthalten. 
Außerdem ist gerade die Scrapper-Datei aufgrund von Selenium sehr ineffizient und fehleranfällig, falls jemand Zeit und Lust hast dies zu ändern immer gerne. Ich hab es nicht, da es meistens aus so funktioniert.
### Was ist toMatch?
In dem hochgeladenen Ordner namens "toMatch" befindet sich eine Excel-Datei namens "matchnames", die als eine Art Namensregister dient. Hier werden den verschiedenen Strain-Namen, die bei den jeweiligen Apotheken zu finden sind, eine eindeutige ID zugeordnet. Dies ist notwendig, da sich die Bezeichnungen bei den Apotheken oft unterscheiden und man diese sonst nicht richtig zuordnen kann.
Im selben Ordner befinden sich auch weitere Dateien, die alle Strain-Namen der jeweiligen Apotheken enthalten. Um den Bot richtig funktionieren zu lassen, müssen diese Strain-Namen also noch in der "matchnames"-Datei den entsprechenden IDs zugeordnet werden.
Sollte eine Strain noch nicht enthalten sein, kann man dieser am Ende der matchnames-Datei eine neue ID zuordnen. Wichtig hierbei ist, dass man die restlichen Spalten mit 'None' füllt.

## Haftungsausschluss

Dieser Telegramm-Bot ist ein Tool zur Unterstützung von Patienten bei der Suche nach den besten Preisen für medizinisches Cannabis und gibt keine medizinischen Ratschläge oder Empfehlungen ab. Der Bot wurde unabhängig von den betreffenden Apotheken entwickelt und soll keinerlei Werbung für diese Apotheken darstellen. Der Bot ist auch keine Art von Werbung für medizinisches Cannabis und soll lediglich als Hilfe-Tool für Patienten dienen, die bereits eine medizinische Verordnung für Cannabis besitzen.

Die Benutzung dieses Bots erfolgt auf eigene Verantwortung. Die Entwickler dieses Bots übernehmen keine Haftung für etwaige Schäden, die durch die Nutzung dieses Bots entstehen können.
