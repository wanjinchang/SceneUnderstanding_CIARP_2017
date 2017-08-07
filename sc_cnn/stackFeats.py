import numpy as np
import caffe, sys, os, spams, csv, time
import cv2,json

import getopt
import ConfigParser
sys.path.append('/homeLocal/guilherme/sc_cnn/src')


from cnnmodel import CNN
from iocsv import *
import pooling
import minimization
import splitfeats

# -----------MAIN-------------#


if __name__ == "__main__":


	coeffs_outputfile = 'features.csv'
	with_pca = False
	scale_number = '0'	
	fold = '0'
	mode = 'Train'
	scale_number = '0'

	try:
	 opts, args = getopt.getopt(sys.argv[1:],'c:p:o:f:m:',['cfg=','pca=','output=','fold=','mode='])
	 print args	   	

	except getopt.GetoptError:

		 
		 print 'Need configuration file to execute.'
		 sys.exit(2)
	
	for opt, arg in opts:

			if opt in ('-p','--pca'):
			
				print arg        	
				with_pca = True
				json_pca = arg
				pca = json.loads(open(json_pca).read())
				eigen_pca = np.array(pca["eigen-vectors"])
				mean_pca = np.array(pca["mean"])


			if opt in ('-c','--cfg'):

				cfg_file = arg
				print cfg_file


			if opt in ('-o','--output'):

				coeffs_outputfile = arg
				print coeffs_outputfile

			if opt in ('-f','--fold'):

				fold = arg
				print fold


			if opt in ('-m','--mode'):

				mode = arg

			
	Config = ConfigParser.ConfigParser()
	
	Config.read(cfg_file)
	
	features_dataset_csv = ConfigSectionMap('folds',Config)['path'+fold]
	folder_ds = ConfigSectionMap('features',Config)['scale'+scale_number]	

	ConfigClasses = ConfigParser.ConfigParser()
	ConfigClasses.optionxform = str
	ConfigClasses.read(features_dataset_csv)

	classes_samples = ConfigSectionClasses(mode,ConfigClasses)

	labels = []
	all_coeffs = []
	label_count = 0

	print mode

	
	for i in sorted(classes_samples.keys()):

		env_class = i
		#all_feats = []
	
		for j in classes_samples[env_class]:
	
			env_sample = folder_ds+'/'+i+'/'+j

			if not os.path.isfile(env_sample+'_feat.npz'):
				print 'Cannot find '+env_sample
				continue

			
			print "Extracting from: ",env_sample
			feat = readNPY(env_sample+'_feat.npz')
			print np.asfortranarray(feat.tolist())	

			if with_pca:

				feat = cv2.PCAProject(np.array(feat),mean_pca,eigen_pca)
				
				if cv2.norm(feat, cv2.NORM_L2) > 0:
                			feat = feat / cv2.norm(feat, cv2.NORM_L2)

			#print feat.shape
			all_coeffs.append(feat.tolist())
		
			labels.append(label_count)

		
		label_count = label_count + 1

	all_coeffs = np.array(all_coeffs)
	all_coeffs = np.concatenate(all_coeffs, axis=0 )
	print all_coeffs.shape

	writeNPY(np.asarray(all_coeffs),coeffs_outputfile)

	outlabel = os.path.splitext(coeffs_outputfile)[0]+"_label"	

	writeNPY(np.asarray(labels),outlabel)





