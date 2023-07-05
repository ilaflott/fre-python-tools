#!/usr/bin/env python
''' tools for generating time averages from various packages '''
import argparse

def generate_frepythontools_timavg(infile=None, outfile=None, avg_type='all',
                                   unwgt=False, stddev=False):
    ''' my own time-averaging function. mostly an exercise. '''
    if __debug__:
        print('calling generate_frepythontools_timavg for file: ' + infile)

    if avg_type!='all':
        print(f'ERROR: avg_type={avg_type} is not supported by this function at this time.')
        return 1

    import math
    import numpy
    from netCDF4 import Dataset
    
    nc_fin = Dataset(infile, 'r')

    nc_fin_var=infile.split('/').pop().split('.')[-2]
    if __debug__:
        print(f'nc_fin_var={nc_fin_var}')


    # check for the variable we're hoping is in the file
    fin_vars=nc_fin.variables
    for key in fin_vars:
        if str(key)==nc_fin_var:
            time_bnds=nc_fin['time_bnds'][:].copy()
            key_found=True
            break
    if not key_found:
        print('requested variable not found. exit.')
        return 1


    # check for mask (will be important for later dev stages)
    #is_masked = ma.is_masked(val_array)

    # read in sizes of specific axes
    fin_dims =nc_fin.dimensions
    time_bnd=fin_dims['time'].size
    if not unwgt: #compute sum of weights
        wgts=numpy.zeros((time_bnd),dtype=float)
        wgts_sum=0
        for tim in range(time_bnd):
            wgts_sum+=(time_bnds[tim][1] - time_bnds[tim][0])
            wgts[tim]=time_bnds[tim][1]-time_bnds[tim][0]
            print(f'wgts[{tim}]={wgts[tim]}')


    # initialize arrays
    lat_bnd=fin_dims['lat'].size
    print(f'lat_bnd={lat_bnd}')
    lon_bnd=fin_dims['lon'].size
    print(f'lon_bnd={lon_bnd}')
    avgvals=numpy.zeros((1,lat_bnd,lon_bnd),dtype=float)
    if stddev:
        print(f'computing std. deviations')
        stddevs=numpy.zeros((1,lat_bnd,lon_bnd),dtype=float)

    # compute average, for each lat/lon coordinate over time record in file
    #count=0
    #COUNT_MAX_DEBUG=15
    if not unwgt: #weighted case
        print(f'computing weighted statistics')
        for lat in range(lat_bnd):
            lon_val_array=numpy.moveaxis( nc_fin[nc_fin_var][:],0,-1)[lat].copy()
            #if (lat%3 == 0):
            #    print(f'lat # {lat}/{lat_bnd}')
            #count+=1
            
            for lon in range(lon_bnd):
                tim_val_array= lon_val_array[lon].copy() #numpy.moveaxis( lon_val_array[:], 0, -1 )[lon].copy()
                avgvals[0][lat][lon]=sum( (tim_val_array[tim] * wgts[tim] )
                                          for tim in range(time_bnd) ) / wgts_sum
                #print(f'avgvals[0][{lat}][{lon}]={avgvals[0][lat][lon]}')
                #return 1
                if stddev: #std dev *of the mean*. not a vanilla std dev.
                    stddevs[0][lat][lon]=math.sqrt(
                                                 sum( wgts[tim] *
                                                      (tim_val_array[tim]-avgvals[0][lat][lon]) ** 2.
                                                     for tim in range(time_bnd) )
                                                  ) / wgts_sum
                del tim_val_array
            del lon_val_array
    else: #unweighted case
        print(f'computing unweighted statistics')
        for lat in range(lat_bnd):
            lon_val_array=numpy.moveaxis( nc_fin[nc_fin_var][:],0,-1)[lat].copy()
            for lon in range(lon_bnd):
                tim_val_array= lon_val_array[lon].copy() #numpy.moveaxis( lon_val_array[:], 0, -1 )[lon].copy()
                avgvals[0][lat][lon]=sum( # no time sum needed here, b.c. unweighted, so sum
                    tim_val_array[tim] for tim in range(time_bnd)
                                        ) / time_bnd
                #print(f'avgvals[0][{lat}][{lon}]={avgvals[0][lat][lon]}')
                #return 1
                if stddev:
                    stddevs[0][lat][lon]=math.sqrt(
                                                 sum(
                                          (tim_val_array[tim]-avgvals[0][lat][lon]) ** 2.
                                                     for tim in range(time_bnd)
                                                    ) / ( (time_bnd - 1. ) * time_bnd )
                                                  )
                del tim_val_array
            del lon_val_array

    # write output file
    #with Dataset( outfile, 'w', format='NETCDF4', persist=True ) as nc_fout:
    nc_fout= Dataset( outfile, 'w', format='NETCDF4', persist=True )
        
    # write file dimensions
    print('\nwriting output dimensions.')
    for key in fin_dims:
        #print(f'key={key}')
        if key=='time':
            try:
                nc_fout.createDimension( dimname='time', size=1 )
            except:
                print(f'problem. cannot read/write time dimensions')
                return 1        
        else:            
            nc_fout.createDimension( dimname=key, size=fin_dims[key].size )
    print('done writing output dimensions.\n')
    ##
        
    # write output variables (aka data)
    print('\nwriting output variables.')
    unwritten_var_list=[]
    for var in fin_vars:
        print(f'\nattempting to create output variable: {var}')    #nc_fout.createVariable(var, fin_vars[var].dtype, (var))
        try:
            nc_fout.createVariable(var, fin_vars[var].dtype, fin_vars[var].dimensions)
            if var ==nc_fin_var:#our averaged variable
                nc_fout.variables[var][:]=avgvals
                if stddev:
                    nc_fout.createVariable(var+'_stddevmean', fin_vars[var].dtype, fin_vars[var].dimensions)
                    nc_fout.variables[var+'_stddevmean'][:]=stddevs
            print(f'\nlooking at attributes of variable: {var}')
            for ncattr in fin_vars[var].ncattrs():
                print(f'ncattr={ncattr}')
                try: nc_fout.variables[var].setncattr(ncattr, fin_vars[var].getncattr(ncattr))
                except: print(f'could not read var={var} ncattr={ncattr}')
        except:
            unwritten_var_list.append(var)
            print(f'WARNING: could not create output variable: {var}')
            print(f'____________________________________________________________________________')
            print(f'var={var}')
            print(f'fin_vars[{var}].dtype={fin_vars[var].dtype}')
            print(f'fin_vars[{var}]={fin_vars[var]}')
            print(f'fin_vars[{var}].dimensions={fin_vars[var].dimensions}')
            print(f'          ------------------------------------------------------------      ')
    print('done writing output variables.')
    ##



    # write file global attributes
    print('writing output attributes.')
    fin_ncattrs=nc_fin.ncattrs()
    unwritten_ncattr_list=[]
    for ncattr in fin_ncattrs:
        print(f'\n_________\nncattr={ncattr}')
        try:
            print(f'{repr(fin_ncattrs.getncattr(ncattr))}')
        except:
            print(f'could not get nc file attribute: {ncattr}')
            unwritten_ncattr_list.append(ncattr)
    #    if key=='time':
    #        nc_fout.createVariable( dimname='time', size=1 )
    #    else:
    #        nc_fout.createVariable( dimname=key, size=fin_dims[key].size)            
        
    


    nc_fout.close()
    #close input file
    nc_fin.close()
    print(f'wrote ouput file: {outfile}')
    if len(unwritten_var_list)>0:
        print(f'WARNING: unwritten_var_list={unwritten_var_list}')
    if len(unwritten_ncattr_list)>0:
        print(f'WARNING: unwritten_ncattr_list={unwritten_ncattr_list}')

    return 0


