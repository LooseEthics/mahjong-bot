from model_eval_random_loop import *

arg = [
    ["-m", "qnet_ep001.pt", "-e", "100000"],
    #["-m", "qnet_ep050.pt", "-e", "100000"],
    #["-m", "qnet_ep150.pt", "-e", "100000"],
    #["-m", "qnet_ep250.pt", "-e", "100000"],
    #["-m", "qnet_ep500.pt", "-e", "41328"],
    #["-m", "qnet_ep600.pt", "-e", "60258"],
    #["-m", "qnet_ep700.pt", "-e", "100000"],
    #["-m", "qnet_ep800.pt", "-e", "100000"],
]

for lst in arg:
    main_eval_random_loop(lst)
