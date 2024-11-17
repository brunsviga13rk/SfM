#!/usr/bin/python

# Indicate the openMVG binary directory
OPENMVG_SFM_BIN = "/home/sfmop/openmvg/build/Linux-x86_64-RELEASE"

OPENMVS_SFM_BIN = "/home/sfmop/openmvs/make/bin"

# Indicate the openMVG camera sensor width directory
CAMERA_SENSOR_WIDTH_DIRECTORY = "/home/sfmop/openmvg/src/software/SfM" + "/../../openMVG/exif/sensor_width_database"

import os
import subprocess
import sys

if len(sys.argv) < 3:
    print ("Usage %s image_dir output_dir" % sys.argv[0])
    sys.exit(1)

input_dir = sys.argv[1]
output_dir = sys.argv[2]
matches_dir = os.path.join(output_dir, "matches")
reconstruction_dir = os.path.join(output_dir, "reconstruction_sequential")
camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")

print ("Using input dir  : ", input_dir)
print ("      output_dir : ", output_dir)

# Create the ouput/matches folder if not present
if not os.path.exists(output_dir):
  os.mkdir(output_dir)
if not os.path.exists(matches_dir):
  os.mkdir(matches_dir)

print ("==> [OpenMVG] Intrinsics analysis")
pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-d", camera_file_params] )
pIntrisics.wait()

print ("==> [OpenMVG] Compute features")
pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT"] )
pFeatures.wait()

print ("==> [OpenMVG] Compute matching pairs")
pPairs = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_PairGenerator"), "-i", matches_dir+"/sfm_data.json", "-o" , matches_dir + "/pairs.bin" ] )
pPairs.wait()

print ("==> [OpenMVG] Compute matches")
pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-p", matches_dir+ "/pairs.bin", "-o", matches_dir + "/matches.putative.bin" ] )
pMatches.wait()

print ("==> [OpenMVG] Filter matches" )
pFiltering = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_GeometricFilter"), "-i", matches_dir+"/sfm_data.json", "-m", matches_dir+"/matches.putative.bin" , "-g" , "f" , "-o" , matches_dir+"/matches.f.bin" ] )
pFiltering.wait()

# Create the reconstruction if not present
if not os.path.exists(reconstruction_dir):
    os.mkdir(reconstruction_dir)

print ("==> [OpenMVG] Do Sequential/Incremental reconstruction")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfM"), "--sfm_engine", "INCREMENTAL", "--input_file", matches_dir+"/sfm_data.json", "--match_dir", matches_dir, "--output_dir", reconstruction_dir] )
pRecons.wait()

print ("==> [OpenMVG] Colorize Structure")
pColorize = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
pColorize.wait()

print ("==> [OpenMVG] Export to OpenMVS")
pExport = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2openMVS"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", reconstruction_dir+"/scene.mvs", "-d", reconstruction_dir+"/scene_undistorted_images"] )
pExport.wait()

print ("==> [OpenMVS] Dense point-cloud reconstruction")
pDensify = subprocess.Popen( [os.path.join(OPENMVS_SFM_BIN, "DensifyPointCloud"), "-w", reconstruction_dir, "-v", "3", "-i", reconstruction_dir+"/scene.mvs", "-o", reconstruction_dir+"/scene_dense.mvs"] )
pDensify.wait()

print ("==> [OpenMVS] Mesh reconstruction")
pMeshify = subprocess.Popen( [os.path.join(OPENMVS_SFM_BIN, "ReconstructMesh"), "-w", reconstruction_dir, "-v", "3", "-i", reconstruction_dir+"/scene_dense.mvs", "-o", reconstruction_dir+"/scene.ply"] )
pMeshify.wait()
