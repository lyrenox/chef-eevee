# Developer-only commands I think

import discord
from discord.ext import commands

class DevTools(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    devtools = discord.SlashCommandGroup('devtools', 'only a Latios can access them', checks=[commands.is_owner().predicate])

    @devtools.command(description='I don\'t even know anymore.')
    async def meow(ctx):
        await ctx.respond('something something owo')
    

def setup(bot):
    bot.add_cog(DevTools(bot))

# I HAVE NO IDEA WHAT TO DO AAAAAAAAAAAAAAA
