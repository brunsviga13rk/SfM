
build:
	# I discourage from building this image by yourself due to its size
	# and excruciating compilation time.
	docker build --tag ghcr.io/brunsviga13rk/sfm:git .

run:
	mkdir output || true
	# Start SfM container, mount the dataset and the output directory.
	# Then start the full automatic reconstruction pipeline.
	docker run -it \
	    -v "./jpg:/home/sfmop/dataset" \
		-v "./output:/home/sfmop/sparse_reconstruction" \
	    ghcr.io/brunsviga13rk/sfm:git

# Convert PNG to JPEG files.
# Used to convert the compression lossless PNG based dataset since
# OpenMVG does not seem to be able to read camera sensor data from PNG EXIF.
# Source: https://superuser.com/a/542671
convert:
	mkdir jpg
	cd png
	for i in *.png ; do magick convert "$i" "../jpg/${i%.*}.jpg" ; done

# Download the JPG dataset and extract into folder `jpg`.
# NOTE: link may change in future.
pull:
	curl -SL https://cloud.montehaselino.de/s/WFXnTMigBmaLWzg/download/dataset-jpg.tar.gz > dataset.tar.gz
	mkdir jpg || true
	tar xvf dataset.tar.gz --directory=jpg
