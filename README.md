SDXL Prompt Styler
=======
Custom node for ComfyUI
-----------
![SDXL Prompt Styler Screenshot](examples/sdxl_prompt_styler.png)

SDXL Prompt Styler is a node that enables you to style prompts based on predefined templates stored in a JSON file. The node specifically replaces a {prompt} placeholder in the 'prompt' field of each template with provided positive text.

The node also effectively manages negative prompts. If negative text is provided, the node combines this with the 'negative_prompt' field from the template. If no negative text is supplied, the system defaults to using the 'negative_prompt' from the JSON template.

In the case where both negative text and the 'negative_prompt' field are present in the JSON template, the node merges them into a unified negative prompt. This flexibility enables the creation of a diverse and specific range of negative prompts.

Here's a template example from a JSON file:

```json
[
    {
        "name": "base",
        "prompt": "{prompt}",
        "negative_prompt": ""
    },
    {
        "name": "enhance",
        "prompt": "breathtaking {prompt} . award-winning, professional, highly detailed",
        "negative_prompt": "ugly, deformed, noisy, blurry, distorted, grainy"
    }
]
```

### Installation

To install and use the SDXL Prompt Styler nodes, follow these steps:

1. Open a terminal or command line interface.
2. Navigate to the `ComfyUI/custom_nodes/` directory.
3. Run the following command:
```git clone https://github.com/twri/sdxl_prompt_styler.git```

This command clones the SDXL Prompt Styler repository into your ComfyUI/custom_nodes/ directory. You should now be able to access and use the nodes from this repository.