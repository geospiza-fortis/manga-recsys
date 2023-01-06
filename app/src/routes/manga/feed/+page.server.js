function preprocess(data) {
  return data.map((row) => {
    return {
      updatedAt: row.attributes.updatedAt,
      id: row.id,
      originalLanguage: row.attributes.originalLanguage,
      name: row.attributes.title.en,
      latestUploadedChapter: row.attributes.latestUploadedChapter,
      description: row.attributes.description.en,
      tags: row.attributes.tags.map((tag) => ({
        name: tag.attributes.name.en,
        id: tag.attributes.group
      })),
      availableTranslatedLanguages: row.attributes.availableTranslatedLanguages
    };
  });
}

export async function load({ fetch }) {
  let resp = await fetch(`/api/v1/feed/recent`);
  let data = await resp.json();
  return {
    feed_data: preprocess(data.data)
  };
}
