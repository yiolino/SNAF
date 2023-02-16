#!/data/salomonis2/LabFiles/Frank-Li/neoantigen/revision/ts/bayesian/pytorch_pyro_mamba_env/bin/python3.7

import anndata as ad  # need to install from -c bioconda, not -c conda-forge, but still fail (install 0.6.2 instead), finally use pip to solve (0.8.0)
import numpy as np
import pandas as pd
import os,sys
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
import pickle
import torch
import pyro
import pickle
import pyro.poutine as poutine
import pyro.distributions as dist
import pyro.distributions.constraints as constraints
from pyro.infer import SVI,Trace_ELBO
from pyro.optim import Adam,ClippedAdam
from kneed import KneeLocator
from scipy.sparse import csr_matrix


# functions
def compute_y(adata,uids):
    info = adata[uids,:]
    y = info.X.toarray() / adata.var['total_count'].values.reshape(1,-1)
    return y

def compute_x(adata,uids,cond_Y):
    adata = adata.copy()
    adata.X = csr_matrix(np.where(cond_Y,adata.X.toarray(),0))
    total_tissue = adata.var['tissue'].unique()
    valid_tissue = [tissue for tissue in total_tissue if adata[:,adata.var['tissue']==tissue].shape[1] >= 10]
    x = np.zeros((len(uids),len(valid_tissue)))
    for i,tissue in enumerate(valid_tissue):
        sub = adata[uids,adata.var['tissue']==tissue]
        total_count = sub.shape[1]
        c = np.count_nonzero(np.where(sub.X.toarray()<1,0,sub.X.toarray()),axis=1)
        scaled_c = np.round(c * (25/total_count),0)
        x[:,i] = scaled_c
    return x,adata

def diagnose(final_path,ylim=(-1,200),output_name='diagnosis.pdf'):
    df = pd.read_csv(final_path,sep='\t',index_col=0)
    fig,ax = plt.subplots()
    im = ax.scatter(df['X_mean'],df['Y_mean'],c=df['mean_sigma'],s=0.5**2,cmap='viridis')
    plt.colorbar(im)
    ax.set_ylabel('average_normalized_counts')
    ax.set_xlabel('average_n_present_samples_per_tissue')
    ax.set_ylim(ylim)
    plt.savefig(output_name,bbox_inches='tight')
    plt.close()

def thresholding_kneedle(cpm,plot=False,S=1,interp_method='polynomial'):
    x = cpm[cpm > 0]  # all non-zero values
    if len(x) <= 2:
        return 0
    else:
        actual_x = np.arange(len(x))
        actual_y = np.sort(x)
        kneedle = KneeLocator(actual_x,actual_y,S=S,curve='convex',direction='increasing',interp_method=interp_method)
        knee = kneedle.knee
        if knee is not None:
            knee_index = round(knee,0)
        else:
            knee_index = 0
        if plot:
            kneedle.plot_knee()
            plt.savefig('kneedle_data.pdf',bbox_inches='tight')
            plt.close()
            kneedle.plot_knee_normalized()
            plt.savefig('kneedle_norm.pdf',bbox_inches='tight')
            plt.close()
        return actual_y[knee_index]

def threshold(cpm,method,**kwargs):
    if method == 'kneedle':
        th = thresholding_kneedle(cpm,**kwargs)
    elif method == 'otsu':
        th = thresholding_otsu(cpm,**kwargs)
    cpm = np.where(cpm>th,cpm,0)
    cond = cpm>th
    return cpm, cond, th

def thresholding_otsu(cpm,step=0.05,dampen_factor=20):
    x = cpm[cpm > 0]  # all non-zero values
    criteria = []
    ths = np.arange(0,x.max(),step)
    for th in ths:
        thresholded_x = np.where(x>=th,1,0)
        w1 = np.count_nonzero(thresholded_x)/len(x)
        w0 = 1 - w1
        if w1 == 0 or w0 == 0:
            value = np.inf
        else:
            x1 = x[thresholded_x==1]
            x0 = x[thresholded_x==0]
            var1 = x1.var()
            var0 = x0.var()
            value = w0 * var0 + w1 * var1 / dampen_factor
        criteria.append(value)
    best_th = ths[np.argmin(criteria)]
    return best_th


adata = ad.read_h5ad('coding.h5ad')
uids = adata.obs_names.tolist()

# from gtex_viewer import *
# gtex_viewer_configuration(adata)
# df = gtex_visual_norm_count_combined('ENSG00000198681',xlim=None,ylim=(0,10),save_df=False)
# Y = compute_y(adata,uids)
# thresholded_Y = np.empty_like(Y,dtype=np.float32)
# cond_Y = np.empty_like(Y,dtype=bool)
# ths = []
# for i in tqdm(range(Y.shape[0]),total=Y.shape[0]):
#     thresholded_Y[i,:], cond_Y[i,:], th = threshold(Y[i,:],'kneedle')
#     ths.append(th)
# pd.Series(index=uids,data=ths,name='threshold').to_csv('threshold.txt',sep='\t')

# with open('Y_threshold.p','wb') as f:
#     pickle.dump(thresholded_Y,f)
# with open('cond_Y.p','wb') as f:
#     pickle.dump(cond_Y,f)


# with open('cond_Y.p','rb') as f:
#     cond_Y = pickle.load(f)
# thresholded_X,adata_new = compute_x(adata,uids,cond_Y)


# uid = 'ENSG00000198681'
# from gtex_viewer import *
# gtex_viewer_configuration(adata)
# df = gtex_visual_norm_count_combined(uid,xlim=None,ylim=None,save_df=True)
# print(threshold(df['value_cpm'].values,'kneedle'));sys.exit('stop')
# gtex_visual_per_tissue_count(uid)


# with open('X_threshold.p','wb') as f:
#     pickle.dump(thresholded_X,f)


with open('X.p','rb') as f:
    X = pickle.load(f)
with open('Y.p','rb') as f:
    Y = pickle.load(f)

# debug
'''
ENSG00000198681  MAGEA1
ENSG00000221867  MAGEA3
ENSG00000150991  a very highly expressed one
'''
# uid = 'ENSG00000150991'
# index = uids.index(uid)
# X = X[[index],:]
# Y = Y[[index],:]
# print(X.shape,Y.shape)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)
Y = np.where(Y==0,1e-5,Y)
amplifier = 10000
X = X * amplifier
X = torch.tensor(X.T,device=device)
Y = torch.tensor(Y.T,device=device)
n = X.shape[1]
s = Y.shape[0]
t = X.shape[0]


adam = Adam({'lr': 0.002,'betas':(0.95,0.999)}) 
clipped_adam = ClippedAdam({'betas':(0.95,0.999)})
elbo = Trace_ELBO()

def model_mle(X,Y):
    sigma = pyro.param('sigma',lambda:torch.tensor(np.full(n,0.5),device=device),constraint=constraints.interval(0.05,1))
    beta_y = pyro.sample('beta_y',dist.Gamma(10,1))
    beta_x = pyro.sample('beta_x',dist.Gamma(250000,1))
    with pyro.plate('data_X',t):
        c = pyro.sample('c',dist.Poisson(beta_x*sigma).expand([t,n]).to_event(1),obs=X)
    with pyro.plate('data_Y',s):
        nc = pyro.sample('nc',dist.LogNormal(beta_y*sigma,0.5).expand([s,n]).to_event(1),obs=Y)



def guide_mle(X,Y):
    pass

# train
n_steps = 5000
pyro.clear_param_store()
svi = SVI(model_mle, guide_mle, adam, loss=Trace_ELBO())
losses = []
for step in tqdm(range(n_steps),total=n_steps):  
    loss = svi.step(X,Y)
    losses.append(loss)
plt.figure(figsize=(5, 2))
plt.plot(losses)
plt.xlabel("SVI step")
plt.ylabel("ELBO loss")
plt.savefig('elbo_loss.pdf',bbox_inches='tight')
plt.close()


sigma = pyro.param('sigma').data.cpu().numpy()
df = pd.Series(index=uids,data=sigma,name='mean_sigma').to_frame()
with open('X.p','rb') as f:
    X = pickle.load(f)
with open('Y.p','rb') as f:
    Y = pickle.load(f)
Y_mean = Y.mean(axis=1)
X_mean = X.mean(axis=1)
df['Y_mean'] = Y_mean
df['X_mean'] = X_mean
df.to_csv('mle_results.txt',sep='\t')
diagnose('mle_results.txt',output_name='pyro_mle_diagnosis.pdf')
sys.exit('stop')


