# CannabisPreiseVergleich
Dieser Telegramm-Bot wurde entwickelt, um Patienten bei der Suche nach den besten Preisen für medizinisches Cannabis in verschiedenen Apotheken zu unterstützen. Der Bot ermöglicht es Patienten, die Preise für medizinisches Cannabis in den verschiedenen Online-Apotheken zu vergleichen und das beste Angebot zu finden. Das Projekt hat ursprünglich als Spaß-Projekt zur Semestervorbereitung und als Übung in Python gestartet. Ich habe es dann aufgrund des großen Interesses im [Cannabis-Medic-Forum](https://www.cannabis-medic.eu/forum/index.php?thread/825-telegramm-bot-zum-anzeigen-der-preise/) weiter ausgebaut.
## Verwendung

Dieses Projekt bietet die folgenden Befehle:

- `/help`: Gibt einen Hilfe-Text aus
- `/getAllStrains`: Gibt alle verfügbaren Strains aus
- `/search "keyword"`: Gibt alle Strains aus, die das Keyword enthalten
- `/getPrices "index1" "index2"...`: Gibt die Preise der Strain mit dem Index zurück
- `/getBelow "amount"`: Gibt alle Strains zurück, die bei einer der Apotheken unter einem bestimmten Preis verfügbar sind
- `/getBestDeal "amount:index1,index2..." "amount:index1,index2..."`: Probiert den besten Preis für den Kauf von zwei Strains zu ermitteln. Hierbei werden für jede der beiden Strains eine Menge, als auch mögliche Optionen angegeben. Bsp.: `/getBestDeal 10:2,3 8:4,6` probiert den besten Preis zu ermitteln, wenn 10g von der ersten Strain gekauft werden sollen und dafür nur die Strains mit den IDs 2 & 3 in Frage kommen. Also auch wenn 8g von der zweiten Strain gekauft werden soll und dafür nur die Strains mit den IDs 4 & 6 in Frage kommen

### Admin-Befehle

Die folgenden Befehle sind nur für Admins zugänglich:

- `/updatePrices`: Updated die Datenbank mit den Preisen
- `/addUser`: Fügt einen neuen User hinzu


## Technische Details
Der Bot wurde mithilfe der Bibliothek python-telegram-bot entwickelt. Dieser nutzt dabei Selenium mit dem chromedriver in Kombination mit beatifulsoup, um die daten von den Webseiten der Apotheken zu verarbeiten.
### Aktuell unterstützte Apotheken
[Helios-Apotheke](https://helios-cannabis.de/)
[Grünhorn-Apotheke](https://www.gruenhorn.de/)
[Abc-Apotheke](https://abc-cannabis.de/)
[420Brokkoli-Apotheke](https://420brokkoli.de/)
[Cannflos-Apotheke](https://cannflos-apo.de/)
## Installation
kommt noch
Für Leute die wissen, was sie machen einfach requirments installieren, config-datei ausfüllen und telegrammbot.py starten.
### Requirments
-   beautifulsoup4
-   configparser
-   regex
-   selenium
-   pandas
-   python-telegram-bot

    `pip install beautifulsoup4 configparser regex selenium pandas python-telegram-bot`

## Wichtig 
Ich habe das Ganze jetzt noch schnell hochgeladen, damit vielleicht auch andere Leute während meiner Klausurenzeit an dem Projekt arbeiten können. Der Großteil des Textes für das Readme wurde von ChatGPT generiert und kann somit Fehler enthalten. Hier noch ein kurzer Auschnitt aus meinem letzten Post im Cannabis-Medic Forum, welcher ausgeblendet wurde:
"Ich habe dort auch einen Ordner toMatch hochgeladen, dort ist eine Excel-Datei matchnames enthalten.

Diese stellt eine Art Namensregister da, welche die Namen der Strains, bei den jeweiligen Apotheken einer ID zuordnet. Dies muss gemacht werden, da sich die Namen bei den Apotheken auf der Website für die selbe Strain oft unterscheiden und ich keine Lust/Zeit/das können habe das ganze über pattern oder der gleichen zu matchen.
Im selben Ordner finden sich auch zwei Dateien Cannflosalle und 420Brokkolialle, welche jeweils alle Strain-Namen auf der jeweiligen website enthalten.

Diese müsste man eben noch in der matchnames-Datei immer einer ID zuordnen, dass der Bot richtig funktioniert.

Eine genaue Installations-Anleitung usw. mache ich wahrscheinlich nach meinen Klausuren, vielleicht hat bis dahin ja noch jemand Lust weiter an dem Projekt zu arbeiten."
## Haftungsausschluss

Dieser Telegramm-Bot ist ein Tool zur Unterstützung von Patienten bei der Suche nach den besten Preisen für medizinisches Cannabis und gibt keine medizinischen Ratschläge oder Empfehlungen ab. Der Bot wurde unabhängig von den betreffenden Apotheken entwickelt und soll keinerlei Werbung für diese Apotheken darstellen. Der Bot ist auch keine Art von Werbung für medizinisches Cannabis und soll lediglich als Hilfe-Tool für Patienten dienen, die bereits eine medizinische Verordnung für Cannabis besitzen.

Die Benutzung dieses Bots erfolgt auf eigene Verantwortung. Die Entwickler dieses Bots übernehmen keine Haftung für etwaige Schäden, die durch die Nutzung dieses Bots entstehen können.
