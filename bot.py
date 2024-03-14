import models

import discord
import os
from dotenv import load_dotenv

import json
from random import randint

import pkmn


load_dotenv()
bot = discord.Bot(owner_id=717408952035573767)


@bot.event
async def on_ready():
    print(f'Connection is successful: {bot.user.display_name}#{bot.user.discriminator} --> Discord')


@bot.event
async def on_guild_join(guild: discord.Guild):
    if guild.system_channel.can_send: # If bot has permissions to the guild's system message channel
        target = guild.system_channel
        # Set target to the guild's system message channel
    else:
        target = next(ch for ch in guild.channels if isinstance(ch, discord.TextChannel) and ('welcome' in ch.name or 'general' in ch.name) and ch.can_send)
        # Set the target channel to the next channel the bot has permissions to
    await target.send('Wassup')


async def filter_names(ctx: discord.AutocompleteContext):
    name = ctx.options['name']
    with open('pkmn.json', 'r') as file:
        data = json.load(file)   
        names = [x['name_en'] for x in data if x['type'] not in ['s', 'sc']]
        if name == '':
            return names[:20]
        else:
            names = sorted([x for x in names if x.lower().startswith(name.lower())])
            if len(names) > 20:
                return names[:20]
            else:
                return names

@bot.slash_command(description='View information on a specific Pokémon.')
@discord.option('name', description='The name of the outfit or Pokémon', autocomplete=discord.utils.basic_autocomplete(filter_names))
async def pokemon(ctx, name):
    try:
        pokemon = pkmn.get_by(name=name)
        file = f"CharaP{pokemon.dex_number}{f'_{pokemon.costume_id}' if not pokemon.costume_id == '00' else ''}.png"
        await ctx.respond(file=discord.File(f'assets/portraits/{file}', filename='portrait.png'),
                          embed=models.Main(pokemon=pokemon), view=models.MainNav(pokemon=pokemon))
    except Exception as error:
        print(f'An error occured: {error}')       
        await ctx.respond(embed=discord.Embed(description='This Pokémon or outfit does not exist. Did you misspell it?'))


@bot.slash_command(description='For testing only.')
async def test(ctx):
    await ctx.respond('Vee!')


class HighlowGame(discord.ui.View):
    def __init__(self, numbers):
        self.numbers = numbers
        self.index = 0
        super().__init__(timeout=15)
        print(self.numbers)

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(content='bye', view=self)

    @discord.ui.button(label='Higher', style=discord.ButtonStyle.primary)
    async def higher(self, button, interaction):
        self.index += 1 # Go to the next number
        if self.numbers[self.index] > self.numbers[self.index-1]:
            if self.index == 9: # Last number
                button.style = discord.ButtonStyle.success
                self.children[1].style = discord.ButtonStyle.secondary
                self.disable_all_items()
                self.stop()
                message = 'congrations\n'
            else:
                message = 'nice, keep going\n'
        else:
            button.style = discord.ButtonStyle.danger
            self.children[1].style = discord.ButtonStyle.secondary
            self.disable_all_items()
            self.stop()
            message = 'sorry for your loss\n'
        await interaction.response.edit_message(content=message + '  '.join([str(n) for n in self.numbers[:self.index+1]]) + (9-self.index) * ' ▒▒', view=self)

    @discord.ui.button(label='Lower', style=discord.ButtonStyle.primary)
    async def lower(self, button, interaction):
        self.index += 1 # Go to next number
        if self.numbers[self.index] < self.numbers[self.index-1]:
            if self.index == 9: # Last number
                button.style = discord.ButtonStyle.success
                self.children[0].style = discord.ButtonStyle.secondary
                self.disable_all_items()
                self.stop()
                message = 'congrations\n'
            else:
                message = 'nice, keep going\n'
        else:
            button.style = discord.ButtonStyle.danger
            self.children[0].style = discord.ButtonStyle.secondary
            self.disable_all_items()
            self.stop()
            message = 'sorry for your loss\n'
        await interaction.response.edit_message(content=message + '  '.join([str(n) for n in self.numbers[:self.index+1]]) + (9-self.index) * ' ▒▒', view=self)

@bot.slash_command(description='A simple game.')
async def game(ctx):
    numbers = [randint(1, 100) for n in range(10)]
    await ctx.respond(f'Higher or lower?\n{numbers[0]}' + 9 * ' ▒▒', view=HighlowGame(numbers)) # Pass numbers into HighlowGame


bot.run(os.getenv('TOKEN'))
