#!/bin/bash

# quick shell script that generates time-averaged output of a test file
# for various tests against the generate_time_averages python module
# to use this script, cd to the fre-python-tools dir and do
#
#     source examples/run_timavgs_CLI_examples.sh
#
# the script should produce three new netcdf files containing the averages
source $PWD/examples/timavgs_CLI_example_funcs.sh

PP_COMP=atmos
VAR=LWP
TESTFILE_DIR=$PWD/tests/time_avg_test_files
TESTFILE=$TESTFILE_DIR/${PP_COMP}.197901-198312.${VAR}.nc

if [ -f $TESFILE ] ; then
	
	echo ""
	echo "--------------------------------------------------"	
	echo "target input file="
	echo "$TESTFILE"
	echo ""
	echo "--------------------------------------------------"	
	echo "running cdo timavg examples"	
	cdo_timmean_ex
	echo ""
	echo "--------------------------------------------------"	
	echo "running fre-nctools timavg examples"	
	fre_nctools_timavg_ex

	return 0
else
	echo "failed to run CLI examples"
fi

return 1
