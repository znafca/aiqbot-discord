import discord
from discord.ext import commands
import json
import codecs
import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
import subprocess
from html import escape

from secrets import *

bot = commands.Bot(command_prefix='/')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def price(ctx, a: str):
    options = a
    lowsymb = options.lower()
    uppsymb = options.upper()
    api_url = requests.get('https://api.coingecko.com/api/v3/coins/artiqox?localization=false')
    market_data_json = api_url.json()
    current_price_json = json.loads(json.dumps(market_data_json['market_data']))
    currency_json = json.loads(json.dumps(current_price_json['current_price']))
    if lowsymb in currency_json:
        btc_price = json.dumps(currency_json['btc'])
        symb_price = json.dumps(currency_json[lowsymb])
        last_price = format(float(btc_price), '.8f')
        if lowsymb == 'btc':
            last_fiat = format(float(symb_price), '.8f')
        else:
            last_fiat = format(float(symb_price), '.4f')
        await ctx.send("Artiqox is valued at {0}฿ ≈ {1}{2}".format(last_price,uppsymb,last_fiat))
    else:
        btc_price = json.dumps(currency_json['btc'])
        usd_price = json.dumps(currency_json['usd'])
        last_price = format(float(btc_price), '.8f')
        last_fiat = format(float(usd_price), '.4f')
        await ctx.send("Artiqox is valued at {0}฿ ≈ USD{1}".format(last_price,last_fiat))

@bot.command()
async def example(ctx, a: str):
    user = ctx.message.author
    await ctx.send("Initiating commands /give & /withdraw have a specfic format,\n use them like so:" + "\n \n Parameters: \n <user> = target user to give AIQ \n <amount> = amount of Artiqox to utilise \n <address> = Artiqox address to withdraw to \n \n Giving format: \n /give <user> <amount> \n \n Withdrawing format: \n /withdraw <address> <amount>")

@bot.command()
async def deposit(ctx, a: str):
    user = ctx.message.author
    options = a
    if user is None:
        await ctx.send("Please set a username in your profile settings!")
    elif options == "qr":
        address = "/usr/local/bin/artiqox-cli"
        result = subprocess.run([address,"getaccountaddress","DI-" + user.lower()],stdout=subprocess.PIPE)
        clean = (result.stdout.strip()).decode("utf-8")
        await ctx.send("@{0} your depositing address is: {1} for qr code follow url the https://chart.googleapis.com/chart?cht=qr&chl=artiqox%3A{1}&chs=180x180&choe=UTF-8&chld=L|2".format(user,clean))
    else:
        address = "/usr/local/bin/artiqox-cli"
        result = subprocess.run([address,"getaccountaddress","DI-" + user.lower()],stdout=subprocess.PIPE)
        clean = (result.stdout.strip()).decode("utf-8")
        await ctx.send("@{0} your depositing address is: {1}".format(user,clean))

@bot.command()
async def give(ctx, a: str, b: str):
    user = ctx.message.author
    target = a
    amount =  b
    if user is None:
        await ctx.send("Please set a username in your profile settings!")
    else:
        machine = "@ArtiqoxBot"
        machine2 = "@username"
        if target.lower() == machine.lower():
            await ctx.send("This ain't Free Parking. HODL.")
        elif target.lower() == machine2.lower():
            await ctx.send("I don't think @username is too fussy about receiving some AIQ. Let's HODL.")
        elif "@" in target:
            target = target[1:]
            core = "/usr/local/bin/artiqox-cli"
            result = subprocess.run([core,"getbalance","DI-" + user.lower()],stdout=subprocess.PIPE)
            balance = float((result.stdout.strip()).decode("utf-8"))
            amount = float(amount)
            if balance < amount:
                await ctx.send("@{0} you have insufficent funds.".format(user))
            elif target == user:
                await ctx.send("You can't give yourself AIQ.")
#            elif len(target) < 5:
#                await ctx.send("Error that user is not applicable. Discord requires users to have 5 or more characters in their @username.")
            else:
                balance = str(balance)
                amount = str(amount)
                tx = subprocess.run([core,"move","TG-" + user.lower(),"TG-" + target.lower(),amount],stdout=subprocess.PIPE)
                await ctx.send("Hey @{1}, @{0} gave you {2} AIQ".format(user, target, amount))
        else:
            await ctx.send("Error that user is not applicable.")

