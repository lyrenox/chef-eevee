import constants

import discord
import time

import pkmn

# Menus / Embeds
class Main(discord.Embed):
    def __init__(self, pokemon: pkmn.Pokemon, level: int=25, ol: int=4):
        if pokemon.date_end is None:
            status = 'always'
        elif int(time.time()) > pokemon.date_end:
            status = 'no longer'
        elif int(time.time()) < pokemon.date_end:
            status = 'currently'

        super().__init__(
            thumbnail = discord.EmbedMedia(url='attachment://portrait.png'),
            description = (
                f"## {pokemon.name}\n"
                f"Introduced in <t:{pokemon.date_added}:d>\n"
                f"This {'pokémon' if pokemon.costume_id == '00' else 'outfit'} is **{status} available** and can be recruited "
                f"{'as a' if pokemon.obtain_method in ['Customer', 'Starter'] else 'from'} **{pokemon.obtain_method}**"
                f"{'.' if pokemon.date_end in [None, 946706400] else f' until <t:{pokemon.date_end}:d>.'}\n"
            ),
            fields = [
                discord.EmbedField(name='Level', value=level, inline=True),
                discord.EmbedField(name='Outfit grade', value=(ol*constants.icons['oltrue'] + (4-ol)*constants.icons['olfalse']), inline=True),
                discord.EmbedField(name='Puzzle score', value=pokemon.calculate_score(level, ol), inline=True),
                discord.EmbedField(name='Specialty', value=constants.icons.get(pokemon.specialty)+pokemon.specialty, inline=True),
                discord.EmbedField(name='Gimmicks', value='\n'.join([g.icon + g.name for g in pokemon.gimmicks]), inline=True)
            ]
        )


class ScoreTable(discord.Embed):
    def __init__(self, pokemon:pkmn.Pokemon):
        table = '''```
╔════════╦═══════════╦════════╦═══════════╗
║   Lv   ║   Score   ║   Lv   ║   Score   ║
╠════════╬═══════════╬════════╬═══════════╣
'''
        for i in range(1, 16):
            if i+15 > 25:
                if pokemon.score_increase is None:
                    score = pokemon.base_score + constants.gacha_score[i-1]
                else:
                    score = pokemon.base_score + pokemon.score_increase*(i-1)
                score = ' '+str(score) if score < 100 else score
                table += f"║   {i}   ║    {score}    ║        ║           ║\n"
            else:
                if pokemon.score_increase is None:
                    scores = [pokemon.base_score + constants.gacha_score[i-1], pokemon.base_score + constants.gacha_score[i+14]]
                else: 
                    scores = [pokemon.base_score + pokemon.score_increase*(i-1), pokemon.base_score + pokemon.score_increase*(i+14)]
                scores = [(' '+str(s) if s < 100 else s) for s in scores]
                table += f"║   {'0' if i<10 else ''}{i}   ║    {scores[0]}    ║   {i+15}   ║    {scores[1]}    ║\n"
        
        table += '╚════════╩═══════════╩════════╩═══════════╝\n```'

        super().__init__(title='Score Table', description=f'Pokémon: **{pokemon.name}**\n{table}')


class GimmickTable(discord.Embed):
    def __init__(self, pokemon: pkmn.Pokemon):
        gim = pokemon.gimmicks

        super().__init__(
            description = '## Gimmicks',
            fields = [
                discord.EmbedField(
                    name = 'Gimmick A',
                    value = gim[0].description + '\n' + '\n'.join([f"**Level {[3,7,11,17,25][i-1]}** —— `{gim[0].amounts[i-1]}` {gim[0].icon}" for i in range(1,6)]),
                    inline = True
                ),
                discord.EmbedField(
                    name = 'Gimmick B',
                    value = gim[1].description + '\n' + '\n'.join([f"**Level {[5,9,13,20][i-1]}** —— `{gim[1].amounts[i-1]}` {gim[1].icon}" for i in range(1,5)]),
                    inline = True
                ),
                discord.EmbedField(
                    name = 'Gimmick C',
                    value = gim[2].description + '\n' + '\n'.join([f"**Level {[15,21,23][i-1]}** —— `{gim[2].amounts[i-1]}` {gim[2].icon}" for i in range(1,4)]),
                    inline= True
                ),
                discord.EmbedField(
                    name = 'Hidden Gimmick',
                    value = (gim[3].description + '\n' + '\n'.join([f"{pow(2,i-1)} Kitchen Note —— `{gim[3].amounts[i-1]}` {gim[3].icon}" for i in range(1,6)])) if len(gim)>3 else 'None',
                )
            ]     
        )


class OLBonus(discord.Embed):
    def __init__(self, pokemon: pkmn.Pokemon):
        super().__init__(
            description = '## Outfit grade bonus',
            fields = [
                discord.EmbedField(name='Outfit grade 1', value=f"Puzzle score +{pokemon.ol_bonus*100}%"),
                discord.EmbedField(name='Outfit grade 2', value=f"Puzzle score +{pokemon.ol_bonus*100}%"),
                discord.EmbedField(name='Outfit grade 3', value=f"Puzzle score +{pokemon.ol_bonus*100}%"),
                discord.EmbedField(name='Outfit grade 4', value=f"Puzzle score +{pokemon.ol_bonus*100}%\n{pkmn.Gimmick(name=pokemon.score_plus_gimmick).icon} Score {'++' if pokemon.score_plusplus is True else '+'}")
            ]
        )


