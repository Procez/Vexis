What is Vexis?
------------------------------------
[public-private]: #what-is-vexis
Vexis is a Spigot plugin which allows you to modify your server's content and gameplay without the limitations and simplicity of Skript, or the endless complexity of Java, but rather with the ease of Python.
Vexis also allows you to access Java classes, although the builtin vexis class makes things a lot easier.
Vexis works by wrapping many of Spigot's base plugins with easier Python alternatives that make use of things like keyword arguments, and are shorter and more concise.
Alongside that, Vexis has many helper classes to make trivial things in Spigot much easier.

Why should I use Vexis over Skript?
-------------------------------------
[public-private]: #why-use-vexis-over-skript
Vexis has several edges over Skript that make Vexis the better tool to use for users who know how to use it.
Firstly, Vexis has many programming constructs that Skript doesn't have, such as Python dictionaries, for loops, generators, and classes, alongside being able to easily disregard function values.
Second of all, Vexis has direct access to Spigot's API without the use of addons, and can convert primitive python objects to Java ones automatically and vice versa. This means you can access the base Java classes that Skript cannot access without the use of other addons.
Next, Vexis also has a considerable speedup over Skript due to Python's grammar being much less unambigious then Skript's, where Python only needs the name of a function and not checking every single effect or expression syntax to see if it matches.
Finally, Vexis is able to import other plugins on the server and make usage of their java classes even if they were never specified, a clear advantage over Skript which depends on external addons, and Vexis can even listen to events from other plugins.

Why should I use Vexis over Java?
------------------------------------
[public-private]: #why-use-vexis-over-java
Vexis has plenty of advantages over plain Java code for Spigot plugins that make it well worth your time.
Firstly, Python is a much more readable programming language over Java. It's much easier to tell what Python code is doing because there isn't any type casting or typed functions, and there is much more usage of normal attributes over getters and setters. Python has many constructs like context managers or generators that make code much more readable and efficient.
Second of all, Python code is much easier to maintain and is much shorter than Java code. In some examples, Python code can be over 3x shorter than the equivalent java code, and is much easier and more consise to write. However, using Python (and especially Vexis with Jython) is usually slightly slower and less performant than Java, so this should be noted as well.
After that, Python has plenty of builtin functions which make Python much quicker and easier than Java for the most part. Alongside that, Vexis has plenty of builtin methods and classes which further speed up the development process of your scripts.
Finally, Vexis integrates well with existing plugins and java classes. You can use java objects in Vexis with all of their methods, and send python objects to Java and receive them back in Python.

Where can I download Vexis?
-----------------------------------
[public-private]: #where-is-download
You can download Vexis at https://github.com/Procez/Vexis/releases. Please note the latest version is `1.0.1-beta`, so it may have bugs or isn't perfect. You can always give us feedback on github as well.

Quickstart
------------------------------------
[public-private]: #quickstart
Let's listen to an event for player joins, so that whenever a player joins, we can send them a join message.
```python
@vexis.event
def PlayerJoinEvent(event):
	player = event.getPlayer()
	event.setJoinMessage(color("&8[&a+&8] &e{}".format(player.getDisplayName())))
```
Let's take a look at what this does. First, we create a `PlayerJoinEvent` function which takes in an `event` argument. This event is a Spigot `PlayerJoinEvent` object that we can listen to.
Vexis will listen to all events with this specific name, and once it finds one, it will call the function with the event object. After that, we get the `player` who joined, and we set the event's join message.
Once we set the event join message, it shows that message in the chat. The message is formatted with the player's name, and then colored with the `color` method. This welcomes the player, and lets other players know they joined as well.
At the top, the `@vexis.event` is a decorator which takes in the function, and listens to all events with the name `PlayerJoinEvent`.

Next, let's create a command that heals a player whenever it is used.
```python
@vexis.command()
def heal(sender, label, args):
	if not sender.hasPermission("basics.heal"):
		sender.sendMessage(color("&c&lBasics &f- Invalid Permissions!"))
		return
	if len(args) > 1:
		sender.sendMessage(color('&c&lBasics &f- Invalid amount of arguments!'))
		return
	if not args:
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
```
This piece of code seems a little bit more overwhelming, but it's actually quite simple. 
`@vexis.command()` at the top registers our command with the name of the function, `heal`. The function has three arguments, `sender`, the player who sent the command, `label`, the command's label, usually the plugin that the command belongs to, but in this case usually the name of our script, and `args`, the arguments of the function. Note that all arguments are strings.
Firstly, the command checks if the sender has the permission `basics.heal` using a builtin Spigot method, and if they don't, it sends them an invalid permissions message and ends the function call.
Secondly, it checks if there is more than 1 argument, and if there is, it sends an invalid amount of arguments message and ends the function call.
Then it checks if there are no arguments, and if there is, it defaults the player to be healed as the function sender. Otherwise, it converts the first argument to the player to heal and tells the sender that they have healed that player.
Finally, we set their health and food level to 20, and remove their potion effects, then sending the healed user the message that they have been healed.

After that, let's create a `teleport` command that can also be used as `tp`
```python
@vexis.command(aliases = ['tp'])
def teleport(sender, label, args):
	if not sender.hasPermission("basics.teleport"):
		sender.sendMessage("You do not have permissions to teleport.")
		return
	try:
		x, y, z = args
		loc = vexis.location(x, y, z)
		target = sender
	except:
		try:
			player, = args
			loc = vexis.asPlayer(player).getLocation()
			target = sender
		except:
			try:
				player, x, y, z = args
				target = Vexis.asPlayer(player)
				loc = vexis.location(x, y, z)
			except:
				sender.sendMessage(color("&c&lBasics &f- Invalid arguments!"))
	if target != sender:
		sender.sendMessage("&c&lBasics - &fTeleporting the selected user.")
	target.teleport(loc)
	target.sendMessage("&c&lBasics - &fYou have been teleported!")
```
This code snippet also seems quite complex, but it really isn't if you break it down.
Firstly, it defines the `teleport` command with a `tp` alias.
Secondly, it ends the function call if the sender doesn't have the permission `basics.teleport` and sends a no-permission message.
Thirdly, it tries to convert the arguments to either an `x, y, z`, a `player`, or a `player, x, y, z` with tuple unpacking, and it sets each of the variables to the corresponding argument. If it fails, it sends an invalid arguments message.
After that, it sends the person who sent the command a message that it is teleporting the user, if that user is not the same person as the person it is teleporting.
Then it teleports the person selected, and sends them a message no matter what.
