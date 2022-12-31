<script>
    import MangaInfoTable from "./MangaInfoTable.svelte";
    import ModelDescription from "../ModelDescription.md";
    import RecommendationGrid from "./RecommendationGrid.svelte";
    import { page } from '$app/stores'
    import { goto } from "$app/navigation";
    import { browser } from '$app/environment';
    export let data;
    let selected_id = $page.url.searchParams.get("id", null);
    $: selected_name = data.manga_info.find(manga => manga.id === selected_id)?.name;

    function mutateQueryParams(id) {
        if (id === null) return;
        let query = new URLSearchParams($page.url.searchParams.toString());
        query.set('id', id);
        history.replaceState({}, '', `${$page.url.pathname}?${query}`);
    }
    $: browser && mutateQueryParams(selected_id);
</script>

# manga explore

This section contains recommendations for manga.
See the [manga](/manga) page for more information.
See the [manga embedding plots](/manga/embedding-plots) page for plots of the manga embedding space.

## descriptions

<ModelDescription />

## available manga

Click on a row to see recommendations for that manga.

<MangaInfoTable data={data.manga_info} bind:selected_id />

{#if selected_id}

## manga recommendations for {selected_name}

<RecommendationGrid {selected_id} />

{/if}
