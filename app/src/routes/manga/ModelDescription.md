<div class="description">

| model              | description                                                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| lsi                | latent semantic indexing, low rank approximation of the tag-manga matrix, cosine distance                                                                                |
| word2vec           | word2vec, neural network word embeddings on tags as a bag of words, cosine distance                                                                                      |
| network-cosine     | manga-manga network through tags, graph laplacian, cosine distance (questionable interpretation)                                                                         |
| network-euclidean  | manga-manga network through tags, graph laplacian, euclidean distance ([commute-time distance](https://csustan.csustan.edu/~tom/Clustering/GraphLaplacian-tutorial.pdf)) |
| network-adj-cosine | manga-manga network through tags, adjacency matrix, cosine distance ([structural equivalence](https://faculty.ucr.edu/~hanneman/nettext/C12_Equivalence.html))           |

</div>

<style>
    /* add borders to the table in the description div */
    .description table {
        border: 1px solid black;
        border-collapse: collapse;
    }
    .description th, .description td {
        border: 1px solid black;
    }
</style>
