import wandb
import subprocess
wandb.login()


# Define sweep configuration
sweep_config = {
    "name": "chronumental-sweep",
    "program": "chronumental.py",
    "method": "bayes",
    "metric": {
        "name": "combination",
        "goal": "minimize"
    },
    "parameters": {
        "lr": {
            "distribution": "log_uniform",
            "min": -5,
            "max": -1
        },
        "steps": {
            "distribution": "int_uniform",
            "min": 3000,
            "max": 7000
        },
        "variance_dates": {
            "distribution": "log_uniform",
            "min": -5,
            "max": 2
        },
        "initial_tau": {
            "distribution": "log_uniform",
            "min": -3,
            "max": 3
        },
        "hs_scale": {
            "distribution": "log_uniform",
            "min": 10,
            "max": 40
        },

        "model": {
            "values": [#"DeltaGuideWithStrictLearntClock",
                        "HorseShoeLike"
                        ]
        }
        
       
        
    }
}

# we want to call at the command line with the parameters

import random 

# Define sweep agent
sweep_id = wandb.sweep(sweep_config, project="chronumental")


# !python -m chronumental --dates tree_dates.tsv --tree time_tree.nwk --treat_mutation_units_as_normalised_to_genome_size 1000 --output_unit years  --use_wandb --steps 15000 --lr 0.02
def run():
    my_run = wandb.init()
    config = my_run.config
    my_id  = my_run.id
    # run the command line
    command = ["python", "-m chronumental", "--lr", str(config.lr), "--steps", str(config.steps), "--variance_dates", str(config.variance_dates), "--model", str(config.model),  "--dates", "tree_dates.tsv", "--tree", "time_tree.nwk", "--treat_mutation_units_as_normalised_to_genome_size", "1000", "--output_unit", "years", "--dates_out", f"dates_{my_id}.tsv", "--tree_out", f"tree_{my_id}.nwk","--initial_tau", str(config.initial_tau), "--hs_scale", str(config.hs_scale)]
    print(" ".join(command))
    subprocess.check_call(" ".join(command), shell=True)
    # to get rmse we call compare.py time_tree.nwk chronumental_timetree_time_tree.nwk and read stdout as float

    output = subprocess.check_output(["python", "compare.py", "time_tree.nwk", f"tree_{my_id}.nwk","--tsv1", "tree_dates.tsv","--tsv2", f"dates_{my_id}.tsv"])
    rmse, rmse2, median_squared_days = output.split(b",")
    rmse = float(rmse)
    rmse2 = float(rmse2)
    median_squared_days = float(median_squared_days)
   
    median_squared = median_squared_days/365
    wandb.log({"rmse": rmse,"rmse2": rmse2, "median_squared": median_squared})
    combination = rmse + median_squared
    wandb.log({"combination": combination})
    return {"rmse": rmse}



wandb.agent(sweep_id, run)


