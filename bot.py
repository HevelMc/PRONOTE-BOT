import discord
import datetime
from discord.ext import commands
import random
import main
import pickle
import os

RED_LABEL = ["Conseil de classe", "Prof. absent", "Modif salle", "Cours annulé", "Reporté"]
BLUE_LABEL = ["Report", "Exceptionnel", "Changement de salle", "Cours maintenu", "Remplacement"]

description = '''Un bot PRONOTE qui t\'envoi les devoirs à faire.'''
bot = commands.Bot(command_prefix='(p) ', description=description)

def save_obj(obj, name):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(name="bot")
async def _bot(ctx):
    await ctx.send('Oui, ce bot est cool. :100:')

def is_me(m):
    return m.author == bot.user

@bot.command(name="travail", description="Donne la liste des devoirs à faire du mois.")
async def _travail(ctx):

    channel_id = 689906178267938895
    channel = bot.get_channel(channel_id)
    
    await channel.purge(limit=200, check=is_me)

    homeworks = main.homeworks()
    await ctx.send(f"`Début de l'envoi des messages dans le salon` <#{channel_id}> <:pronote:689159558475939911>")
    try:
        for homework in homeworks:
            color = homework[4]
            color = color.replace('#', '')
            color = int(color, 16)
            embed=discord.Embed(title=homework[0], description=f"\n**{homework[1]}**\n\n", color=color) 
            embed.set_thumbnail(url="")
            embed.add_field(name="Travail Fait :", value=f"**{homework[2]}**", inline=True)
            embed.add_field(name="Date :", value=f"**{homework[3]}**", inline=True)
            await channel.send(embed=embed)
        await ctx.send(f"`Mise à jour du salon` <#{channel_id}> :white_check_mark:")
    except Exception as e:
        await ctx.send("`Erreur lors de l'envoi des messages.` :no_entry_sign:\n" + e)
        print(e)


@bot.command(name="profs", description="Donne la liste des professeurs absents.")
async def _travail(ctx):

    channel_id = 690251614938071071
    channel = bot.get_channel(channel_id)
    
    await channel.purge(limit=200, check=is_me)

    profs_absents_list = main.profs_absents()
    await ctx.send(f"`Début de l'envoi des messages dans le salon` <#{channel_id}> <:pronote:689159558475939911>")
    try:
        for absence in profs_absents_list:
            if absence[4] in BLUE_LABEL:
                embed=discord.Embed(title=absence[4], description=f"**{absence[1]}**", color=0x0000ff)
            elif absence[4] in RED_LABEL:
                embed=discord.Embed(title=absence[4], description=f"**{absence[1]}**", color=0xff0000)
            else:
                embed=discord.Embed(title=absence[4], description=f"**{absence[1]}**", color=0x808080)
            embed.add_field(name="Matière :", value=f"**{absence[0]}**", inline=True)
            embed.add_field(name="Date :", value=f"**{absence[2]}**", inline=True)
            embed.set_thumbnail(url="https://www.cat-catounette.com/wp-content/uploads/2017/07/warning-icon-24-1024x1024.png")
            await channel.send(embed=embed)
        await ctx.send(f"`Mise à jour du salon` <#{channel_id}> :white_check_mark:")
    except:
        await ctx.send("`Erreur lors de l'envoi des messages.` :no_entry_sign:")


bot.run('Njg4NzczNTc3MjM0NzEwNTQy.Xm5MhQ.NKLUytVotRJGn7QYRc1x3m_mLnA')