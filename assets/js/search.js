/*
 * Fuse.js config for fuzzy client-side search
 */

const default_fuse_options = {
  isCaseSensitive: false,
  findAllMatches: false,
  includeMatches: false,
  includeScore: false,
  useExtendedSearch: false,
  minMatchCharLength: 1,
  shouldSort: true,
  threshold: 0.3,
  location: 0,
  distance: 100,
  keys: ["title", "abstract", "authors"],
};

/*
 * Vue components for rendering the page
 */

const _search_stats_template = `
<div class="uk-grid-match" uk-grid>
  <div class="uk-width-1-2@m">
    <h3>Found {{ n_results }} results</h3>
  </div>
  <div class="uk-width-1-2@m uk-text-right uk-text-small">
    <span class="monospace uk-text-muted">Search finished in {{ qtime }}ms</span>
  </div>
</div>`;

const _search_result_template = `
<div class="search_result">
  <h2 class="uk-h2 uk-text-bold">{{ title }}</h2>
  <div>
    <div><span class="uk-text-bold">Authors:</span> {{ authors }}</div>
    <div><span class="uk-text-bold">Published:</span> {{ published }}</div>
    <div><span class="uk-text-bold">Tags:</span> {{ tags }}</div>
    <p>
      <a v-bind:href="'/entries/' + id">See more</a>
    </p>
  </div>
  <hr>
</div>`;

Vue.component("search-stats", {
  props: ["n_results", "qtime"],
  template: _search_stats_template,
});

Vue.component("search-result", {
  props: ["title", "published", "authors", "tags", "id"],
  template: _search_result_template,
});

function generate_result_component(entry) {
  /* Return a new search-result Vue component based on a search result
   * found using Fuse.js. */
  const el = document.createElement("search-result");

  // Entry title
  el.setAttribute("title", entry.title);
  el.setAttribute("published", get_publication_date(entry));
  el.setAttribute("authors", get_authors(entry));
  el.setAttribute("tags", get_tags(entry));
  el.setAttribute("id", entry.id);

  return el;
}

/*
 * Search filters
 */

function filter_by_tags(tags, entries) {
  // Filter in only entries that have the provided tags
  if (tags.length === 0) {
    return entries;
  }

  return entries.filter((entry) =>
    tags.some((tag) => "tags" in entry && entry.tags.includes(tag))
  );
}

function filter_by_text(text, entries) {
  // Filter in only entries that match a fuzzy text search.
  // When text == "" the default behavior is to filter in every single
  // entry in the compendium.

  if (text.length === 0) {
    return entries;
  }

  const fuse = new Fuse(entries, default_fuse_options);
  const results = fuse.search(text);
  return results.map((res) => res.item);
}

function search(text, tags, entries) {
  // Primary search runner

  // Delete any child elements of the search_results DOM element and add a
  // new <search-stats></search-stats> element in its place.

  const search_stats_container = document.getElementById("search_stats");
  search_stats_container.childNodes.forEach((el) => el.remove());

  const start_time = new Date();
  let results = filter_by_tags(tags, entries);
  results = filter_by_text(text, results);
  const end_time = new Date();

  const search_result_el = document.getElementById("search_results");

  /* Add a new element to the DOM for every search result that was
   * returned. */
  for (let ii = 0; ii < results.length; ++ii) {
    const el = generate_result_component(results[ii]);
    search_result_el.appendChild(el);
  }

  // Add search statistics
  const search_stats = document.createElement("search-stats");
  search_stats.setAttribute("n_results", results.length);
  search_stats.setAttribute("qtime", end_time.getTime() - start_time.getTime());
  search_stats_container.appendChild(search_stats);

  // Display all of the results
  new Vue({
    el: "#search_stats",
  });
  new Vue({
    el: "#search_results",
  });

  return results;
}

/*
 * Script to run on page load
 */

let query = new URLSearchParams(location.search).get("query");
if (query === null) {
  query = "";
} else {
  query = decodeURIComponent(query);
}

let tags = new URLSearchParams(location.search).get("tags");
if (tags === null) {
  tags = [];
} else {
  tags = JSON.parse(decodeURIComponent(tags));
}

search(query, tags, entries);

// Pre-populate the search field with the last query
document.getElementById("id_query").value = query;

// Re-run search whenever something new is put into the search bar
document.getElementById("id_query").onkeyup = function (e) {
  input = document.getElementById("id_query").value;
  console.log(input);

  // Remove all search results that are currently displayed
  document.querySelectorAll(".search_result").forEach((el) => el.remove());

  // Re-run search with new input
  search(input, tags, entries);
};
