###TODO
#Fix which channels commands will be send to and link sharing will happen
#Check triple hash comments for adding functionality
#Store ID but speak username (don't store username)




#Import packages
import os
import discord
from discord.ext import commands
from replit import db
import datetime
import asyncio

#System variables
discord_bot_token = os.environ['DiscordBotKey']
bot = commands.Bot(command_prefix="!")
client = discord.Client()


#Project variables
starting_balance = 10


#Basic bot functions
@client.event
async def on_ready():
  print("logged in as {0.user}".format(client))
  print(db.keys())
  db["sharing_state"] = "unpaused"


#Database balance adjustments
def set_balance(user, amount):
  if "balances" in db.keys():
      balances = db["balances"]
      balances[str(user.id)] = int(amount)
      db["balances"] = balances
  else:
    db["balances"]={user.id: int(amount)}

def add_balance(users, amount):
  if "balances" in db.keys():
      balances = db["balances"]
      for user in users:
        balances[str(user.id)] += int(amount)

def subtract_balance(users, amount):
  if "balances" in db.keys():
      balances = db["balances"]
      for user in users:
        print(user.id)
        print(type(user.id))
        balances[str(user.id)] -= int(amount)

def check_own_balance(user):
  '''Returns a readable string containing the balance.'''
  if "balances" in db.keys():
    balances = db["balances"]
    if str(user.id) in balances.keys():
      balance = f'{user.mention}, you have {str(balances[str(user.id)])} points in the bank'
    else: balance = "You do not have a bank yet! Try /help"
  return balance

def check_balance(user):
  '''Returns the balance as an integer. No balance is returned as None'''
  if "balances" in db.keys():
    balances = db["balances"]
    if str(user.id) in balances.keys():
      balance = balances[str(user.id)]
    else: balance = None
  return balance



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
    db["tasks"] = {invite_link: {"no_invites" : int(no_invites), "users" : []}}
    print("tasks db initialized")

def add_user_to_task(invite_link, user):
  '''If tasks is in the DB, and the link has already been added, and number of current users is less than the number of current invites, add the user to the invite_link in the DB.''' 
  if "tasks" in db.keys():
    if invite_link in db["tasks"].keys():
      if len(db["tasks"][invite_link]["users"]) < db["tasks"][invite_link]["no_invites"]:
        db["tasks"][invite_link]["users"].append([user])

    

#Bot commands
@bot.command()
async def start(message):
  ###Check if balance not already initialized
  if "balances" in db.keys():
    if str(message.author.id) not in db["balances"].keys():
      set_balance(message.author, starting_balance)
      await message.channel.send(
        "Your account is initialized with {0}".format(starting_balance)
        )
    else:
      await message.channel.send(
        "Whoops! You have already initialized your bank. Check out !help"
        )

@bot.command()
async def bank(message):
  if "balances" in db.keys():
    balance = check_own_balance(message.author)
    await message.channel.send(str(balance))

@bot.command()
@commands.has_role("Linkasaurus")
async def share_link(ctx, name_of_project, invite_link, no_invites):
  ##Init variables
  ticker=2
  error_state = None
  user_balance = check_balance(ctx.author)


  ##Validate input
  try:
    no_invites = int(no_invites)
  except:
    error_state = "Your command was incorrect. Try !help"
    await ctx.channel.send(error_state)



  ##Check none ongoing already:
  if db["sharing_state"] == "paused":
    error_state = "There is already a link being shared. Try again once it has finished"
    await ctx.channel.send(error_state)
  elif user_balance < no_invites:
    error_state = f"You only have {user_balance} points but you need {no_invites}. Join other links to gain more points!"
    await ctx.channel.send(error_state)
  elif len(invite_link) != 8:
        error_state = "It seems like your discord link doesn't have the correct amount of characters (8)"
        await ctx.channel.send(error_state)



  if error_state == None:
    ##Turn off link sharing for other people
    db["sharing_state"] = "paused"
    
    ##Announcement
    await ctx.channel.send(f'{ctx.author.mention}')
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
    new_message = await ctx.channel.fetch_message(my_message.id)

    ##Check for reactions
    reactions = discord.utils.get(new_message.reactions)
    reactions_count = reactions.count

    while reactions_count < no_invites:
      await asyncio.sleep(ticker)
      new_message = await ctx.channel.fetch_message(my_message.id)
      
      reactions = discord.utils.get(new_message.reactions)
      reactions_count = reactions.count
      '''
      if reactions_count > 0:
        await my_message.remove_reaction('👍', new_message.author)
      '''

    ##Announce joiners and make balance adjustments
    joiners = await new_message.reactions[0].users().flatten()
    await announce_joiners(ctx, name_of_project, invite_link, no_invites, joiners)
    subtract_balance([ctx.author], no_invites)
    add_balance(joiners, 1)

    ##Turn on link sharing for other people
    db["sharing_state"] = "unpaused"






#Admin functions
@bot.command()
@commands.has_role("Linkasaurus Team")
async def admin_set_balance(ctx, name, amount):
  user = ctx.message.guild.get_member_named(name)
  set_balance(user, amount)

@bot.command()
@commands.has_role("Linkasaurus Team")
async def admin_check_balance(ctx, name):
  user = ctx.message.guild.get_member_named(name)
  await ctx.channel.send(check_own_balance(user))

@bot.command()
@commands.has_role("Linkasaurus Team")
async def admin_print_balances(message):
  if "balances" in db.keys():
    await message.channel.send(str(db["balances"]))

@bot.command()
@commands.has_role("Linkasaurus Team")
async def admin_print_tasks(message):
  if "tasks" in db.keys():
    await message.channel.send(str(db["tasks"]))

@bot.command()
@commands.has_role("Linkasaurus Team")
async def admin_reset_balances(message):
    reset_all_balances()
    await message.channel.send("All balances have been deleted.")

@bot.command()
@commands.has_role("Linkasaurus Team")
async def adjust_db(message, key, value):
    db[key] = value
    await message.channel.send(f"{key} set to {value}")
  






#Bot helper functions
async def announce_joiners(ctx, name_of_project, invite_link, no_invites, joiners):
  time_to_join =1200
  joiners_string = ""
  for i in range(0, no_invites):
    joiners_string += joiners[i].mention + ", "
  joiners_announce_message = discord.Embed(color = 0x2ecc71)
  joiners_announce_message.set_author(name = 'Linkasaurus Bot')
  joiners_announce_message.add_field(name="Congratulations! The following people want to use your invite link!", value=f'{joiners_string}')
  joiners_announce_message = await ctx.channel.send(embed = joiners_announce_message)
  for i in range(0, no_invites):
    await ctx.channel.send(f'{joiners[i].mention}')
  joiners_info_message = discord.Embed(color = 0x2ecc71)
  joiners_info_message.set_author(name = 'Linkasaurus Bot')
  joiners_info_message.add_field(name='INSTRUCTIONS', value=f'You have agreed to join https://discord.gg/{invite_link}. You must do so before {datetime.datetime.utcnow() + datetime.timedelta(seconds = time_to_join)}. Please join now, have a look around, and send some messages! You have recieved 1 point each. Failure to join within the given time will result in you being put on THE NAUGHTY LIST!!!')
  joiners_info_message.set_footer(text = f'{ctx.author}, please check if all users have joined using your code by the deadline. If not, contact a mod for support.')
  joiners_info_message = await ctx.channel.send(embed = joiners_info_message)



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