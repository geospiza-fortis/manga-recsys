// utilities for saving and loading personalization data via localforage

import localforage from "localforage";
import { writable } from "svelte/store";

// store for signaling how many times something has been edited
const library_edits = writable(0);

const LIBRARY_KEY = "manga-library";

async function getLibrary() {
  return (await localforage.getItem(LIBRARY_KEY)) || [];
}

async function addMangaToLibrary(id, name, tags) {
  let library = await getLibrary();
  // the library is a list of objects with id, name, and tags
  let ids = library.map((manga) => manga.id);
  if (!ids.includes(id)) {
    library.push({ id, name, tags, added: new Date().toISOString() });
    await localforage.setItem(LIBRARY_KEY, library);
  }
}

async function removeMangaFromLibrary(id) {
  let library = await getLibrary();
  let ids = library.map((manga) => manga.id);
  if (ids.includes(id)) {
    library = library.filter((manga) => manga.id !== id);
    await localforage.setItem(LIBRARY_KEY, library);
  }
}

export { library_edits, getLibrary, addMangaToLibrary, removeMangaFromLibrary };
