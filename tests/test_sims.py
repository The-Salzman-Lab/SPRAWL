import pytest
import collections
import pandas as pd
import numpy as np
import functools

from sprawl import simulate, scoring

def perm_helper(orig_c,perm_c):
    """
    Common checks to different permutation methods
    """
    #ensure they have the same zslices
    assert list(orig_c.zslices) == list(perm_c.zslices)

    #ensure at least some reordering occured (set seeds to avoid perm resulting in identical orders)
    orig_c_genes = [g for z in orig_c.zslices for g in orig_c.spot_genes[z]]
    perm_c_genes = [g for z in orig_c.zslices for g in perm_c.spot_genes[z]]
    assert orig_c_genes != perm_c_genes

    #ensure the same total number of genes before and after
    orig_gcs = collections.Counter(orig_c_genes)
    perm_gcs = collections.Counter(perm_c_genes)
    assert orig_gcs == perm_gcs


@pytest.mark.parametrize('dataset',['m1s4','m2s4'])
@pytest.mark.parametrize('seed',[1,77])
def test_null_perm_within_z(dataset,seed,request):
    np.random.seed(seed)

    data = request.getfixturevalue(dataset)
    orig_cells = data.cells()
    perm_cells = data.cells()

    for orig_c,perm_c in zip(orig_cells,perm_cells):
        simulate.null_permute_gene_labels(perm_c, within_z=True)
        perm_helper(orig_c,perm_c)

        #gene counts within each slice need to match
        for z in orig_c.zslices:
            assert collections.Counter(orig_c.spot_genes[z]) == collections.Counter(perm_c.spot_genes[z])



@pytest.mark.parametrize('dataset',['m1s4','m2s4'])
@pytest.mark.parametrize('seed',[1,77])
def test_null_perm_across_z(dataset,seed,request):
    np.random.seed(seed)

    data = request.getfixturevalue(dataset)
    orig_cells = data.cells()
    perm_cells = data.cells()

    for orig_c,perm_c in zip(orig_cells,perm_cells):
        simulate.null_permute_gene_labels(perm_c, within_z=False)
        perm_helper(orig_c,perm_c)

@pytest.mark.skip(reason='Dont know how to test gene celltype null sim quickly')
@pytest.mark.parametrize('dataset',['m1s4','m2s4'])
@pytest.mark.parametrize('metric',['peripheral','radial'])
@pytest.mark.parametrize('seed',[25])
def test_gene_celltype_sim_null(dataset,metric,seed,request):
    np.random.seed(seed)
    sample = request.getfixturevalue(dataset)
    cells = sample.iter_cells()

    perm_df_iter = simulate.gene_celltype_sim_null(cells, metric, within_z=True, n_its=5)
    perm_df = pd.concat(perm_df_iter)
    perm_df.shape #forcing perm_df_iter to run

    #Need to figure out how to test the results, xfail for now
    assert False


def test_single_cell_sim_null(m1s4):
    cell = next(m1s4.iter_cells())
    result = simulate.gene_cell_sim_null([cell], metric='peripheral', within_z=True, n_its=10, alpha=0.05)

    assert result['cell_id'].unique() == [cell.cell_id]


def test_sim_null(m1s4):
    cells = m1s4.cells()
    result = simulate.gene_cell_sim_null(cells, metric='peripheral', within_z=False, n_its=10, alpha=0.05)

    assert set(result['cell_id'].values) == set(m1s4.cell_ids)


