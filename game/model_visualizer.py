
import matplotlib.pyplot as plt
import os
import sys
import torch

from model_common import *

if __name__ == "__main__":
    arg_dict = parse_args(sys.argv)
    model_path = arg_dict["model_path"]

    state_dict = torch.load(model_path)
    for name, param in state_dict.items():
        print(f"{name}: {param.shape}")

    layers = [
        ("backbone.0.weight", "Input Layer (370 → 256)", 'viridis'),
        ("backbone.2.weight", "Hidden Layer (256 → 256)", 'viridis'),
        ("policy_head.weight", "Policy Head (256 → 98)", 'viridis'),
        ("value_head.weight", "Value Head (256 → 1)", 'viridis'),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for i, (key, title, cmap) in enumerate(layers):
        weights = state_dict[key].numpy()
        ax = axes[i]
        im = ax.imshow(weights, aspect='auto', cmap=cmap, vmin=-1, vmax=1)
        ax.set_title(title)
        ax.set_xlabel("Input Units")
        ax.set_ylabel("Output Units")
        fig.colorbar(im, ax=ax)

    fig.suptitle(f"Model Weights {model_path}", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()
