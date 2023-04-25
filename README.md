# Cloud Keeper

O Cloud Keeper é um modelo conceptual de uma campainha inteligente usando tecnologias IOT e Cloud, desenvolvido no âmbito do meu projeto final de licenciatura.

Este projeto utiliza o Microsoft Azure, o Telegram e um Raspberry Pi como componentes principais.


<img src="img/Diagrama.jpg" width=100% height=70%> 

<br>
<br>
<br>
<br>

Com base na arquitetura apresentada, o fluxo do projeto é de simples compreensão:
<img align="right" src="img/Telegram_Options.jpg" width=25% height=30%>
1) Quando um utilizador pressiona a campainha, é transmitida a instrução para o Raspberry Pi
gravar um vídeo com duração de 10 segundos através do módulo de câmara, de modo a saber 
quem pressionou a campainha. 

2) Depois de gravar o vídeo, o Raspberry Pi envia-o para a conta de armazenamento do Azure. De seguida é obtido o URI do vídeo na conta de armazenamento do Azure (utilizando Shared Access Signatures).

3) O URI é enviado para a conversa do Telegram através de um bot, de modo a que o utilizador veja quem pressionou a campainha, juntamente com a hora a que foi pressionada e as opções para destrancar a porta ou ignorar. 

4) Após o utilizador responder com uma das opções, a resposta é registada e interpretada pelo bot. Se 
a resposta for a instrução para destrancar a porta, é transmitida para o Raspberry Pi e 
sequencialmente para o servomotor, que irá destrancar a porta.

## Usage

```python
python main.py & >/dev/null
python telegramListener.py
```
