import discord
from discord.ext import commands
import time
import datetime
import threading
import asyncio
import os
import requests
import json
import random
from replit import db
from server_runner import server_runner

downWords = ["Procrastinate","procrastinate","Procrastinating","procrastinating"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='!',intents=intents)

def get_joke() :
  joke = requests.get("https://v2.jokeapi.dev/joke/Any?type=single")
  data = json.loads(joke.text)
  result = ('joke category: '+data['category']+'\n'+data['joke'])
  return(result)

def addBanWords(word):
  if "bannedWords" in db.keys():
    bannedW = db["bannedWords"]
    bannedW.append(word)
    db["bannedWords"] = bannedW
  else:
    db["bannedWords"] = [word]

def deleteBan(word):
  num = 0
  bannedW = db["bannedWords"]
  for i in range(len(bannedW)):
    if bannedW[i] == word:
      del bannedW[i]
      db["bannedWords"] = bannedW

def clearBan():
  db["bannedWords"] = []

@client.event
async def on_ready():
  print("{0.user} has awaken!".format(client))
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="YouTube"))

@client.event
async def on_member_join(self,member):
  await member.guild.system.channel.send("Welcome {0.mention} to {1.name}".format(member,member.guild))

@client.event
async def on_message(message):
  await client.process_commands(message)
  if message.author == client.user:
    return

  string = message.content
  print(string)
  #await message.author.send("Hello I didn't pick up your message!")

##########################################
#encouraging reply function
  if any(w in string for w in downWords):
    await message.reply("Keep up! Don't be lazy!")

##########################################
#words checking and reply functions

  if message.content.startswith("/joke"):
    print("on joke...")
    joke = get_joke()
    await message.channel.send(joke)

#switch every words into upper/lower and check it from there
  if "bannedWords" in db.keys():
    if any(w in string for w in db["bannedWords"]):
      await message.delete(delay=1)

###########################################
#adding and delete ban words functions

  if string.startswith("/addBan"):
    newBan = string.split("/addBan ",1)[1]
    addBanWords(newBan)
    await message.reply("New ban word have been added into the database!\nCurrent banned words: \n" + ",".join(db["bannedWords"]))

  if string.startswith("/delBan"):
    delBan = string.split("/delBan ",1)[1]
    deleteBan(delBan)
    await message.reply("{0.} has been deleted from the database!".format(delBan))
  
  if string.startswith("/clearBan"):
    clearBan()
    await message.reply("All banned words have been removed.\nCurrent banned words: \n" + ",".join(db["bannedWords"]))

  ban = []
  if "bannedWords" in db.keys():
    #ban = ban + db["bannedWords"]
    ban = list(db["bannedWords"])
  
  if string.startswith("/banWords"):
    await message.channel.send("Current banned words: ")
    await message.channel.send(ban)

#############################################
#roll a dice function

  if string.startswith("/roll"):
    await message.channel.send("you got :\t"+str(random.randrange(7)))

#############################################
  #flip a coin function
  coin = ['head','tail']
  if string.startswith("/flipcoin"):
    await message.channel.send("you got :\t"+coin[random.randint(0,1)])

#############################################
#reminder function

  if string.startswith("/reminder"):
    strList = string.split()
    if strList[2] in ["seconds", "second", "sec", "secs", "s"]:
      timerSec = float(strList[1])
      await message.reply("A reminder have been set from " + str(message.author).upper() + ", a DM will be send to you shortly after " + strList[1] + " second(s).")
      await asyncio.sleep(timerSec)
      await message.author.send("REMINDER : "+' '.join(strList[3:]))

    elif strList[2] in ["minutes", "minute", "min", "mins", "m"]:
      timerMin = float(strList[1]) * 60
      await message.reply("A reminder have been set from " + str(message.author).upper() + ", a DM will be send to you shortly after " + strList[1] + " minute(s).")
      await asyncio.sleep(timerMin)
      await message.author.send("REMINDER : "+' '.join(strList[3:]))

    elif strList[2] in ["hour", "hours", "h"]:
      timerH = float(strList[1]) * 3600
      await message.reply("A reminder have been set from " + str(message.author).upper() + ", a DM will be send to you shortly after " + strList[1] + " hour(s).")
      await asyncio.sleep(timerH)
      await message.author.send("REMINDER : "+' '.join(strList[3:]))

    else:
      await message.reply("Error : Invalid input! Here's how you enter a valid command:\n\t/reminder {number} {hour(s)/minute(s)/second(s)} {sentence}.")

#############################################
#send reminder function
  if string.startswith("/sendReminder"):
    strList = string.split()
    print(strList)
    print(message.author)
    us = strList[1]
    await user.send(us,strList[2:])
#############################################
#help command function
  
  if string.startswith("--help"):
    await message.reply("This is an alpha version of the ProcrastonatorBot.\n--help :\n1. /joke\n\tgrabe a joke from the internet.\n2. /addBan (word that you wish to be banned in this server.)\n\te.g: /addBan your mama\n3. /delBan (word that you wish to be banned in this server.)\n\te.g: /delBan your mama\n4. /clearBan\n\tRemove all the banned words.\n5. /banWords\n\tCheck the words that currently being ban.\n6. /roll\n\troll a dice.\n7. /flipcoin\n\tflip a coin.\n8. /reminder\n\tsetting a reminder, bot will DM you a reminder based on how long of the timer.\n\te.g.\n\tuserInput : /reminder 1 hour I want to eat now.\n\toutput : REMINDER : I want to eat now.")

##############################################
#sending DM to user function

@client.command()
async def reminderSec(ctx, user: discord.Member, *, message=None):
  await ctx.reply("Please reply me how many second(s) you want")
  sec = await client.wait_for('message',check = lambda m: m.author.id == ctx.author.id)
  
  if sec.content.isdigit() and int(sec.content) > 0:
    await ctx.reply("A reminder have been set for " + str(user.name).upper() + ", a DM will be send to them shortly after " + str(sec.content) + " second(s).")
    await asyncio.sleep(int(sec.content))
    await user.send("REMINDER : "+message)
  else:
    print("Invalid input!")

@client.command()
async def reminderMin(ctx, user: discord.Member, *, message=None):
  await ctx.reply("Please reply me how many miniute(s) you want")
  min = await client.wait_for('message',check = lambda m: m.author.id == ctx.author.id)
  
  if min.content.isdigit() and int(min.content) > 0:
    m = int(min.content) * 60
    await ctx.reply("A reminder have been set for " + str(user.name).upper() + ", a DM will be send to them shortly after " + str(min.content) + " minute(s).")
    await asyncio.sleep(m)
    await user.send("REMINDER : "+message)
  else:
    print("Invalid input!")

@client.command()
async def reminderH(ctx, user: discord.Member, *, message=None):
  await ctx.reply("Please reply me how many hour(s) you want")
  hour = await client.wait_for('message',check = lambda m: m.author.id == ctx.author.id)
  
  if hour.content.isdigit() and int(hour.content) > 0:
    h = int(hour.content) * 3600
    await ctx.reply("A reminder have been set for " + str(user.name).upper() + ", a DM will be send to them shortly after " + str(hour.content) + " hour(s).")
    await asyncio.sleep(h)
    await user.send("REMINDER : "+message)
  else:
    print("Invalid input!")

server_runner()
client.run(os.getenv("TOKEN"))