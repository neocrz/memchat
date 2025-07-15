
import logging
from .character_system import AICharacter
from .config import DEBUG_MODE 

if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class chat_agent:

    def __init__(self, character: AICharacter, chat_historic = None): # TODO: LLM provider interface for this; 
        self.character = character
        pass

    def run(): # TODO: Add message handling, historic logging (into json file); Call aux. Agents.
        while True:
            user_input = input("You: ")
            


def run():
    logger.info("Hello from memchat!")
    username = input("What is your name? ")
    logger.info(f"Hello, {username}!")
    char_path = input("Insert path of the character to load: ").strip("'\"")
    
    char = AICharacter.load_from_file(char_path)

    if char:
        logger.info(f"Character loaded: {char}")
    else:
        logger.error("Failed to load character.")

    context_block, first_message = char.get_initial_llm_message(username)
    logger.info(first_message)


if __name__ == "__main__":
    run()
