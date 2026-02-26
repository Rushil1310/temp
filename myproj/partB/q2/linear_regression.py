import numpy as np
import matplotlib.pyplot as plt

ROLL_NUMBER = 2025114009 
np.random.seed(ROLL_NUMBER)

def generate_data(n=100):
    X = np.linspace(0, 10, n)
    noise = np.random.randn(n) * 2
    Y = 3*X + 5 + noise
    return X, Y

def train_test_split(X, Y, test_ratio=0.2):
    indices = np.random.permutation(len(X))
    split = int(len(X) * (1 - test_ratio))
    train_idx, test_idx = indices[:split], indices[split:]
    return X[train_idx], X[test_idx], Y[train_idx], Y[test_idx]

def linear_regression_gd(X, Y, lr=0.01, iterations=1000):
    m, c = 0, 0
    N = len(X)

    for i in range(iterations):
        Ypred = m*X + c
        error = Ypred - Y
        m = m - lr*2/N*np.sum(error*X)
        c = c - lr*2/N*np.sum(error)

    return m, c

def linear_regression_cfs(X, Y):
    m, c = 0, 0
    N = len(X)
    X_b = np.column_stack((X, np.ones(N)))
    theta = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ Y # @ is for matrix multiplication
    m = theta[0]
    c = theta[1]
    return m, c

def plot_results(X_train, Y_train, X_test, Y_test, m, c, title):
    plt.figure(figsize=(10, 6))
    
    plt.scatter(X_train,Y_train,color='blue',alpha=0.6,label='Train')
    plt.scatter(X_test,Y_test,color='red',alpha=0.8,label='Test')
    
    # TODO: Plot the regression line y = mx + c
    # Hint: Create x_line from 0 to 10, then plot m*x_line + c
    x = np.linspace(0,10,100)
    y = m*x + c 
    plt.plot(x,y,color='black',alpha = 0.6,label = f"y={m:.2f}x+{c:.2f}")
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{title.replace(" ", "_").lower()}.png', dpi=150)
    plt.show()

if __name__ == "__main__":
    # Generate and split data
    X, Y = generate_data()
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y)
    
    # Method 1: Gradient Descent
    m_gd, c_gd = linear_regression_gd(X_train, Y_train)
    
    # Method 2: Closed Form Solution
    m_cfs, c_cfs = linear_regression_cfs(X_train, Y_train)
    
    # Print and compare results
    print(f"Gradient Descent: m={m_gd:.4f}, c={c_gd:.4f}")
    print(f"Closed Form:      m={m_cfs:.4f}, c={c_cfs:.4f}")
    
    # Visualize
    plot_results(X_train, Y_train, X_test, Y_test, m_gd, c_gd, "Gradient Descent")
    plot_results(X_train, Y_train, X_test, Y_test, m_cfs, c_cfs, "Closed Form Solution")