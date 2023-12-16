# Group-22

## Rock-Paper-Scissors Robot Experiment
The Rock-Paper-Scissors Robot Experiment is an interactive project where users engage in a series of games with different robot personalities. The game involves playing rock, paper, scissors with various robot characters, each exhibiting distinct personalities such as neutral, supportive, and competitive.

To interact with the robot, participants use signs with bright colors: red for rock, blue for paper, and green for scissors.

The goal of running the experiment is to investigate how users perceive and distinguish between variations of competitive and supportive robot personalities, and how clear is the distinction, in the context of human-robot interaction during gameplay.

## Usage
To run the experiment for one participant:

1. Clone the repository:
```
git clone https://bitbucket.org/socialroboticshub/framework.git
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. In the **framework** folder, run the Redis server:
```
redis-server conf/redis/redis.conf
```
* Using NAO:

  * In **main.py**:
    * Set _mode_ to _"robot"_;
    * Set _nao_ to NAO’s IP address.
  * Run the command:
      ```
      python main.py
      ```
* Using Desktop:
  * In **main.py**:
    * Set _mode_ to _"desktop"_.
  * If you want to use the desktop microphone:
    ```
    python framework/sic_framework/services/dialogflow/dialogflow.py
    ```
    ```
    python framework/sic_framework/devices/common_desktop/desktop_microphone.py
    ```
  * If you want to use the desktop camera:
    ```
    python framework/sic_framework/devices/desktop.py
    ```
## Project Modules
### main.py
* Allows the user to configure the experiment by specifying the _mode_ (_"desktop"_ or _"robot"_), NAO's IP address, and microphone/camera usage.
* Utilizes four combinations of robot personalities, including neutral, supportive (2 versions), and competitive (2 versions).
### game.py
* Implements a rock-paper-scissors game with a NAO robot.
* Defines the rules of the game and gesture-color association.
* Handles the interaction between robot and human.
* Defines the algorithms of the game and the experiment.
* Logs game results to text and CSV files.
### personalities.py
* Defines eye color, speech, and gesture for each robot personality depending on the intermediate outcome of the game, final outcome, greeting, and goodbye.
* Defines the instructions for the experiment.
### signdetector.py
* Handles color detection necessary for a robot to understand the color chosen by a user and associate it with a rock-paper-scissors gesture.
* Detects red, green, or blue signs in the form of a circle.
### Recorded Motions
**rock2.motion**, **paper2.motion**, and **scissors2.motion** from the **recorded_motions** folder are used by NAO to show rock-paper-scissors gestures.