@bot.command()
async def balance(ctx, a: str):
    user = ctx.message.author
    options = a
    lowsymb = options.lower()
    uppsymb = options.upper()
    api_url = requests.get('https://api.coingecko.com/api/v3/coins/artiqox?localization=false')
    market_data_json = api_url.json()
    current_price_json = json.loads(json.dumps(market_data_json['market_data']))
    currency_json = json.loads(json.dumps(current_price_json['current_price']))
    if user is None:
        await ctx.send("Please set a username in your profile settings!")
    else:
        if lowsymb in currency_json:
            fiat_price = json.dumps(currency_json[lowsymb])
            if lowsymb == 'btc':
                decplace = 8
            else:
                decplace = 4
        else:
            fiat_price = json.dumps(currency_json['usd'])
            uppsymb = "USD"
            decplace = 4
        core = "/usr/local/bin/artiqox-cli"
        result = subprocess.run([core,"getbalance","DI-" + user.lower()],stdout=subprocess.PIPE)
        clean = (result.stdout.strip()).decode("utf-8")
        balance  = float(clean)
        last_fiat = float(fiat_price)
        fiat_balance = balance * last_fiat
        fiat_balance = str(round(fiat_balance,decplace))
        balance =  str(round(balance,4))
        await ctx.send("@{0} your current balance is: {1} AIQ ≈ {2}{3}".format(user,balance,uppsymb,fiat_balance))

@bot.command()
async def withdraw(ctx, a: str, b: str):
    user = ctx.message.author
    if user is None:
        await ctx.send("Please set a telegram username in your profile settings!")
    else:
        target = a
        address = target[:35]
        amount = float(b)
        core = "/usr/local/bin/artiqox-cli"
        result = subprocess.run([core,"getbalance","DI-" + user.lower()],stdout=subprocess.PIPE)
        clean = (result.stdout.strip()).decode("utf-8")
        balance = float(clean)
        if balance < amount:
            await ctx.send("@{0} you have insufficent funds.".format(user))
        else:
            amount = str(amount)
            tx = subprocess.run([core,"sendfrom","DI-" + user.lower(),address,amount],stdout=subprocess.PIPE)
            await ctx.send("@{0} has successfully withdrew to address: {1} of {2} AIQ" .format(user,address,amount))

@bot.command()
async def hi(ctx):
    user = update.message.from_user.username
    await ctx.send("Hello @{0}, how are you doing today?".format(user))

@bot.command(ctx)
async def moon(bot,update):
    await ctx.send("Rocket to the moon is taking off!")

@bot.command(ctx)
async def tip(ctx, a: str, b: str):
    user = ctx.message.author
    target = a
    amount =  b
    await ctx.send("¯\_(ツ)_/¯ Maybe try /give {0} {1}".format(target,amount))  

@bot.command()
async def info(ctx):
    embed = discord.Embed(title="AIQ bot", description="AIQ bot, give and receive AIQ on discord", color=0xeee657)
    
    # give info about you here
    embed.add_field(name="Author", value="Inetics and Cramer")
    
    # Shows the number of servers the bot is member of.
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")

    # give users a link to invite the bot to their server
#    embed.add_field(name="Invite", value="[Invite link](<insert your OAuth invitation link here>)")

    await ctx.send(embed=embed)

bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="AIQ bot", description="Receive and give AIQ on discord. List of commands are:", color=0xeee657)

    embed.add_field(name="/give @X Y", value="Gives Y of AIQ to user @X", inline=False)
    embed.add_field(name="/withdraw X Y", value="Withdraws Y of AIQ to wallet X", inline=False)
    embed.add_field(name="/balance", value="Gives the balance", inline=False)
    embed.add_field(name="/hi", value="Gives a nice greet message", inline=False)
    embed.add_field(name="/moon", value="Gives a cute moon message.", inline=False)
    embed.add_field(name="/info", value="Gives a little info about the bot", inline=False)
    embed.add_field(name="/help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)

bot.run('token_from_secrets')
