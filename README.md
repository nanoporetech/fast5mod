
![ONT_logo](/ONT_logo.png)
-----------------------------

We have a new bioinformatic resource that largely replaces the functionality of this project! See our new repository here: [https://github.com/epi2me-labs/modbam2bed](https://github.com/epi2me-labs/modbam2bed)


This repository is now unsupported and we do not recommend its use. Please contact Oxford Nanopore: support@nanoporetech.com for help with your application if it is not possible to upgrade to our new resources, or we are missing key features.

******************

Fast5Mod
========

[![](https://img.shields.io/pypi/v/fast5mod.svg)](https://pypi.org/project/fast5mod/)

Fast5mod is a set of two programs for converting Guppy's modified base Fast5 output into:

  * An aligned or unaligned BAM formatted file, and
  * Aggregate modified base calls.

The functionality was originally part of Medaka, but has be removed to this distinct project.

© 2020 Oxford Nanopore Technologies Ltd.

Installation
------------

fast5mod is available on PyPI and can be installed using pip:

    pip install fast5mod

We recommend using fast5mod within a virtual environment, viz.:

    virtualenv fast5mod --python=python3 --prompt "(fast5mod) "
    . fast5mod/bin/activate
    pip install fast5mod

Usage
-----

The basic workflow for aggregating Guppy basecalling results
for Dcm, Dam, and CpG methylation is shown below.

Aggregating the information from Guppy outputs is a two stage process, first
the basecalling results are extracted `.fast5` files and placed in a `.bam`
file:

    FAST5PATH=guppy/workspace
    REFERENCE=grch38.fasta
    OUTBAM=meth.bam
    fast5mod guppy2sam ${FAST5PATH} ${REFERENCE} \
        --workers 74 --recursive \
        | samtools sort -@ 8 | samtools view -b -@ 8 > ${OUTBAM}
    samtools sort ${OUTBAM}

This program will extract both the basecall sequence and methylation scores,
align the basecall to the reference, and store results in a standard format.
In this preliminary workflow the methylation scores are stored in two SAM
tags, 'MC' and 'MA', one each for 5mC and 6mA respectively. The tags are
8bit integer array-values, one value per basecall position. This is a
different form to that proposed in the current
[hts-specs proposition](https://github.com/samtools/hts-specs/pull/418/files),
but allows for more trivial parsing.

The second step is to aggregate the reference-aligned information to produce
a simple tabular summary of read methylation counts:

    BAM=meth.bam
    REFERENCE=grch38.fasta
    REGION=chr20:500000-1000000
    OUTPUT=meth.tsv
    fast5mod call --meth cpg ${BAM} ${REFERENCE} ${REGION} ${OUTPUT}

Here the option `--meth cpg` indicates that loci containing the sequence
motif `CG` should be examined for 5mC presence. Other choices are
`dcm` for which the motifs `CCAGG` and `CCTGG` are examined for 5mC and `dam`
(`GATC`) for 6mA.

The output file is a simple tab-delimited text file with columns:
'ref.name', 'position', 'motif', 'fwd.meth.count', 'rev.meth.count',
'fwd.canon.count', and 'rev.canon.count'. Here fwd./ref. indicate counts on the
two DNA strands and meth./canon. indicate counts for methylated and
canonical bases. Note that the position field records the position of the
first base in the motif recorded.


Help
----

**Licence and Copyright**

© 2020 Oxford Nanopore Technologies Ltd.

`fast5mod` is distributed under the terms of the Mozilla Public License 2.0.

**Research Release**

Research releases are provided as technology demonstrators to provide early
access to features or stimulate Community development of tools. Support for
this software will be minimal and is only provided directly by the developers.
Feature requests, improvements, and discussions are welcome and can be
implemented by forking and pull requests. However much as we would
like to rectify every issue and piece of feedback users may have, the
developers may have limited resource for support of this software. Research
releases may be unstable and subject to rapid iteration by Oxford Nanopore
Technologies.
