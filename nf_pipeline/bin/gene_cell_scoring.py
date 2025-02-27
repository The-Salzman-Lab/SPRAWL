#!/usr/local/bin/python
#Above is python path in the docker container with sprawl installed
import sprawl
from sprawl import simulate

import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hdf5_path')
    parser.add_argument('--metric')
    parser.add_argument('--experiment')
    parser.add_argument('--sample')
    parser.add_argument('--output_name')
    parser.add_argument('--min_genes_per_cell', type=int)
    parser.add_argument('--min_tot_counts_per_cell', type=int)
    parser.add_argument('--processes', type=int, default=1)
    parser.add_argument('--permute_gene_labels', default='no')
    parser.add_argument('--shrink_factor', type=float, default=1.0)
    parser.add_argument('--min_gene_spots', type=int, default=1)

    args = parser.parse_args()

    sample = sprawl.HDF5(args.hdf5_path)
    cells = sample.iter_cells()

    #Permute cells before scoring depending on args
    if args.permute_gene_labels != 'no':
        sys.stdout.write('Preparing to permute gene labels in all cells\n')
        sys.stdout.flush()
 
        cells = (simulate.null_permute_gene_labels(c, within_z=False) for c in cells)

    #Shrink cells
    if args.shrink_factor != 1:
        sys.stdout.write(f'Preparing to shrink cells by a factor of {args.shrink_factor}\n')
        sys.stdout.flush()
 
        cells = (c.shrink_boundaries(scale_factor=args.shrink_factor) for c in cells)

    #Filter out spots from genes with too few counts
    if args.min_gene_spots > 1:
        sys.stdout.write(f'Preparing to filter genes from cells with fewer than {args.min_gene_spots}\n')
        sys.stdout.flush()
 
        cells = (c.filter_genes_by_count(args.min_gene_spots) for c in cells if c.gene_counts) #strange extra filtering because some "cells" are empty w/out gene counts

    #Filter out cells with fewer than min total spots and min total genes
    sys.stdout.write(f'Preparing to remove cells with fewer than {args.min_tot_counts_per_cell} spots and {args.min_genes_per_cell} unique genes\n')
    sys.stdout.flush()

    cells = (
        c for c in cells
        if (c.n >= args.min_tot_counts_per_cell) and (len(c.genes) >= args.min_genes_per_cell)
    )

    #score and write out table
    score_df = sprawl.iter_scores(cells, metric=args.metric, processes=args.processes)
    sys.stdout.write(f'The scoring dataframe has {len(score_df)} rows\n')
    sys.stdout.flush()

    score_df['experiment'] = args.experiment
    score_df['sample'] = args.sample
    score_df.to_csv(args.output_name, index=False)

if __name__ == '__main__':
    main()

