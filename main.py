#Import packages
import os
import discord
from discord.ext import commands
from replit import db

#System variables
discord_bot_token = os.environ['DiscordBotKey']
bot = commands.Bot(command_prefix="/")
client = discord.Client()

#Project variables
starting_balance = 10


#Basic bot functions
@client.event
async def on_ready():
  print("logged in as {0.user}".format(client))



#Database balance adjustments
def set_balance(username, balance):
  if "balances" in db.keys():
      balances = db["balances"]
      balances[username] = balance
      db["balances"] = balances
  else:
    db["balances"]={username: balance}


def reset_all_balances():
  if "balances" in db.keys():
    del db["balances"]

#Invite link task
def start_new_task(invite_link, no_invites):
  if "tasks" in db.keys():
    tasks = db["tasks"]
    tasks[invite_link] = {"no_invites" : no_invites, "users" : []}
    db["tasks"] = tasks
  else:
    db["tasks"] = {invite_link: {"no_invites" : no_invites, "users" : []}
    print("tasks db initialized")
    





#Bot commands
@bot.command()
async def print_balances(message):
  if "balances" in db.keys():
    for user in db["balances"]:
      await message.channel.send(str(db["balances"])) 

@bot.command()
async def start(message):
  set_balance(message.author.name + str(message.author.id), starting_balance)
  await message.channel.send(
    "Your account is initialized with {0}".format(starting_balance)
    )
  await print_balances(message)

@bot.command()
async def reset_balances(message):
    reset_all_balances()
    await message.channel.send("All balances have been deleted.")


    




#Text commands
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('/xstart'):
    set_balance(message.author.name + str(message.author.id), starting_balance)
    await message.channel.send(
      "Your account is initialized with {0}".format(starting_balance)
      )
    await print_balances(message)

  elif message.content.startswith('/xreset'):
    reset_all_balances()
    await message.channel.send("All balances have been deleted.")

  await bot.process_commands(message)

    


bot.run(discord_bot_token)

