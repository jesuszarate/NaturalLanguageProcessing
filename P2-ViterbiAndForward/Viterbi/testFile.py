import numpy as np

# the transition matrix
A_mat = np.array([[.6, .4], [.2, .8]])
# the observation matrix
O_mat = np.array([[.5, .5], [.15, .85]])


num_states = A_mat.shape[0]
log_probs = np.zeros(num_states)

state_ind = 0
obs_val = 0
temp_probs = log_probs + np.log(O_mat[state_ind, obs_val]) + np.log(A_mat[:, state_ind])


temp_probs = log_probs + np.log(O_mat[0, 1]) + np.log(A_mat[:, 0])


# print (np.log(O_mat[state_ind, obs_val]))

#Score[(t, W)] = Pr[(Word[w], Tag[t])] * max_k1(Score[(k, w-1)] * Pr[(Tag[t], Tag[k])])

print (np.argmax(log_probs + np.log(O_mat[state_ind, obs_val])))