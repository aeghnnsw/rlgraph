# Copyright 2018/2019 The RLgraph authors, All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from rlgraph.components import Stack, Layer, get_backend
from rlgraph.components.layers.nn.concat_layer import ConcatLayer
from rlgraph.components.neural_networks.neural_network import NeuralNetwork
from rlgraph.utils.decorators import rlgraph_api

if get_backend() == "tf":
    import tensorflow as tf
elif get_backend() == "pytorch":
    import torch


class SACValueNetwork(NeuralNetwork):
    """
    Value network for SAC which must be able to merge different input types.
    """
    def __init__(self, network_spec, scope="sac-value-network", **kwargs):
        """
        Args:
            network_spec (dict): Network spec.
        """
        super(SACValueNetwork, self).__init__(scope=scope, **kwargs)

        self.network_spec = network_spec

        self.image_stack = None
        self.dense_stack = None

        # If first layer is conv, build image stack.
        self.use_image_stack = self.network_spec[0]["type"] == "conv2d"
        self.build_stacks()

        # The concatenation layer.
        self.concat_layer = ConcatLayer()

        # Add all sub-components to this one.
        if self.image_stack is not None:
            self.add_components(self.image_stack)

        self.add_components(self.dense_stack, self.concat_layer)

    def build_stacks(self):

        """
        Builds a dense stack and optionally an image stack.
        """
        if self.use_image_stack:
            sub_components = []
            for layer_spec in self.network_spec:
                if layer_spec["type"] in ["conv2d", "reshape"]:
                    sub_components.append(Layer.from_spec(layer_spec))
            self.image_stack = Stack(sub_components, scope="image-stack")

        else:
            # Assume dense network otherwise -> onyl a single stack.
            sub_components = []
            for layer_spec in self.network_spec:
                assert layer_spec["type"] == "dense", "Only dense layers allowed if not using" \
                                                      " image stack in this network."
                sub_components.append(Layer.from_spec(layer_spec))
            self.dense_stack = Stack(sub_components, scope="dense-stack")

    @rlgraph_api
    def apply(self, state_actions):
        """
        Computes Q(s,a) by passing states and actions through one or multiple processing stacks.

        Args:
            state_actions (list): Tuple containing state and flat actions.
        """
        states = state_actions[0]
        actions = state_actions[1:]
        if self.use_image_stack:
            image_processing_output = self.image_stack.apply(states)

            # Concat everything together.
            concatenated_data = self.concat_layer.apply(
                image_processing_output,  actions
            )

            dense_output = self.dense_stack.apply(concatenated_data)
        else:
            # Concat states and actions, then pass through.
            concat_state_actions = None
            if get_backend() == "tf":
                concat_state_actions = tf.concat(state_actions, axis=-1)
            elif get_backend() == "pytorch":
                concat_state_actions = torch.cat(state_actions, dim=-1)
            dense_output = self.dense_stack.apply(concat_state_actions)
        return dense_output