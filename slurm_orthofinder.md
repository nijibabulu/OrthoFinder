First run the blast (as in the standard version):

```
module load diamond
./orthofinder/orthofinder.py -op -f testRun
```

Then infer orthogroups and output the tree commands (**the `stdout` output of this command is needed to know which commands to run on the cluster**):

```
module load iqtree mafft
./orthofinder/orthofinder.py -oc -ot -M msa -T iqtree -b testRun/OrthoFinder/Results_Feb11/WorkingDirectory/
```

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

Stride is very fast, can be run on the command line:
```
bash /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Apr02_37/WorkingDirectory/99stride
```

Finally reoncile the trees and output the orthologs:

```
./orthofinder/orthofinder.py -M msa -T iqtree -ft /scratch/rpz/OrthoFinder/testRun/OrthoFinder/Results_Feb11/WorkingDirectory/OrthoFinder/Results_Feb11
```
