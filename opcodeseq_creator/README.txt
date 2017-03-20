
The zip file contains:

	1- A csv file containing Davlik opcodes

	2- Sample directory structure containing
		-apk folder with one sample apk
		-tmp folder to hold the decoded apps
		-opseq folder to store the opcode sequece files

	5- a python file run_opcode_seq_creation.py which takes the following arguments:
		
		Python script arguments:

			<apk file directory>   
			1. Pathname to the directory containing apk file 

			<temp directory>
			2. Pathname of a temporary folder to keep the decoded files during the analysis 

			<opseq directory>
			3. Pathname to an arbitrary directory to store the opcode sequence files

			<include support libraries>
			4. (optional) "incl" (without quotes) to include android support library files
           	   	   Note: default behavior is NOT to include those libraries

Steps to run the script:
	

	1) Apktool installation:

	 	-Make sure you have java install by running "java --version"
		 you can install jre by running "apt-get install default-jre"

 	 	-Follow the installation below to install apktool on Linux
  		 https://ibotpeaches.github.io/Apktool/install/
  		 (folowing the instructions will place apktool files in /usr/local/bin)
		 Note: Make sure that they are executable


	2) Extract the zip file to a folder (extracted_folder) and run the following command:

 		extracted_folder$ ./run_opcode_seq_creation.py ./apk ./tmp ./opseq incl 

	

