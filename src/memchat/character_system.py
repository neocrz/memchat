import json
import base64
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
from typing import List, Dict, Any, Optional
import os
import time
import random
import logging

logger = logging.getLogger(__name__)


def _extract_json_from_png(image_path: str) -> Optional[Dict[str, Any]]:
    logger.debug(f"Attempting to extract JSON from PNG: {image_path}")
    try:
        img = Image.open(image_path)
        character_data_str = None

        logger.debug(f"Image info: {img.info}")

        if hasattr(img, 'text') and isinstance(img.text, dict) and 'chara' in img.text:
            logger.debug("Found 'chara' in img.text")
            encoded_data = img.text['chara']
            try:
                decoded_data_bytes = base64.b64decode(encoded_data)
                character_data_str = decoded_data_bytes.decode('utf-8')
                logger.debug("Successfully decoded 'chara' from img.text (base64)")
            except Exception as e:
                logger.debug(f"Error decoding 'chara' from img.text (base64): {e}")
                if isinstance(encoded_data, str):
                    try:
                        json.loads(encoded_data)
                        character_data_str = encoded_data
                        logger.debug("Successfully loaded 'chara' from img.text (direct JSON)")
                    except json.JSONDecodeError:
                        logger.debug("'chara' in img.text is not valid direct JSON.")
                        pass
        
        if not character_data_str and img.info and "chara" in img.info:
            logger.debug("Found 'chara' in img.info")
            encoded_data = img.info["chara"]
            try:
                decoded_data_bytes = base64.b64decode(encoded_data)
                character_data_str = decoded_data_bytes.decode('utf-8')
                logger.debug("Successfully decoded 'chara' from img.info (base64)")
            except Exception as e:
                logger.debug(f"Error decoding 'chara' from img.info (base64): {e}")
                if isinstance(encoded_data, str):
                    try:
                        json.loads(encoded_data)
                        character_data_str = encoded_data
                        logger.debug("Successfully loaded 'chara' from img.info (direct JSON)")
                    except json.JSONDecodeError:
                        logger.debug("'chara' in img.info is not valid direct JSON.")
                        pass

        if not character_data_str and hasattr(img, 'text') and isinstance(img.text, dict):
            logger.debug("Checking other keys in img.text for JSON data.")
            for key, value in img.text.items():
                if key == 'chara': continue
                if isinstance(value, str):
                    try:
                        decoded_bytes = base64.b64decode(value)
                        json.loads(decoded_bytes.decode('utf-8'))
                        character_data_str = decoded_bytes.decode('utf-8')
                        logger.debug(f"Found and decoded JSON from img.text key '{key}' (base64)")
                        break
                    except Exception:
                        try:
                            json.loads(value)
                            character_data_str = value
                            logger.debug(f"Found and loaded JSON from img.text key '{key}' (direct JSON)")
                            break
                        except json.JSONDecodeError:
                            continue
                if character_data_str:
                    break

        if character_data_str:
            logger.debug("Character data string found. Attempting JSON parse.")
            try:
                parsed_data = json.loads(character_data_str)
                logger.debug("Successfully parsed JSON data.")
                return parsed_data
            except json.JSONDecodeError as e:
                logger.debug(f"JSONDecodeError: Could not parse character data string: {e}")
                return None
        else:
            logger.debug("No character data string found in PNG.")
            return None

    except FileNotFoundError:
        logger.error(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing PNG '{image_path}': {e}")
        return None


class AICharacter:
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.first_mes: str = ""
        self.personality: str = ""
        self.scenario: str = ""
        self.mes_example: str = ""
        self.spec: str = "chara_card_v2"
        self.spec_version: str = "2.0"
        self.data_name: str = ""
        self.data_description: str = ""
        self.data_first_mes: str = ""
        self.data_alternate_greetings: List[str] = []
        self.data_personality: str = ""
        self.data_scenario: str = ""
        self.data_mes_example: str = ""
        self.data_creator: str = ""
        self.data_extensions_talkativeness: str = "0.5"
        self.data_extensions_depth_prompt_prompt: str = ""
        self.data_extensions_depth_prompt_depth: str = "0"
        self.data_system_prompt: str = ""
        self.data_post_history_instructions: str = ""
        self.data_creator_notes: str = ""
        self.data_character_version: str = "0.1"
        self.data_tags: List[str] = []
        self.alt_name: str = ""
        self.alt_description: str = ""
        self.alt_first_mes: str = ""
        self.alt_alternate_greetings: List[str] = []
        self.alt_personality: str = ""
        self.alt_scenario: str = ""
        self.alt_mes_example: str = ""
        self.alt_creator: str = ""
        self.alt_extensions_talkativeness: str = "0.5"
        self.alt_extensions_depth_prompt_prompt: str = ""
        self.alt_extensions_depth_prompt_depth: str = "0"
        self.alt_system_prompt: str = ""
        self.alt_post_history_instructions: str = ""
        self.alt_creator_notes: str = ""
        self.alt_character_version: str = ""
        self.alt_tags: List[str] = []
        self.misc_rentry: str = ""
        self.misc_rentry_alt: str = ""
        self.metadata_version: int = 1
        self.metadata_created: int = int(time.time() * 1000)
        self.metadata_modified: int = int(time.time() * 1000)
        self.metadata_source: Optional[str] = None
        self.metadata_tool_name: str = "airpwm"
        self.metadata_tool_version: str = "0.1"
        self.metadata_tool_url: str = ""
        self.avatar_path: Optional[str] = None

    def _update_metadata_timestamps(self):
        current_time_ms = int(time.time() * 1000)
        self.metadata_modified = current_time_ms
        if not self.metadata_created:
            self.metadata_created = current_time_ms

    def _populate_from_dict(self, char_dict: Dict[str, Any]):
        self.name = char_dict.get("name", self.name)
        self.description = char_dict.get("description", self.description)
        self.first_mes = char_dict.get("first_mes", self.first_mes)
        self.personality = char_dict.get("personality", self.personality)
        self.scenario = char_dict.get("scenario", self.scenario)
        self.mes_example = char_dict.get("mes_example", self.mes_example)
        self.spec = char_dict.get("spec", self.spec)
        self.spec_version = char_dict.get("spec_version", self.spec_version)

        data_block = char_dict.get("data", {})
        self.data_name = data_block.get("name", self.data_name if self.data_name else self.name)
        self.data_description = data_block.get("description", self.data_description if self.data_description else self.description)
        self.data_first_mes = data_block.get("first_mes", self.data_first_mes if self.data_first_mes else self.first_mes)
        self.data_alternate_greetings = data_block.get("alternate_greetings", self.data_alternate_greetings)
        self.data_personality = data_block.get("personality", self.data_personality if self.data_personality else self.personality)
        self.data_scenario = data_block.get("scenario", self.data_scenario if self.data_scenario else self.scenario)
        self.data_mes_example = data_block.get("mes_example", self.data_mes_example if self.data_mes_example else self.mes_example)
        self.data_creator = data_block.get("creator", self.data_creator)
        data_extensions = data_block.get("extensions", {})
        self.data_extensions_talkativeness = data_extensions.get("talkativeness", self.data_extensions_talkativeness)
        data_depth_prompt = data_extensions.get("depth_prompt", {})
        self.data_extensions_depth_prompt_prompt = data_depth_prompt.get("prompt", self.data_extensions_depth_prompt_prompt)
        self.data_extensions_depth_prompt_depth = data_depth_prompt.get("depth", self.data_extensions_depth_prompt_depth)
        self.data_system_prompt = data_block.get("system_prompt", self.data_system_prompt)
        self.data_post_history_instructions = data_block.get("post_history_instructions", self.data_post_history_instructions)
        self.data_creator_notes = data_block.get("creator_notes", self.data_creator_notes)
        self.data_character_version = data_block.get("character_version", self.data_character_version)
        self.data_tags = data_block.get("tags", self.data_tags)

        alt_block = char_dict.get("alternative", {})
        self.alt_name = alt_block.get("name_alt", self.alt_name)
        self.alt_description = alt_block.get("description_alt", self.alt_description)
        self.alt_first_mes = alt_block.get("first_mes_alt", self.alt_first_mes)
        self.alt_alternate_greetings = alt_block.get("alternate_greetings_alt", self.alt_alternate_greetings)
        self.alt_personality = alt_block.get("personality_alt", self.alt_personality)
        self.alt_scenario = alt_block.get("scenario_alt", self.alt_scenario)
        self.alt_mes_example = alt_block.get("mes_example_alt", self.alt_mes_example)
        self.alt_creator = alt_block.get("creator_alt", self.alt_creator)
        alt_extensions = alt_block.get("extensions_alt", {})
        self.alt_extensions_talkativeness = alt_extensions.get("talkativeness_alt", self.alt_extensions_talkativeness)
        alt_depth_prompt = alt_extensions.get("depth_prompt_alt", {})
        self.alt_extensions_depth_prompt_prompt = alt_depth_prompt.get("prompt_alt", self.alt_extensions_depth_prompt_prompt)
        self.alt_extensions_depth_prompt_depth = alt_depth_prompt.get("depth_alt", self.alt_extensions_depth_prompt_depth)
        self.alt_system_prompt = alt_block.get("system_prompt_alt", self.alt_system_prompt)
        self.alt_post_history_instructions = alt_block.get("post_history_instructions_alt", self.alt_post_history_instructions)
        self.alt_creator_notes = alt_block.get("creator_notes_alt", self.alt_creator_notes)
        self.alt_character_version = alt_block.get("character_version_alt", self.alt_character_version)
        self.alt_tags = alt_block.get("tags_alt", self.alt_tags)

        misc_block = char_dict.get("misc", {})
        self.misc_rentry = misc_block.get("rentry", self.misc_rentry)
        self.misc_rentry_alt = misc_block.get("rentry_alt", self.misc_rentry_alt)

        metadata_block = char_dict.get("metadata", {})
        self.metadata_version = metadata_block.get("version", self.metadata_version)
        self.metadata_created = metadata_block.get("created", self.metadata_created)
        self.metadata_modified = metadata_block.get("modified", self.metadata_modified)
        self.metadata_source = metadata_block.get("source", self.metadata_source)
        metadata_tool = metadata_block.get("tool", {})
        self.metadata_tool_name = metadata_tool.get("name", self.metadata_tool_name)
        self.metadata_tool_version = metadata_tool.get("version", self.metadata_tool_version)
        self.metadata_tool_url = metadata_tool.get("url", self.metadata_tool_url)

        if not self.name and self.data_name: self.name = self.data_name
        if not self.description and self.data_description: self.description = self.data_description
        if not self.first_mes and self.data_first_mes: self.first_mes = self.data_first_mes
        if not self.personality and self.data_personality: self.personality = self.data_personality
        if not self.scenario and self.data_scenario: self.scenario = self.data_scenario
        if not self.mes_example and self.data_mes_example: self.mes_example = self.data_mes_example

    @classmethod
    def load_from_file(cls, file_path: str, avatar_path: Optional[str] = None) -> Optional['AICharacter']:
        logger.debug(f"Attempting to load character from file: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"Error: Character file not found at specified path: {file_path}")
            return None

        char_dict: Optional[Dict[str, Any]] = None
        file_path_lower = file_path.lower()
        if file_path_lower.endswith(".png"):
            char_dict = _extract_json_from_png(file_path)
            if char_dict is None:
                logger.error(f"Failed to extract valid character JSON from PNG file: {file_path}")
        elif file_path_lower.endswith(".json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    char_dict = json.load(f)
            except FileNotFoundError:
                logger.error(f"Error: JSON file not found at {file_path}")
                return None
            except json.JSONDecodeError as e:
                logger.error(f"Error: Could not decode JSON from file {file_path}: {e}")
                return None
            except Exception as e:
                logger.error(f"An error occurred while reading JSON file '{file_path}': {e}")
                return None
        else:
            logger.error(f"Error: Unsupported file type: {file_path}. Please use .png or .json.")
            return None

        character = cls()
        if char_dict:
            character._populate_from_dict(char_dict)
        
        if avatar_path:
            character.avatar_path = avatar_path
        elif file_path_lower.endswith(".png") and not avatar_path:
             character.avatar_path = file_path

        if not char_dict and not file_path_lower.endswith(".png"):
            return None
            
        return character

    def to_dict(self) -> Dict[str, Any]:
        data_name = self.data_name if self.data_name else self.name
        data_description = self.data_description if self.data_description else self.description
        data_first_mes = self.data_first_mes if self.data_first_mes else self.first_mes
        data_personality = self.data_personality if self.data_personality else self.personality
        data_scenario = self.data_scenario if self.data_scenario else self.scenario
        data_mes_example = self.data_mes_example if self.data_mes_example else self.mes_example
        
        return {
            "name": self.name,
            "description": self.description,
            "first_mes": self.first_mes,
            "personality": self.personality,
            "scenario": self.scenario,
            "mes_example": self.mes_example,
            "spec": self.spec,
            "spec_version": self.spec_version,
            "data": {
                "name": data_name,
                "description": data_description,
                "first_mes": data_first_mes,
                "alternate_greetings": self.data_alternate_greetings,
                "personality": data_personality,
                "scenario": data_scenario,
                "mes_example": data_mes_example,
                "creator": self.data_creator,
                "extensions": {
                    "talkativeness": self.data_extensions_talkativeness,
                    "depth_prompt": {
                        "prompt": self.data_extensions_depth_prompt_prompt,
                        "depth": self.data_extensions_depth_prompt_depth
                    }
                },
                "system_prompt": self.data_system_prompt,
                "post_history_instructions": self.data_post_history_instructions,
                "creator_notes": self.data_creator_notes,
                "character_version": self.data_character_version,
                "tags": self.data_tags
            },
            "alternative": {
                "name_alt": self.alt_name,
                "description_alt": self.alt_description,
                "first_mes_alt": self.alt_first_mes,
                "alternate_greetings_alt": self.alt_alternate_greetings,
                "personality_alt": self.alt_personality,
                "scenario_alt": self.alt_scenario,
                "mes_example_alt": self.alt_mes_example,
                "creator_alt": self.alt_creator,
                "extensions_alt": {
                    "talkativeness_alt": self.alt_extensions_talkativeness,
                    "depth_prompt_alt": {
                        "prompt_alt": self.alt_extensions_depth_prompt_prompt,
                        "depth_alt": self.alt_extensions_depth_prompt_depth
                    }
                },
                "system_prompt_alt": self.alt_system_prompt,
                "post_history_instructions_alt": self.alt_post_history_instructions,
                "creator_notes_alt": self.alt_creator_notes,
                "character_version_alt": self.alt_character_version,
                "tags_alt": self.alt_tags
            },
            "misc": {
                "rentry": self.misc_rentry,
                "rentry_alt": self.misc_rentry_alt
            },
            "metadata": {
                "version": self.metadata_version,
                "created": self.metadata_created,
                "modified": self.metadata_modified,
                "source": self.metadata_source,
                "tool": {
                    "name": self.metadata_tool_name,
                    "version": self.metadata_tool_version,
                    "url": self.metadata_tool_url
                }
            }
        }

    def save_to_json(self, output_json_path: str):
        self._update_metadata_timestamps()
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
        logger.info(f"Character data saved to {output_json_path}")
        
        

    def save_to_png(self, output_png_path: str, base_image_path: Optional[str] = None):
        self._update_metadata_timestamps()
        try:
            char_data_dict = self.to_dict()
            json_string = json.dumps(char_data_dict, ensure_ascii=False)
            base64_encoded_data = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

            img = None
            resolved_base_path = base_image_path

            if resolved_base_path and os.path.exists(resolved_base_path):
                try:
                    img = Image.open(resolved_base_path)
                except Exception as e:
                    logger.warning(f"Could not open provided base image '{resolved_base_path}': {e}.")
                    img = None

            if img is None and self.avatar_path and not self.avatar_path.startswith(('http://', 'https://')):
                if os.path.exists(self.avatar_path):
                    try:
                        img = Image.open(self.avatar_path)
                    except Exception as e:
                        logger.warning(f"Could not open avatar_path '{self.avatar_path}': {e}.")
                        img = None

            if img is None:
                img = Image.new('RGB', (512, 768), color = (73, 109, 137))
                d = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("arial.ttf", 30)
                except IOError:
                    font = ImageFont.load_default()
                text = self.name if self.name else "Character Card"
                text_bbox = d.textbbox((0,0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = (img.width - text_width) / 2
                text_y = (img.height - text_height) / 2
                d.text((text_x, text_y), text, fill=(255,255,255), font=font)
            
            if img.mode not in ['RGB', 'RGBA']:
                 img = img.convert('RGBA')
            elif img.mode == 'RGB':
                 img = img.convert('RGBA')

            png_info = PngImagePlugin.PngInfo()
            png_info.add_text('chara', base64_encoded_data)
            img.save(output_png_path, "PNG", pnginfo=png_info)
            logger.info(f"Character data successfully embedded and saved to {output_png_path}")
            

        except FileNotFoundError as e:
            logger.error(f"File not found during PNG save: {e}")
            pass
        except Exception as e:
            logger.error(f"An error occurred while saving to PNG '{output_png_path}': {e}")
            pass

    def get_initial_llm_message(self, user_name: str, pick_greeting: Any = False) -> str:
        """
        Constructs the initial message string to send to the LLM, including
        character context and the first character message.

        Args:
            user_name (str): The name of the user interacting with the character.
            pick_greeting (bool or int): Determines how the first message is chosen.
                - False or 0: Uses the default first message.
                - True: Randomly selects between the default and alternate greetings.
                - Positive integer (e.g., 1, 2): Selects the corresponding alternate
                  greeting (1-indexed). Falls back to default if out of bounds or empty.

        Returns:
            str: A formatted string containing character context, a conversation
                 starter line, and the character's first message, with {{user}}
                 and {{char}} placeholders replaced.
        """
        char_name = self.data_name if self.data_name else self.name
        description = self.data_description if self.data_description else self.description

        
        personality = self.data_personality if self.data_personality else self.personality
        scenario = self.data_scenario if self.data_scenario else self.scenario
        mes_example = self.data_mes_example if self.data_mes_example else self.mes_example

        
        chosen_first_message = self.data_first_mes if self.data_first_mes else self.first_mes
        if not chosen_first_message:
            chosen_first_message = f"Hello, I am {char_name}."


        if pick_greeting is True:
            options = []
            if chosen_first_message: 
                options.append(chosen_first_message)
            if self.data_alternate_greetings:
                options.extend(self.data_alternate_greetings)
            
            if options: 
                chosen_first_message = random.choice(options)

        elif isinstance(pick_greeting, int) and pick_greeting > 0:
            if self.data_alternate_greetings and 0 < pick_greeting <= len(self.data_alternate_greetings):
                chosen_first_message = self.data_alternate_greetings[pick_greeting - 1]
            # else, it falls back to the default chosen_first_message already set

        # --- context string ---
        context_parts = []
        if description:
            context_parts.append(f"Description: {description}")
        if personality:
            context_parts.append(f"Personality (Summary): {personality}")
        if scenario:
            context_parts.append(f"Scenario: {scenario}")
        if mes_example:
            context_parts.append(f"Example Messages:\n{mes_example}")
        
        context_block = "[Character Context]\n---\n"
        if context_parts:
            context_block += "\n\n".join(context_parts) + "\n---\n\n"
        else:
            context_block += "No specific context provided.\n---\n\n"

        # conversation_begins_line = "--- Conversation between {{char}} and {{user}} has begun ---\n\n"
        # final_string = context_block + conversation_begins_line + chosen_first_message
        # final_string = self.parse_names(user_name, final_string)
        # return final_string
        context_block = self.parse_names(user_name, context_block)
        chosen_first_message = self.parse_names(user_name, chosen_first_message)
        return context_block, chosen_first_message

    def parse_names(self, user_name: str, text: str):

        text = text.replace("{{char}}", self.name if self.name else "Character")
        text = text.replace("{{user}}", user_name if user_name else "User")
        return text


    def get_system_prompt(self) -> str|None:
        if not self.data_system_prompt:
            return None
        
        if len(self.data_system_prompt) == 0:
            return None
        
        return self.data_system_prompt
        


    def __str__(self):
        return (f"AICharacter(Name: '{self.name or self.data_name}', "
                f"Description: '{self.description or self.data_description}'. "
                f"Avatar Path: '{self.avatar_path}')")
