<script>
    import MangaInfoTable from "./MangaInfoTable.svelte";
    import ModelDescription from "../ModelDescription.md";
    import RecommendationGrid from "./RecommendationGrid.svelte";
    export let data;
    let selected_id = null;

</script>

# manga explore

This section contains recommendations for manga.
See the [manga](/manga) page for more information.
See the [manga embedding plots](/manga/embedding-plots) page for plots of the manga embedding space.

## available manga

Click on a row to see recommendations for that manga.

<MangaInfoTable data={data.manga_info} bind:selected_id />

## manga recommendations

<RecommendationGrid {selected_id} />

## descriptions

<ModelDescription />
