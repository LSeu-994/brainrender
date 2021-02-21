from brainrender import Scene
from brainrender.atlas_specific import GeneExpressionAPI
from brainrender.actor import Actor
import pytest
import sys

gene = "Cacna2d1"


@pytest.fixture
def geapi():
    geapi = GeneExpressionAPI()

    return geapi


@pytest.mark.skipif(
    sys.version_info > (3, 7), reason="requires python3.7 or lower"
)
def test_gebe_expression_api(geapi):

    s = Scene(title="BR")

    geapi.get_gene_id_by_name(gene)
    expids = geapi.get_gene_experiments(gene)

    data = geapi.get_gene_data(gene, expids[0], use_cache=True)

    # make actor
    gene_actor = geapi.griddata_to_volume(
        data, min_quantile=90, cmap="inferno"
    )
    assert isinstance(gene_actor, Actor)
    assert gene_actor.name == gene
    assert gene_actor.br_class == "Gene Data"

    s.add(gene_actor)


@pytest.mark.skipif(
    sys.version_info > (3, 7), reason="requires python3.7 or lower"
)
@pytest.mark.slow
def test_download_no_cache(geapi):
    geapi.get_gene_id_by_name(gene)
    expids = geapi.get_gene_experiments(gene)
    geapi.get_gene_data(gene, expids[0], use_cache=False)
