import json
import pathlib
from collections import defaultdict


class Template:
    def __init__(self, prompt, negative_prompt, **kwargs):
        self.prompt = prompt
        self.negative_prompt = negative_prompt

    def split_template_advanced(self):
        if "{prompt} ." in self.prompt:
            template_prompt_g, template_prompt_l = self.prompt.split("{prompt} .", 1)
            template_prompt_g = template_prompt_g.strip() + " {prompt}"
            template_prompt_l = template_prompt_l.strip()
        else:
            template_prompt_g = self.prompt
            template_prompt_l = ""

        return template_prompt_g, template_prompt_l

    def replace_prompts(self, positive_prompt, negative_prompt):
        positive_result = self.prompt.replace('{prompt}', positive_prompt)
        negative_result = ', '.join(x for x in (self.negative_prompt, negative_prompt) if x)
        return positive_result, negative_result

    def replace_prompts_advanced(self, positive_prompt_g, positive_prompt_l, negative_prompt, negative_prompt_to):
        template_prompt_g, template_prompt_l_template = self.split_template_advanced()
        text_g_positive = template_prompt_g.replace("{prompt}", positive_prompt_g)
        text_l_positive = ', '.join(x for x in (template_prompt_l_template, positive_prompt_l) if x)
        text_positive = f"{text_g_positive} . {text_l_positive}" if text_l_positive else text_g_positive
        text_negative = ', '.join(x for x in (self.negative_prompt, negative_prompt) if x)

        text_g_negative = ""
        if negative_prompt_to in ("Both", "G only"):
            text_g_negative = text_negative

        text_l_negative = ""
        if negative_prompt_to in ("Both", "L only"):
            text_l_negative = text_negative

        return text_g_positive, text_l_positive, text_positive, text_g_negative, text_l_negative, text_negative


class StylerData:
    def __init__(self, datadir=None):
        self._data = defaultdict(dict)
        if datadir is None:
            datadir = pathlib.Path(__file__).parent / 'data'

        for j in datadir.glob('*/*.json'):
            try:
                with j.open('r') as f:
                    content = json.load(f)
                    group = j.parent.name
                    for template in content:
                        self._data[group][template['name']] = Template(**template)
            except PermissionError:
                print(f"Warning: No read permissions for file {j}")
            except KeyError:
                print(f"Warning: Malformed data in {j}")

    def __getitem__(self, item):
        return self._data[item]

    def keys(self):
        return self._data.keys()


styler_data = StylerData()


class SDXLPromptStyler:
    menus = ()

    @classmethod
    def INPUT_TYPES(cls):
        menus = {menu: (list(styler_data[menu].keys()), ) for menu in cls.menus}

        inputs = {
            "required": {
                "text_positive": ("STRING", {"default": "", "multiline": True}),
                "text_negative": ("STRING", {"default": "", "multiline": True}),
                **menus,
                "log_prompt": ("BOOLEAN", {"default": True, "label_on": "Yes", "label_off": "No"}),
            },
        }

        return inputs

    RETURN_TYPES = ('STRING','STRING',)
    RETURN_NAMES = ('text_positive','text_negative',)
    FUNCTION = 'prompt_styler'
    CATEGORY = 'ali1234/stylers'

    def prompt_styler(self, text_positive, text_negative, log_prompt, **kwargs):
        text_positive_styled, text_negative_styled = text_positive, text_negative
        for menu, selection in kwargs.items():
            text_positive_styled, text_negative_styled = styler_data[menu][selection].replace_prompts(text_positive_styled, text_negative_styled)
 
        if log_prompt:
            for menu, selection in kwargs.items():
                print(f"{menu}: {selection}")
            print(f"text_positive: {text_positive}")
            print(f"text_negative: {text_negative}")
            print(f"text_positive_styled: {text_positive_styled}")
            print(f"text_negative_styled: {text_negative_styled}")

        return text_positive_styled, text_negative_styled
    
