#! /usr/bin/env python
from __future__ import print_function

import os
import click
import shutil

import scripts.files
import scripts.orthologues
import scripts.trees_msa
import scripts.util
import scripts.parallel_task_manager
import scripts.stride
import orthofinder


class OrthoFinderContext:
    def __init__(self, wd):
        self.wd = wd
        self.options = orthofinder.Options()
        self.options.qStartFromGroups = True
        scripts.files.InitialiseFileHandler(self.options, continuationDir=wd)
        self.speciesInfoObj, self.speciesToUse_names = \
            orthofinder.ProcessPreviousFiles(wd, False)
        self.ogSet = scripts.orthologues.OrthoGroupsSet(
            scripts.files.FileHandler.GetWorkingDirectory1_Read(),
            self.speciesInfoObj.speciesToUse, self.speciesInfoObj.nSpAll, True,
            idExtractor=scripts.util.FirstWordExtractor)
        self.id_dict = dict(self.ogSet.Spec_SeqDict().items() +
                            self.ogSet.SpeciesDict().items())
        self.tree_gen = scripts.trees_msa.TreesForOrthogroups(None, None, None)

    def __del__(self):
        try:
            results_dir = scripts.files.FileHandler.GetResultsDirectory1()
            if os.path.exists(results_dir):
                shutil.rmtree(results_dir)
        except:
            pass


@click.group()
@click.argument('DIR')
@click.pass_context
def cli(ctx, dir):
    ctx.obj = OrthoFinderContext(dir)


@cli.command(help='Concatenate a multiple alignment')
@click.argument('OG_FILE')
@click.argument('OUTPUT_NAME')
@click.argument('F_SING_COPY', type=float)
@click.pass_obj
def concat(of_ctx, og_file, output_name, f_sing_copy):
    ogs = [int(x.strip()) for x in open(og_file).readlines()]
    scripts.trees_msa.CreateConcatenatedAlignment(
        ogs,
        of_ctx.ogSet.OGs(),
        lambda og: os.path.join(of_ctx.wd, "WorkingDirectory", "Alignments_ids",
                                "OG%07d.fa" % og),
        output_name,
        f_sing_copy
    )


@cli.command(help='rename taxa on a multiple alignment')
@click.argument('IN_ALIGN')
@click.argument('OUT_ALIGN')
@click.pass_obj
def rename_alignment(of_ctx, in_align, out_align):
    of_ctx.tree_gen.RenameAlignmentTaxa([in_align], [out_align], of_ctx.id_dict)


@cli.command(help='rename taxa on a tree')
@click.argument('IN_TREE')
@click.argument('OUT_TREE')
@click.pass_obj
def rename_tree(of_ctx, in_tree, out_tree):
    support = scripts.util.HaveSupportValues(in_tree)
    scripts.util.RenameTreeTaxa(in_tree, out_tree, of_ctx.id_dict, support)


@cli.command(help='rename taxa on a tree')
@click.argument('UNROOTED_SPECIES_TREE')
@click.argument('TREES_DIR')
@click.argument('NUM_THREADS', type=int)
@click.argument('OUTPUT_FILE')
@click.pass_obj
def stride(of_ctx, unrooted_species_tree, trees_dir, num_threads, output_file):
    roots, clusters_counter, rootedSpeciesTreeFN, nSupport, _, _, all_stride_dup_genes = scripts.stride.GetRoot(
            unrooted_species_tree, trees_dir, scripts.stride.GeneToSpecies_dash,
            num_threads, qWriteRootedTree=True)
    nAll = sum(clusters_counter.values())
    nFP_mp = nAll - nSupport
    n_non_trivial = sum([v for k, v in clusters_counter.items() if len(k) > 1])
    if len(roots) > 1:
        print("Observed %d well-supported, non-terminal duplications. %d support the best roots and %d contradict them." % (n_non_trivial, n_non_trivial-nFP_mp, nFP_mp))
        print("Best outgroups for species tree:")  
    else:
        print("Observed %d well-supported, non-terminal duplications. %d support the best root and %d contradict it." % (n_non_trivial, n_non_trivial-nFP_mp, nFP_mp))
        print("Best outgroup for species tree:")  
    spDict = of_ctx.ogSet.SpeciesDict()
    for r in roots: print("  " + (", ".join([spDict[s] for s in r]))  )
    shutil.copy(rootedSpeciesTreeFN[0], output_file)


if __name__ == '__main__':
    try:
        cli()
    except:
        raise
    finally:
        ptm = scripts.parallel_task_manager.ParallelTaskManager_singleton()
        ptm.Stop()
