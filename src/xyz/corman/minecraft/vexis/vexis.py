from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals

try:
  from org.bukkit import Bukkit, ChatColor, OfflinePlayer, Material, Statistic, Location
  from org.bukkit.command import CommandSender
  from org.bukkit.command.defaults import BukkitCommand
  from org.bukkit.event import EventHandler, Listener
  from org.bukkit.inventory import ItemStack
  from org.bukkit.entity import Entity, Player, EntityType, Projectile
  from org.bukkit.projectiles import ProjectileSource
  from org.bukkit.configuration.file import YamlConfiguration
  from org.bukkit.enchantments import Enchantment
  from org.bukkit.potion import PotionEffect, PotionEffectType
  from org.bukkit.util import Vector
  from org.bukkit.attribute import Attribute
  from org.bukkit.plugin.java import JavaPlugin
  from xyz.corman.minecraft.vexis import Vexis, Utils, Execution

  try:
      from xyz.corman.minecraft.vexis import SignMenuFactory
  except:
      pass

  import org.bukkit
  import java.lang
  from java.util import Arrays, Map, HashMap, List, UUID
  from java.io import File
  from java.nio.file import Paths
  from java.lang import Double, Math
  from org.yaml.snakeyaml import DumperOptions, Yaml
  from org.bukkit.scheduler import BukkitRunnable
  from org.bukkit.scoreboard import DisplaySlot
except:
  pass

import threading
import re
import sys
import inspect
import ast
import copy
import functools
import time

#if getServer().getPluginManager().getPlugin("ProtocolLib") != None:
#  from com.comphenix.protocol import ProtocolLibrary, PacketType

try:
    from net.minecraft.server.v1_14_R1 import PacketPlayOutCustomPayload, MinecraftKey, PacketDataSerializer
    from io.netty.buffer import Unpooled
except:
    pass

from pydoc import resolve, describe, html

def getdoc(thing, forceload=0):
    obj, name = resolve(thing, forceload)
    page = html.page(describe(obj), html.document(obj, name))
    return str(page)

def between(num, xy):
  x, y = xy
  return x <= num and num <= y

def open_book(book, player):
  slot = player.getInventory().getHeldItemSlot()
  old = player.getInventory().getItem(slot)
  player.getInventory().setItem(slot, book)
  
  buf = Unpooled.buffer(256)
  buf.setByte(0, 0)
  buf.writerIndex(1)
  
  packet = PacketPlayOutCustomPayload(
      MinecraftKey("minecraft:book_open"),
      PacketDataSerializer(buf)
  )
  
  player.getHandle().playerConnection.sendPacket(packet)
  
  player.getInventory().setItem(slot, old)

class Runnable:
  def __init__(self, func):
    self.func = func
  def run(self):
    return self.func()
  
try:  
  class RunnableBukkit(BukkitRunnable):
    def __init__(self, func):
      self.func = func
    def run(self):
      self.func()
except:
  class RunnableBukkit:
    def __init__(self, func):
      self.func = func
    def run(self):
      self.func()

class getiteminit(type):
  def __getitem__(self, *args):
    return self(*args)

class multidict(dict):
  __metaclass__ = getiteminit
  def __getitem__(self, *args):
    if self == multidict:
      return type(self).__getitem__(self, *args)
    else:
      return super().__getitem__(*args)
  def __new__(cls, *args):
    self = dict.__new__(cls)
    if len(args) == 1 and isinstance(args[0], slice):
      args = ((args[0],))
    if len(args) == 1 and isinstance(args[0], tuple):
      args = args[0]
    data = {}
    for x in args:
      if x.start == None or x.stop == None or x.step != None:
        raise ValueError('invalid step argument')
      if isinstance(x.start, tuple):
        for i in x.start:
          data[i] = x.stop
      else:
        data[x.start] = x.stop
    return data
            
