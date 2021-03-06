import networkx as nx
import sys
import time
import datetime
import os
from _pybgpstream import BGPStream, BGPRecord, BGPElem

stream = BGPStream()
rec = BGPRecord()
graph = nx.Graph()
setNodes = []

epoch = datetime.datetime(1970,1,1)
year = sys.argv[1]
#time1 is the midnight of January 1st of the year specified in command line
time1 = datetime.datetime(int(year), 1, 1, 0, 0)
time1 = int((time1 - epoch).total_seconds())
#time2 is 1am of January 1st of the year specified in command line
time2 = datetime.datetime(int(year), 1, 1, 8, 0)
time2 = int((time2 - epoch).total_seconds())

stream.add_filter('record-type', 'ribs')
stream.add_filter('project', 'ris')
stream.add_filter('project', 'routeviews')

stream.add_interval_filter(time1,time2)
stream.start()

while(stream.get_next_record(rec)):
    if rec.status != "valid":
        print(rec.project, rec.collector, rec.type, rec.time, rec.status)
    else:
        elem = rec.get_next_elem()
        while(elem):
            
            path = elem.fields.get('as-path')

            if '{' in path:
                p = path.split()
                for n in p:
                    if '{' in n:
                        set = n.replace('{', ' ')
                        set = n.replace('}', ' ')
                        set = n.replace(',', ' ')
                        set = n.split()

                        for node in set:
                            if node not in setNodes:
                                setNodes.append(node)

            path = path.replace('{', ' ')
            path = path.replace('}', ' ')
            path = path.replace(',', ' ')
            path = path.split()

            for n in range (len(path)-1):
                graph.add_edge(path[n], path[n+1])
 
            elem = rec.get_next_elem()

graph.remove_edges_from(nx.selfloop_edges(graph))

if not os.path.exists('./results/stage1'):
    os.makedirs('./results/stage1')

saveFile = open('results/stage1/data-all-' + year + '.dat', 'w+')
saveFile.write('number of nodes: ' + str(graph.number_of_nodes()) + '\n')
saveFile.write('number of edges: ' + str(graph.number_of_edges()) + '\n')
saveFile.write('set nodes: ' + str(len(setNodes)) + '\n')

for e in graph.edges:
    saveFile.write(str(e) + '\n')
