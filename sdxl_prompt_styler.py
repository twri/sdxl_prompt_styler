import json
import os

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            return json_data
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def read_sdxl_styles(json_data):
    # Check that data is a list
    if not isinstance(json_data, list):
        print("Error: input data must be a list")
        return None

    names = []

    # Iterate over each item in the data list
    for item in json_data:
        # Check that the item is a dictionary
        if isinstance(item, dict):
            # Check that 'name' is a key in the dictionary
            if 'name' in item:
                # Append the value of 'name' to the names list
                names.append(item['name'])

    return names

def read_sdxl_templates_replace_and_combine(json_data, template_name, positive_prompt, negative_prompt):
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
                positive_prompt = template['prompt'].replace('{prompt}', positive_prompt)
                
                json_negative_prompt = template.get('negative_prompt', "")
                if negative_prompt:
                    negative_prompt = f"{json_negative_prompt}, {negative_prompt}" if json_negative_prompt else negative_prompt
                else:
                    negative_prompt = json_negative_prompt
                
                return positive_prompt, negative_prompt

        # If function hasn't returned yet, no matching template was found
        raise ValueError(f"No template found with name '{template_name}'.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


class SDXLPromptStyler:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        p = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(p, 'sdxl_styles.json')

        self.json_data = read_json_file(file_path)
        styles = read_sdxl_styles(self.json_data)
        
        return {
            "required": {
                "text_positive": ("STRING", {"default": "", "multiline": True}),
                "text_negative": ("STRING", {"default": "", "multiline": True}),
                "style": ((styles), ),
                "log_prompt": (["No", "Yes"], {"default":"No"}),
            },
        }

    RETURN_TYPES = ('STRING','STRING',)
    RETURN_NAMES = ('positive_prompt_text_g','negative_prompt_text_g',)
    FUNCTION = 'prompt_styler'
    CATEGORY = 'utils'

    def prompt_styler(self, text_positive, text_negative, style, log_prompt):
        positive_prompt, negative_prompt = read_sdxl_templates_replace_and_combine(self.json_data, style, text_positive, text_negative)
 
        if log_prompt == "Yes":
            print(f"style: {style}")
            print(f"text_positive: {text_positive}")
            print(f"text_negative: {text_negative}")
            print(f"positive_prompt: {positive_prompt}")
            print(f"negative_prompt: {negative_prompt}")

        return positive_prompt, negative_prompt


NODE_CLASS_MAPPINGS = {
    "SDXLPromptStyler": SDXLPromptStyler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SDXLPromptStyler": "SDXL Prompt Styler",
}