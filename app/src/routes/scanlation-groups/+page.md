<script>
  import GroupSummaryTable from "./GroupSummaryTable.svelte";
  import GroupMangaTable from "./GroupMangaTable.svelte";
  import GroupMangaRecommendationTable from "./GroupMangaRecommendationTable.svelte"
  export let data;
  let selected_group_id = null;
</script>

# scanlation groups

A scanlation group is a group of people who translate manga into their own language.

## group summary

Click on a row to see the manga that the group has translated.

<GroupSummaryTable data={data.group_summary} bind:selected_group_id />

{#if selected_group_id}

## manga by group

<GroupMangaTable group_id={selected_group_id} />

## manga recommendations by group

<GroupMangaRecommendationTable group_id={selected_group_id} />

{/if}

## notes

### building the model

We build a collaborative filtering model using the most straightforward possible relationship: making recommendations for a group based on other groups who have translated the same manga.
We use the number of pages translated as our "rating" that a group gives a manga.
We build the model using the [alternating least-squares (ALS)](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.ml.recommendation.ALS.html) algorithm implemented in PySpark.

The recommendations are bad.
There are a few reasons for this:

- The data is sparse. There are many groups and manga, but a small overlap between the two.
- Scanlation groups tend to avoid sniping each other's projects, so there is often only a single group translating a manga. Recommendations, therefore, tend to occur across groups that translate the same manga but in different languages.

We choose group-manga recommendations as our first model because constructing the dataset is easy.
It serves as a proof of concept for building more complex models.
This methodology is how we would build a recommendation system for user-manga relationships if that data were available.
Training the model and making predictions is relatively cheap computationally, taking less than two minutes to run on a 8-cores @ 3.4GHz .
It takes _far_ longer to copy the pre-computed predictions into static hosting due to the abundance of small files.

Models we build in the future will be content-based, which means we will use similarities between descriptions and tags to make recommendations.
The description-based recommendations will rely on title and description data embedded into vector space using techniques like [word2vec](https://arxiv.org/abs/1301.3781) or, more likely, [GPT-2](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) via [HuggingFace](https://huggingface.co/).
For manga tags, we will build a bi-partite network between manga and tags.
We project the manga-tag network into a unimodal manga network and then factorize the resulting adjacency matrix using an algorithm like ALS.
We might compare the tag-based recommendations to alternative methods such as [latent semantic indexing (LSI)](https://en.wikipedia.org/wiki/Latent_semantic_analysis).

### serving the model

We take inspiration for model service from [similar-manga](https://github.com/similar-manga/similar).
This project builds a manga-manga recommendation model using LSI on tags.
They pre-compute recommendations for all manga and serve them as static content from a [GitHub repository](https://github.com/similar-manga/data).

We also host our model as static content in a Google Cloud Storage bucket and provide an API for the group recommendations at the following endpoint:

```
/api/v1/models/group-manga/recommendations/{group_id}.json
```

The API redirects to the static content in the bucket.
Note that the API is subject to change at any time, but like all other content on this site, is made freely available to experiment with.
