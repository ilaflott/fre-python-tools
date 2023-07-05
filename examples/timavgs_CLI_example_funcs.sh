#!/bin/bash

function cdo_timmean_ex(){

	#avg the variable at each lat/lon point over each month --> 12 #'s per lat/lon point (one per month)
	outfile=$TESTFILE_DIR/cdo_ymonmean_CLI_test_${PP_COMP}_${VAR}_1979_5y.nc
	if [ -f $outfile ] ; then rm -f $outfile ; fi
	cdo ymonmean $TESTFILE $outfile
	unset outfile
	
	## avg the variable at each lat/lon point over each season --> four # per lat/lon point 
	outfile=$TESTFILE_DIR/cdo_yseasmean_CLI_test_${PP_COMP}_${VAR}_1979_5y.nc
	if [ -f $outfile ] ; then rm -f $outfile ; fi
	cdo yseasmean $TESTFILE $outfile
	unset outfile
	
	## avg the variable at each lat/lon point over all points in time --> one # per lat/lon point 
	outfile=$TESTFILE_DIR/cdo_timmean_CLI_test_${PP_COMP}_${VAR}_1979_5y.nc
	if [ -f $outfile ] ; then rm -f $outfile ; fi
	cdo -b F64 timmean $TESTFILE $outfile
	ls $outfile
	unset outfile

	return 0
}

function fre_nctools_timavg_ex(){
	#if you already have fre-nctools, this step is unnecessary
	module load fre-nctools

	outfile=$TESTFILE_DIR/fre_nctools_timavg_CLI_test_r8_mb_${PP_COMP}_${VAR}_1979_5y.nc
	if [ -f $outfile ] ; then rm -f $outfile ; fi
	timavg.csh -d -r8 -mb -o $outfile $TESTFILE
	ls $outfile
	ncdiff $outfile tests/time_avg_test_files/frepytools_timavg_atmos.197901-198312.LWP.nc ./frepytools_v_frenc_timavg_r8mb.nc
	unset outfile

	outfile=$TESTFILE_DIR/fre_nctools_timavg_CLI_test_r8_b_${PP_COMP}_${VAR}_1979_5y.nc
	if [ -f $outfile ] ; then rm -f $outfile ; fi
	./timavg.csh -r8 -b -o $outfile $TESTFILE
	ls $outfile
	ncdiff $outfile tests/time_avg_test_files/frepytools_timavg_atmos.197901-198312.LWP.nc ./frepytools_v_frenc_timavg_r8b.nc
	unset outfile

	return 0
}
