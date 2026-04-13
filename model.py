import numpy as np

# -----------------------
# BASIC WEIGHTS
# -----------------------
def compute_weights(n):
    return np.ones(n)


# -----------------------
# NORMALIZATION
# -----------------------
def normalize(x):
    x = np.array(x, dtype=float)
    total = np.sum(x)

    if total == 0:
        return np.ones(len(x)) / len(x)

    return x / total


# -----------------------
# PROBABILITIES
# -----------------------
def compute_probabilities(weights):
    return normalize(weights)


# -----------------------
# EXPECTED REWARDS
# -----------------------
def expected_rewards(probabilities, total_pool):
    probabilities = np.array(probabilities)
    return probabilities * total_pool


# -----------------------
# FAIRNESS METRICS
# -----------------------
def fairness_variance(probabilities):
    return float(np.var(probabilities))


def fairness_entropy(probabilities):
    """
    Higher entropy = more fair
    """
    p = np.array(probabilities)
    p = p[p > 0]  # remove zeros

    return float(-np.sum(p * np.log(p)))


def fairness_metric(probabilities):
    """
    Combined fairness (lower variance + higher entropy)
    """
    var = fairness_variance(probabilities)
    ent = fairness_entropy(probabilities)

    return {
        "variance": var,
        "entropy": ent
    }


# -----------------------
# DRAW WINNER
# -----------------------
def run_draw(members, probabilities):

    if len(members) == 0:
        return None

    probabilities = normalize(probabilities)

    return np.random.choice(members, p=probabilities)


# -----------------------
# TRUST-BASED MODEL
# -----------------------
def trust_based_weights(success_counts, total_counts, alpha=1, beta=1):
    """
    Bayesian Beta model:
    θ_i = (alpha + success) / (alpha + beta + total)
    """

    success_counts = np.array(success_counts)
    total_counts = np.array(total_counts)

    theta = (alpha + success_counts) / (alpha + beta + total_counts)

    return theta


# -----------------------
# CONTRIBUTION-BASED MODEL
# -----------------------
def contribution_weights(contributions):
    """
    Higher contribution → higher weight
    """
    contributions = np.array(contributions)
    return normalize(contributions)


# -----------------------
# HYBRID MODEL
# -----------------------
def hybrid_weights(trust, contributions, lambda_=0.5):
    """
    Combine trust + contribution
    """
    trust = normalize(trust)
    contributions = normalize(contributions)

    return lambda_ * trust + (1 - lambda_) * contributions


# -----------------------
# CYCLE-AWARE FILTER
# -----------------------
def filter_eligible(members, winners):
    """
    Remove already rewarded members
    """
    return [m for m in members if m not in winners]


# -----------------------
# SIMULATION ENGINE
# -----------------------
def simulate_draws(members, probs, n_sim=1000):
    """
    Monte Carlo simulation of winners
    """
    results = []

    for _ in range(n_sim):
        winner = run_draw(members, probs)
        results.append(winner)

    return results


# -----------------------
# RISK (VARIANCE OF REWARD)
# -----------------------
def reward_risk(probabilities, total_pool):
    rewards = expected_rewards(probabilities, total_pool)
    return float(np.var(rewards))
