<script>
  import TagCounts from "./TagCounts.md";
  let selected_method = 2;
  const methods = ["tsne", "pca", "umap"];
</script>

# manga

Go to the [manga explore](/manga/explore) page to try out the recommendations.
Note that this page may take some time to load.

See the [manga embedding plots](/manga/embedding-plots) page for a visualization of the recommendations through the embedding space.

## notes

### table of contents

### overview

We've reached the point where we can finally build a reasonable model for making content recommendations.
As noted in the [groups notes](/groups), there are two main recommendation models.
The first is collaborative filtering models that rely on implicit user interactions (e.g., favoriting a series).
The second class of models is content-based models that rely on properties of the data (e.g., tags, descriptions, etc.).
User interaction data is not available through the public API.
Instead, we focus on content-based models with the potential for personalization in the future.

We can construct three interesting models with tag data alone.
We treat these as baselines for more complex models.
These all account for the distributional semantics of tags, but in slightly different ways.
The first model is a [latent semantic indexing (LSI)](https://en.wikipedia.org/wiki/Latent_semantic_analysis) model, which uses the singular values of a scaled document-term matrix to project the manga into a low-rank space.
The second builds on the [word2vec](https://en.wikipedia.org/wiki/Word2vec) model, a neural network that learns to represent words in a vector space.
We represent each manga by the average of its tag vectors.
Then we use the cosine similarity between manga vectors to make recommendations.
Again, we recommend the most similar manga based on the cosine similarity of the left singular vector found by the singular value decomposition (SVD).
The final model makes recommendations based on neighbors in the manga-tag bipartite network.
We count all the possible paths between two manga through shared tags to create a manga-manga network.
We then recommend the most similar manga based on the number of shared tags.
To ensure consistency among models, we embed the network onto a manifold using UMAP with justification on both the adjacency and laplacian matrices.

One immediate extension we can make to these models is to use frequent itemsets as words instead of just tags.
In other words, we consider all bi-grams, tri-grams, etc. of tags as words.
Another extension is to incorporate the description of each manga into the vector-space models using transformer models.
One such method is to take the [BERT](https://huggingface.co/docs/transformers/model_doc/bert) or [GPT-Neo](https://huggingface.co/EleutherAI/gpt-neo-1.3B) embeddings of the description and append them to the tag embeddings.
Finally, we can consider adding in popularity or rating statistics to the models.
These statistics would likely act as a bias term to re-rank recommendations, and would likely require hyper-parameter tuning to be effective.

### embedding overview

We will talk about embeddings throughout the rest of this page.
An embedding is a low-dimensional geometric representation of a high-dimensional space which preserves the relative distances between points.
These embeddings are metric spaces defined by their embedding e.g. the Euclidean distance or cosine distance.
The Euclidean distance is the most common metric, and is what you would use to measure the distance between two points in a 2D or 3D space.
It is also known as the $L^2$ norm, and is defined as:

$$
d(p, q) = \sqrt{\sum_{i=1}^n (p_i - q_i)^2} = \|p - q\|
$$

We might instead be interested in the angle between two points.
This is common with very sparse vectors, where each column of the vector might represent a (normalized) count feature.
The cosine distance would then reflect the number of common features between two vectors as an angle.
The cosine distance is defined as the dot product between two points divided by the product of their norms:

$$
d(p, q)
  = 1 - \frac{p \cdot q}{\|p\| \|q\|}
  = \frac{\sum{p_i q_i}}{\sqrt{\sum{p_i^2}} \sqrt{\sum{q_i^2}}}
$$

We build embeddings because the low-dimensional vector space is much easier to work with and visualize.
Our recommendation models can simply compare the distance between two points in the embedding space to determine how similar they are.
We make use of efficient algorithms to find the nearest neighbors to a given point, and can even use the embedding to visualize the data.
One example that we go into depth later is embedding a network (or graph) into a smaller vector.
There are 64k manga in the dataset; when represented as an adjacency matrix of (64464, 64464) elements of 32-bit floats it takes up 15.5 GiB of memory.
We can preserve distances by embedding this into a vector of (64464, 256) elements, which takes up 62 MiB of memory.
This is several orders of magnitude smaller, while preserving nearest neighbor relationships from the original space.

#### distribution of tags

Our embeddings will focus on tag data.
These are available for all manga, and is the primary way that users might search for manga.
All of the embeddings exploit distributional semantics of tags i.e. the meaning of a tag is determined by the tags that appear near it, and the meaning of a manga is determined by the tags that appear on it.

Here we show a histogram often a given tag appears in the dataset.

<img alt="tag count histogram" src="/manga-info/20221221-tag-count-histogram.png">

The histogram represents the distribution of tag counts.
We note that a few tags appear very frequently, while most tags appear very infrequently.
If we take the log of the tag counts, we can see that the distribution looks more like a normal distribution.
The raw aggregated data can be found in the following table:

<TagCounts />

We also take a look at how many tags each manga has.

<img alt="tag count per manga histogram" src="/manga-info/20221221-tag-count-per-manga-histogram.png">

Like before, we note that the distribution is heavy-tailed, and looks more normal when we take the log of the counts.

### latent semantic indexing (LSI)

[Latent semantic indexing (LSI)](https://nlp.stanford.edu/IR-book/html/htmledition/latent-semantic-indexing-1.html) a traditional information retrieval technique used to find similar documents based on the frequency of words in the documents.
It indexes into a latent (low-rank, probabilistic) space formed by the [singular value decomposition (SVD)](https://en.wikipedia.org/wiki/Singular_value_decomposition) of a scaled document-term matrix.
The LSI recommendation model is theoretically sound, and makes a good baseline for comparison.

#### document-term matrix and tf-idf

We generate a term-document matrix $C$ where each row is a manga, and each column is a tag count.
We normalize the tag counts by [term frequency-inverse document frequency (tf-idf)](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) to account for the fact that some tags appear more frequently than others.
This helps the relevance of tags that occur rarely, but form a coherent cluster in the data.
The term frequency is the relative frequency of a term $t$ in a document $d$:

$$
tf(t, d) = \frac{f_{t, d}}{\sum_{t' \in d} f_{t', d}}
$$

The inverse document frequency is a measure of how much information a term provides.
If a term appears in more documents, then it is less informative and is therefore down-weighted.

$$
idf(t, D) = \log \frac{|D|}{|\{d \in D : t \in d\}|}
$$

Together, this gives us the tf-idf score:

$$
tfidf(t, d, D) = tf(t, d) \cdot idf(t, D)
$$

This is a common weighting scheme that is used in information retrieval systems like [Lucene](https://lucene.apache.org/) and [Elasticsearch](https://www.elastic.co/).

#### indexing and querying with SVD

We could use the tf-idf vector representation of terms to find similar manga.
However, this representation doesn't take into account the relationships between terms.
We can use the SVD to find a lower-dimensional representation (latent space) of the data that preserves the relationships between terms.
This is a type of soft-clustering, where each manga is now represented as a weighted sum of membership in various tag clusters.

SVD decomposes a matrix $M$ into a left singular vector, a diagonal matrix of singular values, and a right singular vector.

$$
M = U \Sigma V^T
$$

This is a linear transformation that finds a projection that preserves the largest variance in the data.
To make a query into the latent space, we first transform a set of tags into a tf-idf query vector $q$.
We then map this query vector into the latent space by multiplying it by the left singular vector $U$.

$$
\vec{q_k} = \Sigma_k^{-1} U_k^T \vec{q}
$$

Then, we just find the nearest neighbors by finding the closest points by cosine distance.

### word2vec embeddings

The word2vec model is a neural network that learns to represent words in a vector space.
We use the word2vec model to represent tags in a vector space.
We represent each manga as an average of its tag vectors, and use the cosine similarity between manga vectors to make recommendations.

There are two methods for training word2vec models: continuous bag of words (CBOW) and skip-gram.
The skip-gram model is order-sensitive, and learns the probability of a word given its context.
This is not ideal for our use case, because tags are not ordered.
The PySpark implementation of word2vec relies on the skip-gram model, so we use [`gensim` to train a CBOW word2vec model](https://radimrehurek.com/gensim/models/word2vec.html) on the tag data.
The set of tags on a manga is treated as a sentence in the model.
We set the embedding size to a vector of size 16, which is justified by the [square root of the number of tags rounded to the nearest power of 2](https://stackoverflow.com/questions/66267818/minimum-number-of-words-in-the-vocabulary-for-word2vec-models).
We visualize the tag embeddings using [UMAP](https://umap-learn.readthedocs.io/en/latest/).

<img alt="tag word2vec {methods[selected_method]}" src="/manga-info/20221221-tag-word2vec-{methods[selected_method]}.png">

<div class="selection">
<b>visualization method: </b>
<!-- a radio selector between t-sne, PCA, and umap -->
{#each methods as method, i}
  <label>
    <input
        type="radio"
        checked={i === selected_method}
        on:change={() => selected_method = i} />
    {method}
  </label>
{/each}
</div>

The dimensions are meaningless, but the relative distances between tags are meaningful.
We see meaningful clusters of tags, such as "isekai", "villianess", "reincarnation", and "fantasy".

### network embeddings

We can also look at recommendations through a network representation.

#### construction

#### removing indirect effects

We explore two techniques to remove indirect effects from the network, as described by [this nature article](https://www.nature.com/articles/nbt.2657) ([scihub link](https://sci-hub.se/10.1038/nbt.2657)).
These techniques were designed for a gene regulatory network inference task, but can be applied to our network.
Our network construction is purely indirect, since it relies on paths through tags to connect manga.
As we introduce derivative tags representing pairs and triplets of tags, we introduce even more indirect effects.
Therefore, it might be interesting to determine the effects of removing indirect effects from the network.

##### network deconvolution

[Network deconvolution](https://www.nature.com/articles/nbt.2635) is a general method for removing indirect effects from a network.
We use the following closed form equation to represent the transitive closure over the network.

$$
G_{\text{obs}} = G_{\text{dir}} (I - G_{\text{dir}})^{-1}
$$

The network deconvolution is represented as follows:

$$
G_{\text{dir}} = G_{\text{obs}} (I + G_{\text{obs}})^{-1}
$$

Concretely, we perform the following operation, which rescales the eigenvalues found through the eigen decomposition of the adjacency matrix.

```python
def network_deconvolution(G):
    """Deconvolve a network matrix using the eigen decomposition.
    https://www.nature.com/articles/nbt.2635
    """
    # eigen decomposition
    lam, v = scipy.linalg.eigh(G)
    # rescale the eigenvalues
    # also add small value to avoid division by zero
    lam_dir = lam/(1+lam)
    # reconstruct the deconvolved matrix
    G_deconv = v @ np.diag(lam_dir) @ v.T

    np.fill_diagonal(G_deconv, 0)
    # keep only positive values, in-place
    np.maximum(G_deconv, 0, out=G_deconv)
    # rescale between 0 and 1, in-place
    G_deconv /= np.max(G_deconv)

    # NOTE: check reconstruction
    # G_deconv = v @ np.diag(lam) @ v.T
    return G_deconv
```

We find that finding the naive implementation using scipy's eigen decomposition of the adjacency matrix is _very_ slow.
We left the deconvolution running for 8 hours and aborted the program due to the intractability.
We note that there is an alternative reparameterization that uses gradient descent, but this is out of scale for this experiment.

It would be useful to know if we can use the SVD of the adjacency matrix to approximate the deconvolution.
The eigen decomposition has time complexity $O(n^3)$, while the truncated SVD has time complexity $O(kn^2)$, where $k$ is the number of singular values that we keep.
Our matrix is fairly dense (50%), so even if we only kept non-zero eigenvalues, we would benefit from the time complexity of the truncated SVD.
However, we're unsure of the effects of rescaling the singular values instead of the true eigenvalues of the matrix.

##### global silencing of indirect correlations

[Global silencing of indirect correlations](https://www.nature.com/articles/nbt.2601) is another method for removing indirect effects from a network.
The closed form of the silenced network where indirect effects are removed is given by:

$$
S = (G - I + \mathcal{D}((G-I)G))G^{-1}
$$

where $\mathcal{D}$ is an operator that sets diagonal elements to zero.

This is a closed form solution that can be computed relatively quickly given the inverse of the adjacency matrix.
We can use the psuedo-inverse of the adjacency matrix by computing the truncated SVD of the adjacency matrix.

#### embedding

The spectral embedding model is a method for dimensionality reduction based on network connectivity.
We use this to reduce the dimensionality of the network, and to ensure that modeling backends are represented using the same API.

### approximate nearest neighbors

We make recommendations by finding the nearest neighbors of each manga in vector space.

#### nn-descent

[NN-Descent](https://www.cs.princeton.edu/cass/papers/www11.pdf) is a fast approximate nearest neighbor algorithm that uses a graph to find the nearest neighbors of a point.
[`pynndescent`](https://pynndescent.readthedocs.io/en/latest/) is an implementation of the algorithm that is suitable for our purposes.
It supports a variety of distance metrics including cosine distances.

#### locality-sensitive hashing

[Locality-sensitive hashing (LSH)](https://en.wikipedia.org/wiki/Locality-sensitive_hashing) is a fast approximate nearest neighbor algorithm that uses a hash function to find the nearest neighbors of a point.
LSH is a potential alternative to nn-descent that's implemented [directly in PySpark](https://spark.apache.org/docs/latest/ml-features.html#locality-sensitive-hashing).
However, we are limited to MinHash and Random Projection methods, which only work for Jaccard and Euclidean distances.

### evaluation

#### jaccard index

The [Jaccard index](https://en.wikipedia.org/wiki/Jaccard_index) is a measure of similarity between two sets.
It is defined as follows:

$$
J(A, B) = \frac{|A \cap B|}{|A \cup B|}
$$

#### null model

The null model is a baseline for evaluating the performance of a recommendation model.
We create a null model by selecting random recommendations for each manga.
The null model takes in no information about the data.
We then compare the performance through a [statistical significance test](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-019-3118-5).
We consider using the [jaccard R package](https://github.com/ncchung/jaccard) to perform the tests.

### personalization

Personalization is one future direction we could take in developing a recommendation model.
We might achieve this by incorporating a weighted average of a query vector with a user's personalization vector.
For example, a user is known to like manga X, Y, and Z.
We can represent this preference using the weighted average of tag vectors to form a personalization vector.
Then when we query the database for similar manga to a query manga, we also average in user preferences.

### changelog

- 2022-12-20: Initial version of the manga recommendations page.
- 2022-12-27: Added reference to network analysis, section on embedding plots
- 2022-12-29: Filling in more of the details for embeddings and some models.

<style>
img {
  display: block;
  margin-left: auto;
  margin-right: auto;
  max-width: 100%;
}
.selection {
  display: flex;
  flex-direction: row;
  justify-content: center;
}
</style>