# must have fre-nctools, which is not included in the conda env by default.
def generate_frenctools_timavg(infile=None, outfile=None, avg_type='all', do_weighted_avg=True, do_std_dev=True):
    ''' use fre-nctool's CLI timavg.csh with subprocess call '''
    if __debug__:
        print(f'calling generate_frenctools_timavg for file: {infile}')
    exitstatus=1
    if avg_type!='all':
        print(f'ERROR: avg_type={avg_type} is not supported by this function at this time.')
        return exitstatus

    from subprocess import Popen, PIPE

    precision='-r8'
    timavgcsh_command=['timavg.csh', precision, '-mb','-o', outfile, infile]
    exitstatus=1
    with Popen(timavgcsh_command,
               stdout=PIPE, stderr=PIPE, shell=False) as subp:
        output=subp.communicate()[0]
        print(f'output={output}')

        if subp.returncode < 0:
            print('error')
        else:
            print('success')
            exitstatus=0
    
    return exitstatus


def generate_cdo_timavg(infile=None, outfile=None, avg_type=None):
    ''' use cdo's python module for time-averaging '''
    if __debug__:
        print(f'calling generate_cdo_timavg for file: {infile}')
        print(f'outfile={outfile}')
        print(f'avg_type={avg_type}')

    if all([avg_type!='all',avg_type!='seas',avg_type!='month',
            avg_type is not None]):
        print(f'ERROR, avg_type requested unknown.')
        return 1

    from cdo import Cdo
    _cdo=Cdo()
    
    if avg_type == 'all':
        print(f'time-averaging requested.')
        _cdo.timmean(input=infile, output=outfile, returnCdf=True)
        print(f'done averaging over all time.')
    elif avg_type == 'seas':
        print(f'seasonal time-averaging requested.')
        _cdo.yseasmean(input=infile, output=outfile, returnCdf=True)
        print(f'done averaging over seasons.')
    elif avg_type == 'month':
        print(f'time-averaging requested.')
        _cdo.ymonmean(input=infile, output=outfile, returnCdf=True)
        print(f'done averaging over months.')
    else:
        print(f'problem.')
        return 1

    print(f'done averaging')

    return 0


