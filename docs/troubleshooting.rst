Troubleshooting
================

I will put Frequently asked question here and provide solutions. Please refer to the Github Issue page for all the issues.

1. Singularity Error
----------------------

First, the command I included in the tutorial should work most of time (if not 100%) using singularity/3.1. 

Second, if you happen to run into any issues, it usually has something to do with your HPC permissions. Some scenario and solutions as below:

If you encounter problem like below using higher singularity version::

    module load singularity/3.9.8
    singularity run -B $(pwd):/mnt --writable altanalyze/ identify bam 4
    WARNING: By using --writable, Singularity can't create /gpfs destination automatically without overlay or underlay
    FATAL: container creation failed: mount /gpfs/share/apps/singularity/3.9.8/var/singularity/mnt/session/gpfs->/gpfs error: while mounting /gpfs/share/apps/singularity/3.9.8/var/singularity/mnt/session/gpfs: destination /gpfs doesn't exist in container

Following this `thread <https://git.ligo.org/lscsoft/gstlal/-/issues/94>`_, you just need to first manually create a ``gpfs`` folder in the sandbox, then it should work. Please
modify that as needed, in my case it is ``gpfs`` but in your system, the error message might differ::

    mkdir altanalyze/gpfs

Another way to consider is to be more explict and using ``singularity exec``, sometimes this may solve the issue::

    singularity exec -W /usr/src/app -B $(pwd):/mnt --writable altanalyze/ /bin/bash -c "cd /usr/src/app && /usr/src/app/AltAnalyze.sh identity bam 4"

If you still run into problem, contact me and let's figure something out!

2. AltAnalyze warnings and errors
--------------------------------------

You can ignore messages shown below, it won't affect your program.

Something like that::

    library lxml not supported. WikiPathways and LineageProfiler visualization will not work. Please install with pip install lxml.
    Traceback (most recent call last):
    File "/usr/src/app/altanalyze/import_scripts/BAMtoJunctionBED.py", line 217, in parseJunctionEntries
        try: splicesite_db,chromosomes_found, gene_coord_db = retreiveAllKnownSpliceSites()
    File "/usr/src/app/altanalyze/import_scripts/BAMtoJunctionBED.py", line 133, in retreiveAllKnownSpliceSites
        for file in os.listdir(parent_dir):
    OSError: [Errno 2] No such file or directory: 'S'

Or::

    AltAnalyze depedency not met for: patsy

    ...Combat batch effects correction requires pandas and patsy

    AltAnalyze depedency not met for: wx

    ...The AltAnalyze Results Viewer requires wx

    AltAnalyze depedency not met for: fastcluster

    ...Faster hierarchical cluster not supported without fastcluster

    AltAnalyze depedency not met for: lxml

    ...Wikipathways visualization not supported without lxml

    

    WARNING!!!! Some dependencies are not currently met.

    This may impact AltAnalyze's performance


.. _reference_to_hla_typing:

3. How to do HLA genotyping?
--------------------------------

Here we provide one solution using Optitype, which has been on top-performing HLA genotyping tool for a long time. The author provide a docker container, I usually 
run like that::


    # build image using singularity, you may have to use singularity/3.1 if you run into any errors
    singularity build my_software.sif docker://fred2/optitype

    # run it, assuming the fastq file is in the current directory
    sample='TCGA-XX-XXXX-1'
    singularity run -B $(pwd):/mnt my_software.sif -i ${sample}.1.fastq ${sample}.2.fastq --rna -v -o /mnt

But what if you only have bam files, no worreis, just convert them to fastq first::

    # this step is required, have to sort by chromsome name
    samtools sort -n $BAM -o $SAMPLE.qsort.bam
    # then just convert, more please look at bedtools bamtofastq docs, super easy
    bedtools bamtofastq -i $SAMPLE.qsort.bam -fq $SAMPLE.1.fastq -fq2 $SAMPLE.2.fastq


After that, the result as a tsv file will be generated (30min probably), you can write your own parsing script for post-processing. In addition, this process can be parallelized,
I often write it into a shell function, and use linux parallel tool to run like 20 jobs at the same time to speed thing up.


4. AltAnalyze steps take too long
-------------------------------------

So AltAnalyze first convert your bam file to bed file one by one, and based on the cores you specified, it can parallelize stuffs but still you can only have like 50 cores 
per node in your HPC, and maybe there are memory issues for docker, if you have thousands of samples, you can do it in a more flexible way::

    #!/bin/bash


    function run() {
        mkdir ./tmp/$1
        cp ./bam/$1.bam ./tmp/$1
        cd ./tmp/$1
        docker run -v $PWD:/mnt altanalyze bam_to_bed $1.bam
        cd ../..
    }

    # pre
    mkdir tmp
    mkdir bed

    cd ./bam
    for file in *.bam; do echo $(basename -s .bam $file); done > ../samples.txt 
    cd ..

    # run
    export -f run
    export TMPDIR=/Users/ligk2e/Desktop
    cat samples.txt | xargs -n 1 -P 4 -I {} bash -c "run {}"

    # post
    while read line; do 
        mv ./tmp/${line}/${line}.bam.bai ./bam
        mv ./tmp/${line}/*.bed ./bed
        done < samples.txt
    rm -r ./tmp

The idea is you still in your foler where /bam folder sits, you define a function where it only run bam_to_bed step, this can maximize the efficiency for generating bed fildes. Then once all bed
files are generated, you can run bed_to_junction in one go::

    docker run -v $PWD:/mnt altanalyze bed_to_junction bed

5. Recommended alignment workflow
-------------------------------------

While We accept any sort of bam files, we indeed notice slight differences in the identified junctions when different human references and aligner version were used.
Since we are using TCGA paratumor as one of the control dataset, in our internal workflow, we strictly followed the GDC protocol for how to align the RNA-seq data
for the purpose of splicing detection. The full commands, parameters and explanation can be found in `SNAF align splice <https://github.com/frankligy/SNAF/tree/main/images/alignment_splice>`_.
Particularly, a few things need to keep in mind:

#. Using the ``GDC fasta reference`` and the ``Gencode v36 GTF`` file to maximize reproduction of the TCGA results
#. Make sure to do it in the ``two pass``, such that you need to additionally build an intermediate index for each sample incorporating the novel junctions detected from first pass
#. Using ``STAR 2.4.0`` as this is the one used in TCGA pipeline
#. Other parameters, just make sure to use the TCGA parameters


6. Running MaxQuant in Linux
-------------------------------------

You can certainly check their own website and user group, but I provide the way that usually work for me::

    # make sure you install the right version (these two version guarantee to work)
    module load mono/5.20.1
    module load dotnet/3.1.425

    # run maxquant using the downloaded .exe and the modifed mqpar.xml file
    mono /path/to/MaxQuant_2.0.3.1/bin/MaxQuantCmd.exe /path/to/mqpar.xml





