# Pokemon Cafe Remix API (sort of)
import constants

import json
import math
from datetime import datetime


def get_by(name:str=None, id:str=None):
    '''
    Search for a pokemon that matches either name or id, then return as a Pokemon object.
    '''
    if (name == None and id == None) or (name != None and id != None): # raise error if no/both kwargs are entered
        raise ValueError('Function get_by_name() requires exactly 1 keyword argument')
    else:
        with open('pkmn.json', 'r') as file:
            data = json.load(file)
            if name != None:
                data_entry = next(x for x in data if x['name_en'] == name) # Perform linear search
            if id != None:
                data_entry = next(x for x in data if f"{x['dex_number']}_{x['costume_id']}" == id) # Perform linear search
            file.close()
            pkmn = Pokemon(
                data_entry['name_en'],
                data_entry['dex_number'],
                data_entry['costume_id'],
                data_entry['date_added'],
                data_entry['obtain_method'],
                data_entry['date_end'],
                data_entry['specialty'],
                data_entry['base_score'],
                data_entry['score_increase'],
                data_entry['ol_bonus'],
                data_entry['gimmicks'],
                data_entry['score_plus']
            )
        return pkmn


def get_shiny_pairs(): 
    '''
    Returns a list of tuple (dex_number, dex_number) representing pokemon and their shiny counterparts.
    '''
    with open('pkmn.json', 'r') as file:
        data = json.load(file)
        file.close()
        pairs = []
        for x in data:
            if x['type'] == 's' and x['costume_id'] == '00':
                try:
                    normal = next(y for y in data if y['name_en'] == x['name_en'][:-1]).get('dex_number')
                    pairs.append((normal, x['dex_number']))
                except StopIteration:
                    pass
        return pairs


class Pokemon:
    def __init__(self, name_en, dex_number, costume_id, date_added, obtain_method, date_end, specialty, base_score, score_increase, ol_bonus, gimmicks, score_plus):
        self.name = name_en
        self.dex_number = dex_number
        self.costume_id = costume_id
        self.date_added = int(datetime.strptime(date_added, '%d/%m/%Y').timestamp() + 50400)
        self.specialty = specialty
        self.base_score = int(base_score)
        self.ol_bonus = int(ol_bonus[:-1])/100
        self.score_plus_gimmick = score_plus[0]
        self.score_plusplus = bool(score_plus[1])
        self.obtain_method = obtain_method
        self.gimmicks = [Gimmick(g) for g in gimmicks if g != '']

        if date_end == '':
            self.date_end = None
        else:
            self.date_end = int(datetime.strptime(date_end, '%d/%m/%Y').timestamp() + 50400)

        if score_increase == '#': # Pokémon uses delivery scoring system
            self.score_increase = None 
        else:
            self.score_increase = int(score_increase)

    def calculate_score(self, level: int=25, ol: int=4):
        if self.score_increase is None:
            return math.ceil((self.base_score + constants.gacha_score[level-1]) * (1 + ol*self.ol_bonus))
        else:
            return math.ceil((self.base_score + self.score_increase * (level-1)) * (1 + ol*self.ol_bonus))

    def get_outfits(self):
        '''
        Return a list of Pokemon objects which have the same dex_number (outfits)
        '''
        with open('pkmn.json', 'r') as file:
            data = json.load(file)   
            ids = [f"{x['dex_number']}_{x['costume_id']}" for x in data if x['dex_number'] == self.dex_number]
            file.close()
            return [get_by(id = x) for x in ids]
        
    def get_counterpart(self): 
        '''
        Returns a Pokemon object representing the shiny/normal counterpart of the pokemon.
        '''
        try:
            pair = next(p for p in get_shiny_pairs() if self.dex_number in p)
        except StopIteration:
            return None
        else:
            if pair.index(self.dex_number) == 0:
                return get_by(id=f"{pair[1]}_{self.costume_id}")
            else:
                return get_by(id=f"{pair[0]}_{self.costume_id}")
            

class Gimmick:
    def __init__(self, name) -> None:
        self.name = name
        self.icon = constants.gimmicks[name][0]
        self.description = constants.gimmicks[name][1].replace('{}', constants.gimmicks[name][0])
        self.amounts = constants.gimmicks[name][2]
