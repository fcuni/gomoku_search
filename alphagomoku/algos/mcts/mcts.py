"""
Csabas UCB formula for selecting the best child node is:

Q(s, a) = Q_emp(s, a) + c * P(s, a) * sqrt(sum(N(s)) / N(s, a))

where:
* Q_emp(s, a) is the value of the child node
* U(s, a) is the exploration term for the child node (the square root term)
* c is the exploration
* P(s, a) is the prior probability of the child node
* N(s) is the visit count of the parent
* N(s, a) is the visit count of the child

The MCTS implementation in this file is heavily motivated by the MuZero paper, see appendix B.2 in
https://arxiv.org/pdf/1911.08265.
"""

from copy import deepcopy
from dataclasses import dataclass

import numpy as np
import torch
from algos.mcts.mcts_utils import TreeNode, TreeStats
from game.gomoku_utils import PlayerEnum
from rl_env.env import GomokuEnv


@dataclass
class MCTSConfig:
    """Configuration for MCTS."""
    num_simulations: int = 80
    "Number of simulations to run."
    ct: float = 1.0
    "Exploration constant."
    dirichlet_alpha: float = 0.03
    "Dirichlet noise alpha parameter."
    exploration_fraction: float = 0.25
    "Fraction of exploration."
    rollout_fraction: float = 0.25
    "Fraction of rollout."
    temperature: float = 1.0
    "Temperature for softmax."
    dirichlet_epsilon: float = 0.25
    "Dirichlet noise epsilon parameter"
    deterministic: bool = False
    "Deterministic flag."
    ## Muzero specific parameters
    use_muzero: bool = False
    """Whether to use the MuZero setup."""
    mu_ct_second: float = 19652
    "Initial value for the log correction to the UCB formula. Default is from the MuZero paper."
    mu_ct: float = 1.25
    "Initial value for the UCB exploration constant. Default is from the MuZero paper."


class MCTS:
    """
    Monte Carlo Tree Search.

    In the language of MCTS, the tree is made up of parents and children. When translating back to the RL setup, each
    node in the tree is a state, and we transition through states by taking actions that define (state, action) pairs
    as edges of the tree.
    """
    def __init__(self, mcts_config: MCTSConfig | None = None, policy_network: torch.nn.Module | None = None):
        self.config = mcts_config or MCTSConfig()
        self.policy_network = policy_network

    def _single_rollout(self, root_node: TreeNode, tree_stats: TreeStats,
                        env: GomokuEnv) -> tuple[list[TreeNode], float]:
        current_node = root_node
        valid_actions = env.get_valid_actions()
        tree_path = [current_node]
        reward = 0
        next_children = None
        done = True

        while not current_node.is_leaf():
            next_action, next_children = self.select_children(current_node, tree_stats)
            _, reward, done, _, _ = env.step(next_action)

        assert done, f"We have found a terminal state on the MCTS tree but the environmnet is not done, {next_children}"
        if self.policy_network:
            last_board = env.game.board.to_numpy()
            parent_hidden_state = tree_path[-2].hidden_state
            policy_logits, hidden_state = self.policy_network.predict(last_board, parent_hidden_state)
        else:    # If we do not have a policy network, we will use a uniform policy
            policy_logits = np.zeros(len(valid_actions))
            hidden_state = None
        current_node.expand(
            env.game.current_player,
            valid_actions,
            hidden_state=hidden_state,
            policy_logits=policy_logits,
            reward=reward
        )

    def run(self, env: GomokuEnv):
        cloned_env = deepcopy(env)
        tree_stats = TreeStats()
        root_node = TreeNode(
            prior=1.0,
            to_play=env.game.current_player,
            children={a: TreeNode(prior=1.0) for a in env.get_valid_actions()}
        )

        for _ in range(self.config.num_simulations):
            tree_path, end_value = self._single_rollout(root_node, tree_stats, cloned_env)
            self._backpropagate(tree_path, end_value, player, tree_stats)

    def _backpropagate(self, tree_path: list[TreeNode], end_value: float, player: PlayerEnum, tree_stats: TreeStats):
        for node in tree_path:
            node.value_sum += end_value if node.to_play == player else -end_value
            node.visit_count += 1
            tree_stats.update(node.value())

    def select_children(self, node: TreeNode, tree_stats: TreeStats) -> tuple[int, TreeNode]:
        scores = []
        for action, child_node in node.children.items():
            scores.append((self.compute_ucb_score(child_node, node.visit_count, tree_stats), action, child_node))
        _, best_action, best_child_node = max(scores, key=lambda x: x[0])
        return best_action, best_child_node

    def compute_ucb_score(self, node: TreeNode, parent_visit_count: int, tree_stats: TreeStats) -> float:
        """Compute the UCB score for a node. If use_muzero is True, use the Muzero formula, otherwise use Csabas formula."""
        if self.config.use_muzero:
            return self._compute_ucb_score_muzero(node, parent_visit_count, tree_stats)
        prior_score = self.config.ct * node.prior * np.sqrt(parent_visit_count) / (1 + node.visit_count)
        if node.visit_count == 0:
            return prior_score
        return prior_score + node.value()

    def _compute_ucb_score_muzero(self, node: TreeNode, parent_visit_count: int, tree_stats: TreeStats) -> float:
        """Compute the UCB score for a node using the Muzero formula (B.2) in https://arxiv.org/pdf/1911.08265."""
        # Prior for the state-action pair, P(s, a)
        p_s_a = node.prior
        # UCB fraction, sqrt(sum_b N(s,b)) / (N(s, a) + 1)
        ucb_frac = np.sqrt(parent_visit_count) / (1 + node.visit_count)
        # MuZero introduces a log-correction to Csabas UCB formula
        log_correction = np.log((parent_visit_count + self.config.mu_ct_second + 1) / self.config.mu_ct_second)
        # The exploration term in the UCB is just given by,
        exploration_term = p_s_a * ucb_frac * (self.config.mu_ct + log_correction)
        return exploration_term + tree_stats.normalise(node.value())
