from model_eval_random_loop import *

arg = [
    ["-m", "qnet_ep050.pt", "-e", "90000"],
    ["-m", "qnet_ep150.pt", "-e", "90000"],
    ["-m", "qnet_ep200.pt", "-e", "90000"],
    ["-m", "qnet_ep250.pt", "-e", "90000"],
    ["-m", "qnet_ep300.pt", "-e", "90000"],
]

for lst in arg:
    main_eval_random_loop(lst)