class vexis:
  '''Vexis is the base class for all of the Vexis plugin. This class allows for access and control of Spigot through Java.

  .. include:: ./documentation.md'''

  __file__ = 'vexis.py'

  colorize_alias = 'This method is an alias for the `vexis.colorize` method.'

  guis = []

  _events = {}
  
  modules = {}
  
  try:
    plugin = JavaPlugin.getProvidingPlugin(Vexis)
  except:
    pass
  
  try:
    signfactory = SignMenuFactory(plugin)
  except Exception as e:
    signfactory = None

  @classmethod
  def stat(cls, name):
    '''The `stat` method takes in a single argument, the name of the function, and returns the statistic as an output.
    The output statistic is a spigot object, of the type org.bukkit.Statistic.

    Args:
      name (str): The name of the statistic
    Returns:
      org.bukkit.Statistic: A statistic object'''
    return Statistic.valueOf(vexis.unformat(name))

  @classmethod
  def broadcast(cls, message, permission=None):
    '''The `broadcast` method takes in one message argument and an optional permission argument. It broadcasts
    a message to every user on the server if no permission argument is specified. Otherwise, it broadcasts
    a message only to users with a specific permission.

    Args:
      message (str): The message to broadcast
      permission (str, optional): The permission needed. Defaults to `None`

    Example:
      ```python
      vexis.broadcast(color("&b&lANNOUNCEMENT &fHello! This is my announcement."))
      ```
    '''
    if permission == None:
      Bukkit.broadcastMessage(message)
    else:
      Bukkit.broadcast(message, permission)

  @classmethod
  def _colorizeAlias(cls, string, character = '&'):
    '''This method is an alias for `vexis.colorize`.'''
    return cls.colorize(string, character)
  
  @classmethod
  def colorize(cls, string, character = '&'):
    '''The `colorize` method adds color to a given string, replacing colors preceding a specific character with specific
    minecraft chat colors. This may be used to add colors to chat messages. The character is generally `&`, but
    this can be changed. The `colorize` method takes in the string to add color to, and an optional character.

    Args:
      string (str): The string to add color to.
      character (str): The character to precede the color codes with.

    Returns:
      str: The output string, now with color.

    Examples:
      ```python
      @vexis.command()
      def hello(sender, label, args):
        sender.sendMessage(color("&bHello there!"))
      ```
    '''
    return ChatColor.translateAlternateColorCodes(character, string)

  @classmethod
  def uncolor(cls, string):
    '''The `uncolor` method removes color from any given string. This can uncolor messages previously colored with the
    *colorize* method.

    Args:
      string (str): The string to remove color from.

    Returns:
      str: The output string, with color stripped away.'''
    return ChatColor.stripColor(string)

  @classmethod
  def format(cls, string):
    '''The `format` method converts the case of a string to lowercase, removes underscores, and and adds spacing.
    This method is generally good for a more user friendly name of a Spigot Enum.

    Args:
      string (str): The string to improve formatting on

    Returns:
      str: The formatted string'''
    return " ".join([i.lower() for i in string.upper().split("_")])

  @classmethod
  def unformat(cls, string):
    '''The `unformat` method is used widely internally. It converts spaces to underscores and makes the string uppercase.
    This string allows you to convert a user-friendly string to a Spigot Enum string.

    Arg:
      string (str): The formatted string to be stripped of formatting

    Returns:
      str: The Spigot Enum friendly string.'''
    return string.replace(" ", "_").upper()
  
  try: 
    colourize = _colorizeAlias
    colour = _colorizeAlias
    color = _colorizeAlias
    col = _colorizeAlias
    
    statistic = Statistic
    
    material = Material
    mt = Material
    
    projectile = Projectile
    
    player = Player
    offline_player = OfflinePlayer
    entity = Entity
    
    entities = org.bukkit.entity
    
    gamemode = org.bukkit.GameMode
    gm = gamemode 
  except:
    pass
  
  try:
    _enchantments = multidict [
      ("alldamage", "alldmg", "sharpness", "sharp", "dal"): Enchantment.DAMAGE_ALL,
      ("ardmg", "bane_of_arthopods", "bane_of_arthropod", "arthropod", "dar"): Enchantment.DAMAGE_ARTHROPODS,
      ("undead_damage", "smite", "du"): Enchantment.DAMAGE_UNDEAD,
      ("digspeed", "efficiency", "minespeed", "cutspeed", "ds", "eff"): Enchantment.DIG_SPEED,
      ("durability", "dura", "unbreaking", "d"): Enchantment.DURABILITY,
      ("thorns", "highcrit", "thorn", "highercrit", "t"): Enchantment.THORNS,
      ("fireaspect", "fire", "meleefire", "meleeflame", "fa"): Enchantment.FIRE_ASPECT,
      ("knockback", "kback", "kb", "k"): Enchantment.KNOCKBACK,
      ("blocks_loot_bonus", "fortune", "fort", "lbb"): Enchantment.LOOT_BONUS_BLOCKS,
      ("mobs_loot_bonus", "mobloot", "looting", "lbm"): Enchantment.LOOT_BONUS_MOBS,
      ("oxygen", "respiration", "breathing", "breath", "o"): Enchantment.OXYGEN,
      ("protection", "prot", "protect", "p"): Enchantment.PROTECTION_ENVIRONMENTAL,
      ("explosions_protection", "explosion_protection", "expprot", "blast_protection", "bprotection", "bprotect", "blastprotect", "pe"): Enchantment.PROTECTION_EXPLOSIONS,
      ("fall_protection", "fallprot", "feather_fall", "father_falling", "pfa"): Enchantment.PROTECTION_FALL,
      ("fire_protection", "flame_protection", "fire_protect", "fire_protect", "fireprot", "flameprot", "pf"): Enchantment.PROTECTION_FIRE,
      ("projectile_protection", "projprot", "pp"): Enchantment.PROTECTION_PROJECTILE,
      ("silktouch", "softtouch", "st"): Enchantment.SILK_TOUCH,
      ("water_worker", "aqua_affinity", "watermine", "ww"): Enchantment.WATER_WORKER,
      ("firearrow", "flame", "flamearrow", "af"): Enchantment.ARROW_FIRE,
      ("arrowdamage", "power", "arrowpower", "ad"): Enchantment.ARROW_DAMAGE,
      ("arrowkb", "punch", "arrowpunch", "ak"): Enchantment.ARROW_KNOCKBACK,
      ("infinite_arrows", "infarrows", "infinity", "infinite", "unlimited", "unlimited_arrows", "ai"): Enchantment.ARROW_INFINITE,
      ("luck", "luckofsea", "luckofseas", "rodluck"): Enchantment.LUCK,
      ("lure", "rodlure", "rl"): Enchantment.LURE
    ]
  except:
    pass
  
  class direction:
    '''The direction is a class which allows for much easier usage of Spigot Vectors for direction.
    The direction class implements several methods such as `apply` which allow you to use directions with locations.

    Args:
      *args: either (yaw: Union[int, float], pitch: Union[int, float]) or (x: Union[int, float], y: Union[int, float], z: Union[int, float])

    Returns:
      vexis.direction: The direction from the yaw and pitch or x, y, and z.

    Examples:
      ```python
      vexis.push(player, vexis.facing(player).apply(player.getLocation(), 3))
      ```
    '''
    def __init__(self, *args):
      args = list(args)
      if len(args) == 1:
        self.vector = args[0]
      if len(args) == 2:
        if isinstance(args[0], Entity):
          args[0] = args[0].getLocation()
        if isinstance(args[1], Entity):
          args[1] = args[1].getLocation()
        if isinstance(args[0], Location) and isinstance(args[1], Location):
          vexis.direction.__init__(self, args[0].subtract(args[1]).toVector())
          return
        pitch, yaw = args
        pitch = ((pitch + 90) * Math.PI) / 180
        yaw = ((yaw + 90) * Math.PI) / 180
        self.vector = Vector(
          Math.sin(pitch) * Math.cos(yaw),
          Math.sin(pitch) * Math.sin(yaw),
          Math.cos(pitch)   
        )
        self.pitch, self.yaw = pitch, yaw
      self.locAtSelf = self.getLocationAtSelf()
      self.yaw = self.locAtSelf.getYaw()
      self.pitch = self.locAtSelf.getPitch()
    def getLocationAtSelf(self):
      '''Get a location with its direction set at this direction's vector.'''
      loc = Location(vexis.default_world(), 0, 0, 0)
      loc.setDirection(self.vector)
      return loc     
    def apply(self, location, amount = 1):
      '''Get the location which is an amount (defaulting to 1) blocks in the direction of this direction object.'''
      return location.add(self.vector.multiply(amount))
    def shift_pitch_yaw(self, pitch = 0, yaw = 0):
      '''Create a direction with its pitch and yaw shifted.'''
      return vexis.direction(self.pitch + pitch, self.yaw + yaw)
    def shift_xyz(self, x = 0, y = 0, z = 0):
      '''Create a direction with its x, y, and z shifted.'''
      return vexis.direction(Vector(self.vector.getX() + x, self.vector.getY() + y, self.vector.getZ() + z))
    def shift(self, *args, **kwargs):
      '''Create a direction with either its pitch and yaw shifted, or its x, y, and z shifted.'''
      try:
        self.shift_xyz(*args, **kwargs)
      except:
        self.shift_pitch_yaw(*args, **kwargs)
    
  class scoreboard:
    '''The scoreboard class is an easy way to create and show scoreboards for users.
    The scoreboard class has helper methods which allow making changes to the scoreboard easy.
    The scoreboard also has a simple `show` method to allow for showing scoreboards to players.

    Args:
      type (str): The type of scoreboard. Defaults to `dummy`.
      name (str): The name of the scoreboard. Defaults to `None`.

    Returns:
      vexis.scoreboard: The scoreboard object.

    Examples:
      ```python
      scoreboard = vexis.scoreboard(name = color("&bScoreboard"))
      scoreboard.set({
        0: "Some Text",
        1: "More Text",
        2: "Extra Text"
      })
      scoreboard.show(player)
      ```
    '''
    def __init__(self, type = "dummy", name = None):
      if name == None:
        name = type
      manager = Bukkit.getScoreboardManager();
      self.board = manager.getNewScoreboard();
      self.obj = self.board.registerNewObjective(name, type)
    def setSlot(self, slot):
      '''Set a specific slot of this scoreboard.'''
      self.obj.setDisplaySlot(DisplaySlot.valueOf(vexis.unformat(slot)))
    def setName(self, name):
      '''Set the name of the scoreboard.'''
      self.obj.setDisplayName(name)
    def set(self, scores):
      '''Set the values of the scoreboard with a list of dictionaries.'''
      for index, text in scores.items():
        self.obj.getScore(text).setScore(index)
    def show(self, player):
      '''Show this scoreboard to a player.'''
      player.setScoreboard(self.board)
  
  @classmethod
  def push(cls, entity, by, speed = 1):
    '''The push method is a useful method for moving entities in specific directions at specific speeds.
    The push method takes in an entity, some sort of direction, or a speed.
    The push method's dirction is either a vector, location, vexis direction, or an number of how many blocks forward.
    If the push method direction is a number, it will use the direction the entity faces a specific amount of blocks
    forward.

    Args:
      entity (vexis.entities.Entity): A Spigot Entity to push.
      by (vexis.direction, org.bukkit.util.Vector, org.bukkit.Location, int, float): The direction to push in.
      speed (int, float): The speed to push in the given direction, defaults to `1`.

    Example:
      ```python
      vexis.push(player, 3)
      ```
    '''
    if isinstance(by, (int, float)):
      return cls.push(entity, cls.facing(entity).apply(entity.getLocation(), by))
    if isinstance(by, cls.direction):
      return cls.push(entity, by.vector, speed)
    entity.setVelocity(by.toVector().subtract(entity.getLocation().toVector()).normalize().multiply(speed))
    
  @classmethod
  def facing(cls, entity):
    '''The `facing` method allows you to get the current direction an entity is looking in, a vexis direction.
    This can be used to push an entity where it faces, teleport it to the block it looks at, or other such uses.
    This returns a vexis direction object, which can be applied to locations.

    Args:
      entity (vexis.entities.Entity): The entity to get the direction of.

    Returns:
      vexis.direction: The direction the entity is facing.

    Example:
      ```python
      vexis.push(player, vexis.facing(entity))
      ```
    '''
    return cls.direction(entity.getLocation().getDirection())

  @classmethod
  def summon(cls, name, loc):
    '''The `summon` method allows you to spawn an entity from its name at a specific location.
    Note that this name does not have to be a specific enum, as it uses the `unformat` method to allow for more user-friendly names.
    The `summon` method takes in a name and a location.

    Args:
      name (string): The name of the entity type to spawn.
      loc (org.bukkit.Location): The location to spawn the entity at.

    Example:
      ```python
      vexis.summon("zombie", player.getLocation())
      ```'''
    return loc.getWorld().spawnEntity(loc, EntityType.valueOf(vexis.unformat(name)))
    
  @classmethod
  def shoot(cls, entity, proj, dir = None, speed = 1, shooter = None):
    '''The `shoot` method allows you to shoot a projectile from a location or entity at a specific direction and speed, with an optional shooter that wasn't the entity shot from.
    The `shoot` method allows you to shoot entities which aren't technically projectiles, although it can't set their shooter.
    The `shoot` method also returns the shot projectile.

    Args:
      entity (vexis.entities.Entity, org.bukkit.Location): The entity or location to shoot from.
      proj (string): The name of the projectile type to shoot from.
      dir (vexis.direction, org.bukkit.utils.Vector): The direction to shoot in. Defaults to `None`
      speed (int, float): The speed to shoot in. Defaults to `1`
      shooter (vexis.entities.Entity): The shooter that the projectile's shooter will be set to if it inherits from org.bukkit.entity.Projectile. Defaults to `None`

    Returns:
      vexis.entities.Entity: The entity or projectile that was launched.

    Example:
      ```python
      vexis.shoot(skeleton, "arrow", speed = 3)
      ```
    '''
    if shooter == None:
      shooter = entity
    if dir == None:
      if isinstance(entity, Entity):
        dir = entity.getLocation().getDirection()
      else:
        dir = Vector()
    else:
      if not isinstance(dir, Vector):
        dir = dir.vector
    loc = entity
    if not isinstance(loc, Location):
      loc = loc.getLocation()
    vel = dir.normalize().multiply(speed)
    proj = vexis.summon(proj, loc)
    if isinstance(shooter, ProjectileSource) and isinstance(proj, Projectile):
      proj.setShooter(shooter)
    if proj != None:
      try:
        proj.setVelocity(vel)
      except Exception:
        pass
      except java.lang.Exception:
        pass
    return proj

  @classmethod
  def explode(cls, loc, power = 3, fire = False):
    '''The `explode` method causes an explosion at a specific location with an optional power, and an optional choice of causing fire.
    The `explode` method takes in a location, an optional power, and an optional fire explosion.

    Args:
      loc (org.bukkit.Location): The location to explode at.
      power (int, float): The power of the explosion. Defaults to `3`.
      fire (bool): An optional choice of causing fire or not.

    Example:
      vexis.explode(Player.getLocation(), power = 2)
    '''
    tnt = vexis.summon("primed tnt", loc)
    tnt.setYield(power)
    tnt.setFuseTicks(0)
    tnt.setIsIncendiary(fire)

  @classmethod
  def attribute(cls, entity, value):
    '''The `attribute` method allows you to get a specific attribute from an entity.
    Note that the value does not have to be a perfect spigot enum due to internal usage of the *unformat* method, so more user-friendly strings are acceptable.

    Args:
      entity (vexis.entities.Entity): The entity to get the attribute from.
      value (str): The name of the attribute.

    Returns:
      org.bukkit.attribute.AttributeInstance: The attribute instance of the entity at the value.'''
    return entity.getAttribute(Attribute.valueOf(vexis.unformat(value)))

  get_attribute = attribute
  
  @classmethod
  def handle(cls, func):
    '''Handle a function with a Vexis handler to show errors in the console.'''
    @functools.wraps(func)
    def wrapper(*args):
      return vexis._vexis_execution.handleCall(func, args)
    return wrapper

  @classmethod
  def handleCoroutine(cls, func):
    '''Handle a function with a Vexis handler to show errors in the console.'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      try:
        call = func(*args, **kwargs)
        val = None
        val = yield call.send(val)
        while True:
          val = yield call.send(val)
      except Exception as e:
        vexis._vexis_execution.showError(e)
    return wrapper   
  
  @classmethod
  def after(cls, ticks):
    '''The `after` decorator allows for an easy way to run a task after a specific amount of ticks.
    The `after` decorator takes in `ticks` as an argument of the outer layer of the decorator.
    Inside of the inner layer of the decorator, it takes in a `func` function.

    Args:
      ticks (int): The amount of ticks to execute the decorated function after

    Return:
      function: A wrapper function to be called with a function `func` which schedules the task and then returns the function.

    Example:
      ```python
      @vexis.after(3)
      def callback():
        player.sendMessage(color("&fIt's been &b3 &fticks, that's &b3/20&f of a second!"))
      ```'''
    def inner(func):
      RunnableBukkit(vexis.handle(func)).runTaskLater(vexis.plugin, ticks)
      return func
    return inner

  class enchantment:
    '''An `enchantment` instance is an instance with a `name` and a `level`.
    You can use the `in` operator to check if an instance is enchanted iwth this enchantment, regardless of the level.
    You can enchant an itemstack with this enchantment and its level.
    You can also unenchant an itemstack regardless of its level.

    Args:
      name (str): The name of the enchantment
      level (int): The level of the enchantment, defauls to `1`

    Returns:
      vexis.enchantment: The enchantment instance from the name and level.'''
    def __init__(self, name, level=1):
      self.name = name
      self.level = level
    def __contains__(self, item):
      '''Check if an item has this enchantment.'''
      return item.containsEnchantment(_enchantments[self.name])
    def enchant(self, itemstack):
      '''Enchant an itemstack with this enchantment.'''
      meta = itemstack.getItemMeta()
      meta.addEnchant(vexis._enchantments[self.name], self.level, True)
      itemstack.setItemMeta(meta)
    def unenchant(self, itemstack):
      '''Unenchant an itemstack with this enchantment.'''
      meta = itemstack.getItemMeta()
      meta.removeEnchant(vexis._enchantments[self.name])
      itemstack.setItemMeta(meta)     
    
  
  @classmethod
  def skull_from_uuid(cls, uuid, count=1, name=None, lore=None):
    '''The `skull_from_uuid` method is a wrapper around the `skull` function allowing you to use UUIDs over player objects.
    The `skull_from_uuid` method takes in the uuid, an optional amount of skulls, an optional item name, and an optional item lore.

    Args:
      uuid (str): The uuid of the player to copy the skull from.
      count (int): The amount of skulls to create. Defaults to `1`.
      name (str): The name of the itemstack to create. Defaults to `None`
      lore (str): The lore of the itemstack to create. Defaults to `None`

    Returns:
      org.bukkit.inventory.ItemStack: The itemstack with the skull, count, name, and lore specified.

    Examples:
      ```python
      player.getInventory().addItem(vexis.skull_from_uuid('3e738643-2f7b-44b3-8186-1ed2ba8cf326'))
      ```
    '''
    return vexis.skull(Bukkit.getServer().getOfflinePlayer(UUID.fromString(uuid)))
  
  
  @classmethod
  def skull(cls, player, count=1, name=None, lore=None):
    '''The `skull` method allows you to get itemstacks with skulls of specified players.
    The `skull` method takes in the player object, an optional amount of skulls, an optional item name, and an optional item lore.

    Args:
      player (org.bukkit.Player, org.bukkit.OfflinePlayer): The player object to copy the skull from.
      count (int): The amount of skulls to create. Defaults to `1`.
      name (str): The name of the itemstack to create. Defaults to `None`
      lore (str): The lore of the itemstack to create. Defaults to `None`

    Returns:
      org.bukkit.inventory.ItemStack: The itemstack with the skull, count, name, and lore specified.

    Examples:
      ```python
      player.getInventory().addItem(vexis.skull(player))
      ```
    '''
    item = ItemStack(vexis.material.PLAYER_HEAD, count)
    meta = item.getItemMeta()
    meta.setOwningPlayer(player)
    if name != None:
      meta.setDisplayName(name)
    if lore != None:
      if isinstance(lore, str):
        lore = lore.splitlines()
      meta.setLore(lore)
    item.setItemMeta(meta)
    return item

  @classmethod
  def worlds(cls):
    '''The `worlds` method gives you a list of worlds in the server.

    Returns:
      List[org.bukkit.World]: A list of worlds in the server.'''
    return list(Bukkit.getWorlds())

  
  @classmethod
  def world(cls, name):
    '''The `world` function allows you to get a world from its name.
    If no world is found, this will return `None`.

    Args:
      name (str): The name of the world

    Returns:
      Optional[org.bukkit.World]: The world with the given name.'''
    for i in vexis.worlds():
      if i.getName().lowercase() == name.lowercase(): return i
  
  
  @classmethod
  def default_world(cls): 
    '''The `default_world` method allows you to get the default world of the server, usually the overworld.

    Returns:
      org.bukkit.World: The default world of the server.''' 
    return vexis.worlds()[0]
  
  
  @classmethod
  def location(cls, x, y, z, world=None, yaw=0, pitch=0):
    '''The `location` method allows you to get a world from it's x, y, z, an optional world, and an optional yaw and pitch.
    If no world is specified, it will use the default world from the `default_world` method.

    Args:
      x (int, float): The x coordinate of the location.
      y (int, float): The y coordinate of the location.
      z (int, float): The z coordinate of the location.
      world (org.bukkit.World): The optional world of the location. Defaults to `None`.
      yaw (int, float): The yaw of the location. Defaults to `0`.
      pitch (int, float): The pitch of the location. Defaults to `0`.

    Returns:
      org.bukkit.Location: The location from the x, y, z, optional world, optional yaw, and optional pitch.

    Example:
      ```python
      player.teleport(vexis.location(1, 2, 3))
      ```'''
    if world == None: world = vexis.default_world()
    return Location(world, x, y, z, yaw, pitch)

  
  @classmethod
  def give_inv(cls, player, inv):
    '''Give a player a Spigot inventory.'''
    for i in inv.getContents():
      player.getInventory().addItem(i)
      
  
  @classmethod
  def effect(cls, type, duration, amplifier, ambient = False, particles = False):
    '''The `effect` function allows you to create a potion effect from it's type, duration, amplifier, optional ambience, and optional particles.
    This can be used to create a potion, or to apply the effect to a player.

    Args:
      type (str): The type of potion effect to create.
      duration (int): The amount of time the effect lasts for.
      amplifier (int): The level or amplifier of the effect, how strong the effect is.
      ambient (bool): If the effect is ambient. Does nothing yet. Defaults to `False`
      particles (bool): If the effect has particles. Does nothing yet. Defaults to `False`

    Returns:
      org.bukkit.potion.PotionEffect: The potion effect with the given type, duration, amplifier, optional ambience, and optional particles.

    Examples:
      ```python
      vexis.effect("poison", 20, 2).apply(player)
      ```
    '''
    return PotionEffectType.getByName(vexis.unformat(type)).createEffect(duration, amplifier)

  class radius:
    '''A radius between two locations.'''
    def __init__(self, loc1, loc2):
      self.loc1 = loc1
      self.loc2 = loc2
    def __contains__(self, loc):
      '''Check if a location is inside of this radius.'''
      loc1 = self.loc1
      loc2 = self.loc2
      x1 = min([loc1.getX(), loc2.getX()])
      y1 = min([loc1.getY(), loc2.getY()])
      z1 = min([loc1.getZ(), loc2.getZ()])
      x2 = max([loc1.getX(), loc2.getX()])
      y2 = max([loc1.getY(), loc2.getY()])
      z2 = max([loc1.getZ(), loc2.getZ()])
      x = loc.getX()
      y = loc.getY()
      z = loc.getZ()
      return between(x, (x1, x2)) and between(y, (y1, y2)) and between(z, (z1, z2))


  class cooldown:
    '''A cooldown, managed by a cooldown manager.'''
    def __init__(self, name, duration, manager):
      '''Initialize a cooldown from its name, duration, and manager.'''
      self.name = name
      self.manager = manager
      self.duration = duration
      self.starttime = time.time()
    def timesince(self):
      '''Get the time since this cooldown was made.'''
      return time.time() - self.starttime
    def expired(self):
      '''Check if this cooldown has been expired.'''
      return self.timesince() > self.duration

  class CooldownManager:
    '''A cooldown manager, allowing you to easily manage cooldown objects.'''
    def __init__(self):
      '''Initialize this cooldown manager with no cooldowns.'''
      self.cooldowns = {}
    def __setitem__(self, name, duration):
      '''Create a cooldown from its name and duration..'''
      self.create_cooldown(name, duration)
    def __getitem__(self, name):
      '''Get a cooldown from its name.'''
      return self.cooldowns[name]
    def __contains__(self, name):
      return name in self.cooldowns
    def create_cooldown(self, name, duration):
      '''Create a cooldown from its name and duration.'''
      self.cooldowns[name] = vexis.cooldown(name, duration, self)
      return self
    def expired(self, name):
      '''Check if a cooldown from its name has expired.'''
      return self.cooldowns[name].expired()
    def expire(self, name):
      '''Make a cooldown from its name expire.'''
      self.cooldowns[name].duration = 0
      return self
    def timesince(self, name):
      '''Get the time since a cooldown was created.'''
      return self.cooldowns[name].timesince()
    def pop(self, name):
      '''Remove a cooldown, but return the cooldown object that was removed.'''
      return self.cooldowns.pop(name)
    def __delitem__(self, name):
      '''Remove a cooldown.'''
      self.pop(name)
    def remove(self, name):
      '''Remove a cooldown, and return this cooldown manager.'''
      self.pop(name)
      return self

  @classmethod
  def iter(cls, jiterable):
    '''Convert a java iterable to a generator.'''
    iterator = jiterable.iterator()
    while iterator.hasNext():
      yield iterator.next()
  
  @classmethod
  def itemstack(cls, material, count=1, name=None, lore=None, durability=None):
    '''The `itemstack` methods allows you to create an itemstack from a material, amount of items, name, lore, and durability.
    Note that everything except the material is optional.

    Args:
      material (org.bukkit.Material, org.bukkit.inventory.ItemStack): The material to create the item stack from, or the itemstack to duplicate and modify.
      count (int): The amount of items in the itemstack. Defaults to `1`.
      name (str): The name of the itemstack. Defaults to `None`.
      lore (str, List[str]): The lore of the itemstack. Either a string with multiple lines, or a list of strings. Defaults to `None`.
      durability (int): The durability of the itemstack. Defaults to `None`.

    Example:
      ```python
      player.getInventory().addItem(vexis.itemstack('arrow', count = 64))
      ```
    '''
    if isinstance(material, ItemStack):
        item = material.clone()
    elif isinstance(material, str):
        return vexis.itemstack(Material.valueOf(vexis.unformat(material)), count, name, lore, durability)
    else:
        item = ItemStack(material)
    item.setAmount(count)
    meta = item.getItemMeta()
    if name != None:
      meta.setDisplayName(name)
    if lore != None:
      if isinstance(lore, (str, unicode)):
        lore = lore.splitlines()
      meta.setLore(Arrays.asList(lore))
    if durability != None:
      meta.setDurability(durability)
    item.setItemMeta(meta)
    return item
      
  @classmethod
  def online_players(cls):
    '''The `online_players` method gives a list of all players who are currently on your server..

    Returns:
      List[org.bukkit.Player]: A list of all players on your server.'''
    return list(Bukkit.getServer().getOnlinePlayers())
  
  @classmethod
  def all_players(cls):
    '''The `all_players` method gives a list of all players who have joined your server at one time.

    Returns:
      List[org.bukkit.OfflinePlayer]: A list of all players who ever joined your server.'''
    return list(Bukkit.getServer().getOfflinePlayers())
  
  @classmethod
  def whitelisted_players(cls):
    '''The `whitelisted_players` method gives a list of all players who are whitelisted on your server..

    Returns:
      List[org.bukkit.OfflinePlayer]: A list of all players on your server.'''
    return list(Bukkit.getServer().getWhitelistedPlayers())
  
  @classmethod
  def banned_players(cls):
    '''The `banned_players` method gives a list of all players who are banned on your server..

    Returns:
      List[org.bukkit.OfflinePlayer]: A list of all banned players on your server.'''
    return list(Bukkit.getServer().getBannedPlayers())
  
  @classmethod
  def select_entities(cls, string='@e'):
    '''The `select_entities` method allows you to get a list of all entities with a specific selector.

    Args:
      string (str): The selector to select entities from.

    Returns:
      List[vexis.entities.Entity]: A list of all entities matching the selector.'''
    return list(Bukkit.getServer().selectEntities(None, string))

  @classmethod
  def nearby_entities(cls, location, radius):
    '''The `nearby_entities` method gives you a list of all entities in a radius of a location.
    The radius parameter can also be a list of coordinates in each direction, for example, (1, 2, 3), if an entity is at least one block away in the X axis, two away in the Y axis, and three away in the Z axis.

    Args:
      location (org.bukkit.Location): The location to detect near entities from.
      radius (int, float, tuple, list): The radius or list of coordinates to check if the entity is inside of.

    Returns:
      List[vexis.entities.Entity]: A list of all entities in the radius of the location.'''
    if not isinstance(radius, (tuple, list)):
      return vexis.nearby_entities(location, [radius] * 3)
    else:
      return list(location.getWorld().getNearbyEntities(location, radius[0], radius[1], radius[2]))
  
  @classmethod
  def nearest_in_sight(cls, player, range = 50):
    '''The `nearest_in_site` method gives you the nearest entity in a specific range in the player's sight.
    The `range` defaults to 50 but this can be changed. 
    This only accounts for entities directly in the player's line of sight, the player must be looking at the entity.
    
    Args:
      player (org.bukkit.Player): The player to find the nearest entity in their line of sight.
      range (int, float): The range to check for the nearest entity in.
    '''
    return Utils.getNearestEntityInSight(player, range)
  
  @classmethod
  def operators(cls):
    '''The `operators` method gives a list of all players have operator status on your server.

    Returns:
      List[org.bukkit.OfflinePlayer]: A list of all players who have operator status on your server.'''
    return list(Bukkit.getServer().getOperators())
  
  @classmethod
  def get_data_folder(cls):
    '''Get a data folder specific to this script, for data to be stored.'''
    folder = cls._vexis_data_folder
    folder = File(folder).getParent()
    base = inspect.stack()[-1][0].f_globals["__name"]
    return str(Paths.get(str(folder), base.capitalize()))

  @classmethod    
  def fix_java(cls, obj):
    '''Convert some java objects to their respective types. This is for YML to be parsed.'''
    if isinstance(obj, (HashMap, dict)):
      obj = dict(obj)
      for k, v in list(obj.items()):
        obj[k] = vexis.fix_java(v)
    if isinstance(obj, (List, list)):
      jobj = obj
      obj = []
      for i in list(jobj):
        obj.append(vexis.fix_java(i))
    return obj
  
  class yml:
    '''A YML object, allowing you to load and dump YML.'''
    def __init__(self, flow_style=None, linebreak=None, scalar_style=None):
      '''Initialize a YML object with a flow style, line break, and scalar_style.'''
      options = DumperOptions()
      if flow_style != None:
        options.setDefaultFlowStyle(DumperOptions.FlowStyle.valueOf(flow_style))
      if linebreak != None:
        options.setLineBreak(DumperOptions.LineBreak.valueOf(linebreak))
      if scalar_style != None:
        options.setDefaultFlowStyle(DumperOptions.ScalarStyle.valueOf(scalar_style))
      self.yaml = Yaml(options)
    def load(self, string):
      '''Load yml from a string.'''
      return vexis.fix_java(list(vexis.iter(Utils.load_yml(self.yaml, string))))
    def dump(self, object):
      '''Dump yml to a string, formatted with the given options.'''
      return self.yaml.dump(object)
              
  
  try:
    asPlayer = Bukkit.getPlayer
    matchPlayers = Bukkit.matchPlayer
  except:
    pass
    
  class server:
    '''The server class handles management of your Spigot server.'''
    @classmethod
    def restart(cls):
      '''Restart the server.'''
      Bukkit.spigot().restart()
      
    @classmethod
    def shutdown(cls):
      '''Shutdown the server.'''
      Bukkit.getServer().shutdown()
    stop = shutdown
    
  
  @classmethod
  def schedule(cls, ticks=20, delay=0):
    '''Schedule a function every certain amount of ticks with a certain amount of delay before starting.'''
    def inner(func):
      bukkit = RunnableBukkit(vexis.handle(func))
      bukkit.runTaskTimer(vexis.plugin, delay, ticks)
      return bukkit
    return inner
  
  @classmethod
  def itemize(cls, item):
    '''Convert a String to a ItemStack if a String is inputed, Convert Material to ItemStack, if a Material is inputed. Otherwise, return the input value.'''
    if isinstance(item, str):
      return cls.itemsize(Material.valueOf(vexis.unformat(item)))
    if isinstance(item, Material):
      return ItemStack(item)
    elif isinstance(item, ItemStack):
      return item.clone()
    else:
      return item

  class gui:
    '''The gui class allows for an easy GUI helper.'''
    
    class setters:
      '''
      An internally used class which allows for the `vexis.gui.set` method to be a decorator.
      '''
      def __init__(self, gui, slot, item, movable=False):
        self.gui = gui
        self.slot = slot
        self.item = item
        self.movable = movable
      def __call__(self, func):
        self.gui.set_slot(self.slot, self.item, self.movable, func)
        return func
    
    def __init__(self, name, slots, movable=False):
      '''Create a GUI inventory with a set amount of slots, and a set name.'''
      self.inv = Bukkit.createInventory(None, slots, name)
      self.callbacks = {}
      self.movable = {}
      self.slots = slots
      for i in range(slots):
        if not movable:
          @self.set(i, vexis.mt.AIR)
          def callback(event): pass
      vexis.guis.append(self)
    def set(self, slot, item, movable=False):
      '''Set a specific slot index to a specific item. This returns a wrapper to decorate a function with for a callback. For setting items with no callbacks, use the `vexis.gui.set_slot` method.'''
      return self.setters(self, slot, item, movable=False)
    def set_slot(self, slot, item, movable=False, callback=None):
      '''Set a specific slot index to a specific item.'''
      self.inv.setItem(slot, vexis.itemize(item))
      self.callbacks[slot] = callback, movable
      return self
    def unset(self, slot):
      self.inv.clear(slot)
      del self.callbacks[slot]
      return self
    def get(self, slot):
      '''Get the ItemStack at a specific slot.'''
      return self.inv.getItem(slot)
    def give(self, *players):
      for player in players:
        player.getInventory().setContents(list(self.inv.getContents())[:41])
    def show(self, *players):
      '''Show the GUI to players.'''
      for player in players:
        player.openInventory(self.inv)
      return self
    open = show
    
  class extend:
    '''Extend a function with arguments'''
    def __init__(self, *args):
      '''Initialize this extension object.'''
      self.args = args
    def __call__(self, func):
      '''Decorate a function with this extension object, this extension's arguments are added to the function arguments.'''
      @functools.wraps(func)
      def new(*args, **kwargs):
        args = args + self.args
        func(*args, **kwargs)
      return new

  class menu:
    '''A menu object, allowing you to create menus with multiple pages much easier.'''
    def __init__(self, name, slots, pages=2,
                back=0,
                next=0,
                previous=None,
                finish=None,
                movable=False):
      if back is 0:
        back = vexis.itemstack(vexis.material.NETHER_STAR, name=vexis.color("&c&lBACK"))
      if next is 0:
        next = vexis.itemstack(vexis.material.PAPER, name=vexis.color("&3&lNEXT"))
      if isinstance(name, (str, unicode)):
        def name(x, _name = name):
            return _name
      self.pages = [vexis.gui(name(x), slots, movable=movable) for x in range(pages)]
      self.selected = self.pages[0]
      for count, gui in enumerate(self.pages):
        if back != None and count > 0:
          @gui.set(slots - 9, back)
          @vexis.extend(count)
          def callback(event, count):
            player = event.getWhoClicked()
            self.pages[count - 1].show(player)
        if count == 0 and previous != None:
          @gui.set(slots - 9, back)
          @vexis.extend(count)
          def callback(event, count):
            player = event.getWhoClicked()
            previous.show(player)
        if next != None and count < (pages - 1):
          @gui.set(slots - 1, next)
          @vexis.extend(count)
          def callback(event, count):
            player = event.getWhoClicked()
            self.pages[count + 1].show(player)  
        if count == (pages - 1) and finish != None:
          @gui.set(slots - 9, next)
          @vexis.extend(count)
          def callback(event, count):
            player = event.getWhoClicked()
            finish.show(player)       

    def clear(self, *players):
      '''Clear the inventory of the given players.'''
      for player in players: 
        player.getInventory().clear()
      return self
        
    def give(self, *players):
      '''Give the selected page of this menu to the given players.'''
      self.selected.give(*players)
      return self
        
    def select(self, num):
      '''Select a page of this menu.'''
      self.selected = self.pages[num]
      return self
      
    def set(self, slot, item, movable=False):
      '''Set an item at a specific slot, which can be optionally movable. This returns a wrapper to decorate a function, for setting items at slots without callbacks, use `vexis.menu.set_slot` method.'''
      return self.selected.set(slot, item, movable=False)

    def set_slot(self, slot, item, movable=False):
      '''Set an item at a specific slot, which can be optionally movable.'''
      return self.selected.set(slot, item, movable=False)
  
    def unset(self, slot):
      '''Unset a specific slot.'''
      return self.selected.unset(slot)
  
    def show(self, *players):
      '''Show the selected page to the given players.'''
      self.selected.show(*players)
      return self
      
    def get(self, slot):
      '''Get a slot from the selected GUI.'''
      return self.selected.get(slot)
  
  @classmethod
  def display_text(cls, player, pages):
    '''Display text to a player through a book.'''
    pages = Arrays.asList(pages)
    book = vexis.itemstack(
        vexis.mt.WRITTEN_BOOK
    )
    book.getItemMeta().setPages(pages)
    open_book(book, player)
    
  @classmethod
  def sign_menu(cls, player, text, reopenIfFail = True):
    '''The `sign_menu` method allows you to gather input through signs from users, an alternative to using chat to get user input.
    The `sign_menu` method takes in a player, the text on the sign (a list, or a string with multiple lines), and an option to reopen if the user gives an undesired input.
    This method returns a decorator which decorates a function that gives a `bool` as its output (whether the user gave a good input or not).

    Args:
      player (org.bukkit.Player): The player to show the sign menu to.
      text (str, list): The string or list of strings to have the sign menu's lines be.

    Returns:
      callable: The inner decorator to decorate the sign menu's callback.

    Examples:
      ```python
        @vexis.sign_menu(player, ['', '^^^^^', 'Enter "3"', 'Up There'])
        def callback(player, lines):
          if lines[0] == "3":
            return True
          return False
      ```
    '''
    if isinstance(text, str):
      text = text.split('\n')
    text = Arrays.asList(text)
    def inner(response):
      menu = cls.signfactory.newMenu(player, text)   
      if reopenIfFail:
          menu.reopenIfFail() 
      menu.response(Utils.pyFuncToBiPredicate(vexis._vexis_execution, response))
      return menu
    return inner

  class coro_object:
    '''
    The `vexis.coro_object` class is used internally to convert function calls to coroutine arguments.
    '''
    def __init__(self, f, *args, **kwargs):
      self.f = f
      self.args = args
      self.kwargs = kwargs
      self.gen = f(*args, **kwargs)
    def send(self, value):
      try:
        if not self.gen:
          self.gen = f(*args, **kwargs)
        val = self.gen.send(value)
        if isinstance(val, vexis.coro_function):
          val.execute(self)
        return val
      except StopIteration as e:
        return e.args[0]

  class coro_function:
    '''
    The `vexis.coro_function` class is used internally as a base class for coroutine function classes.
    '''
    def execute(self, coro):
      '''The `execute` method is internally used to execute a coroutine function.'''
      raise NotImplementedError

  class sleep(coro_function):
    '''The `sleep` class is a `vexis.coro_function` subclass that allows you to wait an amount of ticks.
    This only works in functions decorated with `vexis.coroutine`.
    This is an alternative to `vexis.after` if you want to wait and then continue execution more easily.

    Args:
      ticks (int): The amount of ticks to sleep for. Defaults to `0`, which passes control to another scheduled task.

    Returns:
      vexis.sleep: A vexis sleep object.

    Examples:
      ```python
      @vexis.command()
      @vexis.coroutine
      def mycmd(sender, label, args):
          for i in range(5):
            yield vexis.sleep(1)
            player.sendMessage(str(i))
      ```
    '''
    def __init__(self, ticks):
      self.ticks = ticks
    def execute(self, generator):
      @vexis.after(self.ticks)
      def call():
        try:
          generator.send(None)
        except StopIteration:
          pass

  @classmethod
  def coroutine(cls, func):
    '''The `coroutine` method allows you to use generators to manage scheduling and your function.
    If you yield a `vexis.coro_function` object, such as a `vexis.sleep` object, you will pass control to another coroutine for further scheduling and management.

    Args:
      func (callable): The callable generator function to decorate.

    Returns:
      callable: A new function argument which converts your generator function to a vexis coroutine function.

    Examples:
      ```python
      @vexis.coroutine
      def coro():
          for x in range(3):
            for y in range(3):
              print(x, y)
              yield vexis.sleep(20) 
      coro()
      ```
    '''
    class mycoro(vexis.coro_function):
      def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
      def execute(self, coro):
        @functools.wraps(func)
        def f(*args, **kwargs):
          started = func(*args, **kwargs)
          try:
            val = started.send(None)
            while True:
              new = yield val
              val = started.send(new)
          except StopIteration as e:
            coro.send(e.args[0])
        call = vexis.coro_object(vexis.handleCoroutine(f), *self.args, **self.kwargs)
        call.send(None)
      def start(self):
        vexis.coro_object(vexis.handleCoroutine(func), *self.args, **self.kwargs).send(None)
    return mycoro

  @classmethod
  def event(cls, func):
    '''The `event` method allows you to listen to an event using Vexis's event handler. This uses the name of the function to determine what event to listen for.
    This can also hook into other plugins, however you may want to import their classes before hooking into their events.
    This is a wrapper around the `vexis.listen` method.

    Args:
      func (callable): The function to call when the specific event determined by the function name happens.

    Returns:
      callable: The same function that was given as input.

    Example:
      ```python
      @vexis.event
      def PlayerQuitEvent(event):
        player = event.getPlayer()
        event.setQuitMessage(color("&8[&c-&8] &e{}".format(player.getDisplayName())))
      ```
    '''
    name = func.__name__
    return cls.listen(name)(func)
    
  @classmethod
  def listen(cls, *events):
    '''The `listen` method allows you to listen to an event using Vexis's event handler. Unlike the `event` method, this uses an outer decorator with a list of strings as arguments for the events to listen to.
    This can also hook into other plugins, however you may want to import their classes before hooking into their events.

    Args:
      *events (List[str]): A list of events to listen to.

    Returns:
      callable: An inner wrapper which decorates an input function with the list of events given as input.

    Example:
      ```python
      @vexis.listen('PlayerQuitEvent')
      def on_player_quit(event):
        player = event.getPlayer()
        event.setQuitMessage(color("&8[&c-&8] &e{}".format(player.getDisplayName())))
      ```
    '''
    def inner(func):
      for ev in events:
        if ev not in cls._events:
          cls._events[ev] = []
        cls._events[ev].append(func)
      return func
    return inner
  
  @classmethod
  def named_command(cls, name, description="Default Description", usage="Default Usage", aliases=[]):
    '''The `named_command` method allows you to register a command with a given name, an optional description, an optional usage, and optional aliases.
    If you want to use the command name as the function name, `vexis.command` may be more convenient.

    Args:
      name (str): The name of the command.
      description (str): The description of the command. Defaults to `"Default Description"`.
      usage (str): The usage of the command. Defaults to `"Default Usage"`.
      aliases (List[str]): A list of aliases for the command. Defaults to `[]`.

    Returns:
      callable: A decorator which decorates an input function by registering it as the callback for the given command.

    Example:
      ```python
      @vexis.named_command('mycmd', description = 'A Command', usage = '/mycmd', aliases = ['mycmdtwo', 'mycmdthree'])
      def callback(sender, label, args):
        sender.sendMessage(color('&bHi there!'))
      ```
    '''
    def inner(func):    
      class MyMeth(BukkitCommand):
        def execute(self, sender, label, args):
          return vexis._vexis_execution.runCommand(vexis.handle(func), sender, label, list(args))
          
      try:
        label = inspect.stack()[-1][0].f_globals["__name__"]
      except Exception as e:
        label = func.__name__

      Bukkit.getServer().getCommandMap().register(label, MyMeth(name, description, usage, aliases))

      return func
    
    return inner

  @classmethod
  def command(cls, description="Default Description", usage="Default Usage", aliases=[]):
    '''The `command` method allows you to register a command with its name as the function name, an optional description, an optional usage, and optional aliases.
    If you want to use the function name as something other than the command name, `vexis.named_command` is recommended.

    Args:
      description (str): The description of the command. Defaults to `"Default Description"`.
      usage (str): The usage of the command. Defaults to `"Default Usage"`.
      aliases (List[str]): A list of aliases for the command. Defaults to `[]`.

    Returns:
      callable: A decorator which decorates an input function by registering it as the callback for the given command.

    Example:
      ```python
      @vexis.named_command('mycmd', description = 'A Command', usage = '/mycmd', aliases = ['mycmdtwo', 'mycmdthree'])
      def callback(sender, label, args):
        sender.sendMessage(color('&bHi there!'))
      ```
    '''
    def inner(func):
      return cls.named_command(func.__name__, description, usage, aliases)(func)  
    return inner

  @classmethod
  def document(cls):
    '''Create pydoc documentation for this class.'''
    doc = getdoc(cls)
    with open(Paths.get(cls._vexis_folder, "documentation.html").toString(), "w") as f:
      f.write(doc)
      
@vexis.named_command(name = "vexis", description = "Manage Vexis scripts", usage = "/vexis")
def vexis_command(sender, label, args):
  if not args:
    sender.sendMessage(vexis.color('''
&c&lVexis 1.0.0 &f- Creating scripts in Python
 &b/vexis &f- This help page
 &b/vexis &6reload &c<script name> &f- Reload the script with the name <script name>
    '''))
  elif (len(args) > 1 and args[0] == 'reload'):
    script = ' '.join(args[1:])
    sender.sendMessage(vexis.color('&c&lVexis 1.0.0 &f- {}'.format(Vexis.reloadScript(script))))