class SDXLPromptStylerAdvanced:
    menus = () # when we subclass, we will put the list of menus (directories) here

    @classmethod
    def INPUT_TYPES(cls):
        menus = {menu: (list(styler_data[menu].keys()), ) for menu in cls.menus}
        
        return {
            "required": {
                "text_positive_g": ("STRING", {"default": "", "multiline": True}),
                "text_positive_l": ("STRING", {"default": "", "multiline": True}),
                "text_negative": ("STRING", {"default": "", "multiline": True}),
                **menus,
                "negative_prompt_to": (["Both", "G only", "L only"], {"default":"Both"}),
                "log_prompt": ("BOOLEAN", {"default": True, "label_on": "Yes", "label_off": "No"}),
            },
        }

    RETURN_TYPES = ('STRING','STRING','STRING','STRING','STRING','STRING',)
    RETURN_NAMES = ('text_positive_g','text_positive_l','text_positive','text_negative_g','text_negative_l','text_negative',)
    FUNCTION = 'prompt_styler_advanced'
    CATEGORY = 'ali1234/stylers'

    def prompt_styler_advanced(self, text_positive_g, text_positive_l, text_negative, negative_prompt_to, log_prompt, **kwargs):
        text_positive_g_styled, text_positive_l_styled, text_negative_styled = text_positive_g, text_positive_l, text_negative
        text_positive_styled, text_negative_g_styled, text_negative_l_styled = "", "", ""
        for menu, selection in kwargs.items():
            text_positive_g_styled, text_positive_l_styled, text_positive_styled, text_negative_g_styled, text_negative_l_styled, text_negative_styled = styler_data[menu][selection].replace_prompts_advanced(text_positive_l_styled, text_positive_g_styled, text_negative_styled, negative_prompt_to)

        if log_prompt:
            for menu, selection in kwargs.items():
                print(f"{menu}: {selection}")
            print(f"text_positive_g: {text_positive_g}")
            print(f"text_positive_l: {text_positive_l}")
            print(f"text_negative: {text_negative}")
            print(f"text_positive_g_styled: {text_positive_g_styled}")
            print(f"text_positive_l_styled: {text_positive_l_styled}")
            print(f"text_positive_styled: {text_positive_styled}")
            print(f"text_negative_g_styled: {text_negative_g_styled}")
            print(f"text_negative_l_styled: {text_negative_l_styled}")
            print(f"text_negative_styled: {text_negative_styled}")

        return text_positive_g_styled, text_positive_l_styled, text_positive_styled, text_negative_g_styled, text_negative_l_styled, text_negative_styled


NODES = {
    # define your nodes here
    # first the friendly name, then a sequence of strings
    # corresponding to subdirectories of the data dir.

    # individual stylers have one menu item
    # build them automatically from the scanned directories
    **{f'{name.title()} Styler': (name, ) for name in styler_data.keys()},

    # alternatively you can list every single-menu node like this:
    # 'Camera Styler': ('camera', ),
    # etc...

    # perfection styler has everything except artist and milehigh
    # we can define it by excluding those
    # downside of this method is you have no control over the order
    #'Perfection Styler': [x for x in styler_data.keys() if x not in ('artist', 'milehigh')],

    # alternatively define it manually, and you can reorder the items
    'Perfection Styler': (
        'camera', 'composition', 'depth', 'environment', 'filter',
        'focus', 'lighting', 'mood', 'subject', 'theme', 'timeofday'
    ),
}

for k, v in NODES.items():
    assert not isinstance(v, str), f"Error: {k} has a string instead of a sequence for its menu list. Did you forget a comma?"


# now we subclass the base node classes dynamically using 3-arg type

NODE_CLASS_MAPPINGS = {
    **{name.replace(' ', ''): type(name.replace(' ', ''), (SDXLPromptStyler, ), {'menus': menus}) for name, menus in NODES.items()},
    **{name.replace(' ', '') + 'Advanced': type(name.replace(' ', '')+'Advanced', (SDXLPromptStylerAdvanced, ), {'menus': menus}) for name, menus in NODES.items()},
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **{name.replace(' ', ''): name for name in NODES.keys()},
    **{name.replace(' ', '') + 'Advanced': name + ' (Advanced)' for name in NODES.keys()},
}
