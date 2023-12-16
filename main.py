from sic_framework.services.dialogflow.dialogflow import RecognitionResult, QueryResult
from game import Game, Robot
from itertools import product
from random import shuffle
import csv
import os


def create_or_check_csv(csv_file: str):
    """
    Create a CSV file to store the results of experiments if it does not already exist.

    :param csv_file: Name of the CSV file in "file_name.csv" format.
    """
    if not os.path.isfile(csv_file):
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['subject', 'personality', 'name', 'eye_color', 'hello_gesture', 'ties_rock_rock',
                             'tie_1_1', 'NAO_1_0', '0_1_player', 'NAO_wins', 'player_wins', 'outcome_gesture',
                             'winner'])


def run_experiment(mode: str, nao: str, use_mic=False, use_camera=False):
    """
    Runs the experiment for one participant. Each participant plays with one of the 4 combinations of robot
    personalities, resulting in a game with 3 robots featuring different personalities (neutral, supportive,
    competitive) in random order.

    :param mode: Either "desktop" or "robot".
    :param nao: The IP address of the NAO robot.
    :param use_mic: Use the (NAO or desktop) microphone. If True, say "yes" to start the game. If False and mode is set
    to "robot", NAO's button is pressed to start the game. If False and mode is set to "desktop", type "yes" to start
    the game (if use_camera is False) or the game will start automatically in 3 seconds (if use_camera is True).
    :param use_camera: Use the (NAO or desktop) camera. If True, show one of the colored signs to the camera. If False,
    type the color using the keyboard.
    """
    # 2 options for supportive, 2 for competitive robot
    supportive = [f"supportive{s + 1}" for s in range(2)]
    competitive = [f"competitive{s + 1}" for s in range(2)]
    prod = list(product(supportive, competitive))
    combinations = [["neutral"] + list(comb) for comb in prod]

    csv_file = 'results.csv'
    create_or_check_csv(csv_file)
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        existing_subjects = set(int(row[0]) for row in reader)

    # get the participant's ordinal number
    max_subject = max(existing_subjects, default=0)
    subject = max_subject + 1

    # get the ordinal number of a combination; each combination will be played,
    # and the number of repetitions of each combination will be (almost) equal
    n_combination = max_subject % 4
    combination = combinations[n_combination]

    shuffle(combination)

    # create the "output" folder if it doesn't exist
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    rock_paper_scissors_game = Game(n_game=subject)

    robot = Robot(ip=nao,
                  game=rock_paper_scissors_game,
                  mode=mode,
                  use_mic=use_mic,
                  use_camera=use_camera)
    result = robot.play_3_personalities(combination, say_instructions=True)

    rock_paper_scissors_game.print_output(f"Final results for game №{subject}:")
    for personality in list(result.keys()):
        rock_paper_scissors_game.print_output(f"--- Personality: {personality} ---")
        for key in result[personality].keys():
            rock_paper_scissors_game.print_output(f"{key}: {result[personality][key]}")


if __name__ == '__main__':
    run_experiment(mode="robot", nao="10.0.0.91", use_mic=False, use_camera=True)
