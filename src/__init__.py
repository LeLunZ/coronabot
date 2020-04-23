import traceback

import discord
import requests
from discord.ext.tasks import loop
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)

TOKEN = ''

client = discord.Client()
channel_list = {}
school_infos_tuple_list = []
msg_at = ''
msg_de = ''
url_raw_bmbwf = 'https://www.bmbwf.gv.at'
ua = UserAgent()

@loop(hours=1)
async def update_corona():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    user_agent = ua.random
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://info.gesundheitsministerium.at")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'divErkrankungen'))
        )
        text = element.text
        corona = ['Stand in Österreich', f'Bestätigte Fälle: {text}']
        global msg_at, msg_de
        new_msg = '\n'.join(corona)
        if msg_at != new_msg:
            for channel in channel_list:
                if 'at' in channel_list[channel]:
                    await channel.send(new_msg)
            msg_at = new_msg
    except:
        print('error austria', flush=True)

    try:
        url_bmbwf = 'https://www.bmbwf.gv.at/Themen/Hochschule-und-Universität/Aktuelles/corona.html'
        url_bmbwf2 = 'https://www.bmbwf.gv.at/Themen/schule/beratung/corona.html'
        school_corona_page = html.fromstring(requests.get(
            url_bmbwf).content)
        school_infos = school_corona_page.xpath('//main/ul/li/a/@href|//main/ul/li/a/text()')

        school_corona_page = html.fromstring(requests.get(
            url_bmbwf2).content)
        school_infos.extend(school_corona_page.xpath('//main/ul/li/a/@href|//main/ul/li/a/text()'))
        for i in range(0, len(school_infos), 2):
            if (school_infos[i], school_infos[i + 1]) not in school_infos_tuple_list:
                for channel in channel_list:
                    if 'at' in channel_list[channel]:
                        await channel.send(f'{school_infos[i + 1]}: \n{url_raw_bmbwf + school_infos[i]}')
                school_infos_tuple_list.append((school_infos[i], school_infos[i + 1]))
    except:
        print('error austria2', flush=True)


    try:
        url_rki = 'https://corona.rki.de/'
        driver.get(url_rki)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//iframe[@class="iframe-widget_1"]'))
        )
        iframe_url = element.get_attribute('src')
        driver.get(iframe_url)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[name()="svg"]/*[name()="g"][2]/*[name()="svg"]/*[name()="text"]'))
        )
        corona = [e.text for e in element]
        arr = corona[1:4:2]
        arr2 = corona[2:5:2]
        corona_test = []
        for arr3 in zip(arr, arr2):
            corona_test.append(f'{arr3[0]} {arr3[1]}')

        arr = corona[6:-1:2]
        arr2 = corona[7::2]
        for arr3 in zip(arr, arr2):
            corona_test.append(f'{arr3[0]} {arr3[1]}')

        corona_test.insert(2, corona[5])
        corona_test.insert(2, '')
        corona_test.insert(0, corona[0])
        corona = corona_test
        global msg_at, msg_de
        corona.insert(0, 'Stand in Deutschland')
        new_msg = '\n'.join(corona)
        if msg_de != new_msg:
            for channel in channel_list:
                if 'de' in channel_list[channel]:
                    await channel.send(new_msg)
            msg_de = new_msg
    except:
        print("error germany", flush=True)


    driver.quit()



@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!corona '):
        msg_raw = ''.join(message.content.split(' ')[1:]).lower()
        if 'at' in msg_raw or 'austria' in msg_raw:
            if message.channel not in channel_list:
                await message.channel.send('You subscribed to Austrian Corona News')
                channel_list[message.channel] = ['at']
            else:
                if 'at' in channel_list[message.channel]:
                    channel_list[message.channel].remove('at')
                    await message.channel.send('You unsubscribed from Corona News')
                else:
                    await message.channel.send('You subscribed to Austrian Corona News')
                    channel_list[message.channel] = ['at']
        if 'de' in msg_raw or 'germany' in msg_raw:
            if message.channel not in channel_list:
                await message.channel.send('You subscribed to German Corona News')
                channel_list[message.channel] = ['de']
            else:
                if 'de' in channel_list[message.channel]:
                    channel_list[message.channel].remove('de')
                    await message.channel.send('You unsubscribed from Corona News')
                else:
                    await message.channel.send('You subscribed to German Corona News')
                    channel_list[message.channel] = ['de']
        if 'info' in msg_raw:
            for tuple in school_infos_tuple_list:
                await message.channel.send(f'{tuple[1]}: \n{url_raw_bmbwf + tuple[0]}')

    elif message.content.startswith('!corona'):
        await message.channel.send(f'{msg_at}\n\n{msg_de}')


@client.event
async def on_ready():
    update_corona.start()
    print(client.user.name, flush=True)
    print(client.user.id, flush=True)


client.run(TOKEN)
