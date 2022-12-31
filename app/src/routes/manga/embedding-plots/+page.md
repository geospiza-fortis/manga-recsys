<script>
    import EmbeddingPlots from "./EmbeddingPlots.svelte"
    import ModelDescription from "../ModelDescription.md"
</script>

# embedding plots

This section contains plots of embeddings for manga.
Each plot is a 2D projection of the manga embedding space.
The colors represent the most common tag across the neighbors of the manga.
See the [manga](/manga) page for more information.
See the [manga explore](/manga/explore) page for recommendations.

## descriptions

<ModelDescription />

## options

<EmbeddingPlots />
