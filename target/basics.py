from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals		
import random
import itertools

@vexis.command()
def pyeval(sender, label, args):
	if not sender.hasPermission("basics.eval"):
		sender.sendMessage(color("&c&lBasics &f- Invalid Permissions!"))
		return
	if len(args) != 1:
		sender.sendMessage(color('&c&lBasics &f- Invalid amount of arguments!'))
		return
	try:
		sender.sendMessage(repr(eval(args[0])))
	except Exception as e:
		sender.sendMessage(repr(e))
	except java.lang.Exception as e:
		sender.sendMessage(repr(e))
		

@vexis.command()
def heal(sender, label, args):
	if not sender.hasPermission("basics.heal"):
		sender.sendMessage(color("&c&lBasics &f- Invalid Permissions!"))
		return
	if len(args) > 1:
		sender.sendMessage(color('&c&lBasics &f- Invalid amount of arguments!'))
		return
	if len(args) == 0:
		player = sender
	else:
		try:
			player = vexis.asPlayer(args[0])
			sender.sendMessage(color('&c&lBasics &f- You have healed {}!'.format(args[0])))
		except:
			sender.sendMessage(color('&c&lBasics &f- Invalid username!'))
			return
	player.setHealth(20)
	player.setFoodLevel(20)
	for effect in player.getActivePotionEffects():
		player.removePotionEffect(effect.getType())
	player.sendMessage(color('&c&lBasics &f- You have been healed!'))
	
@vexis.command(aliases = ["gm"])
def gamemode(sender, label, args):
	if not sender.hasPermission("basics.gamemode"):
		sender.sendMessage(color("&c&lBasics &f- Invalid Permissions!"))
		return
	if len(args) not in (1, 2):
		sender.sendMessage(color("&c&lBasics &f- Invalid arguments!"))
		return
	if len(args) == 1:
		player = sender
	else:
		try:
			player = vexis.asPlayer(args[1])
		except:
			sender.sendMessage(color('&c&lBasics &f- Invalid username!'))
			return
	if args[0] in ('s', '0'):
		gm = vexis.gm.SURVIVAL
	elif args[0] in ('c', '1'):
		gm = vexis.gm.CREATIVE
	elif args[0] in ('a', '2'):
		gm = vexis.gm.ADVENTURE
	elif args[0] in ('sp', '3'):
		gm = vexis.gm.SPECTATOR
	else:
		sender.sendMessage(color('&c&lBasics &f- Invalid Gamemode!'))
		return
	player.setGameMode(gm)
	player.sendMessage(color('&c&lBasics &f- Gamemode changed.'))
	if len(args) == 2:
		sender.sendMessage(color("&c&lBasics &f- You have changed {}'s gamemode!".format(args[1])))		
		
@vexis.command(aliases = ["fire", "ignite"])
def flame(sender, label, args):
	if not sender.hasPermission("basics.flame"):
		sender.sendMessage(color("&c&lBasics &f- Invalid permissions!"))
		return
	if not len(args) in (0, 1, 2):
		sender.sendMessage(color("&c&lBasics &f- Invalid arguments!"))
		return
	if len(args) == 0:
		player = sender
	else:
		try:
			player = vexis.asPlayer(args[0])
		except:
			sender.sendMessage(color('&c&lBasics &f- Invalid username!'))
			return
	if len(args) == 2:
		ticks = int(args[1])
	else:
		ticks = 100
	player.setFireTicks(ticks)
	player.sendMessage(color('&c&lBasics &f- You have been set aflame!'))
	if len(args) > 0:
		sender.sendMessage(color('&c&lBasics &f- You have set {} aflame!'.format(args[0])))
	
@vexis.event
def PlayerJoinEvent(event):
	player = event.getPlayer()
	event.setJoinMessage(color("&8[&a+&8] &e{}".format(player.getDisplayName())))
	
@vexis.event
def PlayerQuitEvent(event):
	player = event.getPlayer()
	event.setQuitMessage(color("&8[&c-&8] &e{}".format(player.getDisplayName())))
	
@vexis.command()
def tphere(sender, label, args):
	if not sender.hasPermission('basics.tphere'):
		sender.sendMessage(color('&c&lBasics &f- Invalid permissions!'))
		return
	if len(args) != 1:
		sender.sendMessage(color('&c&lBasics &f- Invalid arguments!'))
		return
	try:
		player = vexis.asPlayer(args[0])
	except:
		sender.sendMessage(color('&c&lBasics &f- Invalid username!'))
		return
	player.teleport(sender.getLocation())
	sender.sendMessage(color('&c&lBasics &f- You have teleported {} to yourself!'.format(args[0])))
	player.sendMessage(color('&c&lBasics &f- You have been teleported to {}!'.format(sender.getDisplayName())))

split_into_chunks = lambda l, n: [l[i * n:(i + 1) * n] for i in range((len(l) + n - 1) // n )]

def convert_name(name):
	words = name.split("_")
	words = [word.capitalize() for word in words]
	return " ".join(words)
	
items = vexis.material.BRICK, vexis.material.IRON_INGOT, vexis.material.MAP

@vexis.command()
def stats(sender, label, args):
	itemset = itertools.cycle(items)
	try:
		if len(args) == 1:
			player = vexis.asPlayer(args[0])
		elif len(args) == 0:
			player = sender
		else:
			sender.sendMessage(color('&c&lBasics &f- Invalid arguments!'))
			return
	except:
		sender.sendMessage(color('&c&lBasics &f- Invalid username!'))
		return
	gui = vexis.menu(lambda page: "Stats for {} (pg. {})".format(player.getDisplayName(), page + 1), 54)

	statistics = {}
	
	for statistic in [x for x in vexis.statistic.values()]:
		key = statistic.getKey().getKey()
		try: value = player.getStatistic(statistic)
		except: continue
		if len(statistics) < 54:
			statistics[key] = value
	
	statistics = split_into_chunks(list(statistics.items()), 36)
	
	for count, page in enumerate(statistics):
		gui.select(count)
		for index, (name, value) in enumerate(page):
			@gui.set(index, vexis.itemstack(
				next(itemset), 
				name=color("&6") + convert_name(name), 
				lore=color("&c") + unicode(value)
			))
			def callback(event):
				pass

	gui.select(0)
	gui.show(sender)
	
@vexis.command()
def gms(sender, label, args): gamemode(sender, label, ['s'] + args)
@vexis.command()
def gmc(sender, label, args): gamemode(sender, label, ['c'] + args)
@vexis.command()
def gma(sender, label, args): gamemode(sender, label, ['a'] + args)
@vexis.command()
def gmsp(sender, label, args): gamemode(sender, label, ['sp'] + args)

@vexis.command()
def online(sender, label, args):
	gui = vexis.gui('Online Players', 54)
	for count, player in enumerate(list(vexis.online_players())):
		@gui.set(count, vexis.skull(player, name=color("&6") + player.getDisplayName()))
		@vexis.extend(player)
		def callback(event, player):
			stats(sender, label, [player.getName()])

	gui.show(sender)
	

