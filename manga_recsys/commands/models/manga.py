"""Generate recommendations from from manga to manga."""
import json
import warnings
from functools import partial
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


def _generate_rec(
    manga_info,
    method: str,
    cores=8,
    num_recs=20,
    metric="cosine",
    low_memory=False,
    **kwargs,
):
    func = {
        # we assume for w2v and lsi that the cosine distance is used implicitly
        "w2v": generate_manga_tags_word2vec,
        "lsi": generate_manga_tags_tfidf_lsi,
        "network": partial(generate_manga_tags_network, metric=metric),
    }

    manga_tags = func[method](manga_info, vector_col="emb", **kwargs)
    print("done generating embeddings")
    rec_df = generate_recommendations(
        manga_tags,
        "id",
        "emb",
        k=num_recs,
        metric=metric,
        n_jobs=cores,
        low_memory=low_memory,
    )
    print("done generating recommendations")
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

    rec_df = _generate_rec(manga_info, "w2v", num_recs=num_recs, workers=cores)

    recs = explode_recommendations(spark, rec_df)
    recs = map_names_to_recommendations(manga_info, recs).cache()
    recs.printSchema()
    recs.show()

    write_df(
        spark.createDataFrame(rec_df), Path(output) / "embedding", write_json=False
    )
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

    write_df(
        spark.createDataFrame(rec_df), Path(output) / "embedding", write_json=False
    )
    _write_recs(recs, output, cores)


@manga.command()
@click.argument("input-manga-info", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option(
    "--metric",
    type=click.Choice(["cosine", "euclidean"]),
    default="euclidean",
)
@click.option("--deconvolve/--no-deconvolve", default=False)
@click.option("--solve-k", type=int, default=None)
@click.option("--laplacian/--no-laplacian", default=True)
@click.option("--vector-size", type=int, default=256)
@click.option("--num-recs", type=int, default=20)
@click.option("--cores", type=int, default=4)
@click.option("--memory", default="2g")
def tags_network(
    input_manga_info,
    output,
    metric,
    deconvolve,
    laplacian,
    solve_k,
    vector_size,
    num_recs,
    cores,
    memory,
):
    spark = get_spark(cores=cores, memory=memory)
    manga_info = spark.read.parquet(input_manga_info).cache()

    rec_df = _generate_rec(
        manga_info,
        "network",
        num_recs=num_recs,
        deconvolve=deconvolve,
        laplacian=laplacian,
        metric=metric,
        vector_size=vector_size,
        low_memory=True,
        solve_k=solve_k,
    )

    print("Exploding recommendations...")
    recs = explode_recommendations(spark, rec_df)
    recs = map_names_to_recommendations(manga_info, recs).cache()
    recs.printSchema()
    recs.show()

    write_df(
        spark.createDataFrame(rec_df), Path(output) / "embedding", write_json=False
    )
    _write_recs(recs, output, cores)


def _write_plot_method(output_path, reducer, recs, method, primary_tag, n_dims=2):
    class_name = reducer.__class__.__name__
    plot_recommendation_dims(
        recs,
        "emb",
        reducer,
        title=(f"{primary_tag} {method} embedding ({class_name}) (n={recs.shape[0]})"),
        n_dims=n_dims,
    )
    plt.savefig(output_path / f"{class_name}.png")
    plt.close()


@manga.command()
@click.argument("input-manga-info", type=click.Path(exists=True))
@click.argument("input-model-embedding", type=click.Path(exists=True))
@click.argument("method", type=str)
@click.argument("output", type=click.Path())
@click.option("--n-dims", type=int, default=2)
@click.option("--cores", type=int, default=6)
@click.option("--memory", default="6g")
def plot_models(
    input_manga_info,
    input_model_embedding,
    method,
    output,
    n_dims,
    cores,
    memory,
):
    spark = get_spark(cores=cores, memory=memory)
    manga_info = spark.read.parquet(input_manga_info).cache()

    # find all tags for theme and genre
    theme_genres = (
        manga_info.select("id", F.explode("tags").alias("tag"))
        .select("tag.group", "tag.name")
        .distinct()
    ).toPandas()

    rec_df = spark.read.parquet(input_model_embedding).toPandas()
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
                umap.UMAP(n_components=n_dims),
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
