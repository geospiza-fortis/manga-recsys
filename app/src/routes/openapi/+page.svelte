<script>
  let container;

  function onLoad() {
    Redoc.init("/openapi.yaml", { scrollYOffset: 50 }, container);
  }
</script>

<svelte:head>
  <script
    src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
    on:load={onLoad}
  ></script>
</svelte:head>

<div bind:this={container} />
