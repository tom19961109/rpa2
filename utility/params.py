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
exe_path = config['exe_path']
limit_time = config['role_run']['limit_time']
attack_duration = config['role_run']['attack_duration']
move_delay = config['role_run']['move_delay']
black_limit_time = config['screen']['black_limit_time']
black_threshold = config['screen']['black_threshold']
black_check_interval = config['screen']['black_check_interval']
account = config['login']['account']
password = config['login']['password']
channel = config['login']['channel']
match_conf = 0.85

out_channel_pos = {
    1: [823, 333], 2: [915, 333], 3: [1010, 333], 4: [1101, 333],
    5: [823, 365], 6: [915, 365], 7: [1010, 365], 8: [1101, 365],
    9: [823, 396], 10: [915, 396],  11: [1010, 396], 12: [1101, 396],
    13: [823, 427], 14: [915, 427], 15: [1010, 427], 16: [1101, 427],
    17: [823, 459], 18: [915, 459], 19: [1010, 459], 20: [1101, 459],
}

class ScriptParams:
    status = 'wait'