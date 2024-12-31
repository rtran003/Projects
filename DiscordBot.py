import discord
import random
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
from discord.ext import commands
import requests
import asyncio
import re

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Random Responses
responses = ["yurrr", "hell yeah G", "damnn rightt"]

# Key word to trigger responses
keywords = ["right, eric?", "right eric?", "right eric"]

# Dictionary to store the user's image for session
user_images = {}

# A dictionary to store the choices of users
game_sessions = {}

# Dictionary to store phrases
stored_phrases = {}


# List of words for the game (you can replace this with an API if needed)
words = [
    "apple", "banana", "grape", "orange", "cherry", "mango", "kiwi", "strawberry", "blueberry", "pineapple"
]

@bot.event
async def on_ready():
    print("Bot is active!")

@bot.command()
async def hello(ctx):
    await ctx.send(f"What up G {ctx.author.mention}!")

@bot.event
async def on_message(message):
    # Prevents the bot from responding to itself
    if message.author.bot:
        return

    # Detect the pattern "____ is _____, _____, and/or _____"
    pattern = r'(\w+) is ([\w\s,]+?)(?:, (and/or) (\w+))?$'
    match = re.search(pattern, message.content)

    if match:
        subject = match.group(1)
        descriptors = [desc.strip() for desc in match.group(2).split(',')]  # Split by comma and clean up spaces

        # If "and/or" exists, append it with the next word
        if match.group(3) and match.group(4):
            descriptors.append(f"and/or {match.group(4).strip()}")
        
        response = f"Yeah, {subject} is {', '.join(descriptors)}."
        
        # Store the subject and descriptors in the dictionary
        stored_phrases[subject.lower()] = descriptors
        
        await message.channel.send(response)

    # Check if any keywords are mentioned
    for keyword in keywords:
        if keyword in message.content.lower():
            await message.channel.send(random.choice(responses))
            break  # Exits the loop

    # Allow other commands to be processed
    await bot.process_commands(message)


# Check if the word 'fuwamoco' is mentioned in the message
@bot.event
async def on_message(message):
    # Prevents the bot from responding to itself
    if message.author.bot:
        return

    # Check if the word 'fuwamoco' is mentioned in the message
    if "fuwamoco" in message.content.lower():
        await message.channel.send("BAU BAU!!")

    # Check if there are any keywords
    for keyword in keywords:
        if keyword in message.content.lower():  # Fixed typo here
            await message.channel.send(random.choice(responses))
            break  # Exits the loop

    # Allow other commands to be processed
    await bot.process_commands(message)

@bot.command()
async def recall(ctx, subject: str):
    """Recall previously stored descriptions for a subject."""
    subject = subject.lower()
    if subject in stored_phrases:
        descriptors = ", ".join(stored_phrases[subject])
        await ctx.send(f"{subject.capitalize()} is {descriptors}.")
    else:
        await ctx.send(f"I don't have any record of {subject}.")

# Checks users ping
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    if latency < 50:
        message = "lightning fast! ⚡"
    elif latency < 150:
        message = "Pretty good! 🏎️"
    elif latency < 300:
        message = "Erm not bad 📡"
    else:
        message = "ERM, you might need to check your internet"

    await ctx.send(f"Pong! Your ping is {latency}ms. {message}")


#Frys image
@bot.command()
async def fry(ctx):
    # Check if an image is attached
    if not ctx.message.attachments:
        await ctx.send("Please attach an image for me to fry! 🔥")
        return

    # Get the first attachment
    attachment = ctx.message.attachments[0]
    if not attachment.content_type.startswith("image/"):
        await ctx.send("That doesn't look like an image! Please attach a valid image file. 📷")
        return

    # Download the image
    img_data = await attachment.read()
    with Image.open(io.BytesIO(img_data)) as img:
        # Apply frying effects and distortion
        img = fry_image(img)

        # Save the modified image to the user's session
        user_images[ctx.author.id] = img
        
        # Send the fried image
        await send_fried_image(ctx, img)


#Frys image again
@bot.command()
async def fryagain(ctx):
    # Check if user has already uploaded an image
    if ctx.author.id not in user_images:
        await ctx.send("You need to upload an image first using !fry.")
        return

    # Get the current image
    img = user_images[ctx.author.id]

    # Apply the frying effect again
    img = fry_image(img)

    # Send the fried image
    await send_fried_image(ctx, img)

