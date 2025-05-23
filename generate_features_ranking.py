# generate feature ranking based on their importance in the random subgraphs.
# include datasets to generate feature ranking for them
# the generated ranking (resp. importance) is saved fo each graph in data/synthetic/ranking_synthetic (resp. importance_synthetic)

import random
import networkx as nx
import numpy as np
import os
import random
import pickle
import datetime
import util
from networkx import to_networkx_graph
from util import writeToReport, list_to_str
from sklearn.ensemble import RandomForestClassifier
import torch_geometric
from torch_geometric.utils import to_networkx
#import matplotlib.pyplot as plt
from sklearn import tree
import graphlets
import math

graphs = graphlets.graphs

def generate_features_ranking(dataset):
    start = datetime.datetime.now()
    graph_name=dataset
    G = nx.Graph(pickle.load(open('Synthetic/' + graph_name, 'rb')))
    #data = torch_geometric.utils.from_networkx(pickle.load(open('Synthetic/' + graph_name, 'rb')))
    data = torch_geometric.utils.from_networkx(G)
    G = to_networkx(data,to_undirected = True)
    nodes_count = nx.number_of_nodes(G)
    edges_count = nx.number_of_edges(G)
    report_file_features = 'reports/features_synthetic/' + graph_name + '.csv'
    writeToReport(report_file_features,
                  'degree, degree cent., max neighbor degree, min neighbor degree, avg neighbor degree, std neighbor degree, '
                  'eigenvector cent., closeness cent., harmonic cent., betweenness cent., '
                  'coloring largest first, coloring smallest last, coloring independent set, coloring random sequential,'
                  'coloring connected sequential dfs, coloring connected sequential bfs, edges within egonet,'
                  ' node clique number, number of cliques, clustering coef., square clustering coef., page rank, hubs value,'
                  ' triangles, core number, random ')

    report_file_importance = 'data/synthetic/importance_synthetic_l_' + str(walk_length)+ '.csv'
    #writeToReport(report_file_importance,
    #              'Graph, Nodes Count, Edges Count, ' + list_to_str(list([i for i in range(0, 99)])))
    report_file_ranking = 'data/synthetic/ranking_synthetic_l_' + str(walk_length)+ '_.csv'

    start_total = datetime.datetime.now()
    metrics_count = 26
    np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

    features_count = 0
    for g in graphs:
        features_count += g.number_of_nodes()


    importance_array_total = np.zeros([26])

    for iter_graph in range(1):

        classes_count = np.random.randint(2, 5)

        for vertex_index in range(len(data.y)):
            label = np.random.randint(0, classes_count)
            data.y[vertex_index] = label
        iter_counter = 0

        importance_array = np.zeros([26])

        importance_array_list = []



        # generate random walks

        walks = nx.generate_random_paths(G, iterations, walk_length)
        walks = list(walks)




        walk_counter = 0
        # generate random subgraphs
        for walk in walks:
            subgraph_nodes = set()
            for n in walk:
                #print('n')
                #print(n)
                h = nx.ego_graph(G, n, radius=1)
                for node_h in h.nodes:
                    #print('node_h')
                    #print(node_h)
                    subgraph_nodes.add(node_h)

            subgraph_nodes = list(subgraph_nodes)
            subgraph_nodes = subgraph_nodes[:walk_length]
            H = G.subgraph(subgraph_nodes).copy()
            H_nodes = list(H)

            nodes_count_H = nx.number_of_nodes(H)
            edges_count_H = nx.number_of_edges(H)
            print('nodes count: ' + str(nodes_count_H))
            print('edges count: ' + str(edges_count_H))
            iter_counter += 1


            #H = G
            # print(H)

            res = np.zeros(shape=(H.number_of_nodes(), features_count))
            # print(res)
            # print('number of nodes: ' + str(H.number_of_nodes()))

            feature_index = 0

            total_time_graphlets_list = []
            total_time_graphlets = datetime.timedelta()

            # nx.draw(H)
            # plt.savefig('H.png')

            '''
            for graph_index, g in enumerate(graphs):
                print('Graphlet: ' + str(graph_index))

                start_time_graphlet = datetime.datetime.now()

                GM = nx.isomorphism.GraphMatcher(H, g)

                # print(GM.subgraph_is_isomorphic())
                g_iter = GM.subgraph_isomorphisms_iter()

                # print(H.number_of_nodes())

                for i, index_graphlet in enumerate(g_iter):
                    #print(index_graphlet)
                    # print(type(index_graphlet))
                    # res[int(index_graphlet) - 1][i] = 1
                    keys = index_graphlet.keys()
                    # print(keys)
                    #print(np.shape(res))
                    for key_index,key in enumerate(keys):
                        # print(key)
                        # print(feature_index)
                        # print(index_graphlet[key])
                        res[key_index][int(index_graphlet[key])] = 1
                    # print(res)
                # print(res)
                feature_index += g.number_of_nodes()

                end_time_graphlet = datetime.datetime.now()
                total_time_graphlet = datetime.timedelta()
                total_time_graphlet = (end_time_graphlet - start_time_graphlet)
                total_time_graphlets_list.append(total_time_graphlet)
                total_time_graphlets += total_time_graphlet

            # print(res)
            '''
            res = np.delete(res,
                            [1, 4, 6, 7, 10, 11, 14, 15, 17, 18, 19, 22, 26, 27, 29, 30, 31, 35, 36, 41, 43, 44, 45, 49,
                             51,
                             53,
                             58,
                             61, 63, 64, 65, 66, 70, 75, 78, 80, 81,
                             85, 89, 90, 91, 95, 96, 99, 100, 101, 104, 105, 109, 111, 114, 116, 120, 121, 123, 124,
                             125,
                             129,
                             130,
                             131, 133, 134, 135, 136], axis=1)



            # compute features for the random subgraphs
            start_time_features = datetime.datetime.now()

            start_time_degree_centrality = datetime.datetime.now()
            degree_centrality = nx.degree_centrality(H)
            #print('degree centrality: ')
            #print(degree_centrality)
            #print(list(H))

            end_time_degree_centrality = datetime.datetime.now()
            total_time_degree_centrality = datetime.timedelta()
            total_time_degree_centrality = (end_time_degree_centrality - start_time_degree_centrality)

            start_time_eigenvector_centrality = datetime.datetime.now()
            eigenvector_centrality = nx.eigenvector_centrality(H, max_iter=100, tol=1e-03)
            #print('eigen centrality: ')
            #print(eigenvector_centrality)
            end_time_eigenvector_centrality = datetime.datetime.now()
            total_time_eigenvector_centrality = datetime.timedelta()
            total_time_eigenvector_centrality = (end_time_eigenvector_centrality - start_time_eigenvector_centrality)

            start_time_closeness_centrality = datetime.datetime.now()
            closeness_centrality = nx.closeness_centrality(H)
            end_time_closeness_centrality = datetime.datetime.now()
            total_time_closeness_centrality = datetime.timedelta()
            total_time_closeness_centrality = (end_time_closeness_centrality - start_time_closeness_centrality)

            start_time_harmonic_centrality = datetime.datetime.now()
            harmonic_centrality = nx.harmonic_centrality(H)
            end_time_harmonic_centrality = datetime.datetime.now()
            total_time_harmonic_centrality = datetime.timedelta()
            total_time_harmonic_centrality = (end_time_harmonic_centrality - start_time_harmonic_centrality)

            start_time_betweenness_centrality = datetime.datetime.now()
            betweenness_centrality = nx.betweenness_centrality(H)
            end_time_betweenness_centrality = datetime.datetime.now()
            total_time_betweenness_centrality = datetime.timedelta()
            total_time_betweenness_centrality = (end_time_betweenness_centrality - start_time_betweenness_centrality)

            start_time_coloring_lf = datetime.datetime.now()
            coloring_largest_first = nx.coloring.greedy_color(H, strategy='largest_first')
            end_time_coloring_lf = datetime.datetime.now()
            total_time_coloring_lf = datetime.timedelta()
            total_time_coloring_lf = (end_time_coloring_lf - start_time_coloring_lf)

            start_time_coloring_sl = datetime.datetime.now()
            coloring_smallest_last = nx.coloring.greedy_color(H, strategy='smallest_last')
            end_time_coloring_sl = datetime.datetime.now()
            total_time_coloring_sl = datetime.timedelta()
            total_time_coloring_sl = (end_time_coloring_sl - start_time_coloring_sl)

            start_time_coloring_is = datetime.datetime.now()
            coloring_independent_set = nx.coloring.greedy_color(H, strategy='independent_set')
            end_time_coloring_is = datetime.datetime.now()
            total_time_coloring_is = datetime.timedelta()
            total_time_coloring_is = (end_time_coloring_is - start_time_coloring_is)

            start_time_coloring_rs = datetime.datetime.now()
            coloring_random_sequential = nx.coloring.greedy_color(H, strategy='random_sequential')
            end_time_coloring_rs = datetime.datetime.now()
            total_time_coloring_rs = datetime.timedelta()
            total_time_coloring_rs = (end_time_coloring_rs - start_time_coloring_rs)

            start_time_coloring_dfs = datetime.datetime.now()
            coloring_connected_sequential_dfs = nx.coloring.greedy_color(H, strategy='connected_sequential_dfs')
            end_time_coloring_dfs = datetime.datetime.now()
            total_time_coloring_dfs = datetime.timedelta()
            total_time_coloring_dfs = (end_time_coloring_dfs - start_time_coloring_dfs)

            start_time_coloring_bfs = datetime.datetime.now()
            coloring_connected_sequential_bfs = nx.coloring.greedy_color(H, strategy='connected_sequential_bfs')
            end_time_coloring_bfs = datetime.datetime.now()
            total_time_coloring_bfs = datetime.timedelta()
            total_time_coloring_bfs = (end_time_coloring_bfs - start_time_coloring_bfs)

            start_time_node_clique_number = datetime.datetime.now()
            node_clique_number = nx.node_clique_number(H)
            end_time_node_clique_number = datetime.datetime.now()
            total_time_node_clique_number = datetime.timedelta()
            total_time_node_clique_number = (end_time_node_clique_number - start_time_node_clique_number)

            # number_of_cliques = nx.number_of_cliques(H)
            # print(number_of_cliques)
            start_time_number_of_cliques = datetime.datetime.now()
            number_of_cliques = {n: sum(1 for c in nx.find_cliques(H) if n in c) for n in H}
            end_time_number_of_cliques = datetime.datetime.now()
            total_time_number_of_cliques = datetime.timedelta()
            total_time_number_of_cliques = (end_time_number_of_cliques - start_time_number_of_cliques)
            # print(number_of_cliques_2)
            start_time_clustering_coefficient = datetime.datetime.now()
            clustering_coefficient = nx.clustering(H)
            end_time_clustering_coefficient = datetime.datetime.now()
            total_time_clustering_coefficient = datetime.timedelta()
            total_time_clustering_coefficient = (end_time_clustering_coefficient - start_time_clustering_coefficient)

            start_time_square_clustering = datetime.datetime.now()
            square_clustering = nx.square_clustering(H)
            end_time_square_clustering = datetime.datetime.now()
            total_time_square_clustering = datetime.timedelta()
            total_time_square_clustering = (end_time_square_clustering - start_time_square_clustering)

            start_time_average_neighbor_degree = datetime.datetime.now()
            average_neighbor_degree = nx.average_neighbor_degree(H)
            end_time_average_neighbor_degree = datetime.datetime.now()
            total_time_average_neighbor_degree = datetime.timedelta()
            total_time_average_neighbor_degree = (end_time_average_neighbor_degree - start_time_average_neighbor_degree)

            start_time_hubs = datetime.datetime.now()
            hubs, authorities = nx.hits(H)
            end_time_hubs = datetime.datetime.now()
            total_time_hubs = datetime.timedelta()
            total_time_hubs = (end_time_hubs - start_time_hubs)
            #print(hubs)
            hubs = {k: 0 if v=='NaN' else v for k,v in hubs.items()}
            #print('hubs: ')
            #print(hubs)
            start_time_page_rank = datetime.datetime.now()
            page_rank = nx.pagerank(H)
            end_time_page_rank = datetime.datetime.now()
            total_time_page_rank = datetime.timedelta()
            total_time_page_rank = (end_time_page_rank - start_time_page_rank)

            start_time_core_number = datetime.datetime.now()
            core_number = nx.core_number(H)
            end_time_core_number = datetime.datetime.now()
            total_time_core_number = datetime.timedelta()
            total_time_core_number = (end_time_core_number - start_time_core_number)

            end_time_features = datetime.datetime.now()
            total_time_features = datetime.timedelta()
            total_time_features = (end_time_features - start_time_features)
            print('total time features: ')
            print(total_time_features)

            total_time_egonet = datetime.timedelta()
            total_time_triangles = datetime.timedelta()
            total_time_random = datetime.timedelta()



            X = np.zeros([nx.number_of_nodes(H), metrics_count])
            Y = np.zeros([nx.number_of_nodes(H)])

            for i, v in enumerate(H):
                start_time_degree = datetime.datetime.now()
                X[i][0] = H.degree(v)
                end_time_degree = datetime.datetime.now()
                total_time_degree = datetime.timedelta()
                total_time_degree = (end_time_degree - start_time_degree)
                #print(i)
                #print(np.shape(X))
                #print(np.shape(degree_centrality))

                X[i][1] = degree_centrality[H_nodes[i]]
                neighborhood_degrees = [H.degree(n) for n in nx.neighbors(H, v)]
                if (len(neighborhood_degrees) == 0):
                    max_neighbor_degree = 0
                    min_neighbor_degree = 0
                    std_neighbor_degree = 0
                else:

                    max_neighbor_degree = np.max(neighborhood_degrees)
                    min_neighbor_degree = np.min(neighborhood_degrees)
                    std_neighbor_degree = np.std(neighborhood_degrees)
                X[i][2] = max_neighbor_degree
                X[i][3] = min_neighbor_degree
                X[i][4] = average_neighbor_degree[H_nodes[i]]
                X[i][5] = std_neighbor_degree
                X[i][6] = eigenvector_centrality[H_nodes[i]]
                X[i][7] = closeness_centrality[H_nodes[i]]
                X[i][8] = harmonic_centrality[H_nodes[i]]
                X[i][9] = betweenness_centrality[H_nodes[i]]
                X[i][10] = coloring_largest_first[H_nodes[i]]
                X[i][11] = coloring_smallest_last[H_nodes[i]]
                X[i][12] = coloring_independent_set[H_nodes[i]]
                X[i][13] = coloring_random_sequential[H_nodes[i]]
                X[i][14] = coloring_connected_sequential_dfs[H_nodes[i]]
                X[i][15] = coloring_connected_sequential_bfs[H_nodes[i]]

                start_time_egonet = datetime.datetime.now()
                egonet = nx.ego_graph(H, v, radius=1)
                edges_within_egonet = nx.number_of_edges(egonet)
                end_time_egonet = datetime.datetime.now()
                total_time_egonet += (end_time_egonet - start_time_egonet)

                X[i][16] = edges_within_egonet
                X[i][17] = node_clique_number[H_nodes[i]]
                X[i][18] = number_of_cliques[H_nodes[i]]
                X[i][19] = clustering_coefficient[H_nodes[i]]
                X[i][20] = square_clustering[H_nodes[i]]
                X[i][21] = page_rank[H_nodes[i]]
                X[i][22] = hubs[H_nodes[i]]

                start_time_triangles = datetime.datetime.now()
                X[i][23] = nx.triangles(H, v)
                end_time_triangles = datetime.datetime.now()
                total_time_triangles += (end_time_triangles - start_time_triangles)

                X[i][24] = core_number[H_nodes[i]]

                start_time_random = datetime.datetime.now()
                X[i][25] = np.random.normal(0, 1, 1)[0]
                end_time_random = datetime.datetime.now()
                total_time_random += (end_time_random - start_time_random)
                Y[i] = np.random.randint(0, classes_count)



            #print(len(X))
            #X = np.concatenate((X, res), axis=1)
            #print(len(X))
            X[np.isnan(X)] = 0
            model = RandomForestClassifier(n_estimators=10,max_depth=5,max_features=6)
            model.fit(X, Y)
            trees = model.estimators_

            arr = model.feature_importances_
            #print(len(arr))
            #print(len(importance_array_total))
            importance_array_total += arr
            importance_array += arr

            walk_counter+=1



            for x in X:
                writeToReport(report_file_features, list_to_str(x))
            writeToReport(report_file_features, '\n')

        importance_array_norm = importance_array / iter_counter

        arr_ordered = np.argsort(importance_array)[::-1]
        print('Ranking: ' + str(arr_ordered))

        ranking_str = ''.join(str(m) + ',' for m in arr_ordered)
        writeToReport(report_file_ranking, graph_name + ',' + ranking_str)
        #writeToReport(report_file_ranking,'\n')

        #metrics_str = ''.join(str(np.round(m, 4)) + ',' for m in importance_array_norm)

        #std_str = ''.join(str(np.round(m, 4)) + ',' for m in importance_array_list_std)
        writeToReport(report_file_importance, graph_name + ',' + str(nodes_count) + ',' + str(edges_count) + ',' + list_to_str(importance_array))
        #writeToReport(report_file_importance, ',' + ',' + 'Std: ,' + list_to_str(importance_array_list_std))

        #writeToReport(report_file_importance, '\n')


    report_file = 'reports/computing_time.csv'
    writeToReport(report_file,
                  'graph_name , nodes_count , edges_count, degree, degree cent., max neighbor degree, min neighbor degree, avg neighbor degree, std neighbor degree, '
                  'eigenvector cent., closeness cent., harmonic cent., betweenness cent., '
                  'coloring largest first, coloring smallest last, coloring independent set, coloring random sequential,'
                  'coloring connected sequential dfs, coloring connected sequential bfs, edges within egonet,'
                  ' node clique number, number of cliques, clustering coef., square clustering coef., page rank, hubs value,'
                  ' triangles, core number, random')
    writeToReport(report_file, graph_name + ',' + str(nodes_count) + ',' + str(
        edges_count) + ',' + str(total_time_degree) + ',' + str(total_time_degree_centrality) + ',' + str(
        total_time_average_neighbor_degree) + ',' + str(total_time_average_neighbor_degree)
                  + ',' + str(total_time_average_neighbor_degree) + ',' + str(
        total_time_average_neighbor_degree) + ',' + str(total_time_average_neighbor_degree) + ',' +
                  str(total_time_eigenvector_centrality) + ',' + str(total_time_closeness_centrality) + ',' + str(
        total_time_harmonic_centrality) + ',' + str(total_time_betweenness_centrality)
                  + ',' + str(total_time_coloring_lf) + ',' + str(total_time_coloring_sl) + ',' + str(
        total_time_coloring_is) + ',' + str(total_time_coloring_rs) + ',' + str(total_time_coloring_dfs)
                  + ',' + str(total_time_coloring_bfs) + ',' + str(total_time_egonet) + ',' + str(
        total_time_node_clique_number) + ',' + str(total_time_number_of_cliques) + ',' + str(
        total_time_clustering_coefficient)
                  + ',' + str(total_time_square_clustering) + ',' + str(total_time_page_rank) + ',' + str(
        total_time_hubs) + ',' + str(total_time_triangles) + ',' + str(total_time_core_number) + ',' + str(
        total_time_random))

    end = datetime.datetime.now()
    total_time = datetime.timedelta()
    total_time = (end - start)
    print('Computing features time: ' + str(total_time))



#main
iterations = 2
walk_lengths = [50]
for walk_length in walk_lengths:

    # include datasets to generate feature ranking
    datasets = [f for f in os.listdir('Synthetic/') if 'Erdos_500_' in f or 'Erdos_1000_' in f or 'Erdos_2500_' in f or 'Barabasi_1000_' in f or 'Barabasi_1500_' in f]
    #datasets = ['Erdos_1500_10000_house_200_114_5_1117.pickle']
    #datasets = ['Barabasi_150_12_house_10_17_1_142.pickle']
    for dataset in datasets:
        generate_features_ranking(dataset)

