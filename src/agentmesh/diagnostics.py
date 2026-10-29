"""Numerical conditioning diagnostics for small matrices (dependency-free)."""
from math import isfinite, sqrt
from .inverse import _matrix, matvec

def _transpose(a): return [list(c) for c in zip(*a)]
def _dot(a,b): return sum(x*y for x,y in zip(a,b))
def _norm(v): return sqrt(_dot(v,v))

def conditioning(matrix, steps=80, tolerance=1e-10):
    """Estimate singular values via Jacobi eigenvalues of A^T A.

    Appropriate for small matrices; NOT a substitute for an industrial SVD.
    Near rank deficiency is flagged by relative singular-value threshold.
    """
    a=_matrix(matrix)
    if not 1<=len(a)<=20 or not 1<=len(a[0])<=20: raise ValueError("matrix exceeds 20x20 limit")
    if not 1<=steps<=1000 or not 0<tolerance<1: raise ValueError("invalid convergence parameters")
    n=len(a[0])
    gram=[[_dot(col1,col2) for col2 in _transpose(a)] for col1 in _transpose(a)]
    for _ in range(steps):
        off=[(abs(gram[i][j]),i,j) for i in range(n) for j in range(i+1,n)]
        if not off: break
        maxoff,p,q=max(off)
        if maxoff<=tolerance*max(1.0,max(abs(gram[i][i]) for i in range(n))): break
        import math
        theta=.5*math.atan2(2*gram[p][q],gram[q][q]-gram[p][p])
        c,s=math.cos(theta),math.sin(theta)
        # Rotate matrix symmetrically using Jacobi eigenvector transformation.
        for k in range(n):
            if k==p or k==q: continue
            kp,kq=gram[k][p],gram[k][q]
            gram[k][p]=gram[p][k]=c*kp-s*kq
            gram[k][q]=gram[q][k]=s*kp+c*kq
        app,aqq,apq=gram[p][p],gram[q][q],gram[p][q]
        gram[p][p]=c*c*app-2*c*s*apq+s*s*aqq
        gram[q][q]=s*s*app+2*c*s*apq+c*c*aqq
        gram[p][q]=gram[q][p]=0.0
    singular=sorted((sqrt(max(0.0,gram[i][i])) for i in range(n)),reverse=True)
    maximum=singular[0]
    threshold=max(1e-12,maximum*1e-8)
    rank=sum(v>threshold for v in singular)
    condition=(maximum/min(singular) if singular[-1]>threshold else None)
    return {"singular_values":singular,"estimated_rank":rank,
            "condition_number":condition,"near_singular":rank<n,
            "algorithm":"Jacobi on normal equations; exploratory estimate"}

def residual_report(matrix, state, target):
    a=_matrix(matrix)
    x=[float(v) for v in state]; y=[float(v) for v in target]
    if len(a[0])!=len(x) or len(a)!=len(y) or not all(map(isfinite,x+y)):
        raise ValueError("dimension or finite-value mismatch")
    output=matvec(a,x)
    differences=[u-v for u,v in zip(output,y)]
    absolute=_norm(differences)
    relative=absolute/max(_norm(y),1e-12)
    return {"predicted":output,"errors":differences,
            "absolute_residual":absolute,"relative_residual":relative}
