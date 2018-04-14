import discord
import asyncio
import requests
import time
import string

DISCORD_BOT_TOKEN = 'NDM0MjM2MjI2NTczNDM0ODkx.DbIc-w.ufvbmB_MSVQqd7kIHrUFMQxdxnc'

BTC_PRICE_URL_coinmarketcap = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=RUB'

client = discord.Client()
save_channel = 0
admin_list = ['265474107666202634', '282660110545846272']

prefix = '>'
stops = 0


quiz_channel = 0
quiz = 0
quiz_number = -1
set_answer = [' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ',
              ' ']
question = ['1) ',
            '2) ',
            '3) ',
            '4) ',
            '5) ',
            '6) ',
            '7) ',
            '8) ',
            '9) ',
            '10) ',
            '11) ',
            '12) ',
            '13) ',
            '14) ',
            '15) ',
            '16) ',
            '17) ',
            '18) ',
            '19) ',
            '20) ',
            '21) ',
            '22) ',
            '23) ']
quiz_answer = ['1',
          ['2', 'два'],
          '3',
          '4',
          '5',
          '6',
          '7',
          '8',
          '9',
          '10',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ',
          ' ']

channel_list = []
f = open('channel_list', 'r')
line1 = f.readline()
line2 = f.readline()
c = 0
while line1:
    channel_list.append(line1)
    channel_list.append(line2)
    line1 = f.readline()
    line2 = str(f.readline())
    print(str((c // 2) + 1) + ')' + channel_list[c][:-1] + ' ' + channel_list[c + 1][:-1])
    c = c + 2
f.close()
#print(len(channel_list))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    print('<' + message.channel.name + '>[' + message.author.name + ']' + message.content)
    global stops
    global save_channel
    global question
    global quiz_channel
    global quiz
    global quiz_number
    global set_answer
    global quiz_answer
    if message.content.startswith(prefix + 'btcprice'):
        print('[command]: btcprice ')
        btc_price_usd, btc_price_rub = get_btc_price()
        await client.send_message(message.channel, 'USD: ' + str(btc_price_usd) + ' | RUB: ' + str(btc_price_rub))

    if message.content.startswith(prefix + 'ddos'):
        if message.author.id in admin_list:
            print('[command]:!ddos ' + message.content[6:])
            i = 0
            stops = 0
            while i < 30:
                i = i + 1
                if(stops == 1):
                    break
                await client.send_message(message.channel, message.content[6:])
                time.sleep(0.5)
            stops = 0

    if (strcmp(message.content, prefix + 'stop') == 1):
        print('[command]:!stop')
        stops = 1

    if strcmp(message.content.lower(), 'печенюха') == 1 or strcmp(message.content.lower(), 'печенька') == 1:
        print('[command]:!coockie')
        await client.send_message(message.channel, "О, я тоже хочу, поделитесь?:cookie:")

    if strcmp(message.content, prefix + 'hi') == 1:
        print('[command]:!hi')
        await client.send_message(message.channel, ':sparkles:' + message.author.name + ' приветствует всех:sparkles:')

    if strcmp(message.content, prefix + 'gm') == 1:
        print('[command]:!gm')
        await client.send_message(message.channel, ':hugging:С добрым утречком:hugging:')

    if strcmp(message.content, prefix + 'help') == 1:
        print('[command]:!help')
        await client.send_message(message.channel, '```css\n' +
                                                   '[Coockie help]\n\n' +
                                                   'Печенюха/печенька - Попросит вкуснях. Это две команды. Буквы могут быть любого размера.\nПишется без префикса.\n\n' +
                                                   '>say <текст> - Напишет ваше сообщение.\n\n' +
                                                   '>hi - Поприветствует всех от вашего имени.\n\n' +
                                                   '>gm - Охайё, т.е доброе утро)).\n\n' +
                                                   '>help - Вызов этой справки.' +
                                                   '```')
    if strcmp(message.content, prefix + 'save') == 1 and message.author.id in admin_list:
        print('[command]:!save')
        save_channel = message.channel
        f = open('channel_list', 'a')
        f.write(save_channel.name + '\n' + save_channel.id)
        f.close

    if message.content.startswith(prefix + 'say '):
        print('[command]:!say')
        await client.send_message(message.channel, message.content[5:])

    if message.content.startswith(prefix + 'sayhim') and message.author.id in admin_list:
        print('[command]:!sayhim')
        await client.send_message(client.get_channel(channel_list[int(message.content[8]) * 2 - 1][:-1]), message.content[10:])

#    if message.content.startswith('Канибализм опасен для вашей жизни!!!'):
#        print('[command]:!Кусь')
#        await client.send_message(message.channel, 'Я сделаю тебе кусь')

    if strcmp(message.content, prefix + 'start quiz') == 1 and message.author.id in admin_list:
        print('[command]:!start quiz')
        quiz_channel = message.channel
        quiz = 1
        await client.send_message(message.channel, 'Викторина началась!')

    if strcmp(message.content, prefix + 'stop quiz') == 1 and message.author.id in admin_list:
        print('[command]:!stop quiz')
        quiz_channel = 0
        quiz = 0
        await client.send_message(message.channel, 'Викторина окончена((')

    if message.content.startswith(prefix + 'quiz ')  and message.author.id in admin_list and quiz == 1:
        quiz_number = int(message.content[6:]) - 1
        print('[command]:!quiz ' + str(quiz_number))
        await client.send_message(quiz_channel, question[quiz_number])

    if message.channel == quiz_channel and quiz == 1:
        if quiz_number != -1:
            if message.content in quiz_answer[quiz_number]:
                set_answer[quiz_number] = str(quiz_number + 1) + ')' + message.author.id + ' ' + message.author.name
                await client.send_message(quiz_channel, '<@' + message.author.id + '>, верно!')
                quiz_number = -1

    if strcmp(message.content, prefix + 'quizstat') == 1 and message.author.id in admin_list:
        print('[command]:!quiz stat')
        ret = '```css'
        for s in set_answer:
            ret = ret + '\n' + s
        ret = ret + '\n```'
        await client.send_message(message.channel, ret)

    if strcmp(message.content, prefix + 'quizquestions') == 1 and message.author.id in admin_list:
        print('[command]:!quizquestions')
        ret = '```css'
        for s in question:
            ret = ret + '\n' + s
        ret = ret + '\n```'
        await client.send_message(message.channel, ret)

    if strcmp(message.content, prefix + 'quizanswers') == 1 and message.author.id in admin_list:
        print('[command]:!quizanswers')
        ret = '```css'
        for s in quiz_answer:
            ret = ret + '\n' + s
        ret = ret + '\n```'
        await client.send_message(message.channel, ret)

def strcmp(s1, s2):
    i1 = 0
    i2 = 0
    s1 = s1 + '\0'
    s2 = s2 + '\0'
    while ((s1[i1] != '\0') & (s2[i2] != '\0')):
        if(s1[i1] != s2[i2]):
            return 0
        i1 = i1 + 1
        i2 = i2 + 1
    if(s1[i1] != s2[i2]):
        return 0
    else:
        return 1


def get_btc_price():
    r = requests.get(BTC_PRICE_URL_coinmarketcap)
    response_json = r.json()
    usd_price = response_json[0]['price_usd']
    rub_rpice = response_json[0]['price_rub']
    return usd_price, rub_rpice

client.run(DISCORD_BOT_TOKEN)
