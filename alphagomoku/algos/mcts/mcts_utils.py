from dataclasses import dataclass, field

import numpy as np
from game.gomoku_utils import PlayerEnum


@dataclass
class TreeStats:
    """Node statistics, including the maximum and mininum values in the tree."""
    maximum: float = -np.inf
    mininum: float = np.inf

    def update(self, value: float):
        self.maximum = max(self.maximum, value)
        self.mininum = min(self.mininum, value)

    def normalise(self, value: float):
        """Normalise the value between 0 and 1. Only normalise if the maximum and mininum has been set."""
        if self.maximum > self.mininum:
            return (value - self.mininum) / (self.maximum - self.mininum)
        return value


@dataclass
class TreeNode:
    """Node in the MCTS tree."""
    prior: float
    """Prior probability of selecting the node."""
    visit_count: int = 0
    """Visit count of the node."""
    to_play: PlayerEnum | None = None
    """Player to play at the node."""
    children: dict[int, "TreeNode"] = field(default_factory=dict)
    """Children of the node."""
    value_sum: float = 0.0
    """Sum of the values of the games obtained by traversing the node."""
    # extra info to use with neural networks
    hidden_state: np.ndarray | None = None
    """Hidden state of the node."""
    reward: float = 0.0
    """Reward of the node, in case a value function is used."""
    @property
    def is_expanded(self) -> bool:
        return len(self.children) != 0

    def value(self) -> float:
        if self.visit_count == 0:
            return 0
        return self.value_sum / self.visit_count

    def expand(
        self,
        to_play: PlayerEnum,
        actions: np.ndarray,
        hidden_state: np.ndarray | None = None,
        reward: float = 0.0,
        policy_logits: np.ndarray | None = None
    ):
        """
        Expand the node by adding children.

        The prior is computed from the policy logits, if given. Otherwise, it is set to 1.
        """
        assert actions.ndim == 1, f"Expect the dimensions in the actions array to be (1,), but got {actions.ndim}"
        self.to_play = to_play
        self.hidden_state = hidden_state
        self.reward = reward
        if policy_logits is None:
            policy_logits = np.zeros(len(actions))
        norm_sum = np.sum(np.exp(policy_logits))
        prior = {a: np.exp(policy_logits[ix]) / norm_sum for ix, a in enumerate(actions)}
        self.children = {action: TreeNode(prior=prior[action]) for action in actions.tolist()}

    def add_exploration_noise(self, dirichlet_alpha: float, exploration_fraction: float):
        """In the root node, add Dirichlet noise to the prior of the children. This is the recipe used in the AlphaZero-like papers."""
        valid_actions = list(self.children.keys())
        noise = np.random.dirichlet([dirichlet_alpha] * len(valid_actions))
        for action, n in zip(valid_actions, noise):
            self.children[action
                         ].prior = self.children[action].prior * (1 - exploration_fraction) + n * exploration_fraction
