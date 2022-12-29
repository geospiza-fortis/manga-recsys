"""Generate recommendations from from manga to manga."""
import json
import warnings
from multiprocessing import Pool
from pathlib import Path

import click
import matplotlib.pyplot as plt
import tqdm
import umap
from pyspark.sql import functions as F
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from manga_recsys.commands.utils import write_df, write_df_per_uid
from manga_recsys.models.manga import (
    explode_recommendations,
    generate_manga_tags_network,
    generate_manga_tags_tfidf_lsi,
    generate_manga_tags_word2vec,
    generate_recommendations,
    get_manga_tags,
    map_names_to_recommendations,
    plot_recommendation_dims,
    recs_with_secondary_tag,
)
from manga_recsys.spark import get_spark

# ignore warnings with the following text:
# FutureWarning: iteritems is deprecated and will be removed in a future version
warnings.filterwarnings("ignore", message=".*iteritems.*")


@click.group()
def manga():
    """Generate manga recommendations."""
    pass


def _write_recs(recs, output, cores=8):
    output = Path(output)
    gz_output = Path("/".join([output.parts[0], "gz", *output.parts[1:]]))
    write_df(recs, output / "recommendations")
    print("Writing gzipped files...")
    write_df_per_uid(
        recs, gz_output / "recommendations", uid_col="id", parallelism=cores
    )


def _generate_rec(manga_info, method: str, cores=8, num_recs=20, **kwargs):
    func = {
        "w2v": generate_manga_tags_word2vec,
        "lsi": generate_manga_tags_tfidf_lsi,
        "network": generate_manga_tags_network,
    }

    manga_tags = func[method](manga_info, vector_col="emb", workers=cores, **kwargs)
    rec_df = generate_recommendations(
        manga_tags, "id", "emb", k=num_recs, metric="cosine", n_jobs=cores
    )
    return rec_df


@manga.command()
@click.argument("input-manga-info", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--num-recs", type=int, default=20)
@click.option("--cores", type=int, default=8)
@click.option("--memory", default="6g")
def tags_word2vec(input_manga_info, output, num_recs, cores, memory):
    """Generate word2vec vectors from tags to make recommendations."""
    spark = get_spark(cores=cores, memory=memory)
    manga_info = spark.read.parquet(input_manga_info).cache()

    rec_df = _generate_rec(manga_info, "w2v", num_recs=num_recs)

    recs = explode_recommendations(spark, rec_df)
    recs = map_names_to_recommendations(manga_info, recs).cache()
    recs.printSchema()
    recs.show()

    write_df(spark.createDataFrame(rec_df), output / "embedding")
    _write_recs(recs, output, cores)


@manga.command()
@click.argument("input-manga-info", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--num-recs", type=int, default=20)
@click.option("--cores", type=int, default=8)
@click.option("--memory", default="6g")
def tags_lsi(input_manga_info, output, num_recs, cores, memory):
    spark = get_spark(cores=cores, memory=memory)
    manga_info = spark.read.parquet(input_manga_info).cache()

    rec_df = _generate_rec(manga_info, "lsi", num_recs=num_recs)

    recs = explode_recommendations(spark, rec_df)
    recs = map_names_to_recommendations(manga_info, recs).cache()
    recs.printSchema()
    recs.show()

    write_df(spark.createDataFrame(rec_df), output / "embedding", json=False)
    _write_recs(recs, output, cores)


@manga.command()
@click.argument("input-manga-info", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--deconvolve/--no-deconvolve", default=False)
@click.option("--num-recs", type=int, default=20)
@click.option("--cores", type=int, default=8)
@click.option("--memory", default="6g")
def tags_network(input_manga_info, output, deconvolve, num_recs, cores, memory):
    spark = get_spark(cores=cores, memory=memory)
    manga_info = spark.read.parquet(input_manga_info).cache()

    rec_df = _generate_rec(
        manga_info, "network", num_recs=num_recs, deconvolve=deconvolve
    )

    recs = explode_recommendations(spark, rec_df)
    recs = map_names_to_recommendations(manga_info, recs).cache()
    recs.printSchema()
    recs.show()

    write_df(spark.createDataFrame(rec_df), output / "embedding", json=False)
    _write_recs(recs, output, cores)


def _write_plot_method(output_path, reducer, recs, method, primary_tag, n_dims=2):
    method_name = {
        "w2v": "word2vec",
        "lsi": "LSI",
        "network": "network",
    }[method]
    class_name = reducer.__class__.__name__
    plot_recommendation_dims(
        recs,
        method,
        reducer,
        title=(
            f"{primary_tag} {method_name} embedding ({class_name}) (n={recs.shape[0]})"
        ),
        n_dims=n_dims,
    )
    plt.savefig(output_path / f"{class_name}.png")
    plt.close()


@manga.command()
@click.argument("input-manga-info", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--num-recs", type=int, default=20)
@click.option("--n-dims", type=int, default=2)
@click.option("--cores", type=int, default=6)
@click.option("--memory", default="6g")
def plot_models(input_manga_info, output, num_recs, n_dims, cores, memory):
    spark = get_spark(cores=cores, memory=memory)
    manga_info = spark.read.parquet(input_manga_info).cache()

    # find all tags for theme and genre
    theme_genres = (
        manga_info.select("id", F.explode("tags").alias("tag"))
        .select("tag.group", "tag.name")
        .distinct()
    ).toPandas()

    # first generate recommendations
    for method in ["w2v", "lsi"]:
        rec_df = _generate_rec(manga_info, method, cores=cores, num_recs=num_recs)
        for group in ["theme", "genre"]:
            tags = theme_genres[theme_genres["group"] == group].name.unique().tolist()
            manga_tags = get_manga_tags(manga_info, group).cache()
            for primary_tag in tqdm.tqdm(tags):
                output_path = Path(output) / method / group / primary_tag
                output_path.mkdir(parents=True, exist_ok=True)

                recs = recs_with_secondary_tag(
                    spark, rec_df, manga_tags, primary_tag, verbose=False
                )
                reducers = [
                    umap.UMAP(n_components=n_dims, metric="cosine"),
                    TSNE(n_components=n_dims),
                    PCA(n_components=n_dims),
                ]
                with Pool(3) as p:
                    p.starmap(
                        _write_plot_method,
                        [
                            (output_path, reducer, recs, method, primary_tag, n_dims)
                            for reducer in reducers
                        ],
                    )


@manga.command()
@click.argument("root_path", type=click.Path(exists=True))
def generate_plot_manifest(root_path):
    """Generate a json manifest that contains a list of the paths to all the plots.

    This includes the path convention of "<model>/<group>/<tag>/<reducer>.png"
    """
    root_path = Path(root_path)
    manifest = []
    for path in root_path.glob("**/*.png"):
        parts = path.parts
        manifest.append(
            {
                "path": path.relative_to(root_path).as_posix(),
                "model": parts[-4],
                "group": parts[-3],
                "tag": parts[-2],
                "reducer": parts[-1].replace(".png", ""),
            }
        )
    with open(root_path.joinpath("manifest.json"), "w") as f:
        json.dump(manifest, f)
