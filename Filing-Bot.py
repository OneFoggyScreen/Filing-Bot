#Importing Libaries

#***************************************#

import discord, os, datetime as DT, json, random, collections
from discord.ext import commands

#Custimization for the bot!
#***************************************#

ownerid =  #To get your id, all you have to do is right click your profile in a server or dm and copy Id
currentdir = '' #Chnage this directory to where the everything is being stored Make sure \ are /!
color = 0x0E5476 #Change to whatever you want the embed colors to be
customstat = "Test" #Change to whatever you want the custom status to be
prefix = '!' #Changes this to whatever you want the bot prefix to be

#Basic bot setup
#***************************************#
TOKEN = open("TOKEN.txt", "r")
client = commands.Bot(command_prefix = prefix)
os.chdir(r'' + currentdir)

#***************************************#

@client.command(name='randompicture', aliases=['RandomPic', 'Pic'], help='Gives you a random picture. Allows the use of tags sperated by spaces as arguments.')
async def randompic(ctx, *args):
	if str(args) == "()":
		tags = ""
	else:
		tags = list(args)
		for i in range(len(tags)):
			tags[i] = tags[i].lower()

	await RandomPick(ctx, tags)

@client.command(name='addtag', aliases=['AddTag', 'Add'], help='Adds certain tags to the last photo you called.')
async def addtag(ctx, *args):
	if ctx.message.author.id == ownerid:
		tags = list(args)
		for i in range(len(tags)):
			tags[i] = tags[i].lower()
		await addtag(ctx, tags)

@client.command(name='removetag', aliases=['RemoveTag', 'remove'], help='Removes certain tags of the last photo you called.')
async def removetag(ctx, *args):
	if ctx.message.author.id == ownerid:
		tags = list(args)
		for i in range(len(tags)):
			tags[i] = tags[i].lower()
		await removetags(ctx, tags)

@client.command(name='picture', aliases=['pic', 'PIcture'], help='Shows you the picture and allows you to use addtag and removetag on it.')
async def pic(ctx, *args):
	tags = list(args)
	await searches(ctx, tags)
	
@client.command(name='search', aliases=['Search', 'Se'], help='Allows you to search for an image by it\'s file name.')
async def search(ctx, args):
	await searching(ctx, args)
		
@client.command(name='refresh', aliases=['Refresh', 'Re'], help='Allows you to refresh the images in the storage and cull ones you don\'t have anymore.')
async def refresh(ctx):
	if ctx.message.author.id == ownerid:
		await update_pictures()
		await ctx.send("Images have been refreshed!")
#***************************************#

async def update_pictures():
	with open('ItemStore.json', 'r') as f:
		itemstore = json.load(f)
	old_files = []
	current_files = []
	for filename in os.listdir('./Items'):
		if not filename in itemstore:
			itemstore[filename] = {}
			itemstore[filename]['tags'] = []
		current_files.append(filename)
	for i in itemstore.keys():
		old_files.append(i)
	for i in current_files:
		if old_files != []:
			old_files.remove(i)
	for i in old_files:
		del itemstore[str(i)]
	with open('ItemStore.json', 'w') as f:
		json.dump(itemstore, f)

#***************************************#


#Go through all of the items and compare the tags, if all of them match then it will add it to a list, which it will later draw from later and then send

async def RandomPick(ctx, args):
	with open('ItemStore.json', 'r') as f:
		itemstore = json.load(f)
	tags = args
	if tags == "":
		pics = list(itemstore)
		randomp = random.choice(pics)
		tags = fetchtagsclean(randomp)
		embed = discord.Embed(title="Cute Dog Picute", color=color)
		embed.add_field(name="Tags", value=str(tags), inline=False)
		embed.set_image(url="attachment://" + str(randomp))
		image = discord.File(str(currentdir) + "/Items/" + str(randomp))
		await ctx.send(embed=embed, file=image)
		await userstore(ctx, randomp)
	else:
		masterpics = []
		for key, value in itemstore.items():
			itemstags = []
			for n in value['tags']:
				itemstags.append(n)
				check =  all(item in n for item in tags)
				if check is True:
					masterpics.append(key)		
		if masterpics == []:
			await ctx.send("We couldn't find any posts with those tag(s)")
		randomp = random.choice(masterpics)
		tags = fetchtagsclean(randomp)
		embed = discord.Embed(title="Cute Dog Picute", color=color)
		embed.add_field(name="Tags", value=str(tags), inline=False)
		embed.set_image(url="attachment://" + str(randomp))
		image = discord.File(str(currentdir) + "/Items/" + str(randomp))
		await ctx.send(embed=embed, file=image)
		await userstore(ctx, randomp)
#***************************************#

async def searches(ctx, args):
	with open('ItemStore.json', 'r') as f:
		itemstore = json.load(f)
	args = str(args[0])
	print(args)
	leaders = {}
	for key in itemstore.keys():
		if key.startswith(str(args)):
			leaders[str(key)] = itemstore[str(key)]['tags']
		else:
			print(f'{key} Didn\'t Start with {str(args)}')
	templist = list(leaders)
	templist = templist[0]
	tags = fetchtagsclean(templist)
	embed = discord.Embed(title="Cute Dog Picute", color=0x0E5476)
	embed.add_field(name="Tags", value=str(tags), inline=False)
	embed.set_image(url="attachment://" + str(templist))
	image = discord.File(str(currentdir) + "/Items/" + str(templist))
	await ctx.send(embed=embed, file=image)
	print(templist)
	await userstore(ctx, templist)

