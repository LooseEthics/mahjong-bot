# Mahjong model top level scripts

## Training

### model_train_loop.py [-m model] [-e num] [-v]
Trains a model on self-play for a given number of episodes.
Defaults to the latest model.
Default number of episodes is 1000.
Saves game results to game_results_training.txt.

## Evaluation

### model_eval_random_loop.py [-m model] [-e num] [-v] [-w]
Evaluates random games using model.
Defaults to the latest model.
Default number of episodes is 1.
Saves game results to game_results_eval.txt.

### model_eval_single.py -s state [-m model] [-v] [-w]
Loads and evaluates saved game state using model.
Defaults to the latest model.
Saves game results to game_results_eval.txt.

## Options
- `-e num`
Specifies number of episodes the script is to run.
An episode is one game.
- `-m model`
  Specifies model to be used.
  Loaded from `checkpoints` folder.
- `-s state`
  Specifies game state to load.
- `-v`
  Verbose flag.
  Prints game state after each decision.
- `-w`
  Wait flag.
  Pauses evaluation after each decision.

# Utility scripts
### model_visualizer.py -m model
Creates a visual representation of model layers.

### summarize_results.py
Parses and summarizes game_results_eval.txt.
