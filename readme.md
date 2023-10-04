# Addon Packaging Utility Tool

Created by MACHINE_BUILDER
[https://www.youtube.com/machinebuilder/]()

This tool is designed for packaging Minecraft Bedrock Addons in a quick and easy way.

PLEASE NOTE THAT THIS TOOL IS STILL WIP AND MAY CONTAIN BUGS. REPORT ANY BUGS YOU FIND SO I CAN EASILY TRACK THEM! THANK YOU!

This is a GUI-based tool, so using it should be intuitive to most people. When you open the ui, use the menu bar > Configuration > Packs > To select the pack you wish to package. Packs must be defined in config.json, which will be created for you when the tool is first run.

## Licensing

This project uses PyQt5, which means it cannot be sold without proper licensing.

Any files within resources/3rdparty are provided on Qt's website, and have license files available.

## Requirements

This project uses the following modules:

* PyQt5 (For UI)
* PyQtWebEngine (For MD preview)
* jstyleson (For handling comments in JSON)
* pyperclip (For copying to clipboard)

## Using Config.json

Config.json is where you define pack paths for the packager to list.

An example pack entry would look like:

```json
{
    "packaged_name": "MyCoolAddon",
    "path_bp": "C:/Users/Me/Documents/MinecraftAddons/MyCoolAddon/BP",
    "path_rp": "C:/Users/Me/Documents/MinecraftAddons/MyCoolAddon/RP",
    "outputs": [
        {
            "packaged_suffix": "_Public",
            "post_processing": {
                "minify_js": "esbuild",
                "obscure_json": true
            }
        },
        {
            "packaged_suffix": "_Private",
            "post_processing": {}
        }
    ]
},
```

When this pack is packaged, there will be two outputs:

* MyCoolAddon_Public_0.0.1.mcaddon
* MyCoolAddon_Private_0.0.1.mcaddon

The _Public version is intended for public release, and uses two post processors - JSON UTF-16 encoding, and JS minifying (via esbuild - You can also use terser if you prefer... These are run via the CLI internally).
