# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import unittest

import rustworkx


class TestMinimumCycleBasis(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.graph = rustworkx.PyGraph()
        self.graph.add_nodes_from(list(range(10)))
        self.graph.add_edges_from_no_data(
            [
                (0, 1),
                (0, 3),
                (0, 5),
                (0, 8),
                (1, 2),
                (1, 6),
                (2, 3),
                (3, 4),
                (4, 5),
                (6, 7),
                (7, 8),
                (8, 9),
            ]
        )

    def test_minimum_cycle_basis_default_weights(self):
        """Test minimum_cycle_basis with default weights."""
        graph = rustworkx.PyGraph()
        graph.add_nodes_from(list(range(6)))
        graph.add_edges_from_no_data([(0, 1), (0, 3), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)])

        cycles = rustworkx.minimum_cycle_basis(graph)
        res = sorted(sorted(c) for c in cycles)
        self.assertEqual([[0, 1, 2, 3], [0, 3, 4, 5]], res)

    def test_minimum_cycle_basis_custom_weights(self):
        """Test minimum_cycle_basis with custom weight function."""
        graph = rustworkx.PyGraph()
        graph.add_nodes_from(list(range(6)))
        graph.add_edges_from_no_data([(0, 1), (0, 3), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)])

        def weight_fn(edge):
            source, target, weight = edge
            # Make edge (0, 5) more expensive
            if source == 0 and target == 5:
                return 3.0
            return 1.0

        cycles = rustworkx.minimum_cycle_basis(graph, weight_fn)
        res = sorted(sorted(c) for c in cycles)
        self.assertEqual([[0, 1, 2, 3], [0, 3, 4, 5]], res)

    def test_minimum_cycle_basis_tree(self):
        """Test minimum_cycle_basis with a tree (no cycles)."""
        tree = rustworkx.PyGraph()
        tree.add_nodes_from(list(range(4)))
        tree.add_edges_from_no_data([(0, 1), (1, 2), (2, 3)])

        cycles = rustworkx.minimum_cycle_basis(tree)
        self.assertEqual(cycles, [])

    def test_minimum_cycle_basis_empty_graph(self):
        """Test minimum_cycle_basis with an empty graph."""
        empty_graph = rustworkx.PyGraph()
        cycles = rustworkx.minimum_cycle_basis(empty_graph)
        self.assertEqual(cycles, [])

    def test_minimum_cycle_basis_invalid_types(self):
        """Test minimum_cycle_basis with invalid graph types."""
        digraph = rustworkx.PyDiGraph()
        with self.assertRaises(TypeError):
            rustworkx.minimum_cycle_basis(digraph)

    def test_minimum_cycle_basis_single_cycle(self):
        """Test minimum_cycle_basis with a single cycle."""
        graph = rustworkx.PyGraph()
        graph.add_nodes_from(list(range(3)))
        graph.add_edges_from_no_data([(0, 1), (1, 2), (2, 0)])

        cycles = rustworkx.minimum_cycle_basis(graph)
        res = sorted(sorted(c) for c in cycles)
        self.assertEqual([[0, 1, 2]], res)

    def test_minimum_cycle_basis_disconnected_cycles(self):
        """Test minimum_cycle_basis with disconnected cycles."""
        graph = rustworkx.PyGraph()
        graph.add_nodes_from(list(range(6)))
        graph.add_edges_from_no_data(
            [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)]  # Triangle  # Another triangle
        )

        cycles = rustworkx.minimum_cycle_basis(graph)
        res = sorted(sorted(c) for c in cycles)
        self.assertEqual([[0, 1, 2], [3, 4, 5]], res)

    def test_minimum_cycle_basis_weighted_edges(self):
        """Test minimum_cycle_basis with weighted edges."""
        graph = rustworkx.PyGraph()
        graph.add_nodes_from(list(range(6)))
        graph.add_edges_from_no_data([(0, 1), (0, 3), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)])

        def weight_fn(edge):
            source, target, weight = edge
            # Make some edges more expensive to test weight-based ordering
            if (source == 0 and target == 1) or (source == 1 and target == 0):
                return 2.0
            if (source == 0 and target == 5) or (source == 5 and target == 0):
                return 3.0
            return 1.0

        cycles = rustworkx.minimum_cycle_basis(graph, weight_fn)
        res = sorted(sorted(c) for c in cycles)
        # Should still find the same cycles but ordered by weight
        self.assertEqual([[0, 1, 2, 3], [0, 3, 4, 5]], res)

    def test_minimum_cycle_basis_self_loop(self):
        """Test minimum_cycle_basis with self loops."""
        self.graph.add_edge(1, 1, None)
        cycles = rustworkx.minimum_cycle_basis(self.graph)
        # Should handle self loops gracefully
        self.assertIsInstance(cycles, list)

    def test_minimum_cycle_basis_large_graph(self):
        """Test minimum_cycle_basis with a larger graph."""
        graph = rustworkx.PyGraph()
        graph.add_nodes_from(list(range(8)))
        graph.add_edges_from_no_data(
            [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 0),  # Square
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 4),  # Another square
                (0, 4),
                (1, 5),  # Connecting edges
            ]
        )

        cycles = rustworkx.minimum_cycle_basis(graph)
        res = sorted(sorted(c) for c in cycles)
        # Should find the two squares plus the cycle through connecting edges
        self.assertEqual([[0, 1, 2, 3], [0, 1, 4, 5], [4, 5, 6, 7]], res)
