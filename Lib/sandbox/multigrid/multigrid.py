from scipy import *

import multigridtools
import scipy
import numpy
#import scipy.linsolve.umfpack as um

    
from pydec import gauss_seidel,diag_sparse,inf_norm

def poisson_problem(N):
    """
    Return a sparse CSC matrix for the 2d N*N poisson problem
    with standard 5-point finite difference stencil
    """
    D = 4*numpy.ones(N*N)
    T =  -numpy.ones(N*N)
    O =  -numpy.ones(N*N)
    T[N-1::N] = 0
    return scipy.sparse.spdiags([D,O,T,T,O],[0,-N,-1,1,N],N*N,N*N)


def rs_strong_connections(A,theta):
    if not scipy.sparse.isspmatrix_csr(A): raise TypeError('expected sparse.csr_matrix')

    Sp,Sj,Sx = multigridtools.rs_strong_connections(A.shape[0],theta,A.indptr,A.indices,A.data)
    return scipy.sparse.csr_matrix((Sx,Sj,Sp),A.shape)


def rs_interpolation(A,theta=0.25):
    if not scipy.sparse.isspmatrix_csr(A): raise TypeError('expected sparse.csr_matrix')
    
    S = rs_strong_connections(A,theta)

    T = S.T.tocsr()

    print "RS on A ",A.shape
    
    Ip,Ij,Ix = multigridtools.rs_interpolation(A.shape[0],\
                                               A.indptr,A.indices,A.data,\
                                               S.indptr,S.indices,S.data,\
                                               T.indptr,T.indices,T.data)

    return scipy.sparse.csr_matrix((Ix,Ij,Ip))


def sa_strong_connections(A,epsilon):
    if not scipy.sparse.isspmatrix_csr(A): raise TypeError('expected sparse.csr_matrix')

    Sp,Sj,Sx = multigridtools.sa_strong_connections(A.shape[0],epsilon,A.indptr,A.indices,A.data)
    return scipy.sparse.csr_matrix((Sx,Sj,Sp),A.shape)


def sa_constant_interpolation(A,epsilon=0.08):
    if not scipy.sparse.isspmatrix_csr(A): raise TypeError('expected sparse.csr_matrix')
    
    S = sa_strong_connections(A,epsilon)
    
    #tentative (non-smooth) interpolation operator I
    Ij = multigridtools.sa_get_aggregates(A.shape[0],S.indptr,S.indices)
    Ip = numpy.arange(len(Ij)+1)
    Ix = numpy.ones(len(Ij))
    
    return scipy.sparse.csr_matrix((Ix,Ij,Ip))


def sa_interpolation(A,epsilon=0.08,omega=4.0/3.0):
    if not scipy.sparse.isspmatrix_csr(A): raise TypeError('expected sparse.csr_matrix')
    
    print "SA on A ",A.shape
    
    I = sa_constant_interpolation(A,epsilon)

    D_inv = diag_sparse(1.0/diag_sparse(A))       
    
    D_inv_A  = D_inv * A
    D_inv_A *= -omega/inf_norm(D_inv_A)
    
    #S = (scipy.sparse.spidentity(A.shape[0]).T + D_inv_A)
    #P = S*I

    P = I + (D_inv_A*I)  #same as P=S*I, but faster
        
    return P,I


##def sa_interpolation(A,epsilon=0.08,omega=4.0/3.0):
##    if not scipy.sparse.isspmatrix_csr(A): raise TypeError('expected sparse.csr_matrix')
    
##    S = sa_strong_connections(A,epsilon)
    
##    print "SA on A ",A.shape

##    #tentative (non-smooth) interpolation operator I
##    Ij = multigridtools.sa_get_aggregates(A.shape[0],S.indptr,S.indices)
##    Ip = numpy.arange(len(Ij)+1)
##    Ix = numpy.ones(len(Ij))
    
##    I = scipy.sparse.csr_matrix((Ix,Ij,Ip))
   
##    # (I - \omega D^-1 Af)
##    Jp,Jj,Jx = multigridtools.sa_smoother(A.shape[0],omega,
##                                          A.indptr,A.indices,A.data,
##                                          S.indptr,S.indices,S.data)
    
##    J = scipy.sparse.csr_matrix((Jx,Jj,Jp))

##    return J*I

