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
arrive_x = config['arrive']['x']
arrive_y = config['arrive']['y']
WinTitle = config['title']
limit_time = config['role_run']['limit_time']
move_delay = config['role_run']['move_delay']
black_limit_time = config['screen']['black_limit_time']
black_threshold = config['screen']['black_threshold']
black_check_interval = config['screen']['black_check_interval']
match_conf = 0.85

class ScriptParams:
    status = 'wait'