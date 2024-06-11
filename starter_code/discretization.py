import numpy as np

def adaptive_grid_xy():
    """
    Generate an adaptive grid based on the error state and error threshold.
    3 level grids for x and y
    Whole state space is [-2.5, 2.5]

    for [-0.25, 0.25] divided into 6 parts
    for [-0.5, 0.5] divided into 5 parts
    for [-1.5, 1.5] divided into 5 parts
    """
    # Fine grid for [-0.25, 0.25] divided into 6 parts
    fine_grid = np.linspace(-0.25, 0.25, 7)
    
    # Medium grid for [-0.5, 0.5] divided into 5 parts excluding the overlap with fine grid
    medium_grid = np.concatenate([
        np.linspace(-0.65, -0.25, 5),
        np.linspace(0.25, 0.65, 5)
    ])
    
    # Coarse grid for [-3, 3] divided into 5 parts excluding the overlap with medium and fine grid
    coarse_grid = np.concatenate([
        np.linspace(-1.5, -0.65, 6),
        np.linspace(0.65, 1.5, 6)
    ])
    
    # Combine all grids
    grid = np.sort(np.unique(np.concatenate([fine_grid, medium_grid, coarse_grid])))
    
    return grid

def adaptive_grid_theta():
    """
    Generate an adaptive grid based on the error state and error threshold.
    3 level grids for theta
    Whole state space is [-pi, pi]

    for [-pi/4, pi/4] divided into 10 parts
    for [-pi/2, pi/2] divided into 5 parts
    for [-pi, pi] divided into 5 parts
    """
    # Fine grid for [-pi/4, pi/4] divided into 10 parts
    fine_grid = np.linspace(-np.pi/4, np.pi/4, 11)
    
    # Medium grid for [-pi/2, pi/2] divided into 5 parts excluding the overlap with fine grid
    medium_grid = np.concatenate([
        np.linspace(-np.pi/2, -np.pi/4, 4),
        np.linspace(np.pi/4, np.pi/2, 4)
    ])
    
    # Coarse grid for [-pi, pi] divided into 5 parts excluding the overlap with medium and fine grid
    coarse_grid = np.concatenate([
        np.linspace(-np.pi, -np.pi/2, 7),
        np.linspace(np.pi/2, np.pi, 7)
    ])
    
    # Combine all grids
    grid = np.sort(np.unique(np.concatenate([fine_grid, medium_grid, coarse_grid])))
    
    return grid

def adaptive_control_grid_w():
    """
    Generate an adaptive control grid based on the error state.
    3 level grids for theta
    Whole state space is [-1,1]

    for [-0.25,0.25] divided into 4 parts
    for [-0.6, 0.6] divided into 3 parts
    for [-1, 1] divided into 3 parts
    """
    # Fine grid for [-0.25, 0.25] divided into 4 parts
    fine_grid = np.linspace(-0.25, 0.25, 7)
    
    # Medium grid for [-0.6, 0.6] divided into 3 parts excluding the overlap with fine grid
    medium_grid = np.concatenate([
        np.linspace(-0.6, -0.25, 3),
        np.linspace(0.25, 0.6, 3)
    ])
    
    # Coarse grid for [-1, 1] divided into 3 parts excluding the overlap with medium and fine grid
    coarse_grid = np.concatenate([
        np.linspace(-1, -0.6, 3),
        np.linspace(0.6, 1, 3)
    ])
    
    # Combine all grids
    grid = np.sort(np.unique(np.concatenate([fine_grid, medium_grid, coarse_grid])))
    
    return grid

def adaptive_control_grid_v():
    """
    Generate an adaptive control grid based on the error state.
    3 level grids for theta
    Whole state space is [0,1]

    for [0,0.25] divided into 4 parts
    for [0.25, 0.6] divided into 3 parts
    for [0.6, 1] divided into 3 parts
    """
    # Fine grid for [0, 0.25] divided into 4 parts
    fine_grid = np.linspace(0, 0.3, 4)
    
    # Medium grid for [0.25, 0.6] divided into 3 parts excluding the overlap with fine grid
    medium_grid = np.concatenate([
        np.linspace(0.23, 0.6, 3)
    ])
    
    # Coarse grid for [0.6, 1] divided into 3 parts excluding the overlap with medium and fine grid
    coarse_grid = np.concatenate([
        np.linspace(0.6, 1, 3)
    ])
    
    # Combine all grids
    grid = np.sort(np.unique(np.concatenate([fine_grid, medium_grid, coarse_grid])))
    
    return grid



def adaptive_control_grid(error_state, error_threshold, fine_spacing, coarse_spacing):
    """
    Generate an adaptive control grid based on the current error state.
    
    Args:
    - error_state (float): The current error state.
    - error_threshold (float): The threshold for switching between fine and coarse grids.
    - fine_spacing (float): The spacing for fine grid.
    - coarse_spacing (float): The spacing for coarse grid.
    
    Returns:
    - control_grid (np.ndarray): The adaptive control grid.
    """
    if abs(error_state) <= error_threshold:
        # Use fine control grid
        control_grid = np.arange(0, 1 + fine_spacing, fine_spacing)  # Example for v, adjust as needed
    else:
        # Use coarse control grid
        control_grid = np.arange(0, 1 + coarse_spacing, coarse_spacing)  # Example for v, adjust as needed
    return control_grid

def dynamic_R(self, error_state, obstacle_positions):
    """
    Adjust the R matrix based on the error state and proximity to obstacles.
    """
    base_R = np.diag([0.1, 0.1])  # Example base R matrix, adjust as needed
    increase_factor = 10  # Factor by which to increase R, adjust as needed
    min_distance_to_obstacle = np.min([np.linalg.norm(error_state[:2] - obs[:2]) for obs in obstacle_positions])
    
    if np.linalg.norm(error_state) <= 0.5 or min_distance_to_obstacle <= 0.5:
        return base_R * increase_factor
    else:
        return base_R
    
def create_state_space():
    """
    Create the state space for the system.
    """
    # Define the state space
    ex_space = adaptive_grid_xy()
    ey_space = adaptive_grid_xy()
    eth_space = adaptive_grid_theta()
    v_space = adaptive_control_grid_v()
    w_space = adaptive_control_grid_w()
 
    print("State space created! Shape of state space is: ", ex_space.shape, ey_space.shape, eth_space.shape, v_space.shape, w_space.shape)
    return ex_space, ey_space, eth_space, v_space, w_space


if __name__ == "__main__":
    create_state_space()
    pass