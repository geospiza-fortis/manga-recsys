<script>
    import MangaInfoTable from "./MangaInfoTable.svelte";
    import MangaRecommendationTable from "./MangaRecommendationTable.svelte";
    export let data;
    let selected_id = null;
    const models = ["manga-tags-word2vec", "manga-tags-lsi"]
</script>

# manga explore

This section contains recommendations for manga.
See the [manga](/manga) page for more information.

## available manga

Click on a row to see recommendations for that manga.

<MangaInfoTable data={data.manga_info} bind:selected_id />

{#if selected_id}

## manga recommendations

<div class="rec-container">

{#each models as model}

<div class="rec-row">

### {model}

<MangaRecommendationTable {selected_id} {model} />

</div>

{/each}

</div>

{/if}

<style>
    /** wrap the rec container so there are two columns, but one column when on mobile */
    .rec-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
    }
    /** make the rec row take up half the width */
    .rec-row {
        width: 50%;
    }
    /** make the rec row take up the full width on mobile */
    @media only screen and (max-width: 600px) {
        .rec-row {
            width: 100%;
        }
    }
</style>
