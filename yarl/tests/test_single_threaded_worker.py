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

import unittest

from yarl.agents.random_agent import RandomAgent
from yarl.envs import OpenAIGymEnv
from yarl.execution.single_threaded_worker import SingleThreadedWorker


class TestSingleThreadedWorker(unittest.TestCase):

    environment = OpenAIGymEnv(gym_env='CartPole-v0')

    def test_timesteps(self):
        """
        Simply tests if timestep execution loop works and returns a result.
        """
        agent = RandomAgent(
            actions_spec=self.environment.action_space,
            states_spec=self.environment.observation_space
        )
        worker = SingleThreadedWorker(
            environment=self.environment,
            agent=agent,
            repeat_actions=1
        )

        result = worker.execute_timesteps(100)
        self.assertLessEqual(result['episodes_executed'], 100)
        self.assertGreater(result['episodes_executed'], 0)

    def test_episodes(self):
        """
        Simply tests if episode execution loop works and returns a result.
        """
        agent = RandomAgent(
            actions_spec=self.environment.action_space,
            states_spec=self.environment.observation_space
        )
        worker = SingleThreadedWorker(
            environment=self.environment,
            agent=agent,
            repeat_actions=1
        )

        result = worker.execute_episodes(5, max_timesteps_per_episode=10)
        # Max 5 * 10.
        self.assertLessEqual(result['timesteps_executed'], 50)