def fry_image(img):
    """Apply frying effects and distortion to the image"""
    img = img.convert("RGB")

    # Apply some distortions
    img = distort_image(img)

    # Apply frying effects
    img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(1, 3)))  # Add blur
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(2, 4))  # Enhance contrast
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(random.uniform(1.5, 3))  # Boost saturation
    img = img.rotate(random.randint(-15, 15))  # Random slight rotation

    return img

def distort_image(img):
    """Apply some random distortion effects to the image"""
    distortion_type = random.choice(["pixelate", "stretch", "mirror"])

    if distortion_type == "pixelate":
        img = pixelate_image(img)
    elif distortion_type == "stretch":
        img = stretch_image(img)
    elif distortion_type == "mirror":
        img = mirror_image(img)

    return img

def pixelate_image(img, pixel_size=10):
    """Pixelate the image"""
    width, height = img.size
    img = img.resize((width // pixel_size, height // pixel_size), resample=Image.NEAREST)
    img = img.resize((width, height), resample=Image.NEAREST)
    return img

def stretch_image(img):
    """Apply random stretching to the image"""
    width, height = img.size
    stretch_factor = random.uniform(0.7, 1.3)
    new_width = int(width * stretch_factor)
    new_height = int(height * stretch_factor)
    img = img.resize((new_width, new_height), resample=Image.BICUBIC)
    return img

def mirror_image(img):
    """Apply a mirror distortion to the image"""
    img = ImageOps.mirror(img)
    return img

async def send_fried_image(ctx, img):
    """Send the fried image back to the user"""
    with io.BytesIO() as output:
        img.save(output, format="JPEG")
        output.seek(0)
        await ctx.send("Here's your fried image with distortion! 🔥", file=discord.File(fp=output, filename="fried_image.jpg"))



#Magic 8 ball
@bot.command()
async def magic8ball(ctx, *, question: str):
    """Magic 8 Ball command that answers a yes/no question."""
    # Ensure the user asks a proper question
    if not question.endswith('?'):
        await ctx.send("Please ask a proper question ending with a '?'.")
        return

    # List of possible answers
    answers = [
        "Yes, definitely.",
        "No, not at all.",
        "Maybe, try again later.",
        "I wouldn't count on it.",
        "Absolutely!",
        "It is certain.",
        "Outlook not so good.",
        "Cannot predict now.",
        "Yes, but you must wait.",
        "Don't count on it."
    ]

    # Choose a random answer
    response = random.choice(answers)

    # Send the response
    await ctx.send(f"Question: {question}\nAnswer: {response}")


#Clear messages
@bot.command()
async def clear(ctx, amount: int):
    """Clear messages in a channel. Only admins/mods can use this command."""
    
    # Check if the user has the admin or mod role
    if not any(role.name.lower() in ["admin", "moderator"] for role in ctx.author.roles) and not ctx.author.guild_permissions.administrator:
        await ctx.send("You don't have the required permissions to clear messages.")
        return
    
    # Ensure the amount is a valid number
    if amount <= 0:
        await ctx.send("Please provide a number greater than 0.")
        return
    
    # Limit the number of messages to 100 (Discord API limit)
    if amount > 100:
        amount = 100
    
    # Clear messages
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"Successfully deleted {amount} messages!", delete_after=5)  # Sends a success message and deletes it after 5 seconds.


#Guess the word
@bot.command(name="guessword")
async def guessword(ctx):
    """Start a new 'Guess the Word' game."""
    # Randomly select a word
    word = random.choice(words)
    word_display = "_" * len(word)
    
    # Store the game session for the user
    game_sessions[ctx.author.id] = {
        "word": word,
        "word_display": word_display,
        "attempts": 6,  # Allow 6 incorrect guesses
        "guessed_letters": set()
    }

    # Send a message with the blank word and attempts
    await ctx.send(f"Let's play 'Guess the Word'! The word is {len(word)} letters long.\nGuess a letter!")
    await ctx.send(f"Word: {word_display}\nAttempts left: 6")


#Users make a guess
@bot.command(name="guess")
async def guess(ctx, letter: str):
    """Make a guess by guessing a letter."""
    user_id = ctx.author.id
    
    # Check if the user is in an active game session
    if user_id not in game_sessions:
        await ctx.send("You are not currently in a game. Type !guessword to start a new game!")
        return

    # Get the current game session
    game = game_sessions[user_id]

    # Ensure the letter is a single character and a letter
    if len(letter) != 1 or not letter.isalpha():
        await ctx.send("Please guess a single letter.")
        return

    # Check if the letter has already been guessed
    if letter in game["guessed_letters"]:
        await ctx.send(f"You already guessed the letter '{letter}'. Try a different one!")
        return

    # Add the guessed letter to the set of guessed letters
    game["guessed_letters"].add(letter)

    # Check if the guessed letter is in the word
    if letter in game["word"]:
        # Update the word display with the correct letter
        game["word_display"] = "".join(
            [letter if game["word"][i] == letter else game["word_display"][i] for i in range(len(game["word"]))]
        )
        await ctx.send(f"Good guess! Word: {game['word_display']}")
    else:
        # Deduct an attempt for incorrect guesses
        game["attempts"] -= 1
        await ctx.send(f"Incorrect guess! You have {game['attempts']} attempts left.")

    # Check if the user has guessed the word
    if game["word_display"] == game["word"]:
        await ctx.send(f"Congratulations! You guessed the word: {game['word']}")
        del game_sessions[user_id]  # End the game

    # Check if the user has run out of attempts
    if game["attempts"] <= 0:
        await ctx.send(f"Game over! The word was: {game['word']}")
        del game_sessions[user_id]  # End the game


#Rock paper scissors
@bot.command(name="rps")
async def rps(ctx, opponent: discord.User):
    """Play Rock, Paper, Scissors with another user."""
    
    # Ensure the opponent is not the same person
    if opponent.id == ctx.author.id:
        await ctx.send("You can't play against yourself! Choose another opponent.")
        return

    # Check if the users are already in a game
    if opponent.id in game_sessions or ctx.author.id in game_sessions:
        await ctx.send(f"One of you is already in a game. Please finish the current game first.")
        return
    
    # Start the game and store both players' choices
    game_sessions[ctx.author.id] = {"opponent": opponent.id, "choice": None}
    game_sessions[opponent.id] = {"opponent": ctx.author.id, "choice": None}

    await ctx.send(f"Rock, Paper, Scissors! {ctx.author.mention} vs {opponent.mention}. Please choose your move: `rock`, `paper`, or `scissors`.")

    # Function to check for valid input
    def check(message):
        return message.author.id in [ctx.author.id, opponent.id] and message.content.lower() in ["rock", "paper", "scissors"]

    try:
        # Collect both players' choices
        user_choice = await bot.wait_for('message', check=check, timeout=30)
        game_sessions[user_choice.author.id]["choice"] = user_choice.content.lower()
        await user_choice.channel.send(f"{user_choice.author.mention} has chosen {user_choice.content.lower()}!")

        # Get the opponent's choice
        other_user_id = game_sessions[user_choice.author.id]["opponent"]
        other_user_choice = await bot.wait_for('message', check=check, timeout=30)
        game_sessions[other_user_choice.author.id]["choice"] = other_user_choice.content.lower()
        await other_user_choice.channel.send(f"{other_user_choice.author.mention} has chosen {other_user_choice.content.lower()}!")

        # Determine the winner
        result = determine_winner(game_sessions[ctx.author.id]["choice"], game_sessions[opponent.id]["choice"])
        if result == 0:
            await ctx.send("It's a tie!")
        elif result == 1:
            await ctx.send(f"{ctx.author.mention} wins! 🎉")
        else:
            await ctx.send(f"{opponent.mention} wins! 🎉")

    except asyncio.TimeoutError:
        await ctx.send("Game over! One of the players took too long to choose.")
    
    finally:
        # Clean up the game session
        game_sessions.pop(ctx.author.id, None)
        game_sessions.pop(opponent.id, None)

def determine_winner(choice1, choice2):
    """Determine the winner of the game."""
    if choice1 == choice2:
        return 0  # Draw
    if (choice1 == "rock" and choice2 == "scissors") or (choice1 == "scissors" and choice2 == "paper") or (choice1 == "paper" and choice2 == "rock"):
        return 1  # Player 1 wins
    return -1  # Player 2 wins


#Get help
@bot.command(name="customhelp")
async def custom_help(ctx):
    """List all available commands with descriptions."""
    
    command_list = {
        "!hello": "Sends a greeting message.",
        "!ping": "Displays the users latency.",
        "!fry": "Fry an image (attach an image to fry).",
        "!fryagain": "Fry the image again if you already fried one.",
        "!rps": "Start a Rock Paper Scissors game with another user.",
        "!magic8ball": "Ask the Magic 8 Ball a yes/no question.",
        "!guessword": "Start a Guess the Word game.",
        "!guess": "Guess a letter in the current word game.",
        "!clear": "Clear a specified number of messages (admins/mods only)."
    }
    
    help_message = "Here are all the commands you can use:\n\n"
    
    for command, description in command_list.items():
        help_message += f"**{command}** - {description}\n"
    
    await ctx.send(help_message)

bot.run("")