def generate_time_average(pkg=None, infile=None, outfile=None, avg_type=None,unwgt=False,stddev=False):
    #print(f'unwgt={unwgt}, stddev={stddev}')
    #return 1
    ''' steering function to various averaging functions above'''
    if __debug__:
        print(f'calling generate time averages for file: {infile}')
    exitstatus=1

    #needs a case statement
    if   pkg == 'cdo'            :
        exitstatus=generate_cdo_timavg(            infile=infile, outfile=outfile, avg_type=avg_type )
    elif pkg == 'fre-nctools'    :
        exitstatus=generate_frenctools_timavg(     infile=infile, outfile=outfile, avg_type=avg_type )
    elif pkg == 'fre-python-tools':
        exitstatus=generate_frepythontools_timavg( infile=infile, outfile=outfile, avg_type=avg_type , unwgt=unwgt, stddev=stddev)
    else                         :
        print('requested package unknown. exit.')
        exitstatus=1

    return exitstatus

def main():
    ''' main, for steering, when called like `python generate_time_averages.py` '''
    argparser = argparse.ArgumentParser(
        description='generate time averages for specified set of netCDF files. Example: \
        generate-time-averages.py /path/to/your/files/')
    argparser.add_argument('inf',
                           help='input file name',
                           type=str)
    argparser.add_argument('outf',
                           help='output file name',
                           type=str)
    argparser.add_argument('-p','--pkg',
                          help='package to use for timavg [e.g. cdo, fre-nctools, fre-python-tools]',
                          type=str, default='cdo')
    argparser.add_argument('-a','--avg',
                           help='type of time average to generate [e.g. month,seas,all].\n \
                                 currently, fre-nctools and fre-python-tools pkg options\n \
                                 do not support seasonal and monthly averaging.\n',
                          type=str, default='all')
    argparser.add_argument('-u','--unwgt',
                           help='compute requested statistics with no weights.',
                           action='store_true', default=False)
    argparser.add_argument('-s','--stddev',
                           help='compute standard deviations for time-averages as well.',
                           action='store_true', default=False)
    cli_args = argparser.parse_args()
    exitstatus=generate_time_average( cli_args.pkg, cli_args.inf, cli_args.outf, cli_args.avg ,
                                      cli_args.unwgt, cli_args.stddev)
    if exitstatus!=0:
        print(f'WARNING: exitstatus={exitstatus}!=0. Something exited poorly!')
    else:
        print(f'time averaging finished successfully')

if __name__ == '__main__':
    import time
    start_time=time.perf_counter()
    #main(sys.argv)
    main()
    finish_time=time.perf_counter()
    print(f'Finished in total time {round(finish_time - start_time , 2)} second(s)')
