import os
import yaml

map_w = 190
map_h = 130

with open("./config/config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

jump = config['keybind']['jump']
home_send = config['keybind']['home_send']
attack_multi = config['keybind']['attack_multi']
ConfigMode = config['mode']
ConfigTimes = config['times']
ConfigScriptPath = config['script']['path']


class ScriptParams:
    status = 'wait'