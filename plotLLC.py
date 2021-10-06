import xarray as xr
import xgcm
import matplotlib.pyplot as plt
from matplotlib.colors import from_levels_and_colors
import cartopy.crs as ccrs
import numpy as np
#
levelsT=np.array([-2,-1.5,-1,-0.75,-0.5,-.25,0,0.25,0.5,0.75,1,1.25,1.5,2,2.5,3,4,5,6,8,10])
cmap0=plt.get_cmap('viridis')
cmlist=[];
for cl in np.linspace(0,252,len(levelsT)+1): cmlist.append(int(cl))
cmapT, normT = from_levels_and_colors(levelsT,cmap0(cmlist),extend='both');
# LOAD DATA
data  = xr.open_mfdataset('/projects/NS9869K/LLC2160/LLC2160_Theta_00092160_k*_Arctic.nc')
dataU = xr.open_mfdataset('/projects/NS9869K/LLC2160/LLC2160_U_00092160_k*_Arctic.nc')
dataV = xr.open_mfdataset('/projects/NS9869K/LLC2160/LLC2160_V_00092160_k*_Arctic.nc')
#
all_coords = xr.merge([data.coords.to_dataset(),dataU.coords.to_dataset(),dataV.coords.to_dataset()])
grid = xgcm.Grid(all_coords, periodic=['X', 'Y'])
# PLOT
for k in [0,30]:
    print(k)
    projection2=ccrs.NearsidePerspective(central_longitude=15, central_latitude=88.0, satellite_height = 5E6)
    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(10,10),sharex=True,sharey=True,subplot_kw={'projection':projection2})
    # for whatever reason the plotting seems not to be super straightforward
    cm1 = ax.contourf(data.XC,data.YC,
                      data.Theta.isel(time=0,k=k).where(data.XC>=0),levels=levelsT,extend='max',transform=ccrs.PlateCarree())
    cm1 = ax.contourf(data.XC,data.YC,
                      data.Theta.isel(time=0,k=k).where(data.XC<0),levels=levelsT,extend='max',transform=ccrs.PlateCarree())
    KE = 0.5*(grid.interp((dataU.U.isel(k=k,time=0)*dataU.hFacW.isel(k=k))**2, 'X') + grid.interp((dataV.V.isel(k=k,time=0)*dataV.hFacS.isel(k=k))**2,'Y')).compute()
    ax.contour(data.XC,data.YC,KE.where(data.XC>=0),levels=[0.01,0.05,0.1],colors='gray',linewidths=0.5,transform=ccrs.PlateCarree())
    ax.contour(data.XC,data.YC,KE.where(data.XC<0),levels=[0.01,0.05,0.1],colors='gray',linewidths=0.5,transform=ccrs.PlateCarree())
    ax.coastlines()
    #
    ax.set_extent([-180, 180, 70, 90], crs=ccrs.PlateCarree())
    #
    cax1  = fig.add_axes([0.92,0.11,0.02,0.78])  
    cbar1 = plt.colorbar(mappable=cm1,cax=cax1)
    clab1 = cbar1.ax.set_ylabel(r'Temperature [$\degree$C]',fontsize=16)
    #
    fig.savefig('/projects/NS2345K/www/anu074/LLC2160_Thetao_at_'+str(int(abs(data.Z.isel(k=k).values))).zfill(4)+'m_depth.png',
                dpi=150,bbox_inches='tight',bbox_extra_artists=[clab1])
