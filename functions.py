from collections import defaultdict
import random
import yaml

import numpy as np
import pyfiglet
from tabulate import tabulate


def tabulate_round(participants_info, speed_res, bouldering_res, lead_res, single_round = True):
    """
    Prints and tabulates results from a singe simulation

    Args:
        participants_info (dict):
        speed_res (list): 
        bouldering_res (list): 
        lead_res (list): 
    """
    # tabulate
    scores = {comp: [] for comp in participants_info}
    for rank, item in enumerate(speed_res, 1):
        scores[item[-1]].append(rank)
    for rank, item in enumerate(bouldering_res, 1):
        scores[item[-1]].append(rank)
    for rank, item in enumerate(lead_res, 1):
        scores[item[-1]].append(rank)
    final_scores = sorted([[np.prod(scores[comp]), comp, scores[comp]] for comp in scores])

    if single_round: # print results if single_round
        # print results
        print(
            tabulate([[item[1], item[2][0], item[2][1], item[2][2], item[0]]for item in final_scores], headers=['Name', 'Speed', 'Bouldering', 'Lead', 'Overall'])
        )
        print()
        print("Enter for more information on the SPEED round")
        input()
        print(f"\033[1m{speed_res[0][-1]}\033[0m is the winner for the SPEED round with a time of {round(speed_res[0][0],2)} seconds!")
        print(f"The median performance in this round is {round(speed_res[len(speed_res)//2][0],2)} seconds")
        print()
        print("Enter for more information on the BOULDERING round")
        input()
        print(f"\033[1m{bouldering_res[0][-1]}\033[0m is the winner for the BOULDERING round with {-bouldering_res[0][0]} tops and {-bouldering_res[0][1]} zones!")
        print(f"The median performance in this round is {-bouldering_res[len(bouldering_res)//2][0]} tops and {-bouldering_res[len(bouldering_res)//2][1]} zones")
        print()
        print("Enter for more information on the LEAD round")
        input()
        print(f"\033[1m{lead_res[0][-1]}\033[0m is the winner for the LEAD round, reaching hold {-round(lead_res[0][0])}!")
        print(f"The median performance in this round is {-lead_res[len(lead_res)//2][0]} holds")

    else: # store medal results for aggregate statistics
        return {
            1 : (final_scores[0][1], final_scores[0][0]),
            2 : (final_scores[1][1], final_scores[1][0]),
            3 : (final_scores[2][1], final_scores[2][0]),
        }

def tabulate_rounds(store_medal_count, store_position_points, store_event_performance):
    medal_tally = sorted([(store_medal_count[comp], comp) for comp in store_medal_count])[::-1]
    store_event_performance['speed'] = sorted(store_event_performance['speed'])
    store_event_performance['bouldering'] = sorted(store_event_performance['bouldering'])[::-1]
    store_event_performance['lead'] = sorted(store_event_performance['lead'])[::-1]
    # print medal tally
    print(
        tabulate([[item[-1], item[0][0], item[0][1], item[0][2]]for item in medal_tally], headers=['Name', 'First', 'Second', 'Third'])
    )
    print('Enter to show statistics of winning scores')
    input()
    # print statistics to win each position
    print(
        tabulate([
                [
                    rank, 
                    np.mean(store_position_points[rank]), 
                    round(np.std(store_position_points[rank]),2), 
                    min(store_position_points[rank]),
                    max(store_position_points[rank]),
                ] for rank in store_position_points
            ],
            headers=['Rank', 'Mean', 'Std', 'Min_pts', 'Max_pts']
            )
    )
    print('Enter to show statistics of each event')
    input()
    # print statistics for event performance
    print(f"SPEED rounds best performance is {round(store_event_performance['speed'][0],2)} seconds!")
    print(f"The median performance is {round(store_event_performance['speed'][len(store_event_performance['speed'])//2],2)} seconds")
    print()
    print(f"BOULDERING rounds best performance is {store_event_performance['bouldering'][0][0]} tops and {store_event_performance['bouldering'][0][1]} zones!")
    print(f"The median performance is {store_event_performance['bouldering'][len(store_event_performance['bouldering'])//2][0]} tops and {store_event_performance['bouldering'][len(store_event_performance['bouldering'])//2][1]} zones!")
    print()
    print(f"LEAD rounds best performance is {store_event_performance['lead'][0]} holds!")
    print(f"The median performance is {round(store_event_performance['lead'][len(store_event_performance['lead'])//2],2)} holds")   
    print()


