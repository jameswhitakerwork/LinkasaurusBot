#Import packages
import os
import discord
from discord.ext import commands
from replit import db
import datetime
import asyncio

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
    tasks[invite_link] = {"no_invites" : int(no_invites), "users" : []}
    db["tasks"] = tasks
  else:
    db["tasks"] = {invite_link: {"no_invites" : int(no_invites), "us ers" : []}}
    print("tasks db initialized")

def add_user_to_task(invite_link, user):
  '''If tasks is in the DB, and the link has already been added, and number of current users is less than the number of current invites, add the user to the invite_link in the DB.''' 
  if "tasks" in db.keys():
    if invite_link in db["tasks"].keys():
      if len(db["tasks"][invite_link]["users"]) < db["tasks"][invite_link]["no_invites"]:
        db["tasks"][invite_link]["users"].append([user])
    

#Bot commands
@bot.command()
async def print_balances(message):
  if "balances" in db.keys():
    await message.channel.send(str(db["balances"]))

@bot.command()
async def print_tasks(message):
  if "tasks" in db.keys():
    await message.channel.send(str(db["tasks"]))

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

@bot.command()
@commands.has_role("Linkasaurus")
async def share_link(ctx, name_of_project, invite_link, no_invites):
  ###Check none ongoing already
  ###Validate input
  ###Check points
  ticker=2
  no_invites = int(no_invites)
  '''
  give = discord.Embed(color = 0x2ecc71)
  give.set_author(name = f'GIVEAWAY TIME!', icon_url = 'https://i.imgur.com/VaX0pfM.png')
  give.add_field(name= f'{ctx.author.name} is giving away: {prize}!', value = f'React with 🎉 to enter!\n Ends in {round(time/60, 2)} minutes!', inline = False)
  end = datetime.datetime.utcnow() + datetime.timedelta(seconds = time)
  give.set_footer(text = f'Giveaway ends at {end} UTC!')
  my_message = await channel.send(embed = give)
  '''
  ##Announcement
  sharelinkmessage = discord.Embed(color = 0x2ecc71)
  sharelinkmessage.set_author(name = 'Linkasaurus Bot')
  sharelinkmessage.add_field(
    name=f'{ctx.author.name} is requesting that {str(no_invites)} people join the {name_of_project} server, using their code https://discord.gg/{invite_link}.',
    value=f'Each person will recieve one point from {ctx.author.name}. The first {str(no_invites)} to react to this message with a "👍" will get a point!')
  end = datetime.datetime.utcnow() + datetime.timedelta(seconds = ticker)
  sharelinkmessage.set_footer(text = f'If there are not enough people by {end} then the request is cancelled.')
  my_message = await ctx.channel.send(embed = sharelinkmessage)

  ##React to the message
  await my_message.add_reaction('👍')
  new_message = await channel.fetch_message(my_message.id)

  ##Check for reactions
  users = await new_message.reactions[0].users().flatten()
  while len(users) < no_invites:
    await asyncio.sleep(ticker)
    users = await new_message.reactions[0].users().flatten()
  await message.channel.send("Congratulations! these people want to join this server using your link.")
  



@client.event
async def on_reaction_add(reaction, user):
  await message.channel.send("user added reaction")
  print("user added reaction")




#Test commands
@bot.command()
async def parrot(message, arg):
  await message.channel.send(arg)

@bot.command()
async def start_task(message, invite_link, no_invites):
  start_new_task(invite_link, int(no_invites))

@bot.command()
async def add_user_task(message, invite_link):
  add_user_to_task(invite_link, message.author.name)

#Help command
@bot.command()
async def helpme(ctx):
    # Help command that lists the current available commands and describes what they do
    ghelp = discord.Embed(color = 0x7289da)
    ghelp.set_author(name = 'Commands/Help', icon_url = '')
    ghelp.add_field(name= 'helpme', value = 'This command took you here!', inline = False)
    ghelp.add_field(name= 'version', value = 'Displays the current version number and recent updates.', inline = False)
    ghelp.add_field(name= 'giveaway', value = '__Can only be accessed by users with the "Giveaway Host" role.__\nStarts a giveaway for the server! This command will ask the host 3 questions.  The host will have 30 seconds per question to answer or they will be timed out!', inline = False)
    ghelp.add_field(name= 'reroll `#channel_name` `message id`', value = '__Can only be accessed by users with the "Giveaway Host" role.__\nThey must follow the command with the copied message id from the giveaway.', inline = False)
    ghelp.set_footer(text = 'Use the prefix "g!" before all commands!')
    await ctx.send(embed = ghelp)

bot.run(discord_bot_token)


'''
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
  '''