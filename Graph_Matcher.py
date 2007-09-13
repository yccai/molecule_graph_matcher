# Contains a class to determine whether one graph is isomorphic to a subgraph
# of another.
# based on Ullman, 1976
# The code works by finding every permution of the larger adjacency matrix
# and checking to see if the 1s in the smaller matrix each imply a 1 in the
# same location in the larger matrix.
# Permutation matrices are generated by generating a MxN matrix, were M, the
# rows, is the number of nodes in the smaller graph, and N, the cols, is the
# number of nodes in the larger graph.   We generate each MxN matrix such that
# there is one 1 in each row and at most one 1 in each column.  Certain row-col
# combinations are ruled out if we know a priori that there is no way the
# corresponding nodes could be isomorphic--namely, if their labels are different
# or the node of the smaller graph has a higher degree than the node of the
# larger graph.  For each perm matrix, we do some multiplications and
# transpositions to permute the larger matrix, and then we check to see if this
# describes an isomorphism.

from Graph_Node import Graph_Node
from Graph import Graph
from Isomorphism import Isomorphism
from Numeric import *

class Graph_Matcher:

  #create an object to find isomorphisms between small and a subgraph of large
  def __init__ (self, large, small):
    self.large = large
    self.small = small

  # find every possible isomorphism; return them as a dictionary of nodes
  # in the smaller graph to nodes in the larger.
  def get_isomorphisms (self):
    # A is the smaller adj_matrix, B is the larger
    # M0 is a mask showing what permutation matrices are allowed, and perm
    # is the initial perm matrix.
    (A, B, M0, perm) = self.initial_vals ()
    isomorphisms = []
    # go through every permutation, add it to the list if it is an isomorphism
    while self.next_permutation(M0, perm, 0, A.shape[0]):
      M = self.mat_from_perm(perm)
      if self.is_isomorphic(A,B,M):
        self.isomorphisms.append(self.mat_to_iso_map(M))
    return isomorphisms

  # get the first isomorphism
  def get_isomorphism (self):
    M = self.get_isomorphism_matrix ()
    if M is None:
      return None
    else:
      return self.mat_to_iso_map(M)

  # return whether an iso exists
  def has_isomorphism (self):
    return self.get_isomorphism_matrix() is not None


  # FUNCTIONS BELOW HERE NOT CALLABLE BY OUTSIDE WORLD =======================

  # get the first perm matrix which describes an isomorphism
  def get_isomorphism_matrix (self):
    (A, B, M0, perm) = self.initial_vals ()
    while self.next_permutation(M0, perm, 0, A.shape[0]):
      M = self.mat_from_perm (M0,perm)
      if self.is_isomorphic(A,B,M):
        return M
    return None


  def initial_vals(self):
    #initialize some things
    A = self.small.adj_matrix
    B = self.large.adj_matrix
    M0 = zeros((A.shape[0],B.shape[0]))
    i = 0
    keyf = lambda x : x[1]
    # add a 1 to the initial mask if this row/col combo is allowed a priori
    for (uniquei,ixi) in sorted([x for x in self.small.index_dict.iteritems()], key = keyf):
      j = 0
      for (uniquej,ixj) in sorted([x for x in self.large.index_dict.iteritems()], key = keyf):
        nodei = self.small.node_dict[uniquei]
        nodej = self.large.node_dict[uniquej]
        if nodei.label == nodej.label and nodei.degree <= nodej.degree:
          M0[i,j] = 1
        j += 1
      i += 1
    perm = self.first_permutation(M0)
    
    return (A, B, M0, perm)

  # convert a perm matrix to a dictionary describing the iso
  def mat_to_iso_map(self, M):
    iso_map = {}
    for (uniquei,indexi) in self.small.index_dict.iteritems():
      for (uniquej,indexj) in self.large.index_dict.iteritems():
        if M[indexi, indexj] == 1:
          iso_map[uniquei] = uniquej
          break
    return iso_map


  # create a perm matrix from a list describing the position of the 1 in ea. row
  def mat_from_perm(self, M0, perm):
    M = zeros((M0.shape[0],M0.shape[1]))
    for i in range(0,perm.shape[0]):
      M[i,perm[i]] = 1
    return M

   # find the initial permutation
  def first_permutation(self, M0):
    p = zeros((M0.shape[0]))
    p -= 1
    return p

  # find the next permutation
  def next_permutation(self,M0,perm,depth,max_depth):
    if depth == max_depth - 1:
      return self.find_this_row(M0,perm,depth)
    if perm[depth] != -1:
      if  self.next_permutation(M0,perm,depth+1,max_depth):
        return 1
    while self.find_this_row(M0,perm,depth):
      i = depth + 1
      while i < max_depth:
        perm[i] = -1
        i += 1
      if  self.next_permutation(M0,perm,depth+1,max_depth):
        return 1
    return 0

  # find the next allowable position to put in this row in the perm matrix
  def find_this_row(self,M0,perm,depth):
    i = perm[depth] + 1
    max = M0.shape[1]
    while i < max:
      if self.allowable_position(M0,perm,depth,i):
        perm[depth] = i
        return 1
      i += 1
    return 0

  # check if this position is allowable
  def allowable_position(self,M0,perm,depth,i):
    if M0[depth,i] == 0:
      return 0
    j = 0
    while j < depth:
      if perm[j] == i:
        return 0
      j += 1
    return 1

  # check if a perm matrix describes an iso
  def is_isomorphic (self,A,B,M):
    C = matrixmultiply(M,transpose(matrixmultiply(M,B)))
    for i in range(0,A.shape[0]):
      for j in range(0,A.shape[1]):
        if A[i,j] == 1 and C[i,j] == 0:
          return 0 
    return 1
