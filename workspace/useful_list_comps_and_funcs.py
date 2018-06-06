# some useful list comprehensions and functions for viewing token information in pdb when debugging DORA.
[x.mySemantic.name for x in self.memory.recipient.RBs[0].myObj[0].mySemantics]
[x.mySemantic.name for x in self.memory.recipient.RBs[0].myPred[0].mySemantics]
[x.weight for x in self.memory.recipient.RBs[0].myPred[0].mySemantics]

[x.mySemantic.dimension for x in self.network.memory.recipient.POs[0].mySemantics if x.mySemantic.dimension and x.weight > .9]

# some nice functions for dealing with objects. 
dir() # lists all the fields of an object. 
vars() # lists all the fields of an object and their values. 


