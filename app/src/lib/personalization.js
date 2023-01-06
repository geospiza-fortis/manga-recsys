// utilities for saving and loading personalization data via localforage
import localforage from "localforage";
import { writable } from "svelte/store";
import { mean, dot, norm } from "mathjs";

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

async function fetchTagWordVectors() {
  let resp = await fetch("/api/v1/models/manga-tags-word2vec/word2vec.json?server=true");
  let data = await resp.json();
  return new Map(Object.entries(data["emb"]));
}

function computeMeanVector(vectors) {
  return mean(vectors, 0);
}

function computeTagVector(tags, word_vectors) {
  if (tags.length === 0) {
    return [];
  }
  let vectors = tags.map((tag) => word_vectors.get(tag));
  //   console.log(vectors);
  return computeMeanVector(vectors);
}

function computeVectorSimilarity(v1, v2) {
  // similarity using the cosine distance
  let similarity = dot(v1, v2) / (norm(v1) * norm(v2));
  return similarity;
}

export {
  library_edits,
  getLibrary,
  addMangaToLibrary,
  removeMangaFromLibrary,
  fetchTagWordVectors,
  computeMeanVector,
  computeTagVector,
  computeVectorSimilarity
};
