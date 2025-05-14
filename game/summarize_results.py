import re
from collections import defaultdict

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
    file_path = "game_results_eval.txt"
    result_dict, episode_counts = process_file(file_path)
    eps = sorted(result_dict.keys())
    
    for ep in eps:
        total = episode_counts[ep]
        print(f"Episode {ep} - total: {total}")
        for (res, scores), count in result_dict[ep].items():
            percentage = (count / total) * 100
            print(f"  ({res}, {scores}): {count} ({percentage:.3f}%)")
        print()
