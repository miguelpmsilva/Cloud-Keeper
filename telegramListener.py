#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import subprocess
import telegram
import requests
import time
import json
import os
from bottle import run, post, request as bottle_request

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

def writeLog(logMsg):
   """Escreve no ficheiro de log"""
   f = open("logfile.txt", "a")
   f.write(time.strftime('%Y-%m-%d %H:%M:%S -> ', time.localtime())+logMsg+'\n')
   f.close()

def telegramBotSendMessage(message):
   """Envia mensagem para a conversa"""
   telegramToken=os.environ.get('TELEGRAM_TOKEN') #TOKEN DO TELEGRAM BOT, ESTA NAS VARIAVEIS DE SISTEMA
   chat_id = "698535420"
   bot = telegram.Bot(telegramToken)
   bot.sendMessage(chat_id, "<b>"+message+"</b>", parse_mode='HTML')


def abrirPorta():
   """Abre a porta atraves do motor"""
   p = GPIO.PWM(7,50)
   p.start(7.5)
   p.ChangeDutyCycle(2.5)
   time.sleep(1)
   p.stop()

def fecharPorta():
   """Fecha a porta atraves do motor"""
   p = GPIO.PWM(7,50)
   p.start(2.5)
   p.ChangeDutyCycle(7.5)
   time.sleep(1)
   p.stop()

def ngrok():
   """Inicia o ngrok como subprocesso"""
   
   telegramToken=os.environ.get('TELEGRAM_TOKEN') #TOKEN DO TELEGRAM BOT, ESTA NAS VARIAVEIS DE SISTEMA
   ngrok = subprocess.Popen(
      ['ngrok','http','8080'],
      stdout=subprocess.PIPE)
   #Inicia o ngrok como subprocesso na porta 8080
   time.sleep(5)
   localhost_url = "http://localhost:4040/api/tunnels"
   #URL com detalhes do tunel
   
   tunnel_url = requests.get(localhost_url).text
   #Obtem as informações do tunel

   j = json.loads(tunnel_url)
   tunnel_url = j['tunnels'][1]['public_url']
   #Obtem o URL publico fornecido pelo ngrok

   if(tunnel_url[:7] == "http://"):
       #Caso o URL venha em http é transformado em https e definido o webhook do Telegram bot
       requests.get("https://api.telegram.org/bot"+telegramToken+"/setwebhook?url=https://"+tunnel_url[7:])
   else:
       #Case o URL ja venha em https, apenas e definido o webhook do Telegram bot
       requests.get("https://api.telegram.org/bot"+telegramToken+"/setwebhook?url="+tunnel_url)


@post('/')
def main():
   data = bottle_request.json #Obtem as respostas da conversa do Telegram
   message_text = data['message']['text'] #Obtem o texto das respostas
   if (message_text == "OPEN "):
       #Caso a resposta seja para abrir
       abrirPorta()
       telegramBotSendMessage("Door Open")
       writeLog("Door Open")

   if (message_text == "/close"):
       #Caso a resposta seja o comando para fechar
       fecharPorta()
   print(message_text)

if __name__ == '__main__':
   ngrok()
   run(host='localhost', port=8080) #Inicia o servidor bottle na porta 8080
   GPIO.cleanup()

