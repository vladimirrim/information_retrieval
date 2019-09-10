import matplotlib.pyplot as plt
import networkx as nx

GRAPH_NAME = "graph"
NUMBER_OF_BEST_NODES_PAGERANK = 100
NUMBER_OF_BIGGEST_COMPONENTS = 3

def write_components_info(G, report_file):
    report_file.write("===COMPONENTS_INFO===\n")
    report_file.write("Number of strongly connected components: {}\n".format(nx.number_strongly_connected_components(G)))
    report_file.write("Number of weakly connected components: {}\n".format(nx.number_weakly_connected_components(G)))
    report_file.write("Number of attractive components: {}\n".format(nx.number_attracting_components(G)))
    report_file.write("Is semiconnected: {}\n".format(nx.is_semiconnected(G)))

def write_distance_info(G, report_file):
    report_file.write("===DISTANCE_INFO_STRONGLY_CONNECTED===\n")
    if nx.is_strongly_connected(G):
        report_file.write("Center: {}\n".format(nx.center(G)))
        report_file.write("Diameter: {}\n".format(nx.diameter(G)))
        report_file.write("Periphery: {}\n".format(nx.periphery(G)))
        report_file.write("Radius: {}\n".format(nx.radius(G)))
    else:
        report_file.write("Center: +INF\n")
        report_file.write("Diameter: +INF\n")
        report_file.write("Periphery: +INF\n")
        report_file.write("Radius: +INF\n")


    report_file.write("===DISTANCE_INFO_WEAKLY_CONNECTED===\n")
    if nx.is_weakly_connected(G):
        undirected_G = nx.to_undirected(G)
        report_file.write("Center: {}\n".format(nx.center(undirected_G)))
        report_file.write("Diameter: {}\n".format(nx.diameter(undirected_G)))
        report_file.write("Periphery: {}\n".format(nx.periphery(undirected_G)))
        report_file.write("Radius: {}\n".format(nx.radius(undirected_G)))
    else:
        report_file.write("Center: +INF\n")
        report_file.write("Diameter: +INF\n")
        report_file.write("Periphery: +INF\n")
        report_file.write("Radius: +INF\n")

def write_dag_info(G, report_file):
    report_file.write("===DAG_INFO===\n")
    report_file.write("Is DAG: {}\n".format(nx.is_directed_acyclic_graph(G)))
    report_file.write("Is aperiodic: {}\n".format(nx.is_aperiodic(G)))


def write_graph_info_to_file(G, graph_name=GRAPH_NAME):
    with open("{}_info".format(graph_name), "w") as report_file:
        try:
            report_file.write("Number of nodes: {}\n".format(G.number_of_nodes()))
            report_file.write("Number of edges: {}\n".format(G.number_of_edges()))
            write_components_info(G, report_file)
            write_distance_info(G, report_file)
            write_dag_info(G, report_file)
            report_file.write("Is Eulerian: {}\n".format(nx.is_eulerian(G)))
            report_file.write("Density: {}\n".format(nx.density(G)))
            report_file.write("Flow hierarchy: {}\n".format(nx.flow_hierarchy(G)))
            report_file.write("----INFO FROM NETWORKX----\n")
            report_file.write("{}\n".format(nx.info(G)))
        except ZeroDivisionError as e:
            report_file.write("Zero Division: {}".format(e))


def draw_graph(G):
    plt.subplot(121)
    nx.draw(G)
    plt.show()


def write_pagerank_graph(G, n):
    pagerank = nx.pagerank_numpy(G)
    best_nodes = sorted(pagerank.keys(), key=pagerank.get, reverse=True)[:n]
    best_subgraph = nx.subgraph(G, best_nodes)
    nx.write_edgelist(best_subgraph, "{}_best_{}_pagerank.csv".format(GRAPH_NAME, n), delimiter=';', data=False)
    write_graph_info_to_file(best_subgraph, "{}_best_{}_pagerank".format(GRAPH_NAME, n))


def write_strong_components_graphs(G, n):
    biggest_components = sorted(nx.strongly_connected_components(G), key=lambda c: len(c), reverse=True)[:n]
    for i, biggest_component in enumerate(biggest_components):
        subgraph = G.subgraph(biggest_component)
        nx.write_edgelist(subgraph, "{}_biggest_strongly_connected_component_{}_{}.csv".format(GRAPH_NAME, i + 1, n), delimiter=';', data=False)
        write_graph_info_to_file(subgraph, "{}_biggest_strongly_connected_component_{}_{}".format(GRAPH_NAME, i + 1, n))

def write_weak_components_graphs(G, n):
    biggest_components = sorted(nx.weakly_connected_components(G), key=lambda c: len(c), reverse=True)[:n]
    for i, biggest_component in enumerate(biggest_components):
        subgraph = G.subgraph(biggest_component)
        nx.write_edgelist(subgraph, "{}_biggest_weakly_connected_component_{}_{}.csv".format(GRAPH_NAME, i + 1, n), delimiter=';', data=False)
        write_graph_info_to_file(subgraph, "{}_biggest_weakly_connected_component_{}_{}".format(GRAPH_NAME, i + 1, n))

if __name__ == '__main__':
    G = nx.read_edgelist("{}.csv".format(GRAPH_NAME), delimiter=';', create_using=nx.DiGraph)
    write_graph_info_to_file(G)
    write_pagerank_graph(G, NUMBER_OF_BEST_NODES_PAGERANK)
    write_strong_components_graphs(G, NUMBER_OF_BIGGEST_COMPONENTS)
    write_weak_components_graphs(G, NUMBER_OF_BIGGEST_COMPONENTS)