#***************************************#

async def searching(ctx, search):
	with open('ItemStore.json', 'r') as f:
		itemstore = json.load(f)
	leaders = {}
	for key in itemstore.keys():
		if key.startswith(str(search)):
			leaders[str(key)] = itemstore[str(key)]['tags']
		else:
			print(f'{key} Didn\'t Start with {str(search)}')
	finals = ""
	for i in leaders:
		tags = fetchtags(i)
		content = str(f'{str(i)} has the tags of {tags}\n')
		finals = finals + content
	await ctx.send(finals)

#***************************************#

#The function that is called that adds the tags provided
async def addtag(ctx, tagss):
	#Find user's last image in ItemStore
	with open('users.json', 'r') as t:
		userstore = json.load(t)
	for key in userstore.keys():
		if str(key) != str(ctx.author.id):
			return
		if str(key) == str(ctx.author.id):
			lastphoto = userstore[str(key)]['lastphoto']
			print(f'Found user\'s last phot {lastphoto}')

	#With that information, it finds the tags on the last image	- getting ready to add more to them
	with open('ItemStore.json', 'r') as f:
		itemstore = json.load(f)
	for key in itemstore.keys():
		if str(key) != str(lastphoto):
			print("")
		if str(key) == str(lastphoto):
			old_tags = itemstore[str(key)]['tags']
			print(f'Found {lastphoto}\'s tags - {old_tags}')
			break

	#Go through tags and compare with normal tags, if there's extra, it will ignore

	for i in old_tags:
		if tagss.count(i) > 0 :
			tagss.remove(i)

	#Adds the cleaned tags
	itemstore[str(key)]['tags'] = itemstore[str(key)]['tags'] + tagss
	with open('ItemStore.json', 'w') as f:
		json.dump(itemstore, f)
	await ctx.send('The current tags are ' + str(itemstore[str(key)]['tags']) + ' for image ' + str(lastphoto))

#***************************************#

#The function that is called that removes the tags provided
async def removetags(ctx, tagss):
	#Find user's last image in ItemStore
	with open('users.json', 'r') as t:
		userstore = json.load(t)
	for key in userstore.keys():
		if str(key) != str(ctx.author.id):
			return
		if str(key) == str(ctx.author.id):
			lastphoto = userstore[str(key)]['lastphoto']
			print(f'Found user\'s last phot {lastphoto}')

	#With that information, it finds the tags on the last image	- getting ready to remove them
	with open('ItemStore.json', 'r') as f:
		itemstore = json.load(f)

	for key in itemstore.keys():
		if str(key) != str(lastphoto):
			print("")
		if str(key) == str(lastphoto):
			old_tags = itemstore[str(key)]['tags']
			print(f'Found {lastphoto}\'s tags - {old_tags}')
			break

	#Go through tags and remove any if there are in tagss - which is what a userwants removed!

	for i in tagss:
		if itemstore[str(key)]['tags'].count(i) > 0 :
			itemstore[str(key)]['tags'].remove(i)
			print(itemstore[str(key)]['tags'])

	with open('ItemStore.json', 'w') as f:
		json.dump(itemstore, f)
	await ctx.send('The current tags are ' + str(itemstore[str(key)]['tags']) + ' for image ' + str(lastphoto))

#***************************************#

def fetchtagsclean(image):
	with open('ItemStore.json', 'r') as t:
		itemstore = json.load(t)
	tagger = []
	for key in itemstore.keys():
		if str(key) == str(image):
			tags = itemstore[str(key)]['tags']
			if tags != []:
				tagger.append(tags)
				break
			else:
				tagger = "No Tags!"
		if str(key) != str(image):
			print(f"{key} doesn't match {image}!")
	print(tagger)
	#champ = ", ".join(tagger)
	tagger = str(tagger).strip("[]")
	print(tagger)
	return tagger

def fetchtags(image):
	with open('ItemStore.json', 'r') as t:
		itemstore = json.load(t)
	for key in itemstore.keys():
		if str(key) == str(image):
			tags = itemstore[str(key)]['tags']
	return tags

#***************************************#

#Updates the user's last photo and makes a slot for them if they don't have one already!
async def userstore(ctx, image):
	with open('users.json', 'r') as t:
		userstore = json.load(t)
	userstring = str(ctx.author.id)

	#First Time Setup for new users
	if not userstring in userstore:
		userstore[userstring] = {}
		userstore[userstring]['lastphoto'] = str(image)

	#Sets the last photo
	userstore[userstring]['lastphoto'] = str(image)
	with open('users.json', 'w') as t:
		json.dump(userstore, t)

#***************************************#

#Sets customstatus for some bling
@client.event
async def on_ready():
    activity = discord.Activity(name=customstat, type=discord.ActivityType.watching)
    print(DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Bot Loaded!")
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=activity)

#***************************************#

#Runs the bot
client.run(TOKEN.read())

