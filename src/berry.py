from numpy.random import rand


# Create berry agent
class Berry(object):
    state_list = ['green', 'colour_break_1', 'colour_break_2', 'pink', 'cherry', 'blue']
    states = dict()
    states['green'] = 21
    states['colour_break_1'] = 18
    states['colour_break_2'] = 11
    states['pink'] = 5
    states['cherry'] = 3
    states['blue'] = 0

    def __init__(self, global_days):
        self.global_days = global_days
        self.total_age = 0
        self.stage_age = 0
        self.state = 'green'
        self.in_terminal_state = False

    def step(self, global_days, loss_prob):
        self.global_days = global_days
        self.total_age += 1
        self.stage_age += 1
        if not self.in_terminal_state:
            self.update_stage(loss_prob)
        return self

    def pick(self):
        if self.state == 'blue':
            self.in_terminal_state = True
            self.state = 'picked'
            self.stage_age = 0
        return self

    def loose(self):
        """Set state to loose if berry is lost"""
        if not self.in_terminal_state:
            self.in_terminal_state = True
            self.state = 'lost'
            self.stage_age = 0
        return self

    def get_param(self):
        params = dict()
        params['global_days'] = self.global_days
        params['state'] = self.state
        params['stage_age'] = self.stage_age
        params['total_age'] = self.total_age
        params['states'] = self.states
        return params

    def set_param(self, **kwargs):
        if 'global_days' in kwargs:
            self.global_days = kwargs['global_days']
        if 'state' in kwargs:
            self.state = kwargs['state']
        if 'stage_age' in kwargs:
            self.stage_age = kwargs['stage_age']
        if 'total_age' in kwargs:
            self.total_age = kwargs['total_age']
        if 'states' in kwargs:
            self.states = kwargs['states']

    def update_stage(self, loss_prob):
        # change state
        # check if time to transition to the next state
        if self.states[self.state] < self.stage_age:
            i = self.state_list.index(self.state) + 1
            # sequentially move to next state
            if i < len(self.state_list):
                # has chance of getting lost
                if rand() <= loss_prob:
                    self.loose()
                else:
                    self.state = self.state_list[i]
                self.stage_age = 0

    def __str__(self):
        return 'State: "{}" stage age: {} total age: {} transition times:{}'.format(self.state, self.stage_age, self.total_age,self.states)