class RoundSimulatorHelper:
    def __init__(self, participants_info):
        self.load_configs()
        self.participants_info = participants_info

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

    def get_user_input(self):
        # Interative Mode
        # Step 1 ask for name
        name_check = True
        print("~ ~ ~ Welcome to the first ever Tokyo 2020 Virtual Olymoicss - Sport Climbing ~ ~ ~")
        print("Step 1: Input names of competitors, enter empty input to proceed to Step 2")
        while name_check:
            print(f"Please provide the name of competitor {len(self.participants_info)+1}", flush=True)
            comp_name = input()
            if comp_name:
                self.participants_info[comp_name] = {}
            else:
                name_check=False
        assert len(self.participants_info) > 3, "You will need more than 3 compeitors in the Olympics"
        print(f"OK! There will be {len(self.participants_info)} competitors for YOUR TOKYO 2020 Virtual Olympics - Sport Climbing")
        print("enter to continue")
        input()

        # Step 2 ask for speed statistics
        speed_check = True
        print("Step 2: Input speed skill, standard deviation of speed skill and slippage chance of competitors")
        print(f"Speed skill is the timing you expect your competitor to be capable of acheiving on average, e.g. 6.01s. Default is {self.DEF_SPEED_TIME}")
        print(f"Standard deviation in speed will provide the randomness. Default is {self.DEF_SPEED_TIME_STD}")
        print(f"Slippage chance in speed will provide the randomness, a slip might occur and it will add a 10% time to the competitor. Default is {self.DEF_SPEED_SLIP_CHANCE}")
        
        for comp in self.participants_info:
            self.participants_info[comp]['speed'] = {
                "skill": self.DEF_SPEED_TIME,
                "std": self.DEF_SPEED_TIME_STD,
                "slip": self.DEF_SPEED_SLIP_CHANCE,
            }

       
        print(f"Please provide the speed attributes of competitor in the following format\
 'skill', 'std', 'slip_chance' e.g.: 7.5, 0.5, 0.3", flush=True)
        print("enter to continue")
        input()
        for comp in self.participants_info:
            print(f"Please provide the speed attributes for: {comp}, or enter nothing to use default values")
            atts = input()
            if atts:
                atts = [att.strip() for att in atts.split(',')]
                atts = list(map(float, atts))
                assert len(atts) == 3, "please use the correct format"
                self.participants_info[comp]['speed'] = {
                    "skill": atts[0],
                    "std": atts[1],
                    "slip": atts[2],
                }
        print("Awesome! enter to continue")
        input()

        # Step 3 ask for bouldering statistics
        print("Step 3: Input bouldering skill, standard deviation of bouldering skill for each of 3 boulders")
        print("You will be asked to input 6 vales for each competitor, the skill and standard deviation for each boulder, for 3 boulders")
        print(f"Routesetters have determined that each boulder has a ZONE difficulty range between {self.BOULDERING_ZONE_DIFFICULTY[0]} and {self.BOULDERING_ZONE_DIFFICULTY[1]} ")
        print(f"Routesetters have determined that each boulder has a TOP difficulty range between {self.BOULDERING_TOP_DIFFICULTY[0]} and {self.BOULDERING_TOP_DIFFICULTY[1]} ")
        print("The difficulty in each simulation will be uniformly selected")
        print("The simulation happens as follows.")
        print("Competitors attempts will be simulated by rolling their skill chances accorring to the skill and std provided by you")
        print("If their skill is greater than zone/ top they will get it in this attempt, or the next attempt will happen")
        print(f"After each attempt, the difficulty of the boulder drops by a factor of {self.BOULDERING_DIFFICULTY_DROP_PER_ATTEMPT} and\
 each competitor will have {self.TOTAL_ATTEMPTS} attempts")

        print("enter to continue")
        input()
        print("The first boulder will be slab, the second a coordination puzzle, and third will be in good ol' traditional style")
        print(f"Default skill is {self.DEF_BOULDERING_SKILL}")
        print(f"Default std {self.DEF_BOULDERING_SKILL_STD}")
        
        for comp in self.participants_info:
            self.participants_info[comp]['bouldering'] = {
                "skill_1": self.DEF_BOULDERING_SKILL,
                "std_1": self.DEF_BOULDERING_SKILL_STD,
                "skill_2": self.DEF_BOULDERING_SKILL,
                "std_2": self.DEF_BOULDERING_SKILL_STD,
                "skill_3": self.DEF_BOULDERING_SKILL,
                "std_3": self.DEF_BOULDERING_SKILL_STD,
            }

       
        print(f"Please provide the bouldering attributes of competitor in the following format\
'skill', 'std', 'skill', 'std', 'skill', 'std' e.g.: 6, 1, 6, 1, 6, 1", flush=True)
        print("enter to continue")
        input()
        for comp in self.participants_info:
            print(f"Please provide the bouldering attributes for: {comp}, or enter nothing to use default values")
            atts = input()
            if atts:
                atts = [att.strip() for att in atts.split(',')]
                atts = list(map(float, atts))
                assert len(atts) == 6, "please use the correct format"
                self.participants_info[comp]['bouldering'] = {
                    "skill_1": atts[0],
                    "std_1": atts[1],
                    "skill_2": atts[2],
                    "std_2": atts[3],
                    "skill_3": atts[4],
                    "std_3": atts[5],
                }

        print("Phew, almost there! Enter to continue")
        input()

        # Step 4 ask for lead statistics
        print("Step 4: Lead is simple. Input lead skill, standard deviation of lead skill, and slip chance. First two are measured in number of holds, and the last in probability i.e.[0,1]")
        print(f"Routesetters have set a total of {self.LEAD_WALL_NUM_HOLDS} holds in this lead wall")
        print(f"The simulation is as follows:")
        print(f"By the same random process, the number of holds the competitor will climb out of {self.LEAD_WALL_NUM_HOLDS} will\
 be pre-determined, then the competitor starts climbing from the bottom, and the slip chance die is rolled per hold. It is encourage to keep this chance to below 5%")

        print("enter to continue")
        input()
        print(f"Default skill is {self.DEF_LEAD_SKILL} holds")
        print(f"Default std {self.DEF_LEAD_SKILL_STD} holds")
        print(f"Default slip chance is {self.DEF_LEAD_SLIP_CHANCE} per hold")
        
        for comp in self.participants_info:
            self.participants_info[comp]['lead'] = {
                "skill": self.DEF_LEAD_SKILL,
                "std": self.DEF_LEAD_SKILL_STD,
                "slip": self.DEF_LEAD_SLIP_CHANCE,
            }

       
        print(f"Please provide the lead attributes of competitor in the following format\
'skill', 'std', 'slip e.g.: 35, 3, 0", flush=True)
        print("enter to continue")
        input()
        for comp in self.participants_info:
            print(f"Please provide the lead attributes for: {comp}, or enter nothing to use default values")
            atts = input()
            if atts:
                atts = [att.strip() for att in atts.split(',')]
                atts = list(map(float, atts))
                assert len(atts) == 3, "please use the correct format"
                self.participants_info[comp]['lead'] = {
                    "skill": atts[0],
                    "std": atts[1],
                    "slip": atts[2],
                }

        print("Alright, our athletes are all set for the games! Let the games begin! Enter to continue")
        input()
        return self.participants_info

    def simulate_speed(self):
        # speed 
        speed_res = []
        for comp in self.participants_info:
            comp_atts = self.participants_info[comp]['speed']
            time = np.random.normal(comp_atts['skill'], comp_atts['std'])
            did_slip = random.random() < comp_atts['slip']
            if did_slip:
                time *= 1.1
            speed_res.append((time, comp))
        speed_res = sorted(speed_res)
        return speed_res

    def simulate_bouldering(self):
        """
        Simulates the athletes' attempts on each boulder. The difficulty of the boulder gets easier each round.
        The scoring is by tops, zones, top_attemopts, zone_attempts. The first two being sorted in desc, and the latter two in asc.
        """
        # bouldering 
        bouldering_res = []
        for comp in self.participants_info:
            comp_atts = self.participants_info[comp]['bouldering']
            comp_bouldering_res = [[0,0,0,0] for _ in range(3)]

            # boulder problem 1 (slab)
            boulder_1_difficulty_zone = random.uniform(self.BOULDERING_ZONE_DIFFICULTY[0], self.BOULDERING_ZONE_DIFFICULTY[1])
            boulder_1_difficulty_top = random.uniform(self.BOULDERING_TOP_DIFFICULTY[0], self.BOULDERING_TOP_DIFFICULTY[1])
            for _ in range(self.TOTAL_ATTEMPTS):
                strength_of_attempt = np.random.normal(comp_atts['skill_1'], comp_atts['std_1'])
                if strength_of_attempt > boulder_1_difficulty_zone and comp_bouldering_res[0][2] == 0:
                    comp_bouldering_res[0][2] = 1
                    if strength_of_attempt > boulder_1_difficulty_top and comp_bouldering_res[0][0] == 0:
                        comp_bouldering_res[0][0] = 1
                if comp_bouldering_res[0][2] == 0:
                    comp_bouldering_res[0][3] += 1
                comp_bouldering_res[0][1] += 1
                # break when a top is acheived
                if comp_bouldering_res[0][0]:
                    break 
                else: # decrease boulder difficulty
                    boulder_1_difficulty_zone *= (1-self.BOULDERING_DIFFICULTY_DROP_PER_ATTEMPT)
                    boulder_1_difficulty_top *= (1-self.BOULDERING_DIFFICULTY_DROP_PER_ATTEMPT)
            # remove top attempts
            if comp_bouldering_res[0][0] == 0:
                comp_bouldering_res[0][1] = 0
            # remove zone attempts
            if comp_bouldering_res[0][2] == 0:
                comp_bouldering_res[0][3] = 0
            
            # boulder problem 2 (dynamic)
            boulder_2_difficulty_zone = random.uniform(self.BOULDERING_ZONE_DIFFICULTY[0], self.BOULDERING_ZONE_DIFFICULTY[1])
            boulder_2_difficulty_top = random.uniform(self.BOULDERING_TOP_DIFFICULTY[0], self.BOULDERING_TOP_DIFFICULTY[1])
            for _ in range(self.TOTAL_ATTEMPTS):
                strength_of_attempt = np.random.normal(comp_atts['skill_2'], comp_atts['std_2'])
                if strength_of_attempt > boulder_2_difficulty_zone and comp_bouldering_res[1][2] == 0:
                    comp_bouldering_res[1][2] = 1
                    if strength_of_attempt > boulder_2_difficulty_top and comp_bouldering_res[1][0] == 0:
                        comp_bouldering_res[1][0] = 1
                if comp_bouldering_res[1][2] == 0:
                    comp_bouldering_res[1][3] += 1
                comp_bouldering_res[1][1] += 1
                # break when a top is acheived
                if comp_bouldering_res[1][0]:
                    break 
                else: # decrease boulder difficulty
                    boulder_2_difficulty_zone *= (1-self.BOULDERING_DIFFICULTY_DROP_PER_ATTEMPT)
                    boulder_2_difficulty_top *= (1-self.BOULDERING_DIFFICULTY_DROP_PER_ATTEMPT)
            # remove top attempts
            if comp_bouldering_res[1][0] == 0:
                comp_bouldering_res[1][1] = 0
            # remove zone attempts
            if comp_bouldering_res[1][2] == 0:
                comp_bouldering_res[1][3] = 0

            # boulder problem 3 (traditional)
            boulder_3_difficulty_zone = random.uniform(self.BOULDERING_ZONE_DIFFICULTY[0], self.BOULDERING_ZONE_DIFFICULTY[1])
            boulder_3_difficulty_top = random.uniform(self.BOULDERING_TOP_DIFFICULTY[0], self.BOULDERING_TOP_DIFFICULTY[1])
            for _ in range(self.TOTAL_ATTEMPTS):
                strength_of_attempt = np.random.normal(comp_atts['skill_3'], comp_atts['std_3'])
                if strength_of_attempt > boulder_3_difficulty_zone and comp_bouldering_res[2][2] == 0:
                    comp_bouldering_res[2][2] = 1
                    if strength_of_attempt > boulder_3_difficulty_top and comp_bouldering_res[2][0] == 0:
                        comp_bouldering_res[2][0] = 1
                if comp_bouldering_res[2][2] == 0:
                    comp_bouldering_res[2][3] += 1
                comp_bouldering_res[2][1] += 1
                # break when a top is acheived
                if comp_bouldering_res[2][0]:
                    break 
                else: # decrease boulder difficulty
                    boulder_3_difficulty_zone *= (1-self.BOULDERING_DIFFICULTY_DROP_PER_ATTEMPT)
                    boulder_3_difficulty_top *= (1-self.BOULDERING_DIFFICULTY_DROP_PER_ATTEMPT)
            # remove top attempts
            if comp_bouldering_res[2][0] == 0:
                comp_bouldering_res[2][1] = 0
            # remove zone attempts
            if comp_bouldering_res[2][2] == 0:
                comp_bouldering_res[2][3] = 0
            # tabulation of bouldering results
            tops = sum([item[0] for item in comp_bouldering_res])
            zones = sum([item[2] for item in comp_bouldering_res])
            top_attempts = [item[1] for item in comp_bouldering_res]
            zone_attempts = [item[3] for item in comp_bouldering_res]
            bouldering_res.append((-tops, -zones, top_attempts, zone_attempts, comp))
        bouldering_res = sorted(bouldering_res)
        return bouldering_res


    def simulate_lead(self):
        """
        Simulating athletes moving up the lead wall, with a chance of slipping
        """
        # lead
        lead_res = []
        for comp in self.participants_info:
            comp_atts = self.participants_info[comp]['lead']
            holds = min(int(np.random.normal(comp_atts['skill'], comp_atts['std'])), self.LEAD_WALL_NUM_HOLDS)
            for hold in range(1, holds + 1):
                did_slip = random.random() < comp_atts['slip']
                if did_slip:
                    hold -= 1
                    break
            lead_res.append((-hold, comp))
        lead_res = sorted(lead_res)
        return lead_res