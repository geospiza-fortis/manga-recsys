# manga

Go to the [manga explore](/manga/explore) page to try out the recommendations.
Note that this page may take some time to load.

## notes

We've reached the point where we can finally build a reasonable model for making content recommendations.
As noted before in the [groups notes](/groups), there are two main recommendation models.
The first are collaborative filtering models that rely on implicit user interactions (e.g. favoriting a series).
The second class of models are content-based models that rely on properties of the data (e.g. tags, descriptions, etc.).
User interaction data is not available through the public API, so instead we focus on content-based models, with the potential for personalization in the future.

There are three interesting models that can be constructed with tag data alone, and can be used as a baseline for more complex models.
These all take into account the distributional semantics of tags, but in slightly different ways.
The first builds on the [word2vec](https://en.wikipedia.org/wiki/Word2vec) model, which is a neural network that learns to represent words in a vector space.
We represent each manga by the average of its tag vectors, and then use the cosine similarity between manga vectors to make recommendations.
The second model is a [latent semantic indexing (LSI)](https://en.wikipedia.org/wiki/Latent_semantic_analysis) model, which uses the singular values of a scaled document-term matrix composed of tag counts to project the tags into a low rank space that captures distances between sets of tags.
Again, we recommend the most similar manga based on the cosine similarity of the left singular vector found by the singular value decomposition (SVD).
The third and final model is based on a manga-tag bipartite network.
We count all the possible paths between two manga by folding the network into a manga-manga network.
We then factorize the weighted adjacency matrix representation of the network using a non-negative matrix factorization, like alternating least squares (ALS) seen in the group collaborative filtering model.

### word2vec and embeddings

The word2vec model is a neural network that learns to represent words in a vector space.
We use `gensim` to train a continuous bag of words (CBOW) model on the tag data.

<img alt="tag count histogram" src="/manga-info/20221221-tag-count-histogram.png">

This plot shows how often tag appears in the dataset.

<img alt="tag count per manga histogram" src="/manga-info/20221221-tag-count-per-manga-histogram.png">

This plot shows the distribution of tags that appear on each manga.

<img alt="tag word2vec umap" src="/manga-info/20221221-tag-word2vec-umap.png">

After generating a 16-dimensional word2vec embedding, treating tags on each manga as a sentence, we visualize the tag embeddings using UMAP.
The dimensions are meaningless, but the relative distances between tags are meaningful.

### approximate nearest neighbors

We make recommendations by finding the nearest neighbors of each manga in vector space.

#### nn-descent

NN-descent is a fast approximate nearest neighbor algorithm that uses a graph to find the nearest neighbors of a point.
`pynndescent` is an implementation of the algorithm that is suitable for our purposes.

#### locality sensitive hashing

Locality sensitive hashing (LSH) is a fast approximate nearest neighbor algorithm that uses a hash function to find the nearest neighbors of a point.
This is a potential alternative to nn-descent that's implemented directly in PySpark, but there are significant trade-offs that need to be considered.
We are limited to MinHash and Random Projection methods, which only work for Jaccard and Euclidean distances, respectively.

### evaluation

#### jaccard index

The Jaccard index is a measure of similarity between two sets.
It is defined as follows:

$$
J(A, B) = \frac{|A \cap B|}{|A \cup B|}
$$

#### null model

The null model is a baseline for evaluating the performance of a recommendation model.
We create a null model by selecting a random set of recommendations for each manga.
The null model takes in no information about the data.
We then compare the performance through a statistical significance test.

### personalization

Personalization is one future direction, which could be achieved incorporating a weighted average of a query vector (e.g. tag vector representing a manga) with a user's personalization vector (e.g. tag vector representing tags that the user likes).

### changelog

- 2021-12-20: Initial version of the manga recommendations page.

<style>
img {
  display: block;
  margin-left: auto;
  margin-right: auto;
  max-width: 100%;
}
</style>
