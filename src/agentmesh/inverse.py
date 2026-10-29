"""Linear inverse, cross-coupling and bounded reflexive feedback (small real systems)."""
from dataclasses import dataclass
from math import isfinite, sqrt

def _matrix(a):
    rows=[list(map(float,row)) for row in a]
    if not rows or not rows[0] or any(len(row)!=len(rows[0]) for row in rows):
        raise ValueError("matrix must be nonempty and rectangular")
    if not all(isfinite(v) for row in rows for v in row):
        raise ValueError("matrix must be finite")
    return rows

def matvec(a,x):
    return [sum(v*t for v,t in zip(row,x)) for row in a]

def _solve(a,b,tolerance=1e-12):
    n=len(b)
    aug=[list(a[i])+[float(b[i])] for i in range(n)]
    scale=max((abs(v) for row in a for v in row),default=0.0)
    if scale==0: raise ValueError("singular system")
    for k in range(n):
        pivot=max(range(k,n),key=lambda i:abs(aug[i][k]))
        if abs(aug[pivot][k])<=tolerance*scale:
            raise ValueError("singular or numerically unstable system")
        aug[k],aug[pivot]=aug[pivot],aug[k]
        p=aug[k][k]
        for j in range(k,n+1): aug[k][j]/=p
        for i in range(k+1,n):
            factor=aug[i][k]
            for j in range(k,n+1): aug[i][j]-=factor*aug[k][j]
    x=[0.0]*n
    for i in range(n-1,-1,-1):
        x[i]=aug[i][-1]-sum(aug[i][j]*x[j] for j in range(i+1,n))
    return x

def inverse_linear(a,target,ridge=1e-6):
    """Tikhonov inverse: argmin ||Ax-y||² + ridge||x||², ridge>0."""
    a=_matrix(a)
    y=[float(v) for v in target]
    if len(y)!=len(a) or not all(map(isfinite,y)):
        raise ValueError("target mismatch or nonfinite value")
    if not isfinite(ridge) or ridge<=0: raise ValueError("ridge must be finite and positive")
    n=len(a[0])
    lhs=[[sum(row[i]*row[j] for row in a)+(ridge if i==j else 0)
          for j in range(n)] for i in range(n)]
    rhs=[sum(row[i]*v for row,v in zip(a,y)) for i in range(n)]
    return _solve(lhs,rhs)

def cross_coupling(weights,states):
    """W[i][j] encodes influence from agent j toward agent i."""
    w=_matrix(weights)
    x=[float(v) for v in states]
    if len(w)!=len(x) or any(len(row)!=len(x) for row in w) or not all(map(isfinite,x)):
        raise ValueError("coupling dimension mismatch")
    return matvec(w,x)

@dataclass(frozen=True)
class FeedbackResult:
    state: tuple[float,...]
    converged: bool
    iterations: int
    residual: float
    history: tuple[float,...]

def reflexive_feedback(weights,initial,desired,*,gain=0.5,max_steps=100,tol=1e-7,bounds=None):
    """x <- clip(x + gain*(desired - Wx)); reports failure to converge."""
    w=_matrix(weights)
    x=[float(v) for v in initial]
    d=[float(v) for v in desired]
    n=len(w)
    if any(len(row)!=n for row in w) or len(x)!=n or len(d)!=n or not all(map(isfinite,x+d)):
        raise ValueError("incompatible state or target")
    if not isfinite(gain) or gain<=0 or not isfinite(tol) or tol<=0 or max_steps<1:
        raise ValueError("invalid feedback parameters")
    if bounds is not None and (len(bounds)!=n or any(len(p)!=2 or p[0]>p[1] or not all(map(isfinite,p)) for p in bounds)):
        raise ValueError("invalid bounds")
    history=[]
    for step in range(max_steps+1):
        error=[dv-ov for dv,ov in zip(d,matvec(w,x))]
        residual=sqrt(sum(v*v for v in error))
        history.append(residual)
        if residual<=tol: return FeedbackResult(tuple(x),True,step,residual,tuple(history))
        if step==max_steps: break
        x=[v+gain*e for v,e in zip(x,error)]
        if bounds is not None: x=[max(lo,min(hi,v)) for v,(lo,hi) in zip(x,bounds)]
    return FeedbackResult(tuple(x),False,max_steps,residual,tuple(history))
