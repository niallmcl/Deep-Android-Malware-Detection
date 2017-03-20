#!/usr/bin/env python
import sys
import os
import shutil
import datetime
import logging

sys.path.insert(1, os.path.join(sys.path[0], '../..'))

def main():

    if len(sys.argv) < 4:

        print "Usage", sys.argv[0], "<apk file directory> <temp directory> <opseq directory> <include support libraries>"
        return

    # Reads the location of apk files that need decoding
    apk_file_directory = sys.argv[1]
    print "Reading apks from", apk_file_directory

    # Temporary folder to store the decoded app
    tmp_file_directory = sys.argv[2]
    print "Decoding folder", tmp_file_directory

    # Reads the location that we want to store our opseq files in
    opseq_file_directory = sys.argv[3]
    print "opseq folder", opseq_file_directory

    # Default is not to include smali files in android support libraries unless 4th parameter is provided
    include_libs = False
    if len(sys.argv) == 5:
        include_libs = ((sys.argv[4]) == "incl")
        print "Include Android support library smali files", include_libs

    print "Keep Android support libaray files: "+ str(include_libs)

    # Created a log file in the temp directory
    logging.basicConfig(filename=tmp_file_directory+'/opseq.log', level=logging.DEBUG)

    apks = []

    for name in os.listdir(apk_file_directory):
        if os.path.isfile(os.path.join(apk_file_directory, name)):
            apks.append(name)

    logging.info('Total apks to be decoded {0}'.format(len(apks)))
    print "Total apks to be decoded",len(apks)

    num_local = 0
    before=datetime.datetime.now()
    logging.info('Starting at: {0}'.format(before))
    print "Starting at: {0}",before

    # Looping through all apks
    for apk_hash in apks:
        apk_file_location = os.path.join(apk_file_directory, apk_hash)
        num_local += 1
        logging.info('Decoding apk: {0} apk #: {1}'.format(apk_file_location,num_local))
        print "apk #: ", num_local
        print "apk location: ", apk_file_location

        decoded_location = None
        # Decoding apk into the tmp_file_directory
        decoded_location = decode_application(apk_file_location,tmp_file_directory,apk_hash,include_libs)

        if (not os.path.exists(decoded_location) or not os.listdir(decoded_location)):
            print "smali directory does not exist continue...."
            logging.error('NOT decoded directory: {0}'.format(apk_file_location))
            print "NOT decoded directory:", apk_file_location
            continue

        result =create_opcode_seq(decoded_location,opseq_file_directory,apk_hash)

        if result:
            print "opseq file for apk #",num_local," is created"
            logging.info('opseq file for apk # {0} is created'.format(num_local))
        else:
            logging.error('opseq file creation was not successful')
            print "opseq file creation was not successful"

        if os.path.exists(decoded_location):
            shutil.rmtree(decoded_location)


    after=datetime.datetime.now()
    print "Finished by: {0} ",after
    logging.info('Total time taken:  {0}'.format(after-before))
    print "Total time taken:", after-before

def create_opcode_seq(decoded_dir,opseq_file_directory,apk_hash):
    # Returns true if creating opcode sequence file was successful,
    # searches all files in smali folder,
    # writes the coresponding opcode sequence to a .opseq file
    # and depending on the include_lib value,
    # it includes or excludes the support library files

    dalvik_opcodes = {}
    # Reading Davlik opcodes into a dictionary
    with open("DalvikOpcodes.txt") as fop:
        for linee in fop:
            (key, val) = linee.split()
            dalvik_opcodes[key] = val
    try:
        smali_dir = os.path.join(decoded_dir, "smali")
        opseq_fname=os.path.join(opseq_file_directory,apk_hash+".opseq")

        with open(opseq_fname, "a") as opseq_file:
            for root, dirs, fnames in os.walk(smali_dir):
                for fname in fnames:
                    full_path = os.path.join(root, fname)
                    opseq_file.write(get_opcode_seq(full_path, dalvik_opcodes))
        opseq_file.close()

        return True
    except Exception as e:
        print "Exception occured during opseq creation of apk " ,apk_hash
        logging.error('Exception occured during opseq creation {0}'.format(str(e)))
        return False

def get_opcode_seq(smali_fname, dalvik_opcodes):
    # Returns opcode sequence created from smali file 'smali_fname'.

    opcode_seq=''

    with open(smali_fname, mode="r") as bigfile:
        reader = bigfile.read()
        for i, part in enumerate(reader.split(".method")):
            add_newline = False
            if i!=0:
                method_part=part.split(".end method")[0]
                method_body = method_part.strip().split('\n')
                for line in method_body:
                    if not line.strip().startswith('.') and not line.strip().startswith('#') and line.strip():
                        method_line = line.strip().split()
                        if method_line[0] in dalvik_opcodes:
                            add_newline = True
                            opcode_seq += dalvik_opcodes[method_line[0]]
                if  add_newline:
                    opcode_seq += '\n'
    return opcode_seq

def decode_application (apk_file_location,tmp_file_directory,hash,include_libs):
    # Decodes the apk at apk_file_location and
    # stores the decoded folders in tmp_file_directory

    out_file_location = os.path.join(tmp_file_directory, hash+ ".smali")
    try:
        apktool_decode_apk( apk_file_location, out_file_location,include_libs )
    except ApkToolException:
        print "ApktoolException on decoding"
        logging.error("ApktoolException on decoding apk  {0} ".format(apk_file_location))
        pass
    return out_file_location

def apktool_decode_apk(apk_file, out_file,include_libs):
    # Runs the apktool on a given apk

    apktooldir="/usr/local/bin"

    apktoolcmd = "{0}/apktool d -f {1} -o {2}".format(apktooldir, apk_file, out_file)
    res = os.system(apktoolcmd)
    if res != 0: raise ApkToolException(apktoolcmd)

    # Checks if we should keep the smali files belonging to the android support libraries
    if not include_libs:
        # Don't keep the smali/android folder
        android_folder = os.path.join(out_file, "smali/android")
        if os.path.exists(android_folder):
		    rm_cmd = "rm -r %s" %(android_folder)
 		    os.system(rm_cmd)

# Exception class to signify an Apktool Exception
class ApkToolException(Exception):
    def __init__(self, command):
        self.command = command

    def __str__(self):
        return repr(self.command)

if __name__ == '__main__':
    main()
