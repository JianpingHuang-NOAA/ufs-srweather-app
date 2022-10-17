import xarray as xr
import os
import numpy as np

#Python script to add air quality tracer variables from previous 
#cycle's restart output to atmosphere's initial condition file 
#written by Kai Wang and Jianping Huang 
#04/2022

#previous day aqm tracer file
tracer_file=os.getenv('fv_tracer_file') #'./20200803.120000.fv_tracer.res.tile1.nc'
print(tracer_file)
fv_tracer = xr.open_dataset(tracer_file)


#previous day atmosphere file
gfs_file=os.getenv('wrk_ic_file') #'./gfs_data.tile7.halo0.atmonly.nc'
print(gfs_file)
gfs_atm = xr.open_dataset(gfs_file)

#Remove time dimension and microphysics tracers from previous cycle's
#restart file
ds_out = fv_tracer.drop({'Time','graupel','ice_wat','liq_wat',
                        'o3mr','rainwat','snowwat','sphum'})
ds_out = ds_out.squeeze('Time')

#Rename dimensions and coordinates from restart file to match names
#in atmosphere's IC file
ds_out = ds_out.rename({'xaxis_1':'lon',
                        'yaxis_1':'lat',
                        'zaxis_1':'lev'})

#GFS ICs are defined on one additional (top) layer than tracers in
#the restart file. We extract the top layer from the tracer file 
#and extend the number of vertical levels by 1 (i.e. from 64 to 65) 

ds_out2 = ds_out.isel(lev=slice(1))
ds_new = xr.concat([ds_out2,ds_out],dim='lev')

#rebuild the lev values from 1 to 65
ds_new =ds_new.assign_coords(lev=np.arange(1,66,1.0))

#Add the vertically-extended tracers to the GFS IC file
ds_new2 = xr.merge([gfs_atm,ds_new],join='left')
ds_new2 = ds_new2.drop({'lev','lat','lon'})

#output to a temporary file for the later steps
ds_new2.to_netcdf('tmp1.nc')

