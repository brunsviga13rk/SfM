#!/usr/bin/python

import os
import subprocess
import sys
import logging

def try_popen(args: list[str]):
    """
    Try to run a process by using `subprocess.Popen`.
    In case the command returns a non-exit return code this function
    will terminate the script.
    """
    global logger

    pIntrisics = subprocess.Popen(args)
    if pIntrisics.wait():
        logger.error(f"Subprocess failed with: {pIntrisics.returncode}")
        exit(1)

if __name__ == '__main__':
    # initialize logger
    logging.basicConfig(
        format='%(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    # add module global logger
    global logger
    logger = logging.getLogger(__name__)

    if len(sys.argv) < 3:
        print ("Usage %s image_dir output_dir" % sys.argv[0])
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    matches_dir = os.path.join(output_dir, "matches")
    reconstruction_dir = os.path.join(output_dir, "reconstruction_sequential")

    print ("Using input dir  : ", input_dir)
    print ("      output_dir : ", output_dir)

    # Create the ouput/matches folder if not present
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if not os.path.exists(matches_dir):
        os.mkdir(matches_dir)

    logger.info("[OpenMVG] Intrinsics analysis")
    try_popen([
        "openMVG_main_SfMInit_ImageListing",
        "-i", input_dir,
        "-o", matches_dir,
        "-d", "sensor_width_camera_database.txt"])

    logger.info("[OpenMVG] Compute features")
    try_popen([
        "openMVG_main_ComputeFeatures",
        "-i", matches_dir + "/sfm_data.json",
        "-o", matches_dir,
        "-m", "SIFT"])

    logger.info("[OpenMVG] Compute matching pairs")
    try_popen([
        "openMVG_main_PairGenerator",
        "-i", matches_dir + "/sfm_data.json",
        "-o" , matches_dir + "/pairs.bin"])

    logger.info("[OpenMVG] Compute matches")
    try_popen([
        "openMVG_main_ComputeMatches",
        "-i", matches_dir + "/sfm_data.json",
        "-p", matches_dir + "/pairs.bin",
        "-o", matches_dir + "/matches.putative.bin"])

    logger.info("[OpenMVG] Filter matches" )
    try_popen([
        "openMVG_main_GeometricFilter",
        "-i", matches_dir + "/sfm_data.json",
        "-m", matches_dir+"/matches.putative.bin",
        "-g", "f",
        "-o" , matches_dir+"/matches.f.bin"])

    # Create the reconstruction if not present
    if not os.path.exists(reconstruction_dir):
        os.mkdir(reconstruction_dir)

    logger.info("[OpenMVG] Do Sequential/Incremental reconstruction")
    try_popen([
        "openMVG_main_SfM",
        "--sfm_engine", "INCREMENTAL",
        "--input_file", matches_dir + "/sfm_data.json",
        "--match_dir", matches_dir,
        "--output_dir", reconstruction_dir])

    logger.info("[OpenMVG] Colorize Structure")
    try_popen([
        "openMVG_main_ComputeSfM_DataColor",
        "-i", reconstruction_dir + "/sfm_data.bin",
        "-o", os.path.join(reconstruction_dir, "colorized.ply")])

    logger.info("[OpenMVG] Export to OpenMVS")
    try_popen([
        "openMVG_main_openMVG2openMVS",
        "-i", reconstruction_dir + "/sfm_data.bin",
        "-o", reconstruction_dir + "/scene.mvs",
        "-d", reconstruction_dir + "/scene_undistorted_images"])

    logger.info("[OpenMVS] Dense point-cloud reconstruction")
    try_popen([
        "DensifyPointCloud",
        "-w", reconstruction_dir,
        "-v", "3",
        "-i", reconstruction_dir + "/scene.mvs",
        "-o", reconstruction_dir + "/scene_dense.mvs"])

    logger.info("[OpenMVS] Mesh reconstruction")
    try_popen([
        "ReconstructMesh",
        "-w", reconstruction_dir,
        "-v", "3",
        "-i", reconstruction_dir+"/scene_dense.mvs",
        "-o", reconstruction_dir+"/scene.ply"])
