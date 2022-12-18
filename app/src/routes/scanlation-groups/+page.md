<script>
  import GroupSummaryTable from "./GroupSummaryTable.svelte";
  import GroupMangaTable from "./GroupMangaTable.svelte";
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

{/if}