# UI / Views
class MainNav(discord.ui.View):
    def __init__(self, pokemon: pkmn.Pokemon, level: int=25, ol: int=4):
        super().__init__()
        self.pokemon = pokemon
        self.level = level
        self.ol = ol
        self.add_item(OutfitSelect(pokemon=pokemon, level=level, ol=ol))
        self.add_item(ShinyButton(pokemon=pokemon, level=level, ol=ol))

    async def on_timeout(self):
        self.disable_all_items()
        file = f"CharaP{self.pokemon.dex_number}{f'_{self.pokemon.costume_id}' if not self.pokemon.costume_id == '00' else ''}.png"
        await self.message.edit(file=discord.File(f'assets/portraits/{file}', filename='portrait.png'),
                                embed=Main(pokemon=self.pokemon, level=self.level, ol=self.ol), view=self)

    @discord.ui.button(label='Change Level', style=discord.ButtonStyle.primary, row=1)
    async def changelv_callback(self, button, interaction):
        await interaction.response.send_modal(ChangeLevel(pokemon=self.pokemon, level=self.level, ol=self.ol))

    @discord.ui.button(label='Score Table', row=2)
    async def scoretable_callback(self, button, interaction):
        await interaction.response.send_message(embed=ScoreTable(self.pokemon), ephemeral=True)

    @discord.ui.button(label='Gimmicks', row=2)
    async def gimmicks_callback(self, button, interaction):
        await interaction.response.send_message(embed=GimmickTable(self.pokemon), ephemeral=True)

    @discord.ui.button(label='Bonus', emoji=constants.icons['oltrue'], row=2)
    async def olbonus_callback(self, button, interaction):
        await interaction.response.send_message(embed=OLBonus(self.pokemon), ephemeral=True)


class OutfitSelect(discord.ui.Select):
    def __init__(self, pokemon: pkmn.Pokemon, level: int=25, ol: int=4):
        self.level = level
        self.ol = ol

        outfits = []
        for outfit in pokemon.get_outfits():
            if outfit.costume_id == pokemon.costume_id: # Make currently displayed outfit as default selected option
                selected = True
            else:
                selected = False
            outfits.append(discord.SelectOption(label=outfit.name, description=f"Specialty: {outfit.specialty}", default=selected))

        super().__init__(row=0, placeholder = 'Select an outfit',min_values = 1,max_values = 1,options=outfits)

    async def callback(self, interaction):
        # Pass values pokemon, level and ol into Main and MainNav
        new_pkmn = pkmn.get_by(name=self.values[0])
        file = f"CharaP{new_pkmn.dex_number}{f'_{new_pkmn.costume_id}' if not new_pkmn.costume_id == '00' else ''}.png"
        await interaction.response.edit_message(file=discord.File(f'assets/portraits/{file}', filename='portrait.png'),
                                                embed=Main(pokemon=new_pkmn, level=self.level, ol=self.ol), 
                                                view=MainNav(pokemon=new_pkmn, level=self.level, ol=self.ol))
        

class ShinyButton(discord.ui.Button):
    def __init__(self, pokemon: pkmn.Pokemon, level: int=25, ol: int=4):
        self.level = level
        self.ol = ol
        
        if pokemon.get_counterpart() is None:
            self.has_shiny = False
        else:
            self.has_shiny = True
            self.counterpart = pokemon.get_counterpart()

        super().__init__(row=1, emoji='✨', style=discord.ButtonStyle.success, disabled=(not self.has_shiny))
    
    async def callback(self, interaction):
        file = f"CharaP{self.counterpart.dex_number}{f'_{self.counterpart.costume_id}' if not self.counterpart.costume_id == '00' else ''}.png"
        await interaction.response.edit_message(file=discord.File(f'assets/portraits/{file}', filename='portrait.png'),
                                                embed=Main(pokemon=self.counterpart, level=self.level, ol=self.ol), 
                                                view=MainNav(pokemon=self.counterpart, level=self.level, ol=self.ol))


class ChangeLevel(discord.ui.Modal):
    def __init__(self, pokemon: pkmn.Pokemon, level: int=25, ol: int=2):
        super().__init__(title='Change Level')
        self.pokemon = pokemon
        self.level = level
        self.ol = ol

        self.add_item(discord.ui.InputText(label='Level', placeholder='Enter an integer from 1 to 25', 
                                           min_length=1, max_length=2, value=self.level))
        self.add_item(discord.ui.InputText(label='Outfit Grade', placeholder='Enter an integer from 0 to 4', 
                                           min_length=1, max_length=1, value=self.ol))
        
    async def callback(self, interaction):
        try:
            if not 1 <= int(self.children[0].value) <= 25:
                self.children[0].value = self.level
        except Exception as error:
            print(error)
            self.children[0].value = self.level

        try:
            if not 0 <= int(self.children[1].value) <= 4:
                self.children[1].value = self.ol
        except Exception as error:
            print(error)
            self.children[1].value = self.ol
        
        file = f"CharaP{self.pokemon.dex_number}{f'_{self.pokemon.costume_id}' if not self.pokemon.costume_id == '00' else ''}.png"
        await interaction.response.edit_message(file=discord.File(f'./assets/portraits/{file}', filename='portrait.png'),
                                                embed=Main(pokemon=self.pokemon, level=int(self.children[0].value), ol=int(self.children[1].value)), 
                                                view=MainNav(pokemon=self.pokemon, level=int(self.children[0].value), ol=int(self.children[1].value)))
