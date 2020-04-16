/*
 * Javascript for views of a single entry of the compendium
 */

const entry_id = new URLSearchParams(location.search).get("id");
if ( entry_id === null ) {
  window.location = "/";
}

const entry = entries[entry_id];

new Vue({
  el: "#entry_content",
  delimiters: ["[[", "]]"],
  data: {
    title: entry.title,
    abstract: entry.abstract,
    url: entry.url,
    authors: get_authors(entry),
    published: get_publication_date(entry),
  }
});
