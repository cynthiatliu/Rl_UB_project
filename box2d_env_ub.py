from rllab.envs.box2d.box2d_env import Box2DEnv
from rllab.core.serializable import Serializable
from rllab.misc import autoargs
from rllab.misc.overrides import overrides
from rllab.spaces import UBSpace

import re

BIG = 1e6
class Box2DEnvUB(Box2DEnv, Serializable):
    @autoargs.arg("frame_skip", type=int,
                  help="Number of frames to skip")
    @autoargs.arg('obs_noise', type=float,
                  help='Noise added to the observations (note: this makes the '
                  'problem non-Markovian!)')
    
    @autoargs.inherit(Box2DEnv.__init__)
    def __init__(self, filename=None, *args, **kwargs):
        super(Box2DEnvUB, self).__init__(*args, **kwargs)
        experiment_space = UBSpace("LaMnO3 reflections.txt")
        
        self.hkl_actions = experiment_space.get_hkl_actions()
        self.hkl_space = experiment_space.get_discrete()
        self.all_space = experiment_space.get_all_actions()
        self.last_discrete = experiment_space.get_last_discrete()
    
    @property
    @overrides
    def action_space(self):
        return cont_space
    
    @property
    @overrides
    def observation_space(self):
        d = len(self.extra_data.states)
        ubnd = BIG * np.ones(d)
        return spaces.Box(0, ub) #no such thing as negative structure factor
    
    @overrides
    def forward_dynamics(self, action):
        raise NotImplementedError
    
    @overrides
    def compute_reward(self, action, observation):
        """
        The implementation of this method should have two parts, structured
        like the following:

        <perform calculations before stepping the world>
        yield
        reward = <perform calculations after stepping the world>
        yield reward
        """
        raise NotImplementedError
    
    @overrides
    def step(self, action, observation):
        """   This is identical to the
        original step method, except it takes one more
        parameter (needed by compute_reward).    """
        
        reward_computer = self.compute_reward(action, observation)
        #forward the state
        action = self._inject_action_noise(action)
        for _ in range(self.frame_skip):
            self.forward_dynamics(action)
        # notifies that we have stepped the world
        reward_computer.next()
        # actually get the reward
        reward = reward_computer.next()
        self._invalidate_state_caches()
        done = self.is_current_done()
        next_obs = self.get_current_obs(action)
        return Step(observation=next_obs, reward=reward, done=done)
    
    @overrides
    #CHANGE TO MACHINE READING LATER
    def get_raw_obs(self, action):
        """   Unlike in traditional physics problems, the
        observations are not positions and velocities
        Here, our observations will be read directly from the machine
        
        Now, we are spoon-feeding the program as to whether
        significant observations were made in scans
        """
        choice = action[0]
        if choice == 0:
            ind = action[3]
            assert self.hkl_space.contains(ind), "Sorry, your hkl vector input does not exist for this crystal"
            h_vec = self.hkl_actions[ind]
            self.last_discrete = ind
            
            good = False
            while good != True:
                try:
                    yesorno = int(raw_input("Do you think our first UB matrix was correct? Type 0 if no and 1 if yes. "))
                    if yesorno == 0 or yesorno == 1: good = True
                    else: print "Please input a valid integer"
                except:
                    print "Please input a numerical value"
                    
            if yesorno == 1:
                intensity = self.obs[ind][0]; f_2 = self.obs[ind][1]
                observation = [intensity, f_2]
            else:
                observation = [0,0]
                
        elif choice == 1:
            chi = action[1]; phi = action[2]
            good = False
            while good != True:
                try:
                    yesorno = int(raw_input("We have no moved to %d, %d /"
                    "Do we see a significant peak at this location? Type 0 if no and 1 if yes " % (chi, phi)))
                    if yesorno == 0 or yesorno == 1: good = True
                    else: print "Please input a valid integer"
                except:
                    print "Please input a numerical value"
            
            if yesorno == 1:
                intensity = self.obs[self.last_discrete][0]; f_2 = self.obs[self.last_discrete][1]
                observation = [intensity, f_2]
            else:
                observation = [0, 0]
                
        return observation
    
    @overrides
    def get_current_obs(self, action):
        """ Identical to box2d_env's method, but with different paramters """
        raw_obs = self.get_raw_obs(action)
        noisy_obs = self._inject_obs_noise(raw_obs)
        if self.position_only:
            return self._filter_position(noisy_obs)
        return noisy_obs        
    
    @overrides
    def _get_position_ids(self):
        if self._position_ids is None:
            self._position_ids = []
            for idx, state in enumerate(self.extra_data.states):
                if state.typ in ["xpos", "ypos", "apos", "dist", "angle"]:
                    if state.typ == "xpos": self._position_ids.append("chi")
                    elif state.typ == "ypos": self._position_ids.append("phi")
                    else: self._position_ids.append(state.typ)
                    
        return self._position_ids
