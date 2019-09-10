import matplotlib.pyplot as plt
import networkx as nx


def write_components_info(G, report_file):
    report_file.write("Number of strongly connected components: {}\n".format(nx.number_strongly_connected_components(G)))
    report_file.write("Number of weakly connected components: {}\n".format(nx.number_weakly_connected_components(G)))
    report_file.write("Number of attractive components: {}\n".format(nx.number_attracting_components(G)))
    report_file.write("Is semiconnected: {}\n".format(nx.is_semiconnected(G)))


def write_dag_info(G, report_file):
    report_file.write("Is DAG: {}\n".format(nx.is_directed_acyclic_graph(G)))
    report_file.write("Is DAG: {}\n".format(nx.is_aperiodic(G)))


def write_graph_info_to_file(G, report_file):
    report_file.write("Number of nodes: {}\n".format(G.number_of_nodes()))
    report_file.write("Number of edges: {}\n".format(G.number_of_edges()))
    write_components_info(G, report_file)
    write_dag_info(G, report_file)
    report_file.write("Is Eulerian: {}\n".format(nx.is_eulerian(G)))
    report_file.write("Flow hierarchy: {}\n".format(nx.flow_hierarchy(G)))

def draw_graph(G):
    plt.subplot(121)
    nx.draw(G)
    plt.show()


if __name__ == '__main__':
    with open("graph_report_01_test.csv", "w") as report_file:
        G = nx.read_edgelist("graph_01_test.csv", delimiter=';', create_using=nx.DiGraph)
        write_graph_info_to_file(G, report_file)
        # draw_graph(G)
