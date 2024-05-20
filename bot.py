# -*- coding: utf-8 -*-
import logging
import re
import psycopg2
from psycopg2 import Error
import paramiko
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

db_ip = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASSWORD')
db = os.getenv('DB_DATABASE')

db_host_user = os.getenv('DB_USER')
db_host_pass = os.getenv('DB_PASSWORD')
#db_ssh_port = os.getenv('DB_SSH_PORT')

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

buffer_data = None

TOKEN = os.getenv('TOKEN')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

#def get_logs_from_bd_volume():
#    message = ""
#    try:
#        command = "cat /repl_logs/postgresql.log | grep repl | tail -n 10"
#        res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        if res.returncode != 0 or res.stderr.decode() != "":
#            message = "Can not open log file!"
#        else:
#            logs = res.stdout.decode().strip('\n')
#            message = logs
#    except Exception as e:
#        # Обработка исключений
#        message = f"Error: {str(e)}"
#
#    return message


def execute_sql_select(mystr):
    data = None
    connection = None
    try:
        connection = psycopg2.connect(user=db_user, password=db_pass, host=db_ip, port=db_port, database=db)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {mystr};")
        data = cursor.fetchall()  
        logging.info("PostgreSQL Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    return(data)

def execute_sql_insert(table, column, values):
    result = ""
    connection = None
    try:
        connection = psycopg2.connect(user=db_user, password=db_pass, host=db_ip, port=db_port, database=db)
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES {values};")
        connection.commit()
        result = "Success"
        logging.info("PostgreSQL Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    if not result:
        result = "Failure"
    return result



def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    text = "/find_email - email search\n"
    text += "/find_phone_number - phone number search\n"
    text += "/verify_password - check how strong your password\n"
    text += "/get_release - get relese connected os\n"
    text += "/get_uname - processor architecture, hostname and core version\n"
    text += "/get_uptime - time oh work for a host\n"
    text += "/get_df - get file system information\n"
    text += "/get_free - memory inf\n"
    text += "/get_mpstat - performance of a system\n"
    text += "/get_w - get inf about users\n"
    text += "/get_auths - last 10 auths\n"
    text += "/get_critical - last 5 critical events\n"
    text += "/get_ps - inf about processes\n"
    text += "/get_ss - inf about used ports\n"
    text += "/get_apt_list - inf about installed packets\n"
    text += "/get_services - inf about services\n"
    text += "/get_repl_logs - get replication logs\n"
    text += "/get_emails - get emails from database\n"
    text += "/get_phone_numbers - get emails from database\n"
    update.message.reply_text(text)


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска e-mail: ')

    return 'find_email'

def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки на надежность: ')

    return 'verify_password'

def get_apt_listCommand(update: Update, context):
    update.message.reply_text('Введите название сервиса для отображения информации о нем или введите all для отображения всех сервисов: ')

    return 'get_apt_list'

def find_phone_number (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    phoneNumRegex = re.compile(r'\+?\d[\( -]?[\( -]?\d{3}[\) -]?[\( -]?\d{3}[ -]?\d{2}[ -]?\d{2}')
    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END# Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер

    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    global buffer_data
    buffer_data = phoneNumberList
    update.message.reply_text("Do you want to add these vlues into the database? Yes/No")
    return 'add_phone_numbers'

def add_phone_numbers(update: Update, context):
    user_input = update.message.text
    if user_input == "Yes":
        try:
            send_value = ""
            global buffer_data
            for i in range(len(buffer_data)-1):
                send_value += "(\'"+ buffer_data[i] +"\')," 
            send_value += "(\'"+buffer_data[-1]+"\')"
            
            if execute_sql_insert("phones", "phone", send_value) == "Success":
                update.message.reply_text("Values were added")
            else:
                update.message.reply_text("There was an error")
            buffer_data = None
        except Exception as e:
            logging.error("Ошибка при работе c cycle: %s", e)
    else:
        update.message.reply_text("Vlaues will not be added")

    return ConversationHandler.END # Завершаем работу обработчика диалога

def find_email (update: Update, context):
    user_input = update.message.text # Получаем текст
    emailRegex = re.compile(r'\S+@\w+\.\w+')
    emailList = emailRegex.findall(user_input) # Ищем 

    if not emailList: 
        update.message.reply_text('Email не найдены')
        return ConversationHandler.END
    
    emails = '' # Создаем строку
    for i in range(len(emailList)):
        emails += f'{i+1}. {emailList[i]}\n' 

    update.message.reply_text(emails) # Отправляем сообщение пользователю
    global buffer_data
    buffer_data = emailList
    update.message.reply_text("Do you want to add these vlues into the database? Yes/No")
    return 'add_emails'

def add_emails(update: Update, context):
    user_input = update.message.text
    if user_input == "Yes":
        try:
            send_value = ""
            global buffer_data
            for i in range(len(buffer_data)-1):
                send_value += "(\'"+ buffer_data[i] +"\')," 
            send_value += "(\'"+buffer_data[-1]+"\')"
            
            if execute_sql_insert("emails", "email", send_value) == "Success":
                update.message.reply_text("Values were added")
            else:
                update.message.reply_text("There was an error")
            buffer_data = None
        except Exception as e:
            logging.error("Ошибка при работе c cycle: %s", e)
    else:
        update.message.reply_text("Vlaues will not be added")
    return ConversationHandler.END # Завершаем работу обработчика диалога

def verify_password (update: Update, context):
    user_input = update.message.text # Получаем текст

    passwordRegex = re.compile(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()]).{8,}')

    verified_password = passwordRegex.search(user_input) 

    if not verified_password:
        answer = "Пароль простой"
    else:
        answer = "Пароль сложный"

    update.message.reply_text(answer) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def ssh_execute_get_logs_from_bd ():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=db_ip, username=db_host_user, password=db_host_pass, port='22')
    stdin, stdout, stderr = client.exec_command("cat /var/log/postgresql/postgresql-15-main.log | grep 'repl' | tail -n 10")
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return(data)

def ssh_execute_command (command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data.decode("utf-8")).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return(data)

def get_release (update: Update, context):
    out = ssh_execute_command("uname -r").replace("\n","")
    result = f"Connected system relese is \"{out}\""
    update.message.reply_text(result)

def get_uname (update: Update, context):
    data = ssh_execute_command("uname -m && uname -n && uname -v").split("\n")
    result = f"Architecture is \"{data[0]}\", hostname is \"{data[1]}\" and core version is \"{data[2]}\""
    update.message.reply_text(result)

def get_uptime (update: Update, context):
    data = ssh_execute_command("uptime -p").replace("\n","")
    result = f"Host is {data}"
    update.message.reply_text(result)

def get_df(update: Update, context):
    data = ssh_execute_command("df -h")
    result = f"File system information:\n{data}"
    update.message.reply_text(result)

def get_free(update: Update, context):
    data = ssh_execute_command("free -h")
    result = f"Memory information:\n{data}"
    update.message.reply_text(result)

def get_mpstat(update: Update, context):
    data = ssh_execute_command("mpstat")
    result = f"Performance information:\n{data}"
    update.message.reply_text(result)


def get_w(update: Update, context):
    data = ssh_execute_command("w -f")
    result = f"Users information:\n{data}"
    update.message.reply_text(result)

def get_auths(update: Update, context):
    data = ssh_execute_command("last -n 10 -R")
    result = f"Last 10 authorizations:\n{data}"
    update.message.reply_text(result)

def get_critical(update: Update, context):
    data = ssh_execute_command("journalctl -p 2 | tail -n 5")
    if data == "-- No entries --\n":
        result = "There aren't any critical evenets on the host."
    else:
        result = f"Last 5 critical events:\n{data}"
    update.message.reply_text(result)

def get_ps(update: Update, context):
    data = ssh_execute_command("ps")
    result = f"Processes information:\n{data}"
    update.message.reply_text(result)

def get_ss(update: Update, context):
    data = ssh_execute_command("ss -n4")
    result = f"Used for ipv4 ports:\n{data}"
    update.message.reply_text(result)

def get_apt_list(update: Update, context):
    user_input = re.escape(update.message.text.replace(" ", ""))
    if user_input == "all":
        try:
            data = ssh_execute_command("dpkg --get-selections | grep -v deinstall | head -n 200").split("\n")
            result = "Information about packets:\n"
            for line in data:
                result += line.split()[0] + ", "
            result = result[:-2]
        except Exception as e:
            result = e
    else:
        data = ssh_execute_command(f"dpkg --get-selections | grep -w {user_input}")
        result = f"Information about the packet:\n{data}"
        if not data:
            result = "This packet is not on thr system."
    
    update.message.reply_text(result)
    return ConversationHandler.END

def get_services(update: Update, context):
    data = ssh_execute_command("systemctl list-units --type service --state running -q")
    result = f"Information about running services:\n{data}"
    update.message.reply_text(result)

def get_repl_logs(update: Update, context):
    data = ssh_execute_get_logs_from_bd()
    #data = get_logs_from_bd_volume()
    result = f"Logs from database:\n{data}"
    update.message.reply_text(result)

def get_emails (update: Update, context):
    data = execute_sql_select("emails")
    result = "emails from db:\n"
    if not data:
        result = "In the database no any emails records"
    else:
        i=0
        for iterator in data:
            i+=1
            result += str(i) + ". "  + iterator[1] + "\n"
    update.message.reply_text(result)

def get_phone_numbers (update: Update, context):
    data = execute_sql_select("phones")
    result = "Phone numbers from db:\n"
    if not data:
        result = "In the database no any phone records"
    else:
        i=0
        for iterator in data:
            i+=1
            result += str(i) + ". " + iterator[1] + "\n"
    update.message.reply_text(result)

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'add_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, add_phone_numbers)],
        },
        fallbacks=[]
    )
    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'add_emails': [MessageHandler(Filters.text & ~Filters.command, add_emails)],
        },
        fallbacks=[]
    )
    convHandlerget_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(convHandlerget_apt_list)
    dp.add_handler(CommandHandler("get_services", get_services))
    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
