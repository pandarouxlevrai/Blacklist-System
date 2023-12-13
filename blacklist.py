import discord
import random
import discord_slash
import sqlite3
import time
import asyncio
import requests
import pymongo
import typing 
import datetime
import string 
import os 
import datetime
from typing import Optional
from pymongo import MongoClient
from datetime import datetime, timedelta
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash import SlashCommand, SlashContext
from discord.ext import commands, tasks
from discord_slash import SlashContext, ComponentContext, cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType as OptionType
from discord_slash.utils.manage_components import create_actionrow
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandOptionType
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash import ComponentContext
from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType, utils
from discord_slash.utils import manage_components
from discord_slash import SlashContext, SlashCommand, ComponentContext
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils import manage_components
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import ButtonStyle

intents = discord.Intents.default()
intents.guilds = True 
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix =";", description = "Fusely", intents=intents)
bot.remove_command("help")
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

cluster = pymongo.MongoClient("") #Votre lien MongoDB 
db = cluster["blacklist2"]
blacklist_collection = db["blacklist"]
state_collection = db["state"]

@bot.event
async def on_member_join(member):
    server_id = str(member.guild.id)
    state = state_collection.find_one({"_id": server_id})

    if not state or state.get("status", "OFF") == "ON":
        user = blacklist_collection.find_one({"_id": member.id})

        if user:
            reason = user.get("reason", "Raison non spécifiée")
            owner = member.guild.owner

            embed_admin = discord.Embed( #Embed à personnaliser, reçu par l'owner du serveur. 
                title="",
                description=f"",
                color=0x 
            )
            embed_admin.set_footer(text="")
            embed_admin.set_thumbnail(url="")

            await owner.send(embed=embed_admin)

            embed_user = discord.Embed( #Embed à perosnnaliser, reçu par l'utilisateur blacklist. 
                title="",
                description="",
                color=0x
            )
            embed_user.set_footer(text="")
            embed_user.set_thumbnail(url="")

            await member.send(embed=embed_user)

            await member.kick(reason="Utilisateur blacklisté")
            print(f"Utilisateur blacklisté {member.name}#{member.discriminator} expulsé.")

@slash.slash(name="blacklist", description="Active ou désactive la blacklist.",
             options=[
                 create_option(
                     name="status",
                     description="Choisissez ON pour activer la blacklist ou OFF pour la désactiver.",
                     option_type=SlashCommandOptionType.STRING,
                     required=True,
                     choices=[
                         {"name": "ON", "value": "on"},
                         {"name": "OFF", "value": "off"}
                     ]
                 )
             ])
@commands.has_permissions(administrator=True)
async def toggle_blacklist(ctx: SlashContext, status: str):
    server_id = str(ctx.guild.id)
    state = state_collection.find_one({"_id": server_id})

    if not state:
        state = {"_id": server_id, "status": "OFF"}
        state_collection.insert_one(state)

    embed = discord.Embed() 

    if status.lower() == "on":
        state_collection.update_one({"_id": server_id}, {"$set": {"status": "ON"}})
        embed.title = "" #Embed d'activation
        embed.description = ""
        embed.color = discord.Color.green()
        embed.set_footer(text="")
        embed.set_thumbnail(url="")
    elif status.lower() == "off":
        state_collection.update_one({"_id": server_id}, {"$set": {"status": "OFF"}})
        embed.title = "" #Embed de désactivation 
        embed.description = ""
        embed.color = discord.Color.orange()
        embed.set_footer(text="")
        embed.set_thumbnail(url="")

    await ctx.send(embed=embed)

@toggle_blacklist.error
async def toggle_blacklist_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title = "", description = "", color =0x) #embed erreur missing permissions 
        embed.set_footer(text = "")
        await ctx.send(embed = embed)  

bot.run('') #Votre token