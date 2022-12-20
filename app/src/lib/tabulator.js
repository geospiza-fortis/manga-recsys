import tippy from "tippy.js";
import "tippy.js/dist/tippy.css";
import GroupInfo from "$lib/GroupInfo.svelte";
import MangaInfo from "$lib/MangaInfo.svelte";

function tippyGroupInfo(row, tippyProps = {}) {
  // create a new tippy instance for the row
  let instance = tippy(row.getElement(), tippyProps);
  new GroupInfo({
    // get element from popper instance that has class tippy-content
    target: instance.popper.querySelector(".tippy-content"),
    props: {
      group_id: row.getData().group_id
    }
  });
}

function tippyMangaInfo(row, tippyProps = {}) {
  let instance = tippy(row.getElement(), tippyProps);
  new MangaInfo({
    // get element from popper instance that has class tippy-content
    target: instance.popper.querySelector(".tippy-content"),
    props: {
      manga_id: row.getData().manga_id
    }
  });
}

function destroyTippy(row) {
  let el = row.getElement();
  if (el._tippy) {
    el._tippy.destroy();
  }
}

export { tippyGroupInfo, tippyMangaInfo, destroyTippy };
