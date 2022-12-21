<script>
    import MangaInfoTable from "./MangaInfoTable.svelte";
    import MangaRecommendationTable from "./MangaRecommendationTable.svelte";
    export let data;
    let selected_id = null;
</script>

# manga

This section contains various manga recommendations.

## available manga

<MangaInfoTable data={data.manga_info} bind:selected_id />

{#if selected_id}

## manga recommendations

<MangaRecommendationTable {selected_id} />

{/if}
