import json
import os

def read_json_file(file_path):
    """
    Reads the content of a JSON file and returns it as a Python data structure.
    """
    if not os.access(file_path, os.R_OK):
        print(f"Warning: No read permissions for file {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = json.load(file)
            # Check if the content matches the expected format.
            if not all(['name' in item and 'prompt' in item and 'negative_prompt' in item for item in content]):
                print(f"Warning: Invalid content in file {file_path}")
                return None
            return content
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {str(e)}")
        return None


def read_sdxl_styles(json_data):
    """
    Extracts style names from the provided data.
    """
    if not isinstance(json_data, list):
        print("Error: input data must be a list")
        return []

    return [item['name'] for item in json_data if isinstance(item, dict) and 'name' in item]

def get_all_json_files(directory):
    """
    Retrieves all JSON files present in the specified directory.
    """
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.json') and os.path.isfile(os.path.join(directory, file))]


def load_styles_from_directory(directory):
    """
    Loads style names and combined data from all JSON files in the directory.
    Ensures style names are unique by appending a suffix to duplicates.
    """
    json_files = get_all_json_files(directory)
    combined_data = []
    seen = set()

    for json_file in json_files:
        json_data = read_json_file(json_file)
        if json_data:
            for item in json_data:
                original_style = item['name']
                style = original_style
                suffix = 1
                while style in seen:
                    style = f"{original_style}_{suffix}"
                    suffix += 1
                item['name'] = style
                seen.add(style)
                combined_data.append(item)

    unique_style_names = [item['name'] for item in combined_data if isinstance(item, dict) and 'name' in item]
    
    return combined_data, unique_style_names


def read_sdxl_templates_replace_and_combine(json_data, template_name, positive_prompt_g, positive_prompt_l, negative_prompt, split_style):
    try:
        # Check if json_data is a list
        if not isinstance(json_data, list):
            raise ValueError("Invalid JSON data. Expected a list of templates.")
            
        for template in json_data:
            # Check if template contains 'name' and 'prompt' fields
            if 'name' not in template or 'prompt' not in template:
                raise ValueError("Invalid template. Missing 'name' or 'prompt' field.")
            
            # Replace {prompt} in the matching template
            if template['name'] == template_name:
                if " . " in template['prompt']:
                    template_prompt_g, template_prompt_l = template['prompt'].split(" . ", 1)
                    if split_style in ("G only", "Both"):
                        template_prompt_g = template_prompt_g+', '+template_prompt_l
                else:
                    template_prompt_g = template['prompt']
                    template_prompt_l = ""

                positive_prompt_g = template_prompt_g.replace('{prompt}', positive_prompt_g)
                
                if split_style in ("L only", "Both"):
                    if '{prompt}' in template_prompt_l:
                        positive_prompt_l = template_prompt_l.replace('{prompt}', positive_prompt_l)
                    elif positive_prompt_l:
                        positive_prompt_l = template_prompt_l+', '+positive_prompt_l
                    else:
                        positive_prompt_l = template_prompt_l
                
                json_negative_prompt = template.get('negative_prompt', "")
                if negative_prompt:
                    negative_prompt = f"{json_negative_prompt}, {negative_prompt}" if json_negative_prompt else negative_prompt
                else:
                    negative_prompt = json_negative_prompt
                
                return positive_prompt_g, positive_prompt_l, negative_prompt

        # If function hasn't returned yet, no matching template was found
        raise ValueError(f"No template found with name '{template_name}'.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


class SDXLPromptStyler:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        self.json_data, styles = load_styles_from_directory(current_directory)
        
        return {
            "required": {
                "text_positive_g": ("STRING", {"default": "", "multiline": True}),
                "text_positive_l": ("STRING", {"default": "", "multiline": True}),
                "text_negative": ("STRING", {"default": "", "multiline": True}),
                "style": ((styles), ),
                "split_style": (["L only", "G only", "Both"], {"default":"L only"}),
                "log_prompt": (["No", "Yes"], {"default":"No"}),
            },
        }

    RETURN_TYPES = ('STRING','STRING','STRING')
    RETURN_NAMES = ('positive_prompt_text_g','positive_prompt_text_l','negative_prompt_text_g',)
    FUNCTION = 'prompt_styler'
    CATEGORY = 'utils'

    def prompt_styler(self, text_positive_g, text_positive_l, text_negative, style, split_style, log_prompt):
        # Process and combine prompts in templates
        # The function replaces the positive prompt placeholder in the template,
        # and combines the negative prompt with the template's negative prompt, if they exist.
        positive_prompt_g, positive_prompt_l, negative_prompt = read_sdxl_templates_replace_and_combine(self.json_data, style, text_positive_g, text_positive_l, text_negative, split_style)
 
        # If logging is enabled (log_prompt is set to "Yes"), 
        # print the style, positive and negative text, and positive and negative prompts to the console
        if log_prompt == "Yes":
            print(f"style: {style}")
            print(f"text_positive_g: {text_positive_g}")
            print(f"text_positive_l: {text_positive_l}")
            print(f"text_negative: {text_negative}")
            print(f"positive_prompt_g: {positive_prompt_g}")
            print(f"positive_prompt_l: {positive_prompt_l}")
            print(f"negative_prompt: {negative_prompt}")

        return positive_prompt_g, positive_prompt_l, negative_prompt


NODE_CLASS_MAPPINGS = {
    "SDXLPromptStyler": SDXLPromptStyler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SDXLPromptStyler": "SDXL Prompt Styler",
}