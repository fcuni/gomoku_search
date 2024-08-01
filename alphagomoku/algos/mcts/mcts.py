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

import os
import time
from copy import deepcopy
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
from algos.mcts.mcts_utils import TreeNode, TreeStats
from experiment_logging.base_logging_connector import (
    BaseLoggingConnector,
    NoopLoggingConnector,
)
from experiment_logging.wandb_connector import WandBConnector
from game.gomoku_utils import GridPosition, Move, PlayerEnum
from rl_env.env import GomokuEnv


@dataclass
class MCTSConfig:
    """Configuration for MCTS."""
    num_simulations: int = 800
    "Number of simulations to run."
    ct: float = 5.0
    "Exploration constant."
    initial_prior: float = 1.0
    "Initial prior for unexpanded nodes."
    add_root_noise: bool = False
    "Whether to add Dirichlet noise to the root node."
    dirichlet_alpha: float = 0.03
    "Dirichlet noise alpha parameter."
    exploration_fraction: float = 0.25
    "Exploration fraction for the Dirichlet noise added to the root node."
    deterministic: bool = False
    "Deterministic flag."
    # TODO: Fix parallelisation, see below. Use only one worker for now.
    max_workers: int = 1    #  field(default_factory=lambda: os.cpu_count() // 2)    # type: ignore
    "Number of workers to use for parallel simulations."
    ## Muzero specific parameters
    use_muzero: bool = False
    """Whether to use the MuZero setup."""
    mu_ct_second: float = 19652
    "Initial value for the log correction to the UCB formula. Default is from the MuZero paper."
    mu_ct: float = 1.25
    "Initial value for the UCB exploration constant. Default is from the MuZero paper."
    # Metric logger
    metric_logger: BaseLoggingConnector = WandBConnector()


class MCTS:
    """
    Monte Carlo Tree Search.

    In the language of MCTS, the tree is made up of parents and children. When translating back to the RL setup, each
    node in the tree is a state, and we transition through states by taking actions that define (state, action) pairs
    as edges of the tree.
    """
    def __init__(self, policy_network: torch.nn.Module | None = None, mcts_config: MCTSConfig = MCTSConfig()):
        self.config = mcts_config
        self.policy_network = policy_network
        self.tree_stats: TreeStats = TreeStats()
        self.root_node: TreeNode | None = None
        self.logger = mcts_config.metric_logger
        self.logger.start()
        self.rollout_metrics = {
            "won_ratio": 0.,
            "draw_ratio": 0.,
            "lost_ratio": 0.,
            "matches_played": 0,
        }

    def _single_rollout(self, root_node: TreeNode, tree_stats: TreeStats,
                        env: GomokuEnv) -> tuple[list[TreeNode], float, PlayerEnum | None]:
        """
        Rollout a from a given root node and return the necessary quantities to backpropagate.

        If we reach a unexpanded node, we expand it and random walk from one of the children until we reach a terminal state.
        """
        current_node = root_node
        starting_player = env.game.current_player
        tree_path = [current_node]
        reward = 0
        next_children = None
        done = False

        if self.config.add_root_noise:
            # add Dirichlet noise, a la AlphaX papers
            current_node.add_exploration_noise(self.config.dirichlet_alpha, self.config.exploration_fraction)

        while current_node.is_expanded:
            # while the node has children, select the best child node as (p)UCT
            next_action, next_children = self.select_children(current_node, tree_stats)
            _, reward, done, _, _ = env.step(next_action)
            tree_path.append(next_children)
            current_node = next_children

        # when reaching an unexpanded node, expand it
        if not done:
            if self.policy_network:
                last_board = env.game.board.to_numpy()
                parent_hidden_state = tree_path[-2].hidden_state
                policy_logits, hidden_state = self.policy_network.predict(last_board, parent_hidden_state)
            else:
                policy_logits = None
                hidden_state = None
            current_node.expand(
                ~env.game.current_player,
                env.get_valid_actions(),
                hidden_state=hidden_state,
                policy_logits=policy_logits,
            )

        # simulate to the end of the game and return the path and end reward to backpropagate
        while not done:
            next_action = np.random.choice(env.get_valid_actions())
            _, reward, done, _, _ = env.step(next_action)
        winner = env.game.game_data.winner
        self.rollout_metrics["matches_played"] += 1
        if winner is None:
            self.rollout_metrics["draw_ratio"] = (
                self.rollout_metrics["draw_ratio"] * (self.rollout_metrics["matches_played"] - 1) + 1
            ) / self.rollout_metrics["matches_played"]
        elif winner == starting_player:
            self.rollout_metrics["won_ratio"] = (
                self.rollout_metrics["won_ratio"] * (self.rollout_metrics["matches_played"] - 1) + 1
            ) / self.rollout_metrics["matches_played"]
        else:
            self.rollout_metrics["lost_ratio"] = (
                self.rollout_metrics["lost_ratio"] * (self.rollout_metrics["matches_played"] - 1) + 1
            ) / self.rollout_metrics["matches_played"]
        return tree_path, reward, winner

    def run(self, env: GomokuEnv, visualise_policy: bool = False) -> Move:
        """
        The main MCTS loop.

        The loop is composed of the following steps:
        * Selection: Start from the root node and select the best child node until we reach an unexpanded node.
        * Expansion: If we reach an unexpanded node, expand it.
        * Simulation: Simulate the game until the end, by making random moves.
        * Backpropagation: Backpropagate the results of the simulation to the root node.

        The loop is repeated for a given number of simulations, and the best move is returned at the end.
        """
        starting_player = env.game.current_player
        self.tree_stats = TreeStats()
        self.root_node = TreeNode(
            prior=self.config.initial_prior,
            to_play=starting_player,
        )

        for n in range(self.config.num_simulations):
            cloned_env_ = deepcopy(env)
            tree_path, end_value, winner = self._single_rollout(self.root_node, self.tree_stats, cloned_env_)
            self._backpropagate(tree_path, end_value, winner, self.tree_stats)
            next_board_value = [child.value() for child in self.root_node.children.values()]
            if n % 1000 == 0:
                print(f"Done with {n}/{self.config.num_simulations} simulations.")
                next_board_value_np = np.array(next_board_value).reshape(env.game.board.size)
                self.logger.log_array("next_board_value", next_board_value_np)

            metrics = self.rollout_metrics.copy()
            metrics.update({
                "max_next_board_value": max(next_board_value),
                "min_next_board_value": min(next_board_value),
                "mean_next_board_value": np.mean(next_board_value),
            })
            self.logger.log(metrics)

        # once the simulation is done, return best Move
        best_action, _ = self.select_children(self.root_node, self.tree_stats)

        if visualise_policy:
            self.plot_policy_for_node(self.root_node, board_size=env.game.board.size, store_plot=True)

        return Move(player=starting_player, position=GridPosition.from_int(best_action, board_size=env.game.board.size))

    def _backpropagate(
        self, tree_path: list[TreeNode], end_value: float, winner: PlayerEnum | None, tree_stats: TreeStats
    ):
        for node in tree_path:
            node.value_sum += end_value if node.to_play == winner else -end_value
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
        return prior_score + tree_stats.normalise(node.value())

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

    def plot_policy_for_node(
        self,
        node: TreeNode,
        board_size: tuple[int, int],
        store_plot: bool = False,
        plot_filename: str = "policy_heatmap.png"
    ):
        """
        Plot the policy for a given node.

        Plots the policy as a heatmap for the given node. It can also store the plot in the current working
        directory under the given filename.
        """
        all_children_v = np.array([c.value() for c in node.children.values()]).reshape(board_size)

        # make plot with seaborn and store it if necessary
        plt.figure(figsize=(8, 8))
        sns.heatmap(all_children_v, annot=True, fmt=".2f", cmap="viridis")

        if store_plot:
            plt.savefig(plot_filename)
            print(f"Stored heatmap of policy in {os.getcwd()}/{plot_filename}_{time.time()}")

        plt.show()
