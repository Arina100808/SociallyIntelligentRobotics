from sic_framework.devices import Nao
from sic_framework.devices.nao import NaoqiTextToSpeechRequest
from sic_framework.services.dialogflow.dialogflow import (DialogflowConf, GetIntentRequest, RecognitionResult,
                                                          QueryResult, Dialogflow)
from sic_framework.devices.common_desktop.desktop_microphone import DesktopMicrophone
from sic_framework.devices.common_naoqi.naoqi_leds import NaoLEDRequest, NaoFadeRGBRequest
from sic_framework.devices.nao import NaoqiAnimationRequest
from sic_framework.devices.common_naoqi.naoqi_motion_recorder import (NaoqiMotionRecording, StartRecording,
                                                                      StopRecording, PlayRecording,
                                                                      NaoqiMotionRecorderConf)
from signdetector import ColorDetector
from personalities import expressions, instructions
import random
import time
import json
import csv
import os

answer = ""
button_pressed = False


class Game:
    def __init__(self, n_game, rock_color="red", paper_color="blue",
                 scissors_color="green"):
        """
        Initialize a Game instance by specifying the game number, colors associated with each gesture (rock, paper,
        scissors), and defining rules and robot names based on their personalities.

        :param n_game: The number of the game.
        :param rock_color: The color associated with the rock gesture.
        :param paper_color: The color associated with the paper gesture.
        :param scissors_color: The color associated with the scissors gesture.
        """
        self.n_game = n_game
        # color to gesture translation
        self.gesture_color = {rock_color: "rock",
                              paper_color: "paper",
                              scissors_color: "scissors"}

        # combinations [winner, loser]
        self.rules = [["scissors", "paper"],
                      ["paper", "rock"],
                      ["rock", "scissors"]]

        self.robots = {"instructor": {"name": "NAO"},
                       "neutral": {"name": "Tyrael"},
                       "supportive1": {"name": "Deckard"},
                       "competitive1": {"name": "Zoltun"},
                       "supportive2": {"name": "Leopold"},
                       "competitive2": {"name": "Mephis"}}

    def print_output(self, output):
        """
        Print the output and write it to a txt file.

        :param output: The output to print and write to a file.
        """
        print(output)
        output_file_path = os.path.join("output", f"game_{self.n_game}.txt")
        file = open(output_file_path, 'a')
        file.write('\n' + output)
        file.close()

    def translate_color_to_gesture(self, color):
        """
        Translate a given color to a corresponding gesture.

        :param color: The color to be translated to a gesture.
        :return: The gesture associated with the given color.
        """
        return self.gesture_color.get(color)

    def get_winner(self, nao_choice, player_choice):
        """
        Determine the winner according to the game rules based on the choices of NAO and the player.

        :param nao_choice: The gesture chosen by NAO.
        :param player_choice: The gesture chosen by the player.
        :return: The winner of the round ("NAO", "player", or "No one").
        """
        winner = None
        if [nao_choice, player_choice] in self.rules:
            winner = "NAO"
        elif [player_choice, nao_choice] in self.rules:
            winner = "player"
        elif nao_choice == player_choice:
            winner = "No one"
        return winner

    def on_dialog(self, message):
        """
        Handle the dialog messages and update the global answer variable.

        :param message: The dialog message received.
        """
        global answer
        if message.response:
            if message.response.recognition_result.is_final:
                answer = message.response.recognition_result.transcript
                self.print_output(f"Transcript: {answer}")

    def button_func(self, a):
        """
        Handle the button press event and update the global button_pressed variable.

        :param a: The button press event.
        """
        global button_pressed
        self.print_output(f"Button pressed: {a.value}")
        button_pressed = True


