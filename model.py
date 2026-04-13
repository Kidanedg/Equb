import numpy as np
import pandas as pd

def compute_weights(n):
    return np.ones(n)

def compute_probabilities(weights):
    return weights / weights.sum()

def expected_rewards(probs, total):
    return probs * total

def variance(probs, total):
    return probs * (1 - probs) * (total**2)

def run_draw(members, probs):
    return np.random.choice(members, p=probs)

def fairness_metric(probs):
    return np.var(probs)
