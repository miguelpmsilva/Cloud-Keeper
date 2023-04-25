import os
import time
import picamera
import requests
import telegram
import RPi.GPIO as GPIO
from time import sleep
from subprocess import call
from datetime import datetime,timedelta
from azure.storage.blob import BlockBlobService,ContainerPermissions,BlobPermissions

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

############################################################################

def writeLog(logMsg):
   """Escreve no ficheiro de log"""
   f = open("logfile.txt", "a")
   f.write(time.strftime('%Y-%m-%d %H:%M:%S -> ', time.localtime())+logMsg+'\n')
   f.close()

def VideoShot():
   """Grava video de 10 segundos e converte-o para o formato .mp4"""
   with picamera.PiCamera() as camera:
      camera.rotation = 270
      camera.start_recording("videoshoot.h264")
      sleep(10)
      camera.stop_recording()
   call(["MP4Box -quiet -add videoshoot.h264 videoshoot.mp4"], shell=True) #Converte o ficheiro de .h264 para .mp4 (Necessário ter o MP4Box instalado)
   writeLog("Video recorded")
   os.remove("videoshoot.h264")


def AzureBlob():
    """Conjunto de funcoes que utilizam a API do Azure Blob e do Telegram"""
    accountKey=os.environ.get('AZURE_KEY') #CHAVE DA CONTA AZURE, ESTA NAS VARIAVEIS DE SISTEMA
    accountName = "projetoglobal"
    containerName = "picammel"
    timeNow = datetime.now()
    blobname = "vid"+timeNow.strftime("%Y%m%d%H%M%S%f")+".mp4"
    blobService = BlockBlobService(accountName, accountKey)

    def GetSasWRITEToken():
        """Obtem uma chave SAS com permissoes de escrita"""
        sas_WriteToken = blobService.generate_container_shared_access_signature(containerName, ContainerPermissions.WRITE, datetime.utcnow() + timedelta(hours=1))
        return sas_WriteToken

    def UploadBlob():
       """Carrega o ficheiro local (video gravado) para a conta de armazenamento Azure, atraves da chave SAS com permissoes de escrita"""
       blobService = BlockBlobService(accountName, sas_token=GetSasWRITEToken())
       localfile = "videoshoot.mp4"
       blobService.create_blob_from_path(containerName, blobname, localfile)
       writeLog("Video uploaded to Azure")

    def getBlob():
        """Obtem o URL do blob atraves de uma chave SAS com permissoes de leitura"""
        sas_ReadToken = blobService.generate_container_shared_access_signature(containerName, ContainerPermissions.READ, datetime.utcnow() + timedelta(hours=1))
        blobURL=blobService.make_blob_url(containerName, blobname, "https", sas_token=sas_ReadToken)
        return blobURL

    def telegramBotSendMessage():
       """Envia o URL do blob para a conversa do Telegram, atraves de um Telegram bot"""
       telegramToken=os.environ.get('TELEGRAM_TOKEN') #TOKEN DO TELEGRAM BOT, ESTA NAS VARIAVEIS DE SISTEMA
       chat_id = "698535420"
       bot = telegram.Bot(telegramToken)
       video=getBlob()
       botao_abrir = telegram.KeyboardButton(text="OPEN " u'\U0001F513')
       botao_recusar = telegram.KeyboardButton(text=u'\U000026D4')
       teclado = [[botao_abrir, botao_recusar]]
       reply_markup = telegram.ReplyKeyboardMarkup(teclado,resize_keyboard="true=",one_time_keyboard="true")
       bot.send_video(chat_id, video,caption="\n\n <b>Someone rang the bell</b>\n"+timeNow.strftime("%d/%m/%Y %H:%M")+"\n\n Do you want to unlock the door?"
       ,parse_mode='HTML' ,reply_markup=reply_markup)
       writeLog("Message sent")

    UploadBlob()
    telegramBotSendMessage()

while True:
   inputValue = GPIO.input(18) #Campainha configurada no PIN 22
   if (inputValue == False):
       writeLog("Bell pressed")
       VideoShot()
       AzureBlob()
       os.remove("videoshoot.mp4")
       time.sleep(3)
GPIO.cleanup()

