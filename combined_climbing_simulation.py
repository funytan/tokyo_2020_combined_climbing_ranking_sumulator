from collections import defaultdict
import random
import yaml

import numpy as np
import pyfiglet
from tabulate import tabulate
from tqdm import tqdm

from functions import tabulate_round, tabulate_rounds, RoundSimulatorHelper


"""
Simluating the uncertainties of climbing and it's impact on rankings
through the format of multiplicative scoring
"""

class Simulator:
    def __init__(self):
        self.load_configs()

    def load_configs(self):
        with open('config.yaml') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        self.DEF_SPEED_TIME = self.config['default_speed_timing']
        self.DEF_SPEED_TIME_STD = self.config['default_speed_timing_std']
        self.DEF_SPEED_SLIP_CHANCE = self.config['default_speed_slip_chance']
        self.DEF_BOULDERING_SKILL = self.config['default_bouldering_skill']
        self.DEF_BOULDERING_SKILL_STD = self.config['default_bouldering_skill_std']
        self.BOULDERING_ZONE_DIFFICULTY = self.config['bouldering_zone_difficulty']
        self.BOULDERING_TOP_DIFFICULTY = self.config['bouldering_top_difficulty']
        self.BOULDERING_DIFFICULTY_DROP_PER_ATTEMPT = self.config["bouldering_difficulty_drop_per_attempt"]
        self.TOTAL_ATTEMPTS = self.config["total_attempts"]
        self.LEAD_WALL_NUM_HOLDS = self.config['lead_wall_num_holds']
        self.DEF_LEAD_SKILL = self.config['default_lead_skill']
        self.DEF_LEAD_SKILL_STD = self.config['default_lead_skill_std']
        self.DEF_LEAD_SLIP_CHANCE = self.config['default_lead_slip_chance']

    def get_input(self):
        # ask for user inputs
        self.participants_info = {}
        print(pyfiglet.figlet_format("Welcome to Tokyo 2020!!"))
        print("Do you want to do this interactively, or use values from participants_info.yaml? Enter something to read from file, else enter nothing to go into interactive mode", flush=True)
        decision = input()
        if decision:
            with open('participants_info.yaml') as f:
                self.participants_info = yaml.load(f, Loader=yaml.FullLoader)
            return
        else:
            round_simulator_helper = RoundSimulatorHelper(None)
            self.participants_info = round_simulator_helper.get_user_input()
    
    def simulate(self):
        print("How many rounds do you want to simulate?")
        print(" A '1' response or an empty response would simulate just 1 round, after all, the olympics is only held once!")
        print("If rounds > 1, aggregate statistics will be displayed")
        num_rounds = input()
        if not num_rounds:
            num_rounds = 1
        else:
            num_rounds = int(num_rounds)

        # Store aggregate statistics: 1. score of participant per round 2. Medal Counts 3. Points needed to win each position 4. Best performance/ Average performance of each cateogry
        participants_scores = {comp:[] for comp in self.participants_info}
        store_medal_count = {comp:[0,0,0,0] for comp in self.participants_info} # num_gold, num_silver, num_bronze, total_score_for_gold
        store_position_points = {rank:[] for rank in range(1,4)}
        store_event_performance = {
            "speed": [],
            "bouldering": [],
            "lead": [],
        }
        
        round_simulator_helper = RoundSimulatorHelper(self.participants_info)
        for i in tqdm(range(num_rounds)):
            speed_res = round_simulator_helper.simulate_speed()
            bouldering_res = round_simulator_helper.simulate_bouldering()
            lead_res = round_simulator_helper.simulate_lead()


            if num_rounds == 1:
                tabulate_round(
                    self.participants_info, 
                    speed_res, 
                    bouldering_res, 
                    lead_res, 
                    single_round=True
                )
            else:
                medal_results, final_scores = tabulate_round(
                    self.participants_info, 
                    speed_res, 
                    bouldering_res, 
                    lead_res, 
                    single_round=False
                )

                for score, comp, _ in final_scores:
                    participants_scores[comp].append(score)
            
                for medal in medal_results:
                    comp, score = medal_results[medal]
                    store_medal_count[comp][medal-1] += 1
                    if medal == 1:
                        store_medal_count[comp][3] += score
                    store_position_points[medal].append(score)
                
                store_event_performance['speed'] += [res[0] for res in speed_res]
                store_event_performance['bouldering'] += [(-res[0], -res[1]) for res in bouldering_res]
                store_event_performance['lead'] += [-res[0] for res in lead_res]

        
        if num_rounds > 1:
            tabulate_rounds(participants_scores, store_medal_count, store_position_points, store_event_performance, num_rounds)
        print("Enter for the next simulation")
        input()
        self.simulate()

if __name__ == "__main__":
    simulator = Simulator()
    simulator.get_input()
    simulator.simulate()