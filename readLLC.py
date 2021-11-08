from xmitgcm import llcreader
import xarray as xr
import glob
from dask.distributed import Client, LocalCluster, progress
import os
import socket
import aiohttp
#
# data is at https://data.nas.nasa.gov/ecco/
# visualizations of the LLC4320 at
# https://data.nas.nasa.gov/viz/vizdata/llc4320/index.html

def return_llcreader(resolution):
    if resolution in ['LLC4320']:
        return llcreader.ECCOPortalLLC4320Model()
    elif resolution in ['LLC2160']:
        return llcreader.ECCOPortalLLC2160Model()
    else:
        return 'resolution not available'

def LLC2disk(var,niters,kiters,resolution,path,face=6,read_grid=True):
    '''
    Download LLC data from ecco data portal 
    
    var (str) :: name of the variable
    niters (list,iterable)  :: list of timesteps
    kiters (list,iteranble) :: list of vertical levels
    model (llcreared instance) :: llcreader instance matching the resolution
    resolution (str) :: name of the resolution
    path (str) :: top directory to save, note that the final directory will be
                  path + '/' + resolution + '/'
    face (int) :: tile number
    '''
    model = return_llcreader(resolution)
    for n,niter in enumerate(niters):
        for k,kiter in enumerate(kiters):
            ds = model.get_dataset(varnames=[var],iters=[niter],k_levels=[kiter],read_grid=read_grid)
            try:
                ds[var].isel(face=face).to_netcdf(path+resolution+'/'+resolution+'_'+var+'_'+str(niter).zfill(8)+'_k'+str(kiter).zfill(3)+'_Arctic.nc')
            except aiohttp.ServerDisconnectedError: #if server is disconnected, it seems to help to just connect again
                ds.close()
                model = return_llcreader(resolution)
                ds = model.get_dataset(varnames=[var],iters=[niter],k_levels=[kiter],read_grid=read_grid)
                ds[var].isel(face=face).to_netcdf(path+resolution+'/'+resolution+'_'+var+'_'+str(niter).zfill(8)+'_k'+str(kiter).zfill(3)+'_Arctic.nc')
            #
            ds.close()
            
    return var+' done!'

if __name__ == '__main__':
    # create a dask cluster
    local_dir = '/scratch/anu074/'+socket.gethostname()+'/'
    if not os.path.isdir(local_dir):
        os.system('mkdir -p '+local_dir)
        print('created folder '+local_dir)
    #
    n_workers = 2
    n_threads = 2
    processes = True
    cluster = LocalCluster(n_workers=n_workers,threads_per_worker=n_threads,processes=processes,
                                            local_directory=local_dir,lifetime='48 hour',lifetime_stagger='10 minutes',
                                            lifetime_restart=True,dashboard_address=None,worker_dashboard_address=None)
    client  = Client(cluster)

dt    = {}
t0    = {}
nt    = {}
# create readers
#model = {}
#model['LLC4320'] = llcreader.ECCOPortalLLC4320Model()
#model['LLC2160'] = llcreader.ECCOPortalLLC2160Model()
#ds0    = model['LLC2160'].get_dataset(k_chunksize=90)
#ds1    = model['LLC4320'].get_dataset(k_chunksize=90)
#
# define start times - these need to be checked online
t0['LLC4320'] = 10368
t0['LLC2160'] = 92160
# also the output iteration step depends on resolution
dt['LLC4320'] = 144
dt['LLC2160'] = 80
#
nt['LLC2160'] = 778
# if needed, this is a way to check the whole thing
#ds    = model['LLC4320'].get_dataset(k_chunksize=90)
path  = '/projects/NS9869K/'
#
# Download one timestep
resolution = 'LLC2160'
#var='Eta'
#var='SIheff'
#var='SIarea'
var='SIhsalt'
for d in range(0,nt['LLC2160']): #there are 778 full days in
    print('day '+str(d))
    # load 24 hours
    niters = range(t0[resolution]+d*24*dt[resolution],t0[resolution]+(d+1)*24*dt[resolution],dt[resolution])
    out    = LLC2disk(var,niters,range(0,1),resolution,path,read_grid=False)
    # calculate daily mean and std
    daily  = xr.open_mfdataset(sorted(glob.glob(path+resolution+'/'+resolution+'_'+var+'_*_Arctic.nc')))
    daily[var].mean('time').to_dataset(name=var).to_netcdf(path+resolution+'/'+resolution+'_'+var+'_Arctic_day_'+str(d).zfill(4)+'_mean.nc')
    daily[var].std('time').to_dataset(name=var).to_netcdf(path+resolution+'/'+resolution+'_'+var+'_Arctic_day_'+str(d).zfill(4)+'_std.nc')
    #remove the hourly fields
    os.system('rm '+path+resolution+'/'+resolution+'_'+var+'_*_Arctic.nc')
#out1 = LLC2disk('Theta',range(t0[resolution],t0[resolution]+dt[resolution],dt[resolution]),range(0,85),resolution,path)
#out2 = LLC2disk('Salt',range(t0[resolution],t0[resolution]+dt[resolution],dt[resolution]),range(0,85),resolution,path)
#%time out = LLC2disk('U',range(t0[resolution],t0[resolution]+dt[resolution],dt[resolution]),range(0,85),resolution,path)
#%time out = LLC2disk('V',range(t0[resolution],t0[resolution]+dt[resolution],dt[resolution]),range(0,85),resolution,path)

#resolution = 'LLC4320'
#%time out = LLC2disk('U',range(t0[resolution],t0[resolution]+dt[resolution],dt[resolution]),range(0,1),resolution,path)
