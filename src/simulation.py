from datetime import timedelta

import numpy as np
from pandas import DataFrame
from scipy import stats

from .berry import Berry
from sklearn.preprocessing import StandardScaler


class BerryTransitionModel(object):
    _valid_cols =['green', 'colour_break_1', 'colour_break_2', 'pink', 'cherry']
    def __init__(self, green: int, colour_break_1: int, colour_break_2: int, pink: int, cherry: int, blue: int,
                 y_df: DataFrame, verbose: bool = True):
        self._verbose = verbose
        self.init_vals = dict()
        self.init_vals['green__init'] = green
        self.init_vals['colour_break_1__init'] = colour_break_1
        self.init_vals['colour_break_2__init'] = colour_break_2
        self.init_vals['pink__init'] = pink
        self.init_vals['cherry__init'] = cherry
        self.init_vals['blue__init'] = blue
        self.y_df = y_df
        self.days_since = y_df.days_since_start.values
        self.scalar = StandardScaler().fit(y_df[self._valid_cols])
        self.y_df_scaled = self.scalar.transform(self.y_df[self._valid_cols])

    def init_blueberries(self, param: dict):
        blueberries = []
        for state in param:
            blueberries += self.new_blueberries(param[state]['init'], state, 0, param)
        return blueberries

    def step(self, berry_list: list, global_age: int, params: dict):
        out_berries = []
        for berry in berry_list:
            # only loose for valid states
            if berry.state in params:
                loss_prob = params[berry.state]['loss']
            else:
                loss_prob = 0.
            out_berries.append(berry.step(global_age, loss_prob))
        return out_berries

    def sample_age(self, state: str, params: dict) -> int:
        if 'blue' == state:
            age = 0
        else:
            age = stats.poisson.rvs(params[state]['mu__init'])
        return round(abs(age))

    def sample_state_times(self, params: dict):
        stages = Berry(0).states
        trans_times = dict()
        for state in params:
            if 'blue' == state:
                trans_times[state] = 0
            else:
                trans_times[state] = abs(round(stats.norm.rvs(params[state]['mu__init'], params[state]['sigma__init'])))
        return trans_times

    def new_blueberries(self, n_berries: int, state: str, global_age: int, params: dict):
        new_berries = []
        for n_berry in range(n_berries):
            # create berry
            berry = Berry(global_age)
            # get starting age
            starting_age = self.sample_age(state, params)
            # get state transition times
            states = self.sample_state_times(params)
            berry.set_param(stage_age=0, state=state ,states=states)
            new_berries.append(berry)
        return new_berries

    def pick_berries(self, berry_list: list):
        return [berry.pick() for berry in berry_list]

    def loose_berries(self, berry_list: list, loss_param: dict):
        # sort berries into state
        out_berry = []
        for berry in berry_list:
            # check if in terminal state
            if berry.in_terminal_state:
                out_berry.append(berry)
                continue
            params = berry.get_param()
            # randomly select if to loose
            r = np.random.rand()
            if r <= loss_param[params['state']]['loss']:
                berry = berry.loose()
            out_berry.append(berry)
        return out_berry

    def get_berry_states(self, berry_list: list, global_age: int):
        eval_berry_states = dict()
        eval_berry_states['global_age'] = global_age
        eval_berry_states['green'] = 0
        eval_berry_states['colour_break_1'] = 0
        eval_berry_states['colour_break_2'] = 0
        eval_berry_states['pink'] = 0
        eval_berry_states['cherry'] = 0
        eval_berry_states['blue'] = 0
        eval_berry_states['picked'] = 0
        eval_berry_states['lost'] = 0
        eval_berry_states['new berries'] = 0
        # extract state
        for berry in berry_list:
            params = berry.get_param()
            eval_berry_states['{}'.format(params['state'])] += 1
        return eval_berry_states

    def unwrap(self, params):
        out_params = dict()
        for i, state in enumerate(['green', 'colour_break_1', 'colour_break_2', 'pink', 'cherry']):
            out_params[state] = dict()
            out_params[state]['init'] = self.init_vals['{}__init'.format(state)]
            out_params[state]['mu__init'] = params[i]
            out_params[state]['sigma__init'] = params[i + 5]
            out_params[state]['loss'] = params[i + 10]
        # blue only has initi state
        out_params['blue'] = dict()
        out_params['blue']['init'] = self.init_vals['blue__init']
        out_params['blue']['loss'] = params[-2]
        # set param for green new berry rate
        out_params['green']['lambda'] = params[-1]
        return out_params

    def evaluate(self, days_since, *params, pick=True):
        # green__mu, colour_break_1__mu, colour_break_2__mu, pink__mu, cherry__mu, blue__mu,
        # green__sigma,colour_break_1__sigma, colour_break_2__sigma, pink__sigma, cherry__sigma, blue__sigma,
        # green__loss, colour_break_1__loss, colour_break_2__loss, pink__loss, cherry__loss, blue__loss,
        # green__lam
        start_date = self.y_df.date.min()
        if len(params) != 17:
            raise TypeError('Must have at least 11 arguments. {} given'.format(len(params)))
        # init outputs
        y_hat_eval, y_hat = [], []
        # unwrap params
        unwrapped_params = self.unwrap(params)
        # get initial berry state
        berry_sim = self.init_blueberries(unwrapped_params)

        for days in range(max(days_since) + 1):
            # record
            y = self.get_berry_states(berry_sim, days)
            n_new_berries = stats.poisson.rvs(unwrapped_params['green']['lambda'])
            if len(y_hat)>0:
                y['new berries'] = n_new_berries + y_hat[-1]['new berries']
            else:
                y['new berries'] = n_new_berries
            y_hat.append(y)
            # observer state of berries
            if days in days_since:
                y_hat_eval.append(y)
            # berries picked at the end of the work week? so friday
            if pick and (start_date + timedelta(days=days)).dayofweek == 4:
                berry_sim = self.pick_berries(berry_sim)
            # add progress berries
            berry_sim = self.step(berry_sim, days, unwrapped_params)
            # add new berries
            berry_sim = berry_sim + self.new_blueberries(n_new_berries, 'green', days, unwrapped_params)
            # get data to be evaluated

        return y_hat_eval, y_hat



    def eval_curvefit(self, days_since, *params, samples=20):
        for sample in range(samples):
            _, y = self.evaluate(days_since, *params)
            if sample == 0:
                y_sample = DataFrame(y).set_index('global_age')
            else:
                y_sample += DataFrame(y).set_index('global_age')
        return (y_sample / samples).loc[
            days_since, self._valid_cols].values.sum(1)

    def minimize(self, *params):
        # print(params)
        y_hat_eval, y_hat = self.evaluate(self.days_since, *params[0], pick=True)
        # make into data frame
        y_hat_eval = DataFrame(y_hat_eval).set_index('global_age')
        # standardize
        y_hat_eval_standard = self.scalar.transform(y_hat_eval.loc[self.y_df.days_since_start, self._valid_cols])
        return np.nanmean(((y_hat_eval_standard - self.y_df_scaled)** 2).ravel())
