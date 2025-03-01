import random

def get_random_number():
    return random.randint(1, 5)


def get_funky_response(category):
    response_map = {
        "success": {
            1: "Boom! 💥 You crushed it like a trivia champion! 🏆",
            2: "Correct! 🕺 You’re on fire! 🔥",
            3: "Bam! 🎯 Nailed it like a pro!",
            4: "Whoa! 🚀 You answered faster than a cheetah on roller skates!",
            5: "Ding ding! 🛎️ Genius alert! You got it right! 🤓",
        },
        "failure": {
            1: "Oof! 🥲 That was close, but not quite! Try again?",
            2: "Oh no! 🚨 Incorrect! But don’t worry, you got another shot! 🔄",
            3: "Oopsie! 🙈 That’s not it. But hey, nobody’s perfect!",
            4: "Whomp whomp! 🎭 That’s wrong. One last try before the session ends!",
            5: "Game over! 🎮 You gave it your best shot! Want to try again?",
        },
        "game-over": {
            1: "Oops! Game over! Looks like the trivia gods weren’t on your side. Try again? 😵‍💫🎮",
            2: "Boom! You just hit the ‘Game Over’ zone. But hey, legends make comebacks! 🔥👾",
            3: "That’s a wrap! The scoreboard says NO, but your spirit says GO! 🚀💥",
            4: "Welp, that didn’t end well... but plot twist: you can always retry! 😜🔄",
            5: "Game over, but the fun never stops! Want to roll the dice again? 🎲😎"
        }
    }

    return response_map[category][get_random_number()]
