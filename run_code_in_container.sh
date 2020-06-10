# docker build -t genepattern/conos:1.2 .

docker run --rm \
-v $PWD/data:/temp/data \
-v $PWD/job_1234:/job_1234 \
-w /job_1234 \
-it genepattern/docker-download-from-gdc:1.5 \
python /usr/local/bin/TCGAImporter/download_from_manifest.py -m /temp/data/minifest.txt -g True -c True -t True -o demo
