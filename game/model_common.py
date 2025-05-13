
import os
import re

model_dir = "checkpoints"
state_dir = "save_states"
model_pattern = r'qnet_ep(\d+)\.pt'

mcts_args = {
    'C': 1.41,
    'search_num': 20
}

def latest_model_path(model_dir: str):
    files = os.listdir(model_dir)
    
    max_num = -1
    latest_model = None
    
    pattern = re.compile(model_pattern)
    for filename in files:
        match = pattern.match(filename)
        if match:
            current_num = int(match.group(1))
            if current_num > max_num:
                max_num = current_num
                latest_model = filename
    if latest_model:
        return os.path.join(model_dir, latest_model)
    else:
        return None

def parse_args(args: list[str]) -> dict:
    out = {
        "wait_flag": False,
        "verbose": False
        }
    
    if "-w" in args:
        out["wait_flag"] = True
        
    if "-v" in args:
        out["verbose"] = True
    
    if "-m" in args:
        model_index = args.index("-m") + 1
    elif "--model" in args:
        model_index = args.index("--model") + 1
    else:
        model_index = None
    if model_index and len(args) > model_index:
        model_fname = args[model_index]
        model_path = os.path.join(save_dir, model_fname)
        if not model_fname in os.listdir(model_dir):
            print(f"Model <{model_path}> not found")
    else:
        model_path = latest_model_path(model_dir)
    if model_path is not None:
        out["model_path"] = model_path
    
    if "-s" in args:
        state_index = args.index("-s") + 1
    elif "--state" in args:
        state_index = args.index("--state") + 1
    else:
        state_index = None
    if state_index and len(args) > state_index:
        state_fname = args[state_index]
        state_path = os.path.join(state_dir, state_fname)
        if not state_fname in os.listdir(state_dir):
            print(f"State <{state_path}> not found")
        else:
            out["state_path"] = state_path
    
    if "-e" in args:
        ep_index = args.index("-e") + 1
    elif "--episodes" in args:
        ep_index = args.index("--episodes") + 1
    else:
        ep_index = None
    if ep_index and len(args) > ep_index:
        ep_str = args[ep_index]
        try:
            ep_num = int(ep_str)
        except ValueError:
            print(f"Invalid episode number: <{ep_str}>")
        else:
            out["episode_num"] = ep_num
    
    
    return out
