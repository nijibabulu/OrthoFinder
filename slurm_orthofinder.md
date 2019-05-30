First run the blast (as in the standard version):

```
module load diamond
./orthofinder/orthofinder.py -op -f testRun
```

Then infer orthogroups and output the tree commands (**the `stdout` output of this command is needed to know which commands to run on the cluster**):

```
module load iqtree mafft
./orthofinder/orthofinder.py -oc -ot -M msa -A mafft_trim -T iqtree -b testRun/OrthoFinder/Results_Feb11/WorkingDirectory/
```

Note that I pick the `mafft_trim` version of the aligner. This is not a special mode of `mafft`. Instead it's just the `mafft` command (with `--localpair`), followed by a command to trim the alignments using `trimal`. For now the settings are hardcoded. `trimal` offers several modes of operation, however for very large sets of genes, such as the ones produced by orthofinder (`OG0000000`, for example) makes the process of trimming with a divergence aware method very long. So we simply use the `-gappyout` mode, which takes very little time. Alignment trimming also makes it possible to run very large orthogroups, which are often spread into extremely long, gappy alignments. We will lose information about the relationship of some of the genes to the orthogroup in tree and, in fact, some genes in large analyses will be completely lost and turned into gap-only sequences. These sequences are probably poorly resolved anyway and will not fall well into the tree.

(Manually edited the species tree job to get 8 cores)
Now enqueue the jobs:
```
nq -m 8 -O log_testrun /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Feb11/WorkingDirectory/00species_trees_jobs
nq -d 4865352  -m 8 -O log_testrun /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Feb11/WorkingDirectory/01concat_align_job
nq -d 4865353  -m 64 -c 8 -F array-8core -O log_testrun /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Feb11/WorkingDirectory/02species_tree
nq -m 8 -O log_testrun /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Feb11/WorkingDirectory/03og_trees
nq -g 10 -d 4865353,4865360 -m 8 -O log_testrun /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Feb11/WorkingDirectory/04rename-taxa
nq -g 10 -d 4865353,4865360 -m 8 -O log_testrun /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Feb11/WorkingDirectory/05rename-taxa
```

Note that in some commands I use `-d JOB_ID` in the `nq` command. This adds a "dependency" to the job (adds `#SBATCH --dependency JOB_ID` in the slurm batch file). It makes sure that the previous job is complete before starting the new job. You need to use your job id here, which will be given after submitting. Note that the rename-taxa jobs are dependent on both the `03og_trees` and `00species_trees_jobs` jobs.

A bit about these jobs:
- `00species_trees_jobs` - these are the msa alignments and tree inference jobs for the single copy genes which would be used for species tree inference. 
- `01concat_align_job` - this simply concatenates the alignments from the previous job for inference of the species tree. 
- `02species_tree` - this will determine the species tree. This is a single task and is particularly long. You may consider customizing this.
- `03og_trees` - the msa alignments and trees for the remaining orthogroups. Note there's not really any difference between these jobs and `00species_trees_jobs`. There is no dependency between the two. The tasks are just separated in the orthofinder code. In the end both `00species_trees_jobs` and `03og_trees` will contribute to your final set of gene trees.
- `04rename-taxa` and `05rename-taxa` - these jobs simply rename the taxa (genes/species) from the internal naming scheme (numbers) to the original input scheme you gave it (presumably species and gene identifiers).

It is not necessary to make a species tree if you will supply your own species tree. However, it might be interesting to get feedback on how well your sequences and the method is resolving the taxa.

Stride is very fast, can be run on the command line:
```
bash /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Apr02_37/WorkingDirectory/99stride
```

Finally reoncile the trees and output the orthologs:

```
./orthofinder/orthofinder.py -M msa -T iqtree -ft /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Feb11
```
