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

if __name__ == "__main__":
    arg_dict = parse_args(sys.argv)
    file_path = os.path.join(arg_dict["repo_path"], "game_results_eval.txt")
    result_dict, episode_counts = process_file(file_path)
    eps = sorted(result_dict.keys())
    graph_eps = []
    graph_perc = []
    
    for ep in eps:
        total = episode_counts[ep]
        print(f"Episode {ep} - total: {total}")
        for (res, scores), count in result_dict[ep].items():
            percentage = (count / total) * 100
            print(f"  ({res}, {scores}): {count} ({percentage:.3f}%)")
            if (total >= 10000) and (res, scores) == ("Ryuukyoku", (0, 0, 0, 0)):
                graph_eps.append(ep)
                graph_perc.append(percentage)
        print()

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(graph_eps, graph_perc, marker='o', linestyle='-', color='blue')
    plt.title("Frequency of Noten Ryuukyoku per episode")
    plt.xlabel("Episode")
    plt.ylabel("Percentage")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
