# for a query graph g, the code trains a node classification gnn model NC-GNN after splitting nodes into training, validation, and testing.
# the feature vector for each node consists of the first k fetures according to the predicted ranking from reports/rank_predicted.csv
# results are saved in k_results

graph_name_list = [f for f in os.listdir('Synthetic/') if
                   'Erdos_500_' in f or 'Erdos_1000_' in f or 'Erdos_2500_' in f or 'Barabasi_150_' in f or 'Barabasi_1000_' in f or 'Barabasi_1500_' in f]

graph_name_list = ['MUTAG']
# Cora

import numpy as np
import torch
from torch_geometric.nn import GCNConv
import torch.nn as nn
import torch.nn.functional as F
import ReadData
import os
import torch_geometric
from torch_geometric.utils import to_networkx
from torch_geometric.datasets import Planetoid, Coauthor, Amazon
import torch_geometric.transforms as T
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
import ReadData
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score
import random
import util
from util import writeToReport
from sklearn.feature_selection import mutual_info_classif
from sklearn.tree import export_text
from torch_geometric.datasets import Amazon, CitationFull, HeterophilousGraphDataset
from torch_geometric.datasets import GNNBenchmarkDataset, Airports, AttributedGraphDataset, Entities
import datetime
import pickle


class GCN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(len(X[0]), hidden_layers)
        self.conv2 = GCNConv(hidden_layers, hidden_layers)
        self.conv3 = GCNConv(hidden_layers, classes_count)

    def forward(self, data, X):
        x, edge_index = X, data.edge_index
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        output = self.conv3(x, edge_index)
        return output


def train_node_classifier(model, graph, X, optimizer, criterion, n_epochs=10):
    for epoch in range(1, n_epochs + 1):
        model.train()
        optimizer.zero_grad()
        out = model(graph, X)
        loss = criterion(out[graph.train_mask], graph.y[graph.train_mask])
        loss.backward()
        optimizer.step()
        acc = eval_node_classifier(model, graph, X, graph.val_mask)
        if epoch % 50 == 0:
            print(f'Epoch: {epoch:03d}, Train Loss: {loss:.3f}, Val Acc: {acc:.3f}')
            loss_values.append(loss)
            val_accuracy.append(acc)

    return model


def eval_node_classifier(model, graph, X, mask):
    model.eval()
    pred = model(graph, X).argmax(dim=1)
    correct = (pred[mask] == graph.y[mask]).sum()
    acc = int(correct) / int(mask.sum())

    return acc


data_dir = "./datasets"
os.makedirs(data_dir, exist_ok=True)
dataPath = 'data'
classes_count = 0
optimal_k = 6
acc_list = []
acc_all = []


def list_to_str(list):
    str_list = ''
    for l in list:
        # print(l)
        str_list += str(l) + ','
    return str_list


def getRanking(graph):
    with open('data/synthetic/ranking_synthetic_l_10_.csv') as input_file:
        for line in input_file:
            columns = line.split(',')
            if (graph in columns[0]):
                ranking = [int(columns[c]) for c in range(1, 27)]
                return ranking


