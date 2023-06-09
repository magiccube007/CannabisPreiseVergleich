from typing import Final
from configparser import ConfigParser
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import updater
import time
config = ConfigParser()
config.read('config.ini')

ADMIN_ID: Final = config['TELEGRAMM']['ADMIN_ID']
TOKEN: Final = config['TELEGRAMM']['TOKEN']
BOT_USERNAME: Final = config['TELEGRAMM']['BOT_USERNAME']

app_price = updater.App()

async def controlAccess(update):
    user_id = str(update.message.from_user.id)
    allowed_users = updater.App.get_allowed_users()
    if allowed_users.__contains__(user_id) or user_id == ADMIN_ID:
        return True
    await update.message.reply_text('<b>Bitte erst Registrieren!\nUSER_ID:</b> '+ user_id, constants.ParseMode.HTML)
    return False

#/help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/help')
    if not await controlAccess(update): return 
    result = ('<b>Hier ist eine Liste an Befehlen:</b>\n'
                                    + '/help: Gibt diesen Text aus\n'
                                    +'/getAllStrains: Gibt alle verfügbaren Strains aus\n'
                                    +'/search <b>"keyword"</b>: Gibt alle Strains aus die das Keyword enthalten\n'
                                    +'/getPrices <b>"index1"</b> <b>"index2"</b>...: Gibt die Preise der Strain mit dem Index zurück\n'
                                    +'/getBelow <b>"amount"</b>: Gibt alle Strains zurück, die bei einer der Apotheken unter einem bestimmten Preis verfügbar sind\n'
                                    +'/getLoaded: Gibt die Anzahl der geladenen Strains pro Apotheke zurück\n'
                                    +'/getBestDeal <b>"amount:index1,index2..."</b> <b>"amount:index1,index2..."</b>: Probiert den besten Preis für den Kauf von zwei Strains zu ermitteln.'+' Hierbei werden für jede der beiden' 
                                    +' Strains eine Menge, als auch mögliche Optionen angegeben. Bsp.: /getBestDeal 10:2,3 8:4,6 probiert den besten Preis zu ermitteln, wenn 10g'
                                    +' von der ersten Strain gekauft werden sollen und dafür nur die Strains mit den IDs 2 & 3 in Frage kommen. Also auch wenn 8g von der zweiten Strain '
                                    +'gekauft werden soll und dafür nur die Strains mit den IDs 4 & 6 in Frage kommen\n')
    if ADMIN_ID == str(update.message.from_user.id):
        result += '<b>Admin-Befehle:</b>\n'
        result += '/updatePrices: Updated die Datenbank mit den Preisen\n'
        result += '/addUser: Fügt einen neuen User hinzu\n'
        result += '/getLeftToMatch: Gibt die Namen der Strains zurück, welche noch nicht zugewiesen wurden!'
    await update.message.reply_text(result, parse_mode=constants.ParseMode.HTML)

#Alle Nachrichten die kein Befehl sind
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await controlAccess(update): return
    await update.message.reply_text('Bitte /help schreiben für eine Liste aller Befehle!')

#Zulange Nachrichten werden aufgeteilt
async def sendMessage(update,message):
    max_length = 3700
    message_parts = []
    current_part = ""

    for item in message.split('\n\n'):
        if len(current_part + item) > max_length:
            message_parts.append(current_part.strip())
            current_part = ""
        current_part += item + '\n\n'

    message_parts.append(current_part.strip())

    for part in message_parts:
        await update.message.reply_text(part,parse_mode=constants.ParseMode.HTML)
#/search query
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/search')
    if not await controlAccess(update): return
    result = ''
    if len(context.args) != 0:
        query = ' '.join(context.args)
        result = app_price.search(query)
        if result == '':
            result = "Es konnte kein Ergebnis gefunden werden!"
    else:
        result = 'Probier es mal mit /help !'
    await sendMessage(update, result)

#/getAllStrains
async def getAllStrains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/getAllStrains')
    if not await controlAccess(update): return
    result = app_price.getAllStrains()
    await sendMessage(update,result)

#/getBelow certain value
async def getBelow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/getBelow')
    if not await controlAccess(update): return
    if len(context.args) != 1:
        await update.message.reply_text('Probier es mal mit /help !', parse_mode=constants.ParseMode.HTML)
    else:
        result = ''
        try:
            max_price = float(context.args[0])
            result = app_price.getBelow(max_price)
        except ValueError:
            result = 'Probier es mal mit /help !'
        if result == '':
            result = 'Probier es mal mit einem höheren Preis!'
        await sendMessage(update,result)

