# Copyright 2018 The YARL-Project, All Rights Reserved.
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

from yarl import backend, YARLError, DictOp
from yarl.models.model import Model

from .assert_util import recursive_assert_almost_equal


class ComponentTest(object):
    """
    A very simple (and limited) Model-wrapper to test a single component in a very easy and straightforward
    way.
    """
    def __init__(self, component, input_spaces, seed=10):
        """
        Args:
            component (Component): The Component to be tested (may contain sub-components).
            input_spaces (dict): Dict with component's in-Socket names as keys and Space objects as values.
                Describes the input Spaces for the component.
            seed (Optional[int]): The seed to use for random-seeding the Model object.
                If None, do not seed the Graph (things may behave non-deterministically).
        """
        self.seed = seed

        # Create our Model.
        self.model = Model.from_spec(backend(), execution_spec=dict(seed=self.seed))

        # Add the component to test and expose all its Sockets to the core component of our Model.
        self.core = self.model.get_default_model()
        self.core.add_component(component, expose=True)

        # Add the input-spaces to the in-Sockets.
        for in_socket in self.core.input_sockets:
            name = in_socket.name
            assert name in input_spaces, "ERROR: input_spaces does not contain in-Socket name '{}'!".\
                format(name)
            self.core.connect(input_spaces[name], name)

        # Build the model.
        self.model.build()

    def test(self, out_socket_name, inputs, expected_outputs):
        """
        Does one test pass through the component to test.

        Args:
            out_socket_name (str): The name of the out-Socket to trigger (only one at a time for now).
            inputs (Union[dict,str]): Dict with the in-Socket names as keys and the data (np.arrays, dicts, tuples)
                as values. If not a dict and we only have one in-Socket, in-Socket name (str) may be given.
            expected_outputs (any): The expected output generated by the out-Socket given by `out_socket_name`.

        Returns:
            Whether the test failed or not.
        """
        # We have only one in-Socket and its name (str) is given directly.
        num_inputs = len(self.core.input_sockets)
        only_input = None
        if num_inputs == 1:
            only_input = self.core.get_socket(type_="in").name
        if not isinstance(inputs, dict) or only_input:
            inputs_as_dict = dict({only_input: inputs})
            inputs = inputs_as_dict

        # Get the outs ..
        outs = self.model.call(sockets=out_socket_name, inputs=inputs)
        # .. and compare them with what we want.
        recursive_assert_almost_equal(outs, expected_outputs)

    def get_variable_values(self, variables):
        """
        Executes a session to retrieve the values of the provided variables.
        Args:
            variables (list): Variable objects to retrieve from the graph.

        Returns:
            list: Values of the variables provided.
        """
        return self.model.get_variable_values(variables)