for graph_id, graph_name in enumerate(graph_name_list):
    acc_list = []
    # sample k features
    print(graph_name)
    ranking = getRanking(graph_name)
    print(ranking)

    for iteration in range(1, 2):
        numbers = set()
        while (len(numbers) < optimal_k):
            numbers.add(np.random.randint(0, 98))
        numbers = list(numbers)
        if (graph_name == 'MUTAG'):
            classes_count = 2
            dataset = Entities(root=data_dir, name=graph_name)
        if (graph_name == 'Cora'):
            classes_count = 7
            dataset = Planetoid(root=data_dir, name=graph_name)
        if (graph_name == 'CiteSeer'):
            classes_count = 6
            dataset = Planetoid(root=data_dir, name=graph_name)
        if (graph_name == 'PubMed'):
            classes_count = 3
            dataset = Planetoid(root=data_dir, name=graph_name)
        if (graph_name == 'Photo'):
            classes_count = 8
            dataset = Amazon(root=data_dir, name=graph_name)
        if (graph_name == 'CS'):
            classes_count = 15
            dataset = Coauthor(root=data_dir, name=graph_name)
        if (graph_name == 'Physics'):
            classes_count = 5
            dataset = Coauthor(root=data_dir, name=graph_name)
        if (graph_name == 'Cora_ML'):
            classes_count = 7
            dataset = CitationFull(root=data_dir, name=graph_name)
        if (graph_name == 'DBLP'):
            classes_count = 4
            dataset = CitationFull(root=data_dir, name=graph_name)
        if (graph_name == 'Roman-empire'):
            classes_count = 18
            dataset = HeterophilousGraphDataset(root=data_dir, name=graph_name)
        if (graph_name == 'Amazon-ratings'):
            classes_count = 5
            dataset = HeterophilousGraphDataset(root=data_dir, name=graph_name)
        if (graph_name == 'Minesweeper'):
            classes_count = 2
            dataset = HeterophilousGraphDataset(root=data_dir, name=graph_name)
        if (graph_name == 'Photo'):
            classes_count = 8
            dataset = Amazon(root=data_dir, name=graph_name)
        if (graph_name == 'USA' or graph_name == 'Brazil' or graph_name == 'Europe'):
            classes_count = 4
            dataset = Airports(root=data_dir, name=graph_name)
        if (graph_name == 'Wiki'):
            classes_count = 17
            dataset = AttributedGraphDataset(root=data_dir, name=graph_name)

        if ('house' in graph_name):
            classes_count = 4
        if ('star' in graph_name):
            classes_count = 3
        if ('grid' in graph_name):
            classes_count = 4
        if ('path' in graph_name):
            classes_count = 3
        if ('cycle' in graph_name):
            classes_count = 2

        data = dataset[0]  # for real-world graphs
        # data = torch_geometric.utils.from_networkx(pickle.load(open('Synthetic/' + graph_name, 'rb'))) # for synthetic graphs
        # print(data)
        graph = to_networkx(data, to_undirected=True)
        metrics_count = 26
        path_ranking = 'reports/'
        # ranking = numbers

        report_file_k = 'reports/k_results_real/' + graph_name + '_k.csv'
        writeToReport(report_file_k, 'k , Test Accuracy')
        report_file_k_metrics = 'reports/k_results_metrics/' + graph_name + '_k.csv'
        writeToReport(report_file_k, 'k , Test Accuracy')
        report_file_optimal_k = 'reports/results_optimal_k.csv'
        # writeToReport(report_file_optimal_k, 'Graph, k , Avg Test Accuracy, Std Test Accuracy, k features')
        report_file = 'reports/k_results/' + graph_name + '.txt'
        # writeToReport(report_file, 'depth = ' + str(depth) + ' , trees count = ' + str(trees_count) + ' \n')
        for k in range(1, 27):
            if (k == 6):
                X_train = []
                Y_train = []
                X_test = []
                Y_test = []
                X_val = []
                Y_val = []

                filename = os.path.join("data/synthetic/", graph_name + ".csv")
                # filename = os.path.join("reports/features_synthetic/", graph_name + ".csv")

                X = np.loadtxt(filename, delimiter=',', dtype=str)
                if ('Target' in X[0][-1]):

                    Y = X[1:, -1]
                    X = X[1:, :-1]
                else:
                    Y = X[:, -1]
                    X = X[:, :-1]

                Y = np.array(Y)
                Y = Y.astype(np.float32)
                X = X.astype(np.float32)
                X_metrics = X
                print(np.shape(X_metrics))
                X_vanilla = np.ones((len(X_metrics), metrics_count), dtype=np.float32)

                X_random = X_metrics[:, [25]]
                k_ranking = ranking[:k]
                print(k_ranking)
                # k_ranking = [25,16,21,6,4,20]
                X_metrics = X_metrics[:, k_ranking]
                split = T.RandomNodeSplit(num_val=0.1, num_test=0.2)
                graph = split(data)
                print(graph)

                train_list = []
                test_list = []
                val_list = []

                counter_train = 0
                for i, item in enumerate(graph.train_mask):
                    if (item.item() == True):
                        counter_train += 1
                        X_train.append(X_metrics[i])
                        Y_train.append(Y[i])
                        train_list.append(i)

                counter_test = 0
                for i, item in enumerate(graph.test_mask):
                    if (item.item() == True):
                        counter_test += 1
                        X_test.append(X_metrics[i])
                        Y_test.append(Y[i])

                        test_list.append(i)

                counter_val = 0
                for i, item in enumerate(graph.val_mask):
                    if (item.item() == True):
                        counter_val += 1
                        X_val.append(X_metrics[i])
                        Y_val.append(Y[i])
                        val_list.append(i)

                X_train_m = np.array(X_train)

                for features_count in range(k, k + 1):

                    writeToReport(report_file, 'k= ' + str(k) + ' \n')
                    rf_metrics_acc = []
                    rf_pred_acc = []
                    gcn_metrics_acc = []
                    gcn_pred_acc = []
                    gcn_metrics_pred_acc = []

                    for iteration in range(1, 2):
                        writeToReport(report_file, 'iteration: ' + str(iteration) + '\n\n')

                        loss_values = []
                        val_accuracy = []
                        dataPath = 'data'

                        ## gcn metrics

                        hidden_layers = 128
                        start_gcn_metrics = datetime.datetime.now()
                        X = torch.from_numpy(X_metrics)
                        gcn = GCN()
                        optimizer_gcn = torch.optim.Adam(gcn.parameters(), lr=0.001, weight_decay=5e-4)
                        criterion = nn.CrossEntropyLoss()
                        gcn = train_node_classifier(gcn, graph, X, optimizer_gcn, criterion)

                        test_acc_metrics = eval_node_classifier(gcn, graph, X, graph.test_mask)
                        gcn_metrics_acc.append(test_acc_metrics)
                        print(f' GCN on metrics, Test Acc: {test_acc_metrics:.3f}')
                        end_gcn_metrics = datetime.datetime.now()
                        gcn_time_metrics = datetime.timedelta()
                        gcn_time_metrics = (end_gcn_metrics - start_gcn_metrics)

                        writeToReport(report_file_optimal_k, graph_name + ',' + str(
                            np.round(test_acc_metrics, 3)))
                        writeToReport(report_file, 'GCN on metrics: ' + str(np.round(test_acc_metrics, 3)) + '\n')
                        writeToReport(report_file, 'Time: ' + str(gcn_time_metrics) + '\n')
                        writeToReport(report_file_k, str(k) + ',' + str(np.round(test_acc_metrics, 3)))
                        acc_list.append(np.round(test_acc_metrics, 3))
                        acc_all.append(np.round(test_acc_metrics, 3))

                        loss_values = []
                        val_accuracy = []

    # writeToReport(report_file_optimal_k, graph_name + ',' + str(optimal_k) + ',' + str(np.mean(acc_list)) + ',' + str(
    #    np.std(acc_list)) + ',' + list_to_str(numbers))
    # writeToReport(report_file_optimal_k,
    #              'avg Large,' + str(optimal_k) + ',' + str(np.mean(acc_all)) + ',' + str(np.std(acc_all)) + ',')
    vanilla_train = False
    if (vanilla_train):
        ## gcn vanilla
        X = X_vanilla
        X = torch.from_numpy(X)
        gcn = GCN()
        optimizer_gcn = torch.optim.Adam(gcn.parameters(), lr=0.001, weight_decay=5e-4)
        criterion = nn.CrossEntropyLoss()
        gcn = train_node_classifier(gcn, graph, X, optimizer_gcn, criterion)
        test_acc_vanilla = eval_node_classifier(gcn, graph, X, graph.test_mask)
        print(f'GCN on vanilla, Test Acc: {test_acc_vanilla:.3f}')
        writeToReport(report_file, 'GCN on vanilla: ' + str(np.round(test_acc_vanilla, 3)) + '\n  \n')
        writeToReport(report_file_optimal_k, 'vanilla' + ',' + str(np.round(test_acc_vanilla, 3)))

    '''
      ## gcn random
      X = X_random
      X = torch.from_numpy(X)
      gcn = GCN()
      optimizer_gcn = torch.optim.Adam(gcn.parameters(), lr=0.001, weight_decay=5e-4)
      criterion = nn.CrossEntropyLoss()
      gcn = train_node_classifier(gcn, graph,X, optimizer_gcn, criterion)

      test_acc_random = eval_node_classifier(gcn, graph,X, graph.test_mask)

      print(f'GCN on random, Test Acc: {test_acc_random:.3f}')


      writeToReport(report_file,'GCN on random: '+str(np.round(test_acc_random,3))+ '\n  \n')
      writeToReport(report_file_k_metrics, 'random' + ',' +str(np.round(test_acc_random,3)))
    '''
