
import logging
from .character_system import AICharacter
from .config import DEBUG_MODE 

if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class chat_agent:

    def __init__(self, character: AICharacter): # TODO: LLM provider interface for this
        self.character = character
        pass

    def run():
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

    first_message = char.get_initial_llm_message(username)
    logger.debug(first_message)


if __name__ == "__main__":
    run()
