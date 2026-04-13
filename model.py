import numpy as np

# -----------------------
# INITIAL WEIGHTS
# -----------------------
def compute_weights(n):
    # Equal weights (can upgrade later to trust-based)
    return np.ones(n)

# -----------------------
# PROBABILITIES
# -----------------------
def compute_probabilities(weights):
    total = np.sum(weights)
    if total == 0:
        return np.ones(len(weights)) / len(weights)
    return weights / total

# -----------------------
# EXPECTED REWARDS
# -----------------------
def expected_rewards(probabilities, total_pool):
    return probabilities * total_pool

# -----------------------
# FAIRNESS METRIC
# -----------------------
def fairness_metric(probabilities):
    """
    Using variance: lower variance = more fair
    """
    return float(np.var(probabilities))

# -----------------------
# RUN DRAW
# -----------------------
def run_draw(members, probabilities):
    if len(members) == 0:
        return None

    probabilities = np.array(probabilities)

    # Normalize again (safety)
    probabilities = probabilities / probabilities.sum()

    winner = np.random.choice(members, p=probabilities)
    return winner

# -----------------------
# OPTIONAL: TRUST WEIGHTS (FUTURE)
# -----------------------
def trust_based_weights(trust_scores):
    """
    trust_scores: array of values (0 to 1)
    """
    return np.array(trust_scores)

# -----------------------
# NORMALIZE ANY VECTOR
# -----------------------
def normalize(x):
    x = np.array(x)
    total = np.sum(x)
    if total == 0:
        return np.ones(len(x)) / len(x)
    return x / total
