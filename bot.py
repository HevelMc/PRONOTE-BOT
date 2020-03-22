import datetime
import os
import pickle
import random
import requests
import io

import discord
import env_file
from discord.ext import commands
from discord.ext.commands import Bot, MissingPermissions, has_permissions, CommandNotFound

import main

RED_LABEL = ["Conseil de classe", "Prof. absent",
             "Modif salle", "Cours annulé", "Reporté"]
BLUE_LABEL = ["Report", "Exceptionnel",
              "Changement de salle", "Cours maintenu", "Remplacement"]

description = '''Un bot PRONOTE qui t\'envoi les devoirs à faire.'''
client = commands.Bot(command_prefix='$', description=description)


def save_obj(obj, name):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def is_me(m):
    return m.author == client.user


save_obj(main.profs_backup, "profs_backup")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command()
async def bot(ctx):
    await ctx.send('Oui, ce bot est cool. :100:')


@client.command(name="travail", description="Donne la liste des devoirs à faire du mois.")
async def _travail(ctx):

    channel_id = 689906178267938895
    channel = client.get_channel(channel_id)

    await channel.purge(limit=200, check=is_me)

    homeworks = main.homeworks()
    await ctx.send(f"`Début de l'envoi des messages dans le salon` <#{channel_id}> <:pronote:689159558475939911>")
    try:
        for index, date in sorted(homeworks.items(), key=lambda item: item[1][3]):
            homework = homeworks[index]
            await embed_homeworks(homework, channel)
        await ctx.send(f"`Mise à jour du salon` <#{channel_id}> :white_check_mark:")
    except Exception as e:
        await ctx.send("`Erreur lors de l'envoi des messages.` :no_entry_sign:\n" + str(e))
        print(e)


@client.command(description="Donne la liste des professeurs absents.")
async def profs(ctx):

    channel_id = 690251614938071071
    channel = client.get_channel(channel_id)

    await channel.purge(limit=200, check=is_me)

    profs_absents_list = main.profs_absents()
    await ctx.send(f"`Début de l'envoi des messages dans le salon` <#{channel_id}> <:pronote:689159558475939911>")
    try:
        for date, absence in sorted(profs_absents_list.items()):
            await embed_profs(absence, channel)
        await ctx.send(f"`Mise à jour du salon` <#{channel_id}> :white_check_mark:")
    except:
        await ctx.send("`Erreur lors de l'envoi des messages.` :no_entry_sign:")


@client.command(description="Donne les nouveaux devoirs.")
async def travailtest(ctx):
    dict1 = main.homeworks()
    _temp = []
    for index, homework in dict1.items():
        if homework[3] < datetime.date.today():
            _temp.append(index)
    for index in _temp:
        dict1.pop(index)
    
    if load_obj("homework_backup") == dict1:
        return await ctx.send("**Il n'y a pas de nouveaux devoirs !**")
    else:
        await ctx.send("**Voici les nouveaux devoirs :**")
        for dif in main.compare_homeworks(load_obj("homework_backup"), main.homeworks()):
            await embed_homeworks(dif, ctx.channel)
        for dif in main.compare_homeworks(main.homeworks(), load_obj("homework_backup")):
            await embed_homeworks(dif, ctx.channel)
        save_obj(main.homework_backup, "homework_backup")


@client.command(description="Donne les profs nouveaux absents.")
async def profstest(ctx):
    dict1 = main.profs_absents()
    _temp = []
    for index, prof in dict1.items():
        if prof[3] < datetime.date.today():
            _temp.append(index)
    for index in _temp:
        dict1.pop(index)
    
    if load_obj("profs_backup") == dict1:
        return await ctx.send("**Il n'y a pas de nouveaux devoirs !**")
    else:
        await ctx.send("**Voici les nouveaux devoirs :**")
        for dif in main.compare_profs(load_obj("profs_backup"), main.profs_absents()):
            await embed_profs(dif, ctx.channel)
        for dif in main.compare_profs(main.profs_absents(), load_obj("profs_backup")):
            await embed_profs(dif, ctx.channel)
        save_obj(main.profs_backup, "profs_backup")


@client.command(description="Ajoute un fichier ou un message au casier.")
async def casier(ctx, prof: commands.Greedy[discord.Member] = None, *, message_content="Il n'a pas laissé de message."):
    channel = client.get_channel(691242033049894963)
    if not prof:
        await ctx.send("Vous devez mentionner le professeur !")
    elif message_content == "Il n'a pas laissé de message." and len(ctx.message.attachments) < 1:
        await ctx.send("Vous devez specifier un message ou donner un document !")
    else:
        try:
            await channel.send(f"Bonjour <@{prof[0].id}>, <@{ctx.author.id}> a laissé un message pour vous:\n\n**{message_content}**", files=[await attachment.to_file() for attachment in ctx.message.attachments])
            await ctx.send("Message correctement envoyé dans le casier du professeur !")
        except Exception as e:
            await ctx.send("Une erreur est survenue, veuillez réessayer.\n" + str(e))
    await ctx.message.delete()


async def embed_homeworks(homework, channel):
    color = homework[4]
    color = color.replace('#', '')
    color = int(color, 16)
    date = datetime.date.strftime(homework[3], "%d/%m/%Y")
    
    embed = discord.Embed(
        title=homework[0], description=f"\n**{homework[1]}**\n\n", color=color)
    embed.add_field(name="Travail Fait :",
                    value=f"**{homework[2]}**", inline=True)
    embed.add_field(
        name="Date :", value=f"**{date}**", inline=True)
    
    await channel.send(embed=embed)


async def embed_profs(absence, channel):
    if absence[4] in BLUE_LABEL:
        embed = discord.Embed(
            title=absence[4], description=f"**{absence[1]}**", color=0x0000ff)
    elif absence[4] in RED_LABEL:
        embed = discord.Embed(
            title=absence[4], description=f"**{absence[1]}**", color=0xff0000)
    else:
        embed = discord.Embed(
            title=absence[4], description=f"**{absence[1]}**", color=0x808080)
    embed.add_field(name="Matière :",
                    value=f"**{absence[0]}**", inline=True)
    embed.add_field(
        name="Date :", value=f"**{absence[2]}**", inline=True)
    embed.set_thumbnail(
        url="https://www.cat-catounette.com/wp-content/uploads/2017/07/warning-icon-24-1024x1024.png")
    await channel.send(embed=embed)


client.run(env_file.get(path='.env')['TOKEN'])