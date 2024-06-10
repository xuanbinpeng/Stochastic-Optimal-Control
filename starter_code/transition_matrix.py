import numpy as np
from joblib import Parallel, delayed
import tqdm
import utils
import time
from scipy.special import logsumexp
from discretization import adaptive_grid_theta, adaptive_grid_xy, adaptive_control_grid_v, adaptive_control_grid_w  

# Example grid definitions
error_threshold = 0.5
fine_spacing = 0.1
coarse_spacing = 0.6

nt = 1
ex_space = adaptive_grid_xy()    
ey_space = adaptive_grid_xy()
eth_space = adaptive_grid_theta()
v_space = adaptive_control_grid_v()
w_space = adaptive_control_grid_w()

# Initialize transition matrix
transition_matrix = np.zeros((nt, len(ex_space), len(ey_space), len(eth_space), 
                              len(v_space), len(w_space), 6, 4), dtype=np.float32)

print("transition_matrix shape:", transition_matrix.shape)
# Precompute the lissajous curve
lissajous_curve = np.array([utils.lissajous(t) for t in range(100)])

def mean_next_state(e, u, t, delta_t):
    r_x_curr, r_y_curr, r_theta_curr = lissajous_curve[t]
    r_x_next, r_y_next, r_theta_next = lissajous_curve[t + 1]

    G_e = np.array([[delta_t * np.cos(e[2] + r_theta_curr), 0],
                    [delta_t * np.sin(e[2] + r_theta_curr), 0],
                    [0, delta_t]])
    
    next_e = e + G_e @ u + np.array([r_x_curr - r_x_next, r_y_curr - r_y_next, r_theta_curr - r_theta_next])
    return next_e

def find_6_neighbor_indices(mean_state, ex_space, ey_space, eth_space):
    i = np.digitize(mean_state[0], ex_space) - 1
    j = np.digitize(mean_state[1], ey_space) - 1
    k = np.digitize(mean_state[2], eth_space) - 1
    
    # Pre-compute indices
    i_indices = [np.clip(i+1, 0, len(ex_space)-1), np.clip(i-1, 0, len(ex_space)-1), i, i]
    j_indices = [j, j, np.clip(j+1, 0, len(ey_space)-1), np.clip(j-1, 0, len(ey_space)-1)]
    k_indices = [k, k, k, k]
    k_indices += [np.clip(k+1, 0, len(eth_space)-1), np.clip(k-1, 0, len(eth_space)-1)]
    
    return list(zip(i_indices[:4], j_indices[:4], k_indices[:4])) + list(zip([i]*2, [j]*2, k_indices[4:]))

def compute_transition_matrix_for_state_control(tasks, delta_t, sigma, ex_space, ey_space, eth_space, v_space, w_space):
    results = []
    for task in tasks:
        t, ix, iy, it, iv, iw = task
        ex = ex_space[ix]
        ey = ey_space[iy]
        eth = eth_space[it]
        v = v_space[iv]
        w = w_space[iw]

        local_transition_matrix = np.zeros((6, 4), dtype=np.float32)
        e = np.array([ex, ey, eth])
        u = np.array([v, w])
        mean_next_e = mean_next_state(e, u, t, delta_t)
        neighbors = find_6_neighbor_indices(mean_next_e, ex_space, ey_space, eth_space)
        
        sigma_inv_squared = (1 / sigma) ** 2
        diag_sigma_inv_squared = np.diag(sigma_inv_squared)
        
        neighbor_states = np.array([[ex_space[ni], ey_space[nj], eth_space[nk]] for ni, nj, nk in neighbors])
        diffs = neighbor_states - mean_next_e
        log_probs = -0.5 * np.sum(diffs @ diag_sigma_inv_squared * diffs, axis=1)
        
        log_probs -= logsumexp(log_probs)  # Normalize log probabilities
        probs = np.exp(log_probs)  # Convert to probabilities
        
        for idx, (ni, nj, nk) in enumerate(neighbors):
            local_transition_matrix[idx] = [ni, nj, nk, probs[idx]]
        
        results.append((t, ix, iy, it, iv, iw, local_transition_matrix))
    return results

def compute_transition_matrix(transition_matrix, ex_space, ey_space, eth_space, v_space, w_space, delta_t, sigma, batch_size=100):
    tasks = []
    for t in range(nt):
        for ix in range(len(ex_space)):
            for iy in range(len(ey_space)):
                for it in range(len(eth_space)):
                    for iv in range(len(v_space)):
                        for iw in range(len(w_space)):
                            tasks.append((t, ix, iy, it, iv, iw))
    
    # Create batches of tasks
    task_batches = [tasks[i:i + batch_size] for i in range(0, len(tasks), batch_size)]
    
    start_time = time.time()
    results = Parallel(n_jobs=-1)(delayed(compute_transition_matrix_for_state_control)(
        batch, delta_t, sigma, ex_space, ey_space, eth_space, v_space, w_space) for batch in tqdm.tqdm(task_batches))
    end_time = time.time()
    print(f"Time taken for parallel computation: {end_time - start_time:.2f} seconds")
    
    start_time = time.time()
    for result_batch in results:
        for t, ix, iy, it, iv, iw, local_transition_matrix in result_batch:
            transition_matrix[t, ix, iy, it, iv, iw, :, :] = local_transition_matrix
    
    end_time = time.time()
    print(f"Time taken for combining results: {end_time - start_time:.2f} seconds")

    # Save the transition matrix to a npz file
    np.savez('transition_matrix.npz', transition_matrix=transition_matrix)

# Example usage
sigma = np.array([0.04, 0.04, 0.004])
delta_t = 0.5
compute_transition_matrix(transition_matrix, ex_space, ey_space, eth_space, v_space, w_space, delta_t, sigma, batch_size=2100)
