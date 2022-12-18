<script>
  import GroupSummaryTable from "./GroupSummaryTable.svelte";
  export let data;
</script>

# scanlation groups

A scanlation group is a group of people who translate manga into their own language.

<GroupSummaryTable data={data.group_summary} />