class Robot:
    def __init__(self, ip, game, personality="neutral", name="NAO", mode="robot", use_mic=False, use_camera=True):
        """
        Initialize a Robot instance.

        :param ip: The IP address of the robot.
        :param game: The Game instance.
        :param personality: The personality of the robot.
        :param name: The name of the robot.
        :param mode: The mode in which the game is played ("robot" or "desktop").
        :param use_mic: Whether a microphone is used.
        :param use_camera: Whether a camera is used.
        """
        self.ip = ip
        self.game = game
        self.personality = personality
        self.name = name
        self.mode = mode
        self.use_mic = use_mic
        self.use_camera = use_camera
        sample_rate = 0
        connect = None
        if self.mode == "robot":
            self.nao = Nao(ip=self.ip)
            if self.use_camera:
                self.color_detector = ColorDetector(ip=self.ip)
            # button
            self.nao.buttons.register_callback(self.game.button_func)
            if self.use_mic:
                connect = self.nao.mic
                sample_rate = 16000
        elif self.mode == "desktop":
            if self.use_camera:
                self.color_detector = ColorDetector(ip=self.ip, use_pc_webcam=True)
            if self.use_mic:
                connect = DesktopMicrophone(ip='localhost')
                sample_rate = 44100
        if self.use_mic:
            json_file = "my-dialogflow.json"
            keyfile_json = json.load(open(json_file))
            conf = DialogflowConf(keyfile_json=keyfile_json, sample_rate_hertz=sample_rate, language='en')
            self.dialogflow = Dialogflow(ip='localhost', conf=conf)
            self.dialogflow.connect(connect)
            self.dialogflow.register_callback(self.game.on_dialog)

    def change_name(self, new_name):
        """
        Change the name of the robot.

        :param new_name: The new name for the robot.
        """
        self.name = new_name

    def change_personality(self, new_personality):
        """
        Change the personality of the robot.

        :param new_personality: The new personality for the robot.
        """
        self.personality = new_personality

    def say(self, speech, speed=90, block=True):
        """
        Make the robot say a speech with a specified speed if mode is set to "robot". Otherwise, just print the speech.

        :param speech: The speech for the robot.
        :param speed: The speed at which the robot should speak.
        :param block: Whether to block until the speech is finished.
        """
        self.game.print_output(f"- {speech}")
        if self.mode == "robot":
            self.nao.tts.request(NaoqiTextToSpeechRequest(f"\\rspd={speed}\\" + speech), block=block)

    def recognize_speech(self, expected, use_mic, time_limit=8, speech_button=""):
        """
        Recognize speech from the user or a button press. If the microphone is used, the method employs Dialogflow for
        speech recognition. Otherwise, it waits for the user to type the answer using the keyboard or to press NAO's
        button. If NAO doesn't receive an answer from the list of *expected* answers after 2 attempts, the game
        continues automatically. If NAO doesn't receive any answer within the *time_limit* seconds, it repeats its
        speech asking for an action.

        :param expected: List of expected speech inputs.
        :param use_mic: Whether to use the microphone for speech recognition.
        :param time_limit: The time limit for speech recognition.
        :param speech_button: The speech to prompt the user for a button press.
        :return: The recognized speech.
        """
        global button_pressed
        global answer
        answer = ""
        attempts = 0
        max_attempts = 2
        self.game.print_output(f"*** NAO is listening, expected input: '{expected[0]}' "
                               f"or button press (waiting for {time_limit} seconds) ***")

        if use_mic:
            if expected[0] == "yes":
                self.say("Are you ready to start the game?")
            while answer not in expected and attempts < max_attempts:
                self.dialogflow.request(GetIntentRequest())
                attempts += 1
        elif not use_mic and self.mode == "desktop":
            if self.use_camera:
                time.sleep(3)
                self.say("Ok, let's continue")
                answer = expected[0]
            else:
                if expected[0] == "yes":
                    self.say("Are you ready to start the game?")
                while answer not in expected and attempts < max_attempts:
                    answer = input()
                    attempts += 1

        if answer not in expected:
            if self.mode == "robot":
                self.say(speech_button)
                self.say("Press the black button on one of my feet.")
                button_pressed = False
                start_time = time.time()
                while button_pressed is False:
                    answer = ""
                    if time.time() - start_time >= time_limit:
                        # Timeout occurred
                        answer = expected[1]
                        return answer
                answer = expected[0]
            else:
                self.say("Ok, let's continue")
                answer = expected[0]

        return answer

    def show_gesture(self, gesture, block=False):
        """
        Display a gesture using motion or animation based on the robot's mode.

        :param gesture: The gesture to display. It can be one of the predefined gestures ("rock", "paper", "scissors")
        or a custom gesture with the format "animations/Stand/Gestures/gesture", for example, "Hey_1". (refer to
        http://doc.aldebaran.com/2-5/naoqi/motion/alanimationplayer-advanced.html for available tags).
        :param block: Whether to block until the gesture is finished.
        """
        self.game.print_output(f"*** NAO is showing {gesture} ***")
        if self.mode == "robot":
            if gesture == "rock":
                recording = NaoqiMotionRecording.load("recorded_motions/rock2.motion")
                self.nao.motion_record.request(PlayRecording(recording), block=block)
            elif gesture == "paper":
                recording = NaoqiMotionRecording.load("recorded_motions/paper2.motion")
                self.nao.motion_record.request(PlayRecording(recording), block=block)
            elif gesture == "scissors":
                recording = NaoqiMotionRecording.load("recorded_motions/scissors2.motion")
                self.nao.motion_record.request(PlayRecording(recording), block=block)
            else:
                self.nao.motion.request(NaoqiAnimationRequest(f"animations/Stand/Gestures/{gesture}"), block=block)
                if gesture == "Hey_1":
                    self.change_eye_color(expressions[self.personality]["eye color"])

    def change_eye_color(self, color):
        """
        Change the color of NAO's eyes based on the specified color.

        :param color: The desired eye color. Supported colors: "red", "green", "blue", "yellow", "purple". For all other
        values, the color is set to the default white.
        """
        self.game.print_output(f"*** NAO's eyes turned {color} ***")
        if self.mode == "robot":
            if color in ["red", "green", "blue"]:
                colors = [int((color == "red")), int((color == "green")), int((color == "blue"))]
            elif color == "yellow":
                colors = [255, 239, 0]
            elif color == "purple":
                colors = [120, 0, 225]
            else:  # white
                colors = [255, 255, 255]
            self.nao.leds.request(NaoLEDRequest("FaceLeds", True))
            self.nao.leds.request(NaoFadeRGBRequest("FaceLeds", colors[0], colors[1], colors[2], 0))

    def recognize_player_color(self):
        """
        Recognize the color shown to the camera or typed by the user.

        :return: The recognized color ("red", "green", or "blue").
        """
        recognized_color = None
        if not self.use_camera:
            recognized_color = self.recognize_speech(expected=list(self.game.gesture_color.keys()),
                                                     use_mic=False)
        else:
            print("Recognizing color...")
            while recognized_color is None:
                recognized_color = self.color_detector.detect_sign()
                if recognized_color is None:
                    self.say("Sorry, I didn't catch which sign you're showing. "
                             "Could you please show it to me again?")
                else:
                    print(f"Recognized {recognized_color} color")
        return recognized_color

    def personal_greeting(self):
        """
        Output a personalized greeting based on the robot's personality.
        """
        greeting = expressions[self.personality]["greeting"]
        gesture = greeting["gesture"]
        speech = greeting["speech"].format(self=self)
        if gesture is not None:
            self.show_gesture(gesture, block=False)
        self.say(speech, block=True)

    def personal_goodbye(self):
        """
        Output a personalized goodbye based on the robot's personality.
        """
        self.say(expressions[self.personality]["goodbye"])

    def personal_reaction_intermediate(self, NAO_wins, player_wins):
        """
        Output a personalized reaction based on intermediate game results.

        :param NAO_wins: The number of wins by NAO.
        :param player_wins: The number of wins by the player.
        """
        reaction = {}
        self.game.print_output(f"*** NAO's {self.personality} reaction ***")
        exp = expressions[self.personality]
        if NAO_wins > player_wins:
            self.say("One, zero in my favor!")
            reaction = exp["intermediate result"]["NAO winning"]
        elif NAO_wins < player_wins:
            self.say("One, zero in your favor!")
            reaction = exp["intermediate result"]["player winning"]
        elif NAO_wins == player_wins:
            self.say("One, one!")
            reaction = exp["tie"]["1:1"]
        gesture = reaction["gesture"]
        speech = reaction["speech"]
        if gesture is not None:
            self.show_gesture(gesture)
        self.say(speech)

    def personal_tie(self):
        """
        Output a personalized reaction in the event of a tie (when both user and robot chooses the same color/gesture).
        """
        reaction = expressions[self.personality]["tie"]["rock-rock"]
        gesture = reaction["gesture"]
        speech = reaction["speech"]
        if gesture is not None:
            self.show_gesture(gesture)
        self.say(speech)

    def personal_reaction_outcome(self, NAO_wins, player_wins):
        """
        Output a personalized reaction based on the final game outcome.

        :param NAO_wins: The total number of wins by NAO.
        :param player_wins: The total number of wins by the player.
        :return: The gesture and winner of the game.
        """
        reaction = {}
        winner = ""
        if NAO_wins == 2:
            winner = "NAO"
            self.say(f"Two, {player_wins} in my favor!")
            reaction = expressions[self.personality]["game outcome"]["NAO wins"]
        elif player_wins == 2:
            winner = "player"
            self.say(f"Two, {NAO_wins} in your favor!")
            reaction = expressions[self.personality]["game outcome"]["player wins"]
        gesture = reaction["gesture"]
        speech = reaction["speech"]
        if gesture is not None:
            self.show_gesture(gesture)
        self.say(speech)
        return gesture, winner

    def play_game(self):
        """
        Play a single game and return the result. The game consists of playing with a robot until one side achieves 2
        wins, resulting in a maximum of 3 rounds. The first to win 2 rounds wins the entire game. In case the robot and
        user choose the same gesture, they choose their gestures again.

        :return: A dictionary containing the game result.
        """
        self.game.print_output(f"------- {self.personality} personality -------")
        personality_eye_color = expressions[self.personality]["eye color"]
        result = {'name': self.name,
                  'eye_color': personality_eye_color,
                  'hello_gesture': expressions[self.personality]["greeting"]["gesture"],
                  'ties_rock_rock': 0,
                  'tie_1_1': 0,
                  'NAO_1_0': 0,
                  '0_1_player': 0,
                  'NAO_wins': 0,
                  'player_wins': 0,
                  'outcome_gesture': None,
                  'winner': ""}
        self.change_eye_color(personality_eye_color)
        self.personal_greeting()
        self.change_eye_color(personality_eye_color)
        start = "no"
        while start != "yes":
            start = self.recognize_speech(["yes", "no"], use_mic=self.use_mic,
                                          time_limit=8,
                                          speech_button="To start the game,")
        NAO_wins = 0
        player_wins = 0
        while NAO_wins < 2 and player_wins < 2:
            winner_defined = False
            while not winner_defined:
                self.say("On the count of three...")
                nao_color = random.choice(list(self.game.gesture_color.keys()))
                nao_choice = self.game.translate_color_to_gesture(nao_color)
                self.say("Ready?")
                self.show_gesture(nao_choice, block=False)
                self.say("One, two, three!", speed=85)
                self.change_eye_color(nao_color)
                player_color = self.recognize_player_color()
                player_choice = self.game.translate_color_to_gesture(player_color)
                time.sleep(1)
                self.say(f"I chose {nao_choice}, and you chose {player_choice}!")
                winner = self.game.get_winner(nao_choice, player_choice)
                self.game.print_output(f"NAO: {nao_color}/{nao_choice}\tPLAYER: {player_color}/{player_choice}")
                self.game.print_output(f"{winner} won")
                time.sleep(1)
                self.change_eye_color(personality_eye_color)
                if winner == "NAO":
                    winner_defined = True
                    NAO_wins += 1
                elif winner == "player":
                    winner_defined = True
                    player_wins += 1
                elif winner == "No one":
                    result["ties_rock_rock"] += 1
                    self.personal_tie()
            if NAO_wins < 2 and player_wins < 2:
                result["tie_1_1"] += int(NAO_wins == player_wins)
                result["NAO_1_0"] += int(NAO_wins > player_wins)
                result["0_1_player"] += int(NAO_wins < player_wins)
                self.personal_reaction_intermediate(NAO_wins, player_wins)
        outcome_gesture, final_winner = self.personal_reaction_outcome(NAO_wins, player_wins)
        result["NAO_wins"] = NAO_wins
        result["player_wins"] = player_wins
        result["outcome_gesture"] = outcome_gesture
        result["winner"] = final_winner
        self.personal_goodbye()
        # change eye color back to the default white color
        self.change_eye_color("white")
        self.show_gesture("BowShort_1")
        return result

    def play_3_personalities(self, combination, say_instructions=True):
        """
        Conduct an experiment where the user plays a sequence of games with different robot personalities. The
        instructor robot explains the rules initially. After playing with each personality, the results are stored in a
        CSV file, and the instructor robot prompts the user to complete a short survey, waiting for a button press after
        completion. After playing with all three personalities, the user is asked to complete the final questionnaire.

        :param combination: The combination of personalities to play.
        :param say_instructions: Whether to say instructions at the beginning of the experiment.
        :return: A dictionary containing the results for each personality.
        """
        self.change_eye_color("white")
        self.say(f"Hello, I'm {self.name}! Welcome to the experiment.")
        ready = "repeat"
        final_result = {}
        while ready != "ready":
            if say_instructions:
                self.say(instructions)
            ready = self.recognize_speech(["ready", "repeat"], use_mic=False, time_limit=8,
                                          speech_button="If you understand the rules and are "
                                                        "ready to begin the experiment,")
        for i, personality in enumerate(combination):
            self.change_personality(personality)
            self.change_name(self.game.robots[personality]["name"])
            result = self.play_game()
            final_result[personality] = result

            personality_result = [self.game.n_game] + [personality] + list(result.values())
            with open('results.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(personality_result)

            if i + 1 < len(combination):
                self.say("Now, please take a short survey about your gaming experience with my friend.")
                next_robot = "wait"
                while next_robot != "next":
                    next_robot = self.recognize_speech(["next", "wait"], use_mic=False, time_limit=300,
                                                       speech_button="After completing the survey, "
                                                                     "to play with the next robot,")
        self.say("Now, similarly, please take a survey about your gaming experience with my friend and "
                 "thank you for participating in our experiment! "
                 "After this survey, please also complete the final questionnaire. "
                 "Your feedback is valuable to us!")

        return final_result
