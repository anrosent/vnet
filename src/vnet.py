#!/usr/bin/env python3
import sys
import argparse
from threading import Thread

import cli
import core

def stop_network(nodes):
    def executor():
        print("Killing nodes and quitting..")
        for node in nodes:
            node.die()
    return executor

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('topology_file', help='file containing the virtual network topology specification')
    args = parser.parse_args()

    # Parse topology spec
    topology = core.NetTopology(args.topology_file) 

    # Build driver
    driver = cli.CLI()
    for node in topology.get_nodes():
        driver.add_cli(node.get_name(), node.get_cli())

    # Graceful shutdown
    driver.add_func(stop_network(topology.get_nodes()), ['q', 'quit'])

    # Activate virtual network
    node_threads = [Thread(target=node.run) for node in topology.get_nodes()]
    for t in node_threads:
        t.start()

    # Run driver
    driver.run()

    # Driver is done, wait for threads
    for t in node_threads:
        t.join()

    print("Virtual network successfully brought down.")