#/getPrices index1 index2 ...
async def getPrices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/getPrices')
    if not await controlAccess(update): return
    result = ''
    if len(context.args) != 0:
        for i in context.args:
            try:
                index = int(i)
                result += app_price.getPriceAndNameByIndexToString(index) + '\n\n'
            except ValueError:
                result = "Eine der IDs war keine Nummer!"
    else:
        result = 'Probier es mal mit /help !'
    await sendMessage(update,result)

#/updatePrices
async def updatePrices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/updatePrices')
    if not str(update.message.from_user.id) == ADMIN_ID: 
        await update.message.reply_text('Bitte /help schreiben für eine Liste aller Befehle!')
        return
    await update.message.reply_text('Starting to update the datasets now...', parse_mode=constants.ParseMode.HTML)
    app_price.updateAll()
    await update.message.reply_text('<b>Updated the datasets!</b>', parse_mode=constants.ParseMode.HTML)
    anzahl = app_price.getAmountInDatabase()
    await update.message.reply_text(anzahl, parse_mode=constants.ParseMode.HTML)

#addUser to have Access
async def addUser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/addUser')
    if not str(update.message.from_user.id) == ADMIN_ID: 
        await update.message.reply_text('Bitte /help schreiben für eine Liste aller Befehle!')
        return
    if len(context.args) != 1:
        response = ''
        if len(context.args) == 0:
            response = '<b>Allowed Users: </b>\n' + str(updater.App.get_allowed_users())
        else:
            response = 'Probier es mal mit /help !'
        await update.message.reply_text(response, parse_mode=constants.ParseMode.HTML)
    else:
        user_id = str(context.args[0])
        updater.App.add_new_user(user_id)
        await update.message.reply_text('<b>Added User-ID: </b>' + user_id, parse_mode=constants.ParseMode.HTML)


#getBestDeal
async def getBestDeal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/getBestDeal')
    if not await controlAccess(update): return
    result = 'Probier es mal mit /help !'
    if len(context.args) == 2:
        dict1 = getAmountAndIndexList(context.args[0])
        dict2 = getAmountAndIndexList(context.args[1])
        if dict1 != {} and dict2 != {}:
            result = app_price.getBestDeal(dict1['index_list'], dict2['index_list'], dict1['amount'], dict2['amount'])
    await update.message.reply_text(result, parse_mode=constants.ParseMode.HTML)

def getAmountAndIndexList(value):
    try:
        parts = value.split(":")
        amount = int(parts[0])
        numbers_str = parts[1].split(",")
        numbers = [int(n) for n in numbers_str]
        return {'amount': amount, 'index_list': numbers}
    except (ValueError, IndexError):
        return {}
#getLoaded
async def getLoaded(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/getLoaded')
    anzahl = app_price.getAmountInDatabase()
    await update.message.reply_text(anzahl, parse_mode=constants.ParseMode.HTML)

async def getLeftToMatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('USER-ID:', update.message.from_user.id , 'COMMAND:', '/getLeftToMatch')
    if not str(update.message.from_user.id) == ADMIN_ID: 
        await update.message.reply_text('Bitte /help schreiben für eine Liste aller Befehle!')
        return
    if len(context.args) != 0:
        await update.message.reply_text('Probier es mal mit /help !', parse_mode=constants.ParseMode.HTML)
    else:
        result = app_price.getLeftToMatch()
        await sendMessage(update,result)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('start', help_command))
    app.add_handler(CommandHandler('search', search))
    app.add_handler(CommandHandler('getAllStrains', getAllStrains))
    app.add_handler(CommandHandler('getPrices', getPrices))
    app.add_handler(CommandHandler('updatePrices', updatePrices))
    app.add_handler(CommandHandler('getBelow', getBelow))
    app.add_handler(CommandHandler('getBestDeal', getBestDeal))
    app.add_handler(CommandHandler('addUser', addUser))
    app.add_handler(CommandHandler('getLoaded', getLoaded))
    app.add_handler(CommandHandler('getLeftToMatch', getLeftToMatch))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)
    print('Waiting 10seks for everything to setup')
    time.sleep(10)
    print('Polling...')
    app.run_polling(poll_interval=5)


if __name__ == '__main__':
    main()
