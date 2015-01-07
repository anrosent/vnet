vnet
===
anrosent

### What is it

This project is the start of a couple experiments I plan on doing in the realm of Distributed Systems over the 2014-2015 winter break. It is a lightweight network emulator, with nodes implemented as threads and a UNIX pipe link layer. This provides great visibility and control from the driver program, since all node state is shared with the driver. 


### Some Plans for This

I'm looking at a few toy applications of this framework.

 - Routing Schemes (Distance Vector, Link State)
 - TCP on top of the routing layer
 - Distributed Hash Tables (Consistent Hashing, Rendezvous Hashing)
 - Maybe even some SDN applications (see ```mininet```)

This might also be a cool way to simulate network dynamics to get a sense of network stability in the face of certain traffic regimes or protocols.

### TODOs

 - Finish link layer and node abstractions
 - Tunable links? (delay, dropping)
