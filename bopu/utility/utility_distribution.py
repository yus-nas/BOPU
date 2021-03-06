# Copyright (c) 2019, Raul Astudillo

import numpy as np
from core import preference_encoder


class UtilityDistribution(object):
    """
    Class to handle the parameter distribution of the utility function.
    There are two possible ways to specify a parameter distribution: ...
    """
    def __init__(self, support=None, prob_dist=None, prior_sample_generator=None, use_full_support=None, utility_func=None, elicitation_strategy=None):
        if support is None and prior_sample_generator is None:
            raise Exception('Either a finite support or a sample generator have to be provided.')
        self.support = support
        self.prior_prob_dist = np.copy(prob_dist)
        self.prob_dist = np.copy(prob_dist)
        self.prior_sample_generator = prior_sample_generator
        self.utility_func = utility_func
        self.elicitation_strategy = elicitation_strategy
        self.preference_information = []
        if support is not None:
            self.support_cardinality = len(support)
        if use_full_support is not None:
            self.use_full_support = use_full_support
        else:
            if support is not None and self.support_cardinality < 20:
                self.use_full_support = True
            else:
                self.use_full_support = False

    def sample_from_prior(self, number_of_samples=1, seed=None):
        if self.support is None:
            parameter_samples = self.prior_sample_generator(number_of_samples, seed)
        else:
            if seed is not None:
                random_state = np.random.RandomState(seed)
                indices = random_state.choice(int(len(self.support)), size=number_of_samples, p=self.prior_prob_dist)
                parameter_samples = self.support[indices, :]
            else:
                indices = np.random.choice(int(len(self.support)), size=number_of_samples, p=self.prior_prob_dist)
                parameter_samples = self.support[indices, :]

        if number_of_samples > 1 and parameter_samples.ndim < 2:
            parameter_samples = parameter_samples.reshape((number_of_samples, ))
        return parameter_samples
    
    def sample(self, number_of_samples=1):
        if self.support is None:
            if len(self.preference_information) == 0:
                parameter_samples = self.sample_from_prior(number_of_samples)
            else:
                parameter_samples = []
                number_of_gathered_samples = 0
                test_counter = 0
                while number_of_gathered_samples < number_of_samples:
                    suggested_sample = self.sample_from_prior(1)[0]
                    test_counter += 1
                    keep_verifying = True
                    counter = 0
                    while keep_verifying and counter < len(self.preference_information):
                        preference_information_item = self.preference_information[counter]
                        u1 = self.utility_func(preference_information_item[0], suggested_sample)
                        u2 = self.utility_func(preference_information_item[1], suggested_sample)
                        pref = preference_encoder(u1, u2)
                        if not pref == preference_information_item[2]:
                            #print(pref)
                            #print(preference_information_item[2])
                            #print(self.preference_information)
                            #print('Parameter sample does not agree with preference information')
                            keep_verifying = False
                        counter += 1
                    if counter == len(self.preference_information):
                        parameter_samples.append(suggested_sample)
                        number_of_gathered_samples += 1
                parameter_samples = np.atleast_2d(parameter_samples)
                print('Required parameter samples = {}'.format(test_counter))
        else:
            indices = np.random.choice(int(len(self.support)), size=number_of_samples, p=self.prob_dist)
            parameter_samples = self.support[indices, :]
        return parameter_samples

    def add_preference_information(self, underlying_true_utility_func, Y, number_of_pairwise_comparisons=1):
        if self.elicitation_strategy is not None:
            for i in range(number_of_pairwise_comparisons):
                suggested_pair = self.elicitation_strategy(Y=Y)
                u1 = underlying_true_utility_func(suggested_pair[0])
                u2 = underlying_true_utility_func(suggested_pair[1])
                pref = preference_encoder(u1, u2)
                if self.support is not None:
                    feasible_indices = []
                    for index in range(len(self.support)):
                        parameter = self.support[index]
                        u1_aux = self.utility_func(suggested_pair[0], parameter)
                        u2_aux = self.utility_func(suggested_pair[1], parameter)
                        pref_aux = preference_encoder(u1_aux, u2_aux)
                        if pref_aux == pref:
                            feasible_indices.append(index)
                    self.support = self.support[feasible_indices]
                    self.prob_dist = self.prob_dist[feasible_indices]
                    self.prob_dist /= np.sum(self.prob_dist)
                    print('New support and posterior probability distribution.')
                    print(suggested_pair)
                    print(self.support)
                    print(self.prob_dist)
                suggested_pair.append(pref)
                self.preference_information.append(suggested_pair)
            print(self.preference_information)







