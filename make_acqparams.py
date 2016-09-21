import nibabel as nib
import os, sys
import tempfile
import subprocess
import argparse

def file_exists(fname):
    if not os.path.exists(fname):
        if 'dwell' not in fname:
            print 'ERROR: ' + str(fname) + 'not found.'
            sys.quit(1)
        else:
            return False
    return True

def get_dwell_time():
    if file_exists(dwell_file):
        print 'Reading dwell_time from ' + str(dwell_file)
        dwell_time = subprocess.check_output(str('cat ' + dwell_file), shell=True)
    else:
        if file_exists(par_file) and file_exists(par_file.replace('.PAR','.REC')):
            print 'Assuming 3T magnet strength for calculation of dwell time'
            temp_dir = tempfile.mkdtemp()
            print temp_dir
            convert_cmd = 'parrec2nii -d --field-strength=3 -o ' + str(temp_dir) + ' ' + str(par_file)
            os.system(convert_cmd) 
            temp_dwell_file = dwell_file.replace(dti_dir, temp_dir)
            dwell_time = subprocess.check_output(str('cat ' + temp_dwell_file), shell=True)
            os.remove(temp_dwell_file)
            os.remove(temp_dwell_file.replace('.dwell_time','.nii'))
            os.removedirs(temp_dir)
    return dwell_time

def get_prep_dir():
    par_hdr = nib.load(par_file).header.general_info
    return par_hdr['prep_direction']

def get_prefix():
    if prep_dir in prefixes:
        return prefixes[prep_dir]
    else:
        print 'ERROR: can\'t find the phase encoding direction!'
        sys.quit(1)
        
def write_acq_file():
    with open(out_fname, 'w') as out_file:
        out_file.write(str(prefix + ' ' + dwell_time + '\n'))
    print 'Saved acqparams.txt to ' + out_fname

#This script currently accepts following input:
parser = argparse.ArgumentParser(description='User-defined settings')
parser.add_argument('--dti_file', '-d', required=True, help='DTI file')
parser.add_argument('--par_file', '-p', required=True, help='PAR file')
parser.add_argument('--out_file', '-o', required=False, help='Out file')
args = parser.parse_args()

dti = str(args.dti_file)
par = str(args.par_file)

dti_name = os.path.basename(dti).replace('.nii.gz','')
dti_dir = os.path.dirname(dti)
parrecs_dir = os.path.dirname(par)
par_file = parrecs_dir + '/' + str(dti_name) + '.PAR'
dwell_file = dti_dir + '/' + dti_name + '.dwell_time'

if args.out_file:
    out_fname = str(args.out_file)
else:
    out_fname = dti_dir + '/' + 'acqparams.txt'

#if file_exists(str(args.acq_file)):
#	print 'Found ' + str(args.acq_file)
#	quit()
#else:
#	print 'AcqParams file not specified. Creating from scratch...'

#Main commands
# acqparams.txt should start with prefix that depends on phase encoding direction
# http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy/Faq#How_do_I_know_what_to_put_into_my_--acqp_file
prefixes = {'Left-Right':'-1 0 0','Right-Left':'1 0 0','Anterior-Posterior':'0 -1 0','Posterior-Anterior':'0 1 0'}

prep_dir = get_prep_dir()
dwell_time = get_dwell_time()
prefix = get_prefix()
write_acq_file()


