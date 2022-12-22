<script>
    let selected_method = 2;
    const methods = ["tsne", "pca", "umap"];
</script>

# manga

Go to the [manga explore](/manga/explore) page to try out the recommendations.
Note that this page may take some time to load.

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
The first builds on the [word2vec](https://en.wikipedia.org/wiki/Word2vec) model, a neural network that learns to represent words in a vector space.
We represent each manga by the average of its tag vectors.
Then we use the cosine similarity between manga vectors to make recommendations.
The second model is a [latent semantic indexing (LSI)](https://en.wikipedia.org/wiki/Latent_semantic_analysis) model, which uses the singular values of a scaled document-term matrix to project the manga into a low-rank space.
Again, we recommend the most similar manga based on the cosine similarity of the left singular vector found by the singular value decomposition (SVD).
The final model performs soft-clustering on a manga-tag bipartite network.
We count all the possible paths between two manga through shared tags to create a manga-manga network.
We then factorize the weighted adjacency matrix and find the nearest neighbors to each manga.

One immediate extension we can make to these models is to use frequent itemsets as words instead of just tags.
In other words, we consider all bi-grams, tri-grams, etc. of tags as words.
Another extension is to incorporate the description of each manga into the vector-space models using transformer models.
One such method is to take the [BERT](https://huggingface.co/docs/transformers/model_doc/bert) or [GPT-Neo](https://huggingface.co/EleutherAI/gpt-neo-1.3B) embeddings of the description and append them to the tag embeddings.
Finally, we can consider adding in popularity or rating statistics to the models.
These statistics would likely act as a bias term to re-rank recommendations, and would likely require hyper-parameter tuning to be effective.

### word2vec and embeddings

The word2vec model is a neural network that learns to represent words in a vector space.
We use `gensim` to train a continuous bag of words (CBOW) model on the tag data.

<img alt="tag count histogram" src="/manga-info/20221221-tag-count-histogram.png">

This plot shows how often a tag appears in the dataset.

<img alt="tag count per manga histogram" src="/manga-info/20221221-tag-count-per-manga-histogram.png">

This plot shows the distribution of tags that appear in each manga.

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

After generating a 16-dimensional word2vec embedding, treating tags on each manga as a sentence, we visualize the tag embeddings using [UMAP](https://umap-learn.readthedocs.io/en/latest/).
The dimensions are meaningless, but the relative distances between tags are meaningful.

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

- 2021-12-20: Initial version of the manga recommendations page.

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
