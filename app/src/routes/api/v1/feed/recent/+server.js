/**
 * This endpoint is the get the most recent manga from the
 * api.mangadex.org/manga endpoint. We do our best to cache the last 500
 * responses every 60 minutes on demand. Our caching logic will check the bucket
 * for a timestamped item which we will use if it exists. We will serve the
 * content as-is, will just come out of the bucket.
 *
 */
import { Storage } from "@google-cloud/storage";
import { error, json } from "@sveltejs/kit";

const fetchMostRecentManga = async (fetch, limit = 100) => {
  let url = `https://api.mangadex.org/manga?&order[updatedAt]=desc&limit=${limit}`;
  let resp = await fetch(url);
  return await resp.json();
};

export async function GET({ fetch }) {
  const limit = 100;
  // first lets check if we have a cached version of the response
  // get a date string YYYY-MM-DDTHH:00 rounded to the current hour
  let date = new Date();
  date.setMinutes(0);
  date.setSeconds(0);
  date.setMilliseconds(0);
  let dateStr = date.toISOString().slice(0, 16);
  let prefix = `api/v1/feed/recent/${dateStr}.json`;
  // get the storage bucket
  const cacheBucket = import.meta.env.VITE_CACHE_BUCKET;
  const storage = new Storage();

  const bucket = storage.bucket(cacheBucket);
  // check if we have a cached version of the response

  let content = null;

  try {
    content = JSON.parse(await bucket.file(prefix).download());
    console.log(`Serving cached content for ${prefix}`);
  } catch (e) {
    // the contents don't exist, so fetch it from mangadex and upload it into
    // the bucket
    let data = await fetchMostRecentManga(fetch, limit);
    await bucket.file(prefix).save(JSON.stringify(data));
    content = data;
    console.log(`Fetched and cached content for ${prefix}`);
  }

  // check that the content is valid
  if (content === null) {
    return error(500, "Unable to fetch content");
  }
  // now serve the content
  return json(content);
}
