import os
import re
import sys
from collections import defaultdict
import matplotlib.pyplot as plt

from model_common import parse_args

def parse_line(line):
    match = re.match(r"model checkpoints\\qnet_ep(\d+)\.pt (.*?) (\[.*\])", line.strip())
    if match:
        ep_num = int(match.group(1))
        result = match.group(2)
        scores_str = match.group(3)
        try:
            scores = eval(scores_str)
            if isinstance(scores, list) and len(scores) == 4:
                return ep_num, result, tuple(scores)
        except:
            pass
    return None

def process_file(file_path):
    result_dict = defaultdict(lambda: defaultdict(int))
    episode_counts = defaultdict(int)

    with open(file_path, 'r') as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                ep_num, result, scores = parsed
                result_dict[ep_num][(result, scores)] += 1
                episode_counts[ep_num] += 1

    return result_dict, episode_counts

def get_model_folders(base_path):
    model_folders = []
    for entry in os.listdir(base_path):
        full_path = os.path.join(base_path, entry)
        if os.path.isdir(full_path) and entry.startswith("mahjong-model-"):
            eval_file = os.path.join(full_path, "game_results_eval.txt")
            if os.path.exists(eval_file):
                model_folders.append((entry, eval_file))
    return model_folders

if __name__ == "__main__":
    arg_dict = parse_args(sys.argv)
    model_folders = get_model_folders("../..")
    
    plt.figure(figsize=(10, 6))
    all_agari_data = {}
    
    for model_name, file_path in model_folders:
        result_dict, episode_counts = process_file(file_path)
        eps = sorted(result_dict.keys())
        graph_eps = []
        noten_perc = []
        agari_perc = []
        print(model_name)
        
        for ep in eps:
            total = episode_counts[ep]
            print(ep, total)
            if total >= 100000:
                agari_cnt = 0
                noten_cnt = 0
                for (res, scores), count in result_dict[ep].items():
                    print(" ", res,scores, count)
                    if (res, scores) == ("Ryuukyoku", (0, 0, 0, 0)):
                        graph_eps.append(ep)
                        noten_cnt = count
                    elif "Tsumo" in res or "Ron" in res:
                        agari_cnt += count
                
                if graph_eps and graph_eps[-1] == ep:
                    print(f"appending {noten_perc}, {agari_perc}")
                    noten_perc.append((noten_cnt / total) * 100)
                    agari_perc.append((agari_cnt / total) * 100)
        
        all_agari_data[model_name] = (graph_eps, agari_perc)
        ls = '-' if 'h1-' in model_name else ':' if 'h5-' in model_name else '--'
        plt.plot(graph_eps, noten_perc, marker='o', linestyle=ls, label=model_name)

    plt.title("Frequency of Noten Ryuukyoku per episode")
    plt.xlabel("Episode")
    plt.ylabel("Percentage")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    
    plt.figure(figsize=(10, 6))
    
    for model_name, (graph_eps, agari_perc) in all_agari_data.items():
        ls = '-' if 'h1-' in model_name else ':' if 'h5-' in model_name else '--'
        plt.plot(graph_eps, agari_perc, marker='o', linestyle=ls, label=model_name)

    plt.title("Frequency of Agari (Wins) per episode")
    plt.xlabel("Episode")
    plt.ylabel("Percentage")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
