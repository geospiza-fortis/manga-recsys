<script>
    import MangaInfoTable from "./MangaInfoTable.svelte";
    import MangaRecommendationTable from "./MangaRecommendationTable.svelte";
    export let data;
    let selected_id = null;
</script>

# manga explore

This section contains recommendations for manga.
See the [manga](/manga) page for more information.

## available manga

Click on a row to see recommendations for that manga.

<MangaInfoTable data={data.manga_info} bind:selected_id />

{#if selected_id}

## manga recommendations

<MangaRecommendationTable {selected_id} />

{/if}
