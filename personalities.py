expressions = {
    "instructor": {
        "eye color": "white"
    },
    "neutral": {
        "eye color": "white",
        "greeting": {
            "gesture": None,
            "speech": "Hello, my name is {self.name}! Let's play rock, paper, scissors."
        },
        "tie": {
            "rock-rock": {
                "speech": "It is a tie. Let’s play again.",
                "gesture": None
            },
            "1:1":  {
                "speech": "We have a draw. Get ready for the final round.",
                "gesture": None
            },
        },
        "intermediate result": {
            "NAO winning": {
                "gesture": None,
                "speech": "I won this round. Get ready for the next one.",
            },
            "player winning": {
                "gesture": None,
                "speech": "You won this round. Get ready for the next one."
            }
        },
        "game outcome": {
            "NAO wins": {
                "gesture": None,
                "speech": "I won the game."
            },
            "player wins": {
                "gesture": None,
                "speech": "You won the game"
            }
        },
        "goodbye": "Goodbye!"
    },
    "supportive1": {
            "eye color": "yellow",
            "greeting": {
                "gesture": "Hey_6",
                "speech": "Hi! I'm {self.name}. I hope you are having a good \\pau=100\\ day. "
                          "Let's play a fun game together."
            },
            "tie": {
                "rock-rock": {
                    "speech": "Wow, we have a tie! We both did a good job, let's go again.",
                    "gesture": None
                },
                "1:1":  {
                    "speech": "Impressive, it's a tie! Great effort from both of us. Ready for the next round?",
                    "gesture": None
                },
            },
            "intermediate result": {
                "NAO winning": {
                    "gesture": None,
                    "speech": "This round is mine, but you still have a chance to win.",
                },
                "player winning": {
                    "gesture": None,
                    "speech": "Congrats on this round! If you win the next round, this game is yours!"
                }
            },
            "game outcome": {
                "NAO wins": {
                    "gesture": "Explain_3",
                    "speech": "Great effort! Remember, every defeat is just a step towards a future victory."
                },
                "player wins": {
                    "gesture": "Explain_10",
                    "speech": "Congratulations! Your skills are truly impressive."
                }
            },
            "goodbye": "Goodbye for now! Stay positive and keep moving forward."
        },
    "supportive2": {
                "eye color": "yellow",
                "greeting": {
                    "gesture": "Hey_6",
                    "speech": "Hey, you! I am {self.name}! Ready for an awesome time?"
                },
                "tie": {
                    "rock-rock": {
                        "speech": "Haha, fun! We tied! Are you ready to win the next try?",
                        "gesture": None
                    },
                    "1:1":  {
                        "speech": "Fun times! We're even! I’m sure you’ll win the next round!",
                        "gesture": None
                    },
                },
                "intermediate result": {
                    "NAO winning": {
                        "gesture": None,
                        "speech": "Fantastic fight! I won for now, but your win is inevitable.",
                    },
                    "player winning": {
                        "gesture": None,
                        "speech": "You owned it! The next round is set for your win."
                    }
                },
                "game outcome": {
                    "NAO wins": {
                        "gesture": "Explain_11",
                        "speech": "You did great! Never give up, remember that, keep up the good energy!"
                    },
                    "player wins": {
                        "gesture": "Enthusiastic_5",
                        "speech": "Wow, wow, wow! Congratulations! I knew you would win!"
                    }
                },
                "goodbye": "Goodbye! Hopefully we'll meet again soon!"
            },
    "competitive1": {
                "eye color": "purple",
                "greeting": {
                    "gesture": "Hey_1",
                    "speech": "Hi there, I'm {self.name}. Get ready to be challenged."
                },
                "tie": {
                    "rock-rock": {
                        "speech": "A tie! Do you dare to try again?",
                        "gesture": None
                    },
                    "1:1":  {
                        "speech": "We've got a tie! Is that the best you've got?",
                        "gesture": None
                    },
                },
                "intermediate result": {
                    "NAO winning": {
                        "gesture": None,
                        "speech": "Victory is sweet, and I’ll repeat it in the next round.",
                    },
                    "player winning": {
                        "gesture": None,
                        "speech": "Well played. I'll give you this victory, "
                                  "but the next round will be a different story."
                    }
                },
                "game outcome": {
                    "NAO wins": {
                        "gesture": "YouKnowWhat_5",
                        "speech": "That was a solid victory for me! "
                                  "Don't feel too bad; not everyone can keep up with my level of skill."
                    },
                    "player wins": {
                        "gesture": "YouKnowWhat_1",
                        "speech": "Impressive! You managed to outsmart me this time. "
                                  "Don't get too comfortable, I'll be coming back stronger."
                    }
                },
                "goodbye": "Until we meet again!"
            },
    "competitive2": {
                    "eye color": "purple",
                    "greeting": {
                        "gesture": "Hey_1",
                        "speech": "Hey there, I'm {self.name}! Get ready for a fierce competition. "
                                  "Time to test your skills in a thrilling game."
                    },
                    "tie": {
                        "rock-rock": {
                            "speech": "We've got a tie! Let's try again and I will beat you!",
                            "gesture": None
                        },
                        "1:1":  {
                            "speech": "Well, look at that—a tie! Are you even trying? "
                                      "Ready for another round, or is that too much for you?",
                            "gesture": None
                        },
                    },
                    "intermediate result": {
                        "NAO winning": {
                            "gesture": None,
                            "speech": "This win was just the beginning. I'm ready to be the best once more.",
                        },
                        "player winning": {
                            "gesture": None,
                            "speech": "You got lucky this time. But I'll be ready to crush you in the next round!"
                        }
                    },
                    "game outcome": {
                        "NAO wins": {
                            "gesture": "Excited_1",
                            "speech": "Success is sweet! I'm just on a different level than you."
                        },
                        "player wins": {
                            "gesture": "Desperate_1",
                            "speech": "You won? No way! That must be a mistake! "
                        }
                    },
                    "goodbye": "Anyway, goodbye!"
                }
}

instructions = ("In this experiment, you'll play three games of rock-paper-scissors with my three friends. "
                "In each of the three games, the player who wins two times first wins. "
                "When a robot counts to three, show your choice to the robot using one of the three "
                "signs with colored circles: "
                "red for rock, blue for paper, and green for scissors. "
                "Place the sign in front of the robot's eyes.")
