import datetime
import os
import random
import requests

import discord
import env_file
from discord.ext import commands
from discord.ext.commands import Bot, MissingPermissions, has_permissions, CommandNotFound

import main

# locale.setlocale(locale.LC_TIME, 'fr_FR')

RED_LABEL = ["Conseil de classe", "Prof. absent",
             "Modif salle", "Cours annulé", "Reporté"]
BLUE_LABEL = ["Report", "Exceptionnel",
              "Changement de salle", "Cours maintenu", "Remplacement"]

description = '''Un bot PRONOTE qui t\'envoi les devoirs à faire.'''
client = commands.Bot(command_prefix='$', description=description)


def is_me(m):
    return m.author == client.user


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command()
async def bot(ctx):
    await ctx.send('Oui, ce bot est cool. :100:')


@client.command(description="Donne la liste des devoirs à faire du mois.")
async def travail(ctx):

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

    if main.load_obj("homework_backup") == dict1:
        return await ctx.send("**Il n'y a pas de nouveaux devoirs !**")
    else:
        await ctx.send("**Voici les nouveaux devoirs :**")
        for dif in main.compare_homeworks(main.load_obj("homework_backup"), main.homeworks()):
            await embed_homeworks(dif, ctx.channel)
        for dif in main.compare_homeworks(main.homeworks(), main.load_obj("homework_backup")):
            await embed_homeworks(dif, ctx.channel)
        main.save_obj(main.homework_backup, "homework_backup")


@client.command(description="Donne les profs nouveaux absents.")
async def profstest(ctx):
    dict1 = main.profs_absents()
    _temp = []
    for index, prof in dict1.items():
        if prof[3] < datetime.date.today():
            _temp.append(index)
    for index in _temp:
        dict1.pop(index)

    if main.load_obj("profs_backup") == dict1:
        return await ctx.send("**Il n'y a pas de nouveaux devoirs !**")
    else:
        await ctx.send("**Voici les nouveaux devoirs :**")
        for dif in main.compare_profs(main.load_obj("profs_backup"), main.profs_absents()):
            await embed_profs(dif, ctx.channel)
        for dif in main.compare_profs(main.profs_absents(), main.load_obj("profs_backup")):
            await embed_profs(dif, ctx.channel)
        main.save_obj(main.profs_backup, "profs_backup")


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


@client.command(description="Ajoute un fichier ou un message dans ressources-pédagogiques.")
@commands.has_permissions(administrator=True)
async def add_source(ctx, *, args=None):
    channel = client.get_channel(689157099837718546)
    if args:
        message, matiere, prof, *date = args.split(' |-| ')
        date = date[0] if date else "Date limite non renseignée"
        list_matieres = main.list_matieres()
        if list_matieres.get(matiere):
            color = list_matieres.get(matiere)
            try:
                await channel.send(embed=await embed_source(matiere, prof, message, color, date, channel), files=[await attachment.to_file() for attachment in ctx.message.attachments])
                await ctx.send(f"Message correctement envoyé dans <#{channel.id}> ! :white_check_mark:")
            except Exception as e:
                await ctx.send("Une erreur est survenue, veuillez réessayer.\n" + str(e))
        else:
            list_text = '\n'.join(list_matieres)
            embed = discord.Embed(
                title="La matière specifiée n'est pas correcte, voici une liste des matières disponibles :", color=0x5a5a5a, description=list_text)
            await ctx.send(embed=embed)
    else:
        await channel.send(files=[await attachment.to_file() for attachment in ctx.message.attachments])
    await ctx.message.delete()


@client.command(description="Ajoute un devoir dans travail de la semaine.")
@commands.has_permissions(administrator=True)
async def add_travail(ctx, *, args=None):
    if args:
        s = args
        matiere = s[ s.find( '<mat>' )+5 : s.find( '</mat>' ) ].upper()
        description = s[ s.find( '<desc>' )+6 : s.find( '</desc>' ) ]
        fait = s[ s.find( '<fait>' )+6 : s.find( '</fait>' ) ]
        date = s[ s.find( '<date>' )+6 : s.find( '</date>' ) ]
        date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        liens_final = {}
        if '<lien>' in s:
            lien = s[ s.find( '<lien>' )+6 : s.find( '</lien>' ) ]
            liens = lien.split(', ')
            for lien in liens:
                lien = lien.split(' : ')
                liens_final[lien[0]] = lien[1]
        list_matieres = main.list_matieres()
        if list_matieres.get(matiere):
            couleur = list_matieres.get(matiere)
            manual_add_list = main.load_obj("manual_add_list")
            manual_add_list[description] = [matiere, description, fait, date, couleur, liens_final]
            main.save_obj(manual_add_list, "manual_add_list")
            await travail(ctx)
        else:
            list_text = '\n'.join(list_matieres)
            embed = discord.Embed(
                title="La matière specifiée n'est pas correcte, voici une liste des matières disponibles :", color=0x5a5a5a, description=list_text)
            await ctx.send(embed=embed)
    else:
        await ctx.send("Exemple de commande: \n\n```html\n$add_travail\n<mat>MATIERE</mat>\n<desc>Description du travail à faire</desc>\n<fait>Non</fait>\n<date>26/03/2020</date>\n<lien>nom du lien : https://example.com, nom du lien 2 : https://google.com</lien>```")
    await ctx.message.delete()


@client.command(description="Retire un devoir dans travail de la semaine.")
@commands.has_permissions(administrator=True)
async def remove_travail(ctx, *, args=None):
    manual_add_list = main.load_obj("manual_add_list")
    if args:
        manual_add_list.pop(args)
        main.save_obj(manual_add_list, "manual_add_list")
        await travail(ctx)
    else:
        print(manual_add_list)


async def embed_homeworks(homework, channel):
    date = datetime.date.strftime(homework[3], "%A %d/%m/%Y")
    if homework[3] - datetime.date.today() < datetime.timedelta(seconds=0):
        color = int("4c4c4c", 16)
        old = "-- [Passée !]"
    else:
        color = homework[4]
        color = color.replace('#', '')
        color = int(color, 16)
        old = ""

    embed = discord.Embed(
        title=homework[0], description=f"\n**{homework[1]}**\n\n", color=color)
    embed.add_field(name="Travail Fait :",
                    value=f"**{homework[2]}**", inline=True)
    embed.add_field(
        name="Date :", value=f"**{date}{old}**", inline=True)

    i = 0
    for name, url in homework[5].items():
        i += 1
        embed.add_field(
            name=f"Pièce jointe n°{i} :", value=f"**[{name}]({url})**", inline=False)

    await channel.send(embed=embed)


async def embed_source(matiere, prof, devoir, color, date, channel):
    color = color.replace('#', '')
    color = int(color, 16)

    embed = discord.Embed(
        title=matiere, description=f"\n**{devoir}**\n\n", color=color)
    embed.add_field(name="Pour le :", value=f"**{date}**", inline=True)
    embed.add_field(name="Professeur :", value=f"**{prof}**", inline=True)

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
