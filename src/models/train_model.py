import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import sys
import pickle
import logging
import time
import torch
import torch.nn.functional as F
from torch_geometric_temporal.signal import StaticGraphTemporalSignal
from torch_geometric_temporal.signal import temporal_signal_split
import matplotlib.pyplot as plt

from model import RecurrentGCN


def train_model(lr, batch_size, epochs):
    start_time = time.time()

    # Create and configure logger
    logging.basicConfig(filename="std.log", format='%(asctime)s %(message)s', filemode='w')

    # Create an object
    logger = logging.getLogger()
    # Set log level to DEBUG
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # GPU support
    DEVICE = torch.device('cpu')  # Change to cuda if available
    shuffle = True

    # Change the current working directory to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Load the data from the pickle file
    with open('../../data/processed/data_node10.pickle', 'rb') as file:
        loaded_data = pickle.load(file)

    # Access the loaded data
    edge_index = loaded_data['edge_index']
    edge_weight = loaded_data['edge_weight']
    features_seq = loaded_data['features_seq']
    targets_seq = loaded_data['targets_seq']

    dataset = StaticGraphTemporalSignal(
        edge_index=edge_index, edge_weight=edge_weight,
        features=features_seq, targets=targets_seq
    )

    train_dataset, test_dataset = temporal_signal_split(dataset, train_ratio=0.8)

    model = RecurrentGCN(node_features=11)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    costs, model = model._train(model, train_dataset=train_dataset, epochs=epochs, lr=lr, h=None, c=None)

    print(f"Training completed in {time.time() - start_time:.2f} seconds.")

    return costs, model_path

if __name__ == "__main__":
    
    cost_list = []
    time_list = []
    learning_rates = 0.01
    batch_size = 32
    num_epochs = 100

    
    costs, model = train_model(lr=0.05, batch_size=batch_size, epochs=num_epochs)
    # Plot the predictions
    # plt.plot(range(len(costs)), costs, marker='o', linestyle='-')
    # plt.xlabel('Data Points')
    # plt.ylabel('Predictions')
    # plt.title('Predictions Plot')
    # plt.grid(True)
    # plt.show()

    # Save the model at the end of training
    model_path = f"model_final.pt"
    torch.save(model.state_dict(), model_path)

    # with open('costs_final.pkl', 'wb') as f:
    #     pickle.dump(cost_list